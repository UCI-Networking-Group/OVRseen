#!/usr/bin/env python3

import subprocess
import os
from pathlib import Path
import sys

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

assert sys.version_info >= (3, 7)  # need py 3.7+ for ordered dict


# make data type names shorter
def rename_dtype(s):
    s = s.replace("information", "info")
    s = s.replace("geographical location", "geolocation")
    return s


def rename_entity(s):
    if s == 'we':
        return '1st party'
    else:
        return s


DTYPE_CATEGORY_MAP = {
    'session info': 'Fingerprint',
    'cookie': 'Fingerprint',
    'hardware info': 'Fingerprint',
    'language': 'Fingerprint',
    'app name': 'Fingerprint',
    'sdk version': 'Fingerprint',
    'system version': 'Fingerprint',
    'build version': 'Fingerprint',
    'flags': 'Fingerprint',
    'usage time': 'Fingerprint',

    'android id': 'PII',
    'device id': 'PII',
    'serial number': 'PII',

    'email address': 'PII',
    'person name': 'PII',
    'user id': 'PII',
    'geolocation': 'PII',

    'vr field of view': 'VR Sensory Data',
    'vr movement': 'VR Sensory Data',
    'vr play area': 'VR Sensory Data',
    'vr pupillary distance': 'VR Sensory Data',
}

DTYPE_CATEGORY_ORDER = ['PII', 'Fingerprint', 'VR Sensory Data']
# or by # of apps: ['Fingerprint', 'PII', 'VR Sensory Data']

CONSISTENCY_MAP = {
    'clear': True,
    'vague': True,
    'omitted': False,
    'incorrect': False,
    'ambiguous': False,
}


def setup_dtype_axis(axis):
    for tick in axis.get_major_ticks():
        if tick.label.get_text().startswith('('):
            tick.label.set_weight("bold")
            tick.tick1line.set_visible(False)


def draw_heatmaps(df):
    # order of data types
    dtype_app_counts = df.groupby(['flowData'])['packageName'].nunique()

    # order of entities
    ent_app_counts = df.groupby(['flowEntity'])['packageName'].nunique().sort_values(kind='mergesort')
    ent_app_counts['facebook'] = ent_app_counts.pop('facebook')
    ent_app_counts['oculus'] = ent_app_counts.pop('oculus')
    ent_app_counts['1st party'] = ent_app_counts.pop('1st party')
    ent_app_counts = ent_app_counts.iloc[::-1]

    # build heatmaps
    combined_hm = None
    for idx, disclosure_type in enumerate(CONSISTENCY_MAP.keys()):
        subdf = df[df.consistencyResult == disclosure_type]
        heatmap = subdf.pivot_table(index='flowData', columns='flowEntity', values='packageName', aggfunc='nunique')

        valid_ents = []
        for e, ct in ent_app_counts.items():
            if e in heatmap.columns and ct > 1 and e != 'unknown entity':
                valid_ents.append(e)

        # add aggregated columns for big heatmaps
        if disclosure_type in ['omitted', 'vague']:
            idx_platform = subdf.flowEntity.isin(['oculus', 'facebook'])
            idx_other3 = ~subdf.flowEntity.isin(['oculus', 'facebook', 'unity', '1st party'])

            agg_platform = subdf[idx_platform].groupby(['flowData'])['packageName'].nunique().rename('(platform)')
            agg_other3 = subdf[idx_other3].groupby(['flowData'])['packageName'].nunique().rename('(other 3rd parties)')
            heatmap = pd.concat([heatmap, agg_platform, agg_other3], axis=1)

            valid_ents.insert(valid_ents.index('1st party') + 1, "(platform)")
            valid_ents.insert(valid_ents.index('unity') + 1, "(other 3rd parties)")

        heatmap = heatmap[valid_ents]

        if combined_hm is None:
            group_pos = [(0.0, disclosure_type)]
            combined_hm = heatmap
        else:
            combined_hm[" " * idx] = np.nan
            group_pos.append((combined_hm.shape[1] - 0.5, disclosure_type))
            combined_hm = pd.concat([combined_hm, heatmap], axis=1)

    assert combined_hm is not None
    group_pos.append((combined_hm.shape[1] + 1, ''))

    fontsize = 'medium'

    # categorize data types
    y_ticks = []
    for cat in DTYPE_CATEGORY_ORDER:
        cat_cols = [k for k, v in DTYPE_CATEGORY_MAP.items() if v == cat]
        cat_cols.sort(key=lambda x: (-dtype_app_counts[x], x))
        dis_label = r"(%s)" % cat
        y_ticks.append(dis_label)
        y_ticks.extend(cat_cols)

    combined_hm = combined_hm.reindex(y_ticks)

    # draw heatmaps
    plt.figure(figsize=(10, 6.0))
    ax = sns.heatmap(
            combined_hm,
            linewidths=0.2, square=True,
            vmin=0.0, vmax=round(combined_hm.max().max() + 4.99, -1),
            annot=True, annot_kws={'size': "small"},
            cmap='YlOrRd', cbar_kws={'shrink': 0.8, 'aspect': 50, 'pad': 0.02})

    # colorbar style
    colorbar = ax.collections[0].colorbar
    colorbar.ax.tick_params(labelsize=fontsize)
    colorbar.ax.set_ylabel('Number of Data Flows', size=fontsize)

    # heatmap title
    for (p1, label), (p2, _) in zip(group_pos[:-1], group_pos[1:]):
        ax.annotate(label, ((p1 + p2) / 2, 0.3), ha='center', va='bottom', weight="bold", color="grey", annotation_clip=False)
        if p1 >= 1:
            ax.axvline(x=p1, lw=0.75, color="lightgrey")

    ax.plot([-0.2, 0, 15, 15.2], [-0.6, -1.1, -1.1, -0.6], 'k', lw=0.8, clip_on=False, zorder=-1)
    t = ax.annotate('consistent', (7.5, -0.8), ha='center', weight="bold", annotation_clip=False, zorder=-0.5)
    t.set_bbox(dict(facecolor='white', edgecolor='white'))

    ax.plot([15.8, 16, 40.5, 40.7], [-0.6, -1.1, -1.1, -0.6], 'k', lw=0.8, clip_on=False, zorder=-1)
    t = ax.annotate('inconsistent', (28, -0.8), ha='center', weight="bold", annotation_clip=False, zorder=-0.5)
    t.set_bbox(dict(facecolor='white', edgecolor='white'))

    # border
    for _, spine in ax.spines.items():
        spine.set_visible(True)

    left, right = ax.get_xlim()
    down, up = ax.get_ylim()
    ax.set_xlim([left - 0.5, right + 0.5])
    ax.set_ylim([down + 0.5, up + 0.5])

    # Y-tick style (data types)
    setup_dtype_axis(ax.yaxis)
    for tick in ax.yaxis.get_major_ticks():
        if tick.label.get_text().startswith('('):
            ax.axhline(y=tick.get_loc(), lw=0.75, color="lightgrey")

    # X-tick style (entities)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right", size=fontsize)
    for tick in ax.xaxis.get_major_ticks():
        if tick.label.get_text() in ['other 3rd parties', 'platform']:
            tick.label.set_weight('semibold')

        if tick.label.get_text().startswith(" "):
            tick.tick1line.set_visible(False)

    # XY-label style
    ax.set_xlabel('Entity', size=fontsize, va="bottom")
    ax.set_ylabel('Data Type', size=fontsize, va="top")


