#!/usr/bin/env python3

# This file is a part of OVRseen <https://athinagroup.eng.uci.edu/projects/ovrseen/>.
# Copyright (c) 2021 UCI Networking Group.
#
# This file incorporates content from the HtmlToPlaintext repo <https://github.com/benandow/HtmlToPlaintext>.
#
# OVRseen is dual licensed under the MIT License and the GNU General Public
# License version 3 (GPLv3). This file is covered by the GPLv3. If this file
# get used, GPLv3 applies to all of OVRseen.
#
# See the LICENSE.md file along with OVRseen for more details.

import json
import os
from pathlib import Path
import shlex
import sys

import networkx as nx
import spacy


def proc_json(json_data):
    ADJUSTED_VALUE_PREDICTIONS_KEY = "adjusted_value_predictions"
    CATEGORY_PREDICTIONS_KEY = "category_predictions"

    for segment_data in json_data.values():
        segment_categories = {x[0] for x in segment_data[CATEGORY_PREDICTIONS_KEY]}
        segment_categories &= {'third-party-sharing-collection', 'first-party-collection-use'}
        info_dict = {p: {"data-types": [], "purposes": []} for p in ("first-party", "third-party")}

        # only consider parties that exist in segment_categories
        for category_prediction in segment_categories:
            main_key_dtype = category_prediction + "_personal-information-type_"
            main_key_purpose = category_prediction + "_purpose_"

            dtypes_found = []
            purposes_found = []

            for adjusted_predictions in segment_data[ADJUSTED_VALUE_PREDICTIONS_KEY]:
                name = adjusted_predictions[0]

                if name.startswith(main_key_dtype):
                    dtype = name[len(main_key_dtype):].replace("-", " ")
                    dtypes_found.append(dtype)
                elif name.startswith(main_key_purpose):
                    purpose = name[len(main_key_purpose):].replace("-", " ")
                    purposes_found.append(purpose)

            party_name = category_prediction.split('-')[0] + '-party'
            info_dict[party_name]["data-types"].extend(dtypes_found)
            info_dict[party_name]["purposes"].extend(purposes_found)

        yield segment_data['fg_segments'], info_dict


def main():
    SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(os.path.join(SCRIPT_DIR, '..', 'network-to-policy_consistency'))
    from Preprocessor import TextPostProcessor, NonEnglishException
    from PatternExtractionNotebook import Analytics, PatternDiscover, val, valTxt
    from ConsistencyAnalysis import processPrivacyPolicyResults, DATA_MAP
    import lib.Consistency as con

    DATA_ROOT = Path(sys.argv[1])

    # get list of data types that each term subsumes
    data_ontology = nx.read_gml(DATA_ROOT / 'data' / 'data_ontology.gml')
    flow_dtypes = frozenset(DATA_MAP.values())
    dtype_map = dict()

    for n1 in data_ontology.nodes:
        dtype_map[n1] = [n1] if n1 in dtype_map else []

        for n2 in flow_dtypes:
            if nx.has_path(data_ontology, n1, n2):
                dtype_map[n1].append(n2)

    # PoliCheck initialization
    spacy.prefer_gpu()
    nlp = spacy.load(DATA_ROOT / 'NlpFinalModel')

    con.init(
        dataOntologyFilename=DATA_ROOT / 'data' / 'data_ontology.gml',
        entityOntologyFilename=DATA_ROOT / 'data' / 'entity_ontology.gml')

    analytics = Analytics()
    pd = PatternDiscover(nlpModel=nlp, analyticsObj=analytics)

    with open(os.path.join(SCRIPT_DIR, '..', 'network-to-policy_consistency', "extra_training_data.txt")) as fin:
        for sentence in fin:
            pd.train(sentence)

    first_party_names = dict()
    with open(DATA_ROOT / 'output' / 'first_party_names.list') as fin:
        for line in fin:
            packageName, *alterNames = shlex.split(line.strip())
            first_party_names[packageName] = alterNames

    # process analysis files
    os.makedirs(DATA_ROOT / 'polisis_out', exist_ok=True)

    for json_path in (DATA_ROOT / 'polisis_output').glob('*_analysis.json'):
        package_name = json_path.name.rsplit('_', 1)[0]

        if package_name == 'N/A':
            continue

        with json_path.open() as fin:
            json_data = json.load(fin)

        analytics.startDoc("POLISIS")
        output = []

        for text, polisis_info in proc_json(json_data):
            # fix Polisis encoding problem
            fixed_text = text
            if not text.isprintable():
                try:
                    fixed_text = text.encode('ISO-8859-1').decode()
                except UnicodeDecodeError:
                    pass

            # PoliCheck Step 1: Preprocessor
            try:
                proc_text = (TextPostProcessor([fixed_text]).postProcess() or [''])[0]
            except NonEnglishException:
                proc_text = ""

            # PoliCheck Step 2: PatternExtractionNotebook
            res = pd.test(proc_text)
            policies = []
            for ent, col, dat, sen, actionLemma in res or []:
                policies.append((val(ent), val(col), val(dat), valTxt(sen), val(actionLemma)))

            # PoliCheck Step 3: ConsistencyAnalysis (ontology mapping)
            proc_policies = []
            for e, c, d, _ in processPrivacyPolicyResults(policies, package_name, nlp,
                                                          first_party_names.get(package_name, [])):
                if dtype_map[d]:
                    proc_policies.append((e, c, d, dtype_map[d]))

            output.append({
                "text": text,
                "policheck-text": proc_text,
                "polisis": polisis_info,
                "policheck": proc_policies
            })

        with open(DATA_ROOT / 'polisis_out' / (package_name + ".json"), "w") as fout:
            json.dump(output, fout)

        analytics.endDoc()


if __name__ == '__main__':
    main()
