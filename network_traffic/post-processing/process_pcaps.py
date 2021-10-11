#!/usr/bin/python

'''
This script calls the other scripts in the data_preparation directory to perform the second phase of the pipeline.
Basically, the scripts perform:
1) Merge PCAP files for each app into one PCAP file for encrypted traffic and one PCAP file for decrypted traffic.
2) Produce tshark JSON files, each for encrypted and decrypted traffic PCAP files.
3) Produce a unified JSON file in NoMoAds-style.
4) Run the unified JSON file through the filter-list matching script.
5) Finally, produce a CSV file that contains the flow of traffic for further processing (e.g., ATS analyses, policy analyses, etc.)
'''

import argparse
import os
import subprocess
import shutil
import pandas as pd

from utils.utils import DIR_DELIMITER
from pandasql import sqldf
pysqldf = lambda q: sqldf(q, globals())

# Filter list result directory
FL_RESULT_DIR = "filters_matching_results"

if __name__ == '__main__':
    ap = argparse.ArgumentParser(description='Runs the full Oculus pipeline')
    ap.add_argument('dataset_root_dir', type=str, help='root directory of dataset')
    ap.add_argument('app_store_csvs_dir', type=str, help='directory of csvs about app stores')

    args = ap.parse_args()

    # Get the absolute paths
    dataset_root_abs_dir = os.path.abspath(args.dataset_root_dir)
    app_store_csvs_abs_dir = os.path.abspath(args.app_store_csvs_dir)

    TEMP_OUTPUT_NAME = "temp_output"
    CSV_TMP_NAME = "csv"
    output_tmp_dir = dataset_root_abs_dir + os.sep + TEMP_OUTPUT_NAME
    if os.path.isdir(output_tmp_dir):
        shutil.rmtree(output_tmp_dir)
    os.makedirs(output_tmp_dir)

    # keep track of dfs per store
    data_frames = []

    # For each app store:
    #   Iterate over APK subdirectories that contain the PCAP files and call the necessary scripts
    for app_store_name in os.listdir(dataset_root_abs_dir):

        if app_store_name == ".DS_Store" or app_store_name == TEMP_OUTPUT_NAME:
            continue

        apk_dir_path_tuple = []
        app_store_dir = os.path.join(dataset_root_abs_dir, app_store_name)
        print(f"Processing data from App Store: {app_store_name}")
        for apk_dir in os.listdir(app_store_dir):

            if apk_dir == ".DS_Store" or apk_dir == CSV_TMP_NAME:
                continue

            # Get the absolute path
            apk_dir_path = os.path.join(app_store_dir, apk_dir)
            if apk_dir == '__MACOSX' or not os.path.isdir(apk_dir_path):
                continue

            print(f"[.] {app_store_name}: Begin the pipeline for app " + apk_dir + "...\n")

            # The pipeline
            # 1) Merge PCAP files for each app into one PCAP file for encrypted traffic and
            #    one PCAP file for decrypted traffic.
            # 2) Produce tshark JSON files, each for encrypted and decrypted traffic PCAP files.
            print(f"[+] {app_store_name}: Merging decrypted PCAP files and creating a JSON file using tshark...")
            ret = subprocess.check_call(["python3", "merge_cap.py", "-dec", apk_dir_path])
            print(f"[+] {app_store_name}: Merging encrypted PCAP files and creating a JSON file using tshark...")
            ret = subprocess.check_call(["python3", "merge_cap.py", "-enc", apk_dir_path])

            # 3) Produce a unified JSON file in NoMoAds-style.
            print(f"[+] {app_store_name}: Creating a unified JSON file...\n")
            ret = subprocess.check_call(["python3", "extract_from_tshark.py",
                "--enc_file",
                os.path.join(apk_dir_path, apk_dir + "-ENC-out.json"),
                "--dec_file",
                os.path.join(apk_dir_path, apk_dir + "-DEC-out.json"),
                "--out_file",
                os.path.join(apk_dir_path, apk_dir + "-out-nomoads.json"),
                "--include_http_body"
                ])

            apk_dir_path_tuple.append((apk_dir_path, apk_dir))

        apk_dir_paths_only = [x for x, _ in apk_dir_path_tuple]

        # 4) Run the unified JSON file through the filter-list matching script.
        print(f"[+] {app_store_name}: Running the unified JSON file and matching the entries against filter lists...")
        ret = subprocess.check_call(["python3", "filter_list_checker_mult_dirs.py", DIR_DELIMITER.join(apk_dir_paths_only), "filter_lists", FL_RESULT_DIR])
        print("\n")
        print(f"[+] {app_store_name}: Filter lists matching results are saved in " + DIR_DELIMITER.join(apk_dir_paths_only) + "...\n")

        # Make CSV directory to hold output
        csv_app_store_dir = app_store_dir + os.sep + "csv"
        if not os.path.isdir(csv_app_store_dir):
            os.makedirs(csv_app_store_dir, exist_ok=True)

        # 5) Finally, produce a CSV file that contains the flow of traffic for further processing
        #    (e.g., ATS analyses, policy analyses, etc.)
        for apk_dir_path_tmp, apk_dir_tmp in apk_dir_path_tuple:
            fl_result_dir = os.path.join(apk_dir_path_tmp, FL_RESULT_DIR)
            print(f"[+] {app_store_name}: Generating the final CSV file in " + fl_result_dir + "...\n")
            csv_file_path = os.path.join(fl_result_dir, apk_dir_tmp + ".csv")
            ret = subprocess.check_call([
                "python3",
                "compare_results.py", fl_result_dir,
                "filter_lists", csv_file_path,
                "--include_http_body"
                ])
            print(f"[+] {app_store_name}: Copying the final CSV file into " + csv_app_store_dir + "...\n\n")
            shutil.copy(csv_file_path, csv_app_store_dir)

        # merge csv into one per store
        merged_file_one_store = os.path.join(output_tmp_dir, f"{app_store_name}-merged.csv")

        cmd = f"awk '(NR == 1) || (FNR > 1)' *.csv > {merged_file_one_store}"
        subprocess.check_output(cmd, shell=True, cwd=csv_app_store_dir)
        print(f"[+] {app_store_name}: Created merged csv {merged_file_one_store}")

        # add the app_store column with the name
        df = pd.read_csv(merged_file_one_store)
        df["app_store"] = app_store_name
        data_frames.append(df)

    # merge everything together
    all_merged = pd.concat(data_frames)
    all_merged_file = output_tmp_dir + os.sep + "all-merged.csv"
    all_merged.to_csv(all_merged_file, index=False)

    # add esld
    all_merged_with_esld_file = output_tmp_dir + os.sep + "all-merged-with-esld.csv"
    ret = subprocess.check_call(["python3", "append_sld_to_csv.py", all_merged_file, all_merged_with_esld_file])

    # read in other CSVs
    all_merged_with_esld_df = pd.read_csv(all_merged_with_esld_file)
    all_150_top_apps_df = pd.read_csv(app_store_csvs_abs_dir + os.sep + "all_150_top_apps.csv")
    oculus_store_apps_df = pd.read_csv(app_store_csvs_abs_dir + os.sep + "oculus_store_apps.csv")
    sidequest_store_apps_df = pd.read_csv(app_store_csvs_abs_dir + os.sep + "sidequest_store_apps.csv")

    # add in app title,game engine, and developer privacy policy
    all_merged_with_esld_engine_privacy_df = pysqldf("select merged.*, App_Title, Game_Engine, Actual_Developer_Privacy_Policy, Final_Status  from all_merged_with_esld_df  as merged left join all_150_top_apps_df as topapps on merged.app_id == topapps.package_name;")

    all_merged_with_esld_engine_privacy_df = all_merged_with_esld_engine_privacy_df[all_merged_with_esld_engine_privacy_df["Final_Status"] == "Working"]

    # add in developer name
    sql_query = \
        """
        select ocmerged.*, oc.Developer as "oculus_creator", s.Creator as "sidequest_creator" from all_merged_with_esld_engine_privacy_df as ocmerged
        left join oculus_store_apps_df as oc on ocmerged.App_Title == oc.App_Title
        left join sidequest_store_apps_df as s on ocmerged.App_Title == s.App_Title;
        """
    all_merged_with_esld_engine_privacy_developer_df = pysqldf(sql_query)
    all_merged_with_esld_engine_privacy_developer_file = output_tmp_dir + os.sep + "all-merged-with-esld-engine-privacy-developer.csv"
    all_merged_with_esld_engine_privacy_developer_df.to_csv(all_merged_with_esld_engine_privacy_developer_file,
                                                            index=False)
    # add party label
    all_merged_with_esld_engine_privacy_developer_party_file = output_tmp_dir + os.sep + "all-merged-with-esld-engine-privacy-developer-party.csv"
    ret = subprocess.check_call(
        ["python3", "oculus_hostname_fp_tp_csv_generator.py", all_merged_with_esld_engine_privacy_developer_file, all_merged_with_esld_engine_privacy_developer_party_file])

    # copy final CSV to the root dir
    shutil.copy(all_merged_with_esld_engine_privacy_developer_party_file, dataset_root_abs_dir)
    print(f"Final CSV is in {dataset_root_abs_dir + os.sep + os.path.basename(all_merged_with_esld_engine_privacy_developer_party_file)}")