def agg_consistency(e):
    s = int(e.consistency.sum())
    if s == e.shape[0]:
        return 'Consistent'
    elif s == 0:
        return 'Inconsistent'
    else:
        return 'Partial'


def draw_dtype_barplot(df):
    agg = df.groupby(['consistencyResult', 'flowData']).size().unstack().fillna(0).T[CONSISTENCY_MAP.keys()]
    colors = ['#083763', '#45818e', '#a51d01', '#e99a99', '#ffe59a']

    sorted_cols = []
    for category in DTYPE_CATEGORY_ORDER[::-1]:
        cat_cols = [k for k, v in DTYPE_CATEGORY_MAP.items() if v == category]
        cat_cols.sort(key=lambda x: agg.loc[x].sum())
        sorted_cols.extend(cat_cols)
        sorted_cols.append(f'({category})')

    agg = agg.reindex(sorted_cols)

    ax = agg.plot.barh(stacked=True, color=colors, figsize=(4, 4))
    setup_dtype_axis(ax.yaxis)
    ax.set_ylabel('Data Type', va='top')
    ax.set_xlabel('Number of Data Flows')
    ax.grid(axis='x')
    ax.legend(loc='lower right', labelspacing=0.1)


def draw_entity_barplot(df):
    agg = df.groupby(['consistencyResult', 'flowEntity']).size().unstack().fillna(0).T[CONSISTENCY_MAP.keys()]
    colors = ['#083763', '#45818e', '#a51d01', '#e99a99', '#ffe59a']

    ent_app_counts = df.groupby(['flowEntity'])['packageName'].nunique().sort_values(kind='mergesort')
    selected_parties = ent_app_counts[ent_app_counts > 1].drop('unknown entity').index
    figsize = (4, 2.6)

    sorted_cols = agg.sum(1)[selected_parties].sort_values(ascending=True, kind="mergesort").index.tolist()
    sorted_cols.remove('1st party')
    sorted_cols.append('1st party')
    agg = agg.reindex(sorted_cols)

    ax = agg.plot.barh(stacked=True, color=colors, figsize=figsize)
    ax.set_xlabel('Number of Data Flows')
    ax.set_ylabel('Entity', va="top")
    ax.grid(axis='x')
    ax.legend(loc='lower right', labelspacing=0.1)


