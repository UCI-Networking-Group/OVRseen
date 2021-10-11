#!/usr/bin/python
import argparse, pandas as pd, sys
import os
import logging
from pandasql import sqldf
pysqldf = lambda q: sqldf(q, globals())

sys.path.append('../../../privacy_policy/network-to-policy_consistency')
import data_types

csv_key_data_types = 'pii_types'
csv_key_hostname = 'hostname'
csv_key_app_id = 'app_id'
csv_key_app_store = 'app_store'
csv_key_party_labels = 'party_labels'


def get_pii_groups() -> dict:
    """
    Make the reverse dict, where the group label -> list[PII_NAMES]
    WARNING: Not this does not handle special groupings in ConsistencyAnalysis.py
    """
    pii_groups = dict()
    for key, value in data_types.PII_VALUES.items():
        if value not in pii_groups:
            pii_groups[value] = []
        pii_groups[value].append(key)
    return pii_groups


def output_pii_stats(df:pd.DataFrame, output_directory: str, suffix: str, logger: logging.Logger):
    pii_groups = get_pii_groups()
    #logger.debug("Found %d PII groups", len(pii_groups))

    app_stores = ["Oculus", "SideQuest"]
    parties = ["first_party", "third_and_unknown", "platform_party",
               "third_party", "unknown_party"]

    aggregate_across_all_pii = dict()
    aggregate_across_app_stores = dict()
    aggregate_vr_movement = dict()
    vr_movement_piis = ["vr_movement", "vr_position", "vr_rotation"]
    app_store_all = "_".join(app_stores)
    rows = []
    for pii_group, pii_values in pii_groups.items():
        #logger.debug("checking pii group %s with values %s", pii_group, str(pii_values))
        for app_store in app_stores:

            for party in parties:
                data_row = {}
                data_row["pii_group"] = pii_group
                data_row[csv_key_app_store] = app_store
                data_row[csv_key_party_labels] = party

                pii_group_tmp = pii_group
                vr_movement_key = None
                if pii_group in vr_movement_piis:
                    vr_movement_key = app_store + party
                    pii_group_tmp = "vr_movement_all"
                    if vr_movement_key not in aggregate_vr_movement:
                        aggregate_vr_movement[vr_movement_key] =  \
                        {"pii_group": pii_group_tmp,
                         csv_key_app_store: app_store,
                         csv_key_party_labels: party,
                         "app_count": 0,
                         "app_count_app_ids": [],
                         "fqdn_count": 0,
                         "fqdn_count_hostnames": [],
                         "fqdn_blocked": 0,
                         "fqdn_blocked_hostnames": []}

                app_store_key = pii_group_tmp + app_store_all + party
                if app_store_key not in aggregate_across_app_stores:
                    aggregate_across_app_stores[app_store_key] = \
                        {"pii_group": pii_group_tmp,
                         csv_key_app_store: app_store_all,
                         csv_key_party_labels: party,
                         "app_count": 0,
                         "app_count_app_ids": [],
                         "fqdn_count": 0,
                         "fqdn_count_hostnames": [],
                         "fqdn_blocked": 0,
                         "fqdn_blocked_hostnames": []}

                # aggregate for each app store
                aggregate_across_pii_key = app_store + party
                if aggregate_across_pii_key not in aggregate_across_all_pii:
                    aggregate_across_all_pii[aggregate_across_pii_key] = \
                        {"pii_group": "all",
                         csv_key_app_store: app_store,
                         csv_key_party_labels: party,
                         "app_count": 0,
                         "app_count_app_ids": [],
                         "fqdn_count": 0,
                         "fqdn_count_hostnames": [],
                         "fqdn_blocked": 0,
                         "fqdn_blocked_hostnames": []}

                # aggregate for the COMBINED app store
                aggregate_combined_appstore_key = app_store_all + party
                if aggregate_combined_appstore_key not in aggregate_across_all_pii:
                    aggregate_across_all_pii[aggregate_combined_appstore_key] = \
                        {"pii_group": "all",
                         csv_key_app_store: app_store_all,
                         csv_key_party_labels: party,
                         "app_count": 0,
                         "app_count_app_ids": [],
                         "fqdn_count": 0,
                         "fqdn_count_hostnames": [],
                         "fqdn_blocked": 0,
                         "fqdn_blocked_hostnames": []}

                #logger.debug("keys aggregate_across_pii_key %s, aggregate_combined_appstore_key %s" %
                #      (aggregate_across_pii_key, aggregate_combined_appstore_key ))

                # first filter by store, pii, and party
                if party == "third_and_unknown":
                    df_tmp = df[df[csv_key_data_types].str.contains("|".join(pii_values)) & df[csv_key_app_store].str.contains(app_store) & ((df[csv_key_party_labels].str.contains("third_party")) | (df[csv_key_party_labels].str.contains("unknown_party"))) & ~df[csv_key_party_labels].str.contains("platform")]
                elif party == "third_party":
                    df_tmp = df[df[csv_key_data_types].str.contains("|".join(pii_values))  & df[csv_key_app_store].str.contains(app_store) & df[csv_key_party_labels].str.contains(party) & ~df[csv_key_party_labels].str.contains("platform")]
                else:
                    df_tmp = df[df[csv_key_data_types].str.contains("|".join(pii_values))  & df[csv_key_app_store].str.contains(app_store) & df[csv_key_party_labels].str.contains(party)]

                # then get the stats
                app_ids = df_tmp[csv_key_app_id]
                app_ids = set([x for x in app_ids if len(x.strip()) > 1])
                data_row["app_count"] = len(app_ids)
                data_row["app_count_app_ids"] = str(app_ids)
                aggregate_across_app_stores[app_store_key]["app_count_app_ids"] += app_ids
                aggregate_across_all_pii[aggregate_across_pii_key]["app_count_app_ids"] += app_ids
                aggregate_across_all_pii[aggregate_combined_appstore_key]["app_count_app_ids"] += app_ids
                if vr_movement_key:
                    aggregate_vr_movement[vr_movement_key]["app_count_app_ids"] += app_ids

                df_tmp[csv_key_hostname] = df_tmp[csv_key_hostname].astype('str')
                host_names = df_tmp[csv_key_hostname]
                host_names = set([x for x in host_names if len(x.strip()) > 1 and x.strip() != "nan"])
                if "github-releases.githubusercontent.com" in host_names:
                    host_names.remove("github-releases.githubusercontent.com")
                data_row["fqdn_count"] = len(host_names)
                data_row["fqdn_count_hostnames"] = str(host_names)
                aggregate_across_app_stores[app_store_key]["fqdn_count_hostnames"] += host_names
                aggregate_across_all_pii[aggregate_across_pii_key]["fqdn_count_hostnames"] += host_names
                aggregate_across_all_pii[aggregate_combined_appstore_key]["fqdn_count_hostnames"] += host_names
                if vr_movement_key:
                    aggregate_vr_movement[vr_movement_key]["fqdn_count_hostnames"] += host_names

                df_tmp_blocked = df_tmp[(df_tmp["piholeblocklist_default_smarttv_abp_block_decision"] == 1) | (df_tmp["moaab_abp_block_decision"] == 1) | (df_tmp["disconnectme_abp_block_decision"] == 1)]

                host_names_blocked = df_tmp_blocked[csv_key_hostname].unique()
                data_row["fqdn_blocked"] = len(host_names_blocked)
                data_row["fqdn_blocked_hostnames"] = str(host_names_blocked)
                aggregate_across_app_stores[app_store_key]["fqdn_blocked_hostnames"] += list(host_names_blocked)
                aggregate_across_all_pii[aggregate_across_pii_key]["fqdn_blocked_hostnames"] += list(host_names_blocked)
                aggregate_across_all_pii[aggregate_combined_appstore_key]["fqdn_blocked_hostnames"] += list(host_names_blocked)
                if vr_movement_key:
                    aggregate_vr_movement[vr_movement_key]["fqdn_blocked_hostnames"] += list(host_names_blocked)

                data_row["fqdn_blocked_percent"] = 0
                if data_row["fqdn_count"] > 0:
                    data_row["fqdn_blocked_percent"] = round((data_row["fqdn_blocked"]/data_row["fqdn_count"]) * 100)

                data_row["display_latex"] = str(data_row["app_count"]) + " / " + str(data_row["fqdn_count"]) + " / " + str(data_row["fqdn_blocked_percent"]) + "\\%"

                rows.append(data_row)

    misc_rows = list(aggregate_across_all_pii.values()) + list(aggregate_across_app_stores.values()) + list(aggregate_vr_movement.values())

    # turn lists into counts of sets
    for aggregate_row in misc_rows:
        aggregate_row["fqdn_blocked_percent"] = 0
        aggregate_row["app_count"] = len(set(aggregate_row["app_count_app_ids"]))
        aggregate_row["app_count_app_ids"] = str(set(aggregate_row["app_count_app_ids"]))
        aggregate_row["fqdn_count"] = len(set(aggregate_row["fqdn_count_hostnames"]))
        aggregate_row["fqdn_count_hostnames"] = str(set(aggregate_row["fqdn_count_hostnames"]))
        aggregate_row["fqdn_blocked"] = len(set(aggregate_row["fqdn_blocked_hostnames"]))
        aggregate_row["fqdn_blocked_hostnames"] = str(set(aggregate_row["fqdn_blocked_hostnames"]))
        if aggregate_row["fqdn_count"] > 0:
            aggregate_row["fqdn_blocked_percent"] = round((aggregate_row["fqdn_blocked"] / aggregate_row["fqdn_count"]) * 100)
            aggregate_row["display_latex"] = str(aggregate_row["app_count"]) + " / " + str(aggregate_row["fqdn_count"]) + " / " + str(
                aggregate_row["fqdn_blocked_percent"]) + "\\%"
        rows.append(aggregate_row)

    df_output = pd.DataFrame(columns=list(rows[0].keys()))
    df_output = df_output.from_dict(rows)

    # filter out and keep first,third,platform parties and keep aggregated store "Oculus_SideQuest"
    df_output = df_output[df_output["party_labels"].isin(["first_party", "third_party", "platform_party"]) & df_output["app_store"].isin(["Oculus_SideQuest"])]

    # make new data to match Table 3
    app_count_col = "app_count"
    fqdn_count_col = "fqdn_count"
    percent_blocked_col = "fqdn_blocked_percent"
    rows = []
    for pii_group in df_output["pii_group"].unique():
        #logger.debug(pii_group)

        if pii_group == "mac_address":
            continue

        first_tmp_rows = df_output[(df_output["pii_group"] == pii_group) & (df_output["party_labels"].isin(["first_party"]))]
        third_tmp_rows = df_output[(df_output["pii_group"] == pii_group) & (df_output["party_labels"].isin(["third_party"]))]
        platform_tmp_rows = df_output[(df_output["pii_group"] == pii_group) & (df_output["party_labels"].isin(["platform_party"]))]

        # Apps Column
        first_tmp_value = first_tmp_rows[app_count_col].iloc[0]
        third_tmp_value = third_tmp_rows[app_count_col].iloc[0]
        platform_tmp_value = platform_tmp_rows[app_count_col].iloc[0]

        apps_str = f"{first_tmp_rows[app_count_col].iloc[0] if len(first_tmp_rows) > 0 else 0} / {third_tmp_rows[app_count_col].iloc[0] if len(third_tmp_rows) > 0 else 0} / {platform_tmp_rows[app_count_col].iloc[0] if len(platform_tmp_rows) > 0 else 0} "
        #logger.info("Apps: " + apps_str)
        sum_apps = first_tmp_value + third_tmp_value + platform_tmp_value

        # FQDNs Column
        fdns_str = f"{first_tmp_rows[fqdn_count_col].iloc[0] if len(first_tmp_rows) > 0 else 0} / {third_tmp_rows[fqdn_count_col].iloc[0] if len(third_tmp_rows) > 0 else 0} / {platform_tmp_rows[fqdn_count_col].iloc[0] if len(platform_tmp_rows) > 0 else 0} "
        #logger.info("FQDNS: " + fdns_str)

        # % FQDNs Blocked Column
        percent_blocked_fqdns_str = f"{first_tmp_rows[percent_blocked_col].iloc[0] if len(first_tmp_rows) > 0 else 0} / {third_tmp_rows[percent_blocked_col].iloc[0] if len(third_tmp_rows) > 0 else 0} / {platform_tmp_rows[percent_blocked_col].iloc[0] if len(platform_tmp_rows) > 0 else 0} "
        #logger.info("% Blocked FQDNs: " + percent_blocked_fqdns_str)
        data = {"Data Type": pii_group,
                "Apps": apps_str,
                "FQDNs": fdns_str,
                "% Blocked FQDNS": percent_blocked_fqdns_str,
                "Apps Total": sum_apps
                }
        if pii_group == "all":
            data["Data Type"] = "Total"
        rows.append(data)

    df_output = pd.DataFrame(columns=list(rows[0].keys()))
    df_output = df_output.from_dict(rows)
    df_output = df_output.sort_values(by="Apps Total", ascending=False)
    df_output = df_output.drop("Apps Total", axis=1)
    file_name = output_directory + os.sep + "Table_3_DatatypesExposed" + suffix + ".csv"
    df_output.to_csv(file_name, index=False)
    return file_name


