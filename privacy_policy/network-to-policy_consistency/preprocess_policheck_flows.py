#!/usr/bin/env python3

import argparse
import ast
import csv
import data_types
import sys

# =================== CSV column names ===================
csv_key_data_types = 'pii_types'
csv_key_hostname = 'hostname'
csv_key_app_id = 'app_id'
# ========================================================

# a function to check if the data type already exists in the map
def exists(dest_to_pii_map, hostname, data_type):
    # check if the hostname (as key) is in the dictionary
    # if yes, we check the PII types it maps to
    # if not, we have to create an entery for it
    if hostname in dest_to_pii_map:
        data_type_set = dest_to_pii_map[hostname]
        if data_type in data_type_set:
            return True
    else:
        dest_to_pii_map[hostname] = set()
    data_type_set = dest_to_pii_map[hostname]
    data_type_set.add(data_type)

    return False


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description='Converts the CSV file produced by our pipeline into a policheck_flows.csv file.')
    ap.add_argument('in_csv', type=str, help='input CSV file')
    ap.add_argument('out_csv', type=str, help='output CSV file')

    args = ap.parse_args()
    # get mapping for data types
    data_types_map = data_types.PII_VALUES
    # prepare the dict that maps every destination to a PII label
    # this makes sure that we don't write 2 identical PoliCheck flows into the file
    # this map needs to memorize things within the scope of an app (we need to clear it for every new app)
    dest_to_pii_map = dict()

    output_columns = ['app_id', 'pii_types', 'hostname', 'dst_ip', 'creator',
                      'developer_privacy_policy', 'extra_policies']

    # first pass: construct IP-to-domain mapping
    ip_map = dict()
    with open(args.in_csv, 'r', newline="") as in_csv_file:
        csv_reader = csv.DictReader(in_csv_file, delimiter=",", quotechar='"')
        for row in csv_reader:
            if row['hostname']:
                ip_map[row['dst_ip']] = row['hostname']

    # read the input CSV, unroll the PII types (write multiple lines, one for each PII type)
    with open(args.in_csv, 'r', newline="") as in_csv_file:
        csv_reader = csv.DictReader(in_csv_file, delimiter=",", quotechar='"')

        # open the output CSV and start by writing the field names
        with open(args.out_csv, 'w', newline="") as out_csv_file:
            csv_writer = csv.writer(out_csv_file)
            csv_writer.writerow(output_columns)

            # this is just to declare the 2 variables
            curr_app = ''
            prev_app = ''
            # check every row and unroll accordingly
            for row in csv_reader:
                # we have to clear dest_to_pii_map if we have moved to a new app
                curr_app = row[csv_key_app_id]
                if curr_app != prev_app:
                    dest_to_pii_map.clear()
                prev_app = curr_app

                # workaround for some CSVs using a different column name for policy url
                if 'developer_privacy_policy' not in row:
                    row['developer_privacy_policy'] = row['Actual_Developer_Privacy_Policy']

                # this is for extracting first party names
                row['creator'] = row['oculus_creator'] or row['sidequest_creator']

                extra_policies = ['oculus']
                if row['Game_Engine'] != 'Others':
                    extra_policies.append(row['Game_Engine'].lower())

                row['extra_policies'] = "+".join(extra_policies)

                # try to fill empty hostname fields
                if row['hostname'] == '':
                    row['hostname'] = ip_map.get(row['dst_ip'], '')

                # get pii_types and unroll the content into multiple lines
                pii_types_set = ast.literal_eval(row[csv_key_data_types])
                for pii_type in pii_types_set:
                    # find the right PII label for PoliCheck from our map
                    if pii_type in data_types_map:
                        data_type = data_types_map[pii_type]
                    else:
                        # this should never happen since we should have all the PII types in data_types.py
                        print('WARNING: Found an unlabeled PII: ' + pii_type)
                    # check if we have had this entity in the PoliCheck's flows file
                    # basically PoliCheck's flows file preserves a unique PII data type for every destination
                    # if such a row already exists, then we skip it
                    if exists(dest_to_pii_map, row[csv_key_hostname], data_type):
                        continue
                    # record unique PoliCheck flow
                    row[csv_key_data_types] = data_type
                    data_row = [row[header_name] for header_name in output_columns]
                    csv_writer.writerow(data_row)
