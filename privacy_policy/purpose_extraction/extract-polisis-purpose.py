#!/usr/bin/env python3

from collections import Counter
import csv
import json
from pathlib import Path
import re
import sys


def match_sentence(sent1, sent2):
    set1 = set(w.lower() for w in re.findall(r'\w+', sent1))
    set2 = set(w.lower() for w in re.findall(r'\w+', sent2))
    intersection = set1 & set2
    return intersection == set1 or intersection == set2


def main():
    DATA_ROOT = Path(sys.argv[1])
    counter = Counter()
    purpose_counter = Counter()

    # load polisis results
    polisis_results = dict()
    for json_path in (DATA_ROOT / 'polisis_out').glob('*.json'):
        package_name = json_path.name.rsplit('.', 1)[0]
        with json_path.open() as fin:
            polisis_results[package_name] = json.load(fin)

    # load policheck results and annotate
    with open(DATA_ROOT / 'policheck_results.csv', newline="") as fin, \
         open(DATA_ROOT / 'policheck_results_w_purposes.csv', "w", newline="") as fout1, \
         open(DATA_ROOT / 'policheck_results_w_purposes_expanded.csv', "w", newline="") as fout2:
        reader = csv.DictReader(fin)
        writer1 = csv.DictWriter(fout1, reader.fieldnames + ["party", "purposes"])
        writer2 = csv.DictWriter(fout2, reader.fieldnames + ["party", "purpose"])
        writer1.writeheader()
        writer2.writeheader()

        for row in reader:
            counter["flow"] += 1
            package_name = row['packageName']

            if row["flowEntity"] == "we":
                row["party"] = "first_party"
            elif row["flowEntity"] in ["oculus", "facebook"]:
                row["party"] = "platform_party"
            else:
                row["party"] = "third_party"

            if row["consistencyResult"] not in ['clear', 'vague']:
                row['purposes'] = 'N/A'
                writer1.writerow(row)
                row['purpose'] = row.pop('purposes')
                writer2.writerow(row)
                counter["consistent_flow"] += 1
                continue
            elif package_name not in polisis_results:
                row['purposes'] = 'NO_POLISIS_OUTPUT'
                writer1.writerow(row)
                row['purpose'] = row.pop('purposes')
                writer2.writerow(row)
                counter["failed"] += 1
                continue

            entity = row["flowEntity"]
            party = "first-party" if entity == "we" else "third-party"

            purposes = set()
            matched = False

            for sent in row["policySentences"].split('||'):
                if sent.startswith('@'):
                    polisis_key, sent = sent.split(':', 1)
                    polisis_key = polisis_key.replace('@', '@' + 'extra.')
                    polisis_party = 'first-party'
                else:
                    polisis_key = package_name
                    polisis_party = party

                n_match = 0
                for item in polisis_results[polisis_key]:
                    if item["policheck-text"] and match_sentence(item["policheck-text"], sent):
                        purposes.update(item["polisis"][polisis_party]["purposes"])
                        n_match += 1

                if n_match != 1:
                    print(f"{package_name}, N-match={n_match}, Sentence={sent}")
                if n_match >= 1:
                    matched = True

            if matched:
                row["purposes"] = "||".join(sorted(purposes))
                writer1.writerow(row)
                row.pop("purposes")

                if len(purposes):
                    counter["with_purpose"] += 1

                    for p in purposes:
                        counter["expanded"] += 1
                        row["purpose"] = p
                        purpose_counter[p] += 1
                        writer2.writerow(row)
                else:
                    counter["no_purpose"] += 1
                    row["purpose"] = 'UNKNOWN'
                    writer2.writerow(row)
            else:
                counter["failed"] += 1
                row["purposes"] = "NO_MATCH"
                writer1.writerow(row)
                row['purpose'] = row.pop('purposes')
                writer2.writerow(row)

    print()
    print(f"all flows: {counter['flow']}")
    print(f"  consistent flows: {counter['consistent_flow']}")
    print(f"    success and found purpose: {counter['with_purpose']} (expanded to {counter['expanded']} tuples)")
    print(f"    success but no purpose: {counter['no_purpose']}")
    print(f"    failed: {counter['failed']}")
    print()
    for k, v in purpose_counter.items():
        print(f"{k}: {v}")


if __name__ == '__main__':
    main()