def draw_2cmp_barplot(df1, df2):
    disclosre_types = list(CONSISTENCY_MAP.keys())
    colors = ['#083763', '#45818e', '#a51d01', '#e99a99', '#ffe59a']
    groups = {
        '1st party': lambda r: r == '1st party',
        'oculus': lambda r: r.isin(['oculus', 'facebook']),
        'unity': lambda r: r == 'unity',
    }

    all_bars = []

    for df in df2, df1:
        heatmap = None
        for group_name, filter_func in reversed(groups.items()):
            subdf = df[filter_func(df.flowEntity)]

            agg = subdf.groupby(['consistencyResult']).size().fillna(0).rename(group_name)
            heatmap = pd.concat([heatmap, agg], axis=1)

        all_agg = heatmap.reindex(disclosre_types).fillna(0).T
        for prev_k, k in zip(disclosre_types[:-1], disclosre_types[1:]):
            all_agg[k] += all_agg[prev_k]

        all_bars.append(all_agg)

    _, ax = plt.subplots(figsize=(4, 2.2))
    overlay_data = None

    for dis_type, color_name in zip(disclosre_types[::-1], colors[::-1]):
        data = None
        for j, hm in enumerate(all_bars):
            data = pd.concat([data, hm[dis_type].rename(dis_type + " " * j)], axis=1)

        data.plot.barh(ax=ax, color=[color_name, color_name])
        if overlay_data is None:
            overlay_data = data

    overlay_data.iloc[:, 0] = 0
    overlay_data.columns = ['previous results', '']
    overlay_data.plot.barh(ax=ax, color='none', alpha=0.40, hatch='////', edgecolor="white", lw=0.0)

    for tick in ax.yaxis.get_major_ticks():
        ax.axhline(y=tick.get_loc(), lw=2, color="white", zorder=1)
    ax.set_xlabel('Number of Data Flows')
    ax.set_ylabel('Entity')

    handles, labels = [], []
    for handle, label in zip(*ax.get_legend_handles_labels()):
        if not label.endswith(" "):
            if label == 'previous results':
                handle = (matplotlib.patches.Patch(color='lightgrey', lw=0.0), handle)
            handles.insert(0, handle)
            labels.insert(0, label)

    ax.grid(axis='x')
    ax.legend(handles, labels, labelspacing=0.1, loc="upper right")


def main():
    DATA_ROOT = Path(sys.argv[1])
    try:
        DATA_ROOT_CMP = Path(sys.argv[2])
    except IndexError:
        DATA_ROOT_CMP = None

    os.makedirs(DATA_ROOT / 'plots', exist_ok=True)

    df = pd.read_csv(DATA_ROOT / 'policheck_results.csv', na_filter=False)
    df["flowEntity"] = df.flowEntity.apply(rename_entity)
    df["flowData"] = df.flowData.apply(rename_dtype)
    df["consistency"] = df.consistencyResult.apply(CONSISTENCY_MAP.__getitem__)

    matplotlib.use('Agg')
    matplotlib.rc('font', family='DejaVu Sans', stretch="condensed")

    # HEATMAPS
    draw_heatmaps(df)
    plt.tight_layout()
    plt.savefig(DATA_ROOT / 'plots' / 'heatmap_all.pdf', bbox_inches='tight')

    # BARPLOTS (policheck flow)
    draw_dtype_barplot(df)
    plt.tight_layout()
    plt.savefig(DATA_ROOT / 'plots' / 'bar_dtype_5types.pdf')

    draw_entity_barplot(df)
    plt.tight_layout()
    plt.savefig(DATA_ROOT / 'plots' / 'bar_entity_5types.pdf')

    # BARPLOTS (compare)
    if DATA_ROOT_CMP:
        df_cmp = pd.read_csv(DATA_ROOT_CMP / 'policheck_results.csv', na_filter=False)
        df_cmp["flowEntity"] = df_cmp.flowEntity.apply(rename_entity)
        df_cmp["flowData"] = df_cmp.flowData.apply(rename_dtype)
        df_cmp["consistency"] = df_cmp.consistencyResult.apply(CONSISTENCY_MAP.__getitem__)

        draw_2cmp_barplot(df, df_cmp)
        plt.tight_layout()
        plt.savefig(DATA_ROOT / 'plots' / 'bar_entity_cmp.pdf')


if __name__ == "__main__":
    main()