def output_missed_by_blocklists(df_original:pd.DataFrame, output_directory: str, suffix: str, logger: logging.Logger):
    pii_groups = get_pii_groups()

    df = df_original[(df_original["piholeblocklist_default_smarttv_abp_block_decision"] == 0) & (
            df_original["moaab_abp_block_decision"] == 0) & (df_original["disconnectme_abp_block_decision"] == 0)]

    parties = ["first_party", "third_and_unknown", "platform_party",
               "third_party", "unknown_party"]

    output_rows = dict()
    for index, row_data in df.iterrows():
        hostname = row_data[csv_key_hostname]
        if str(hostname) == "nan":
            continue
        if hostname not in output_rows:
            output_rows[hostname] = \
                {
                    csv_key_hostname: hostname,
                    "second_level_domain": row_data["second_level_domain"],
                    "pii_in_first_party": [],
                    "app_in_first_party": [],
                    "pii_in_third_party": [],
                    "app_in_third_party": [],
                    "pii_in_platform_party": [],
                    "app_in_platform_party": []
                }

        app_party_key = None
        pii_party_key = None
        if "first" in row_data[csv_key_party_labels]:
            app_party_key = "app_in_first_party"
            pii_party_key = "pii_in_first_party"
        elif "third" in row_data[csv_key_party_labels] and "platform" not in row_data[csv_key_party_labels]:
            app_party_key = "app_in_third_party"
            pii_party_key = "pii_in_third_party"
        elif "platform" in row_data[csv_key_party_labels]:
            app_party_key = "app_in_platform_party"
            pii_party_key = "pii_in_platform_party"
        if not app_party_key:
            continue

        output_rows[hostname][app_party_key].append(row_data[csv_key_app_id])
        data_types = row_data[csv_key_data_types]
        for pii_group, pii_values in pii_groups.items():
            match = any(pii in data_types for pii in pii_values)
            if match:
                output_rows[hostname][pii_party_key].append(pii_group)

    for row in output_rows.values():
        row["app_in_first_party"] = set(row["app_in_first_party"])
        row["app_in_first_party_len"] = len(set(row["app_in_first_party"]))
        row["app_in_third_party"] = set(row["app_in_third_party"])
        row["app_in_third_party_len"] = len(set(row["app_in_third_party"]))
        row["app_in_platform_party"] = set(row["app_in_platform_party"])
        row["app_in_platform_party_len"] = len(set(row["app_in_platform_party"]))

        row["pii_in_first_party"] = set(row["pii_in_first_party"])
        row["pii_in_first_party_len"] = len(set(row["pii_in_first_party"]))
        row["pii_in_third_party"] = set(row["pii_in_third_party"])
        row["pii_in_third_party_len"] = len(set(row["pii_in_third_party"]))
        row["pii_in_platform_party"] = set(row["pii_in_platform_party"])
        row["pii_in_platform_party_len"] = len(set(row["pii_in_platform_party"]))

    rows = [x for key, x in output_rows.items() if (x["pii_in_first_party_len"] > 0 or x["pii_in_third_party_len"] > 0 or x["pii_in_platform_party_len"] > 0)]
    df_output = pd.DataFrame(columns=list(rows[0].keys()))
    df_output = df_output.from_dict(rows)
    df_output = df_output.sort_values(by="pii_in_third_party_len", ascending=False)

    file_name = output_directory + os.sep + "Table_2_MissingedByBlocklists" + suffix + ".csv"
    df_output.to_csv(file_name, index=False)
    return file_name


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Given the CSV from OVRseen post-processing, we generate data for the tables and figures.')

    # REQUIRED
    parser.add_argument('--csv_file_path',
                        required=True,
                        help='File path to post-processing CSV')
    parser.add_argument('--output_directory',
                        required=True,
                        help='directory output')
    parser.add_argument('--log_level', default="DEBUG", help='Log level')

    args = parser.parse_args()
    print(args)

    # set up logger
    numeric_level = getattr(logging, args.log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % args.log_level)
    logging.basicConfig(format='%(asctime)s %(message)s', level=numeric_level)

    logger = logging.getLogger(__name__)

    df = pd.read_csv(args.csv_file_path)

    # Create Table 1
    logger.info("Creating Table 1...")
    data = []
    for app_store_name in ["Oculus-Free", "Oculus-Paid", "SideQuest"]:
        query_distinct_apps = f"select distinct app_id from df where app_id is not null and app_store = \"{app_store_name}\";"
        query_distinct_domains = f"select distinct hostname from df where hostname is not null and app_store = \"{app_store_name}\";"
        query_distinct_eslds = f"select distinct second_level_domain from df where hostname is not null and app_store = \"{app_store_name}\";"
        query_packets = f"select pkt_id from df where  app_store = \"{app_store_name}\";"
        query_tcp_flows = f"select * from (select distinct app_id, tcp_stream, hostname from df where app_store = \"{app_store_name}\");"

        distinct_apps = pysqldf(query_distinct_apps)
        apps_count = distinct_apps.shape[0]
        domains_count = pysqldf(query_distinct_domains).shape[0]
        eslds_count = pysqldf(query_distinct_eslds).shape[0]
        pkts_count = pysqldf(query_packets).shape[0]
        tcp_flows_count = pysqldf(query_tcp_flows).shape[0]
        data.append((app_store_name, apps_count, domains_count, eslds_count, pkts_count, tcp_flows_count))

    # do for Total (based on unique counts, so we cannot simply add the numbers from each app store
    query_distinct_apps = f"select distinct app_id from df where app_id is not null;"
    query_distinct_domains = f"select distinct hostname from df where hostname is not null;"
    query_distinct_eslds = f"select distinct second_level_domain from df where hostname is not null;"
    query_packets = f"select pkt_id from df;"
    query_tcp_flows = f"select * from (select distinct app_id, tcp_stream, hostname from df);"

    apps_count = pysqldf(query_distinct_apps).shape[0]
    domains_count = pysqldf(query_distinct_domains).shape[0]
    eslds_count = pysqldf(query_distinct_eslds).shape[0]
    pkts_count = pysqldf(query_packets).shape[0]
    tcp_flows_count = pysqldf(query_tcp_flows).shape[0]
    data.append(('Total', apps_count, domains_count, eslds_count, pkts_count, tcp_flows_count))

    table_1_df = pd.DataFrame(data, columns=['App Store', 'Apps', 'Domains', 'eSLDs', 'Packets', 'TCP Flows'])
    file_name = args.output_directory + os.sep + "Table_1_NetworkTrafficDataSetSummary.csv"
    table_1_df.to_csv(file_name, index=False)
    logger.info(f"\tSee file {file_name}")

    # create data for Fig 2
    fig_2a_query = f"select second_level_domain, party_labels, count(second_level_domain) as apps_count from (select distinct app_id, second_level_domain, party_labels from df where second_level_domain is not NULL and second_level_domain != \".\" and (party_labels like '%platform%' or party_labels like '%third%')) group by second_level_domain, party_labels order by count(second_level_domain) desc;"
    fig_2a_df = pysqldf(fig_2a_query)
    fig_2a_df.to_csv(args.output_directory + os.sep + 'Figure_2a.csv', index=False)

    fig_2b_query = f"select hostname, party_labels, count(hostname) as apps_count from (select distinct app_id, hostname, party_labels from df where hostname is not NULL and (party_labels like \"%third%\" or party_labels  like \"%platform%\") and (piholeblocklist_default_smarttv_abp_block_decision=1 or moaab_abp_block_decision=1 or disconnectme_abp_block_decision-1) ) group by hostname, party_labels order by count(hostname) desc;"
    fig_2b_df = pysqldf(fig_2b_query)
    fig_2b_df.to_csv(args.output_directory + os.sep + 'Figure_2b.csv', index=False)
    logger.info("Creating data for Figure 2...")
    logger.info(f"\tSee file {args.output_directory + os.sep + 'Figure_2a.csv'}")
    logger.info(f"\tSee file {args.output_directory + os.sep + 'Figure_2b.csv'}")

    # create data for Table 3 and 4
    file_name = output_missed_by_blocklists(df, args.output_directory, "", logger)
    logger.info("Creating data for Table 2...")
    logger.info(f"\tSee file {file_name}")

    file_name = output_pii_stats(df, args.output_directory, "", logger)
    logger.info("Creating data for Table 3...")
    logger.info(f"\tSee file {file_name}")

    logger.info("Done")

