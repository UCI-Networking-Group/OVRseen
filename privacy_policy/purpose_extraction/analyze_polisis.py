import json
import requests
import argparse
import time
import os
import re
import pandas as pd
import sys

sleep_time = 60
confidence_threshold = 0.5


def save_json(name, data):
    file_name = name + ".json"
    with open(file_name, "w") as outfile:
        json.dump(data, outfile)


def get_file_name(raw_name):
    return re.sub(r"[><:\"\\\/|?*]", " ", raw_name)


def analyze_api(name, data):
    output = dict()
    categories = data["category_predictions"].keys()
    adjusted_value_predictions_keys = data['adjusted_value_predictions'].keys()
    value_predictions_keys = data["value_predictions"].keys()

    for i in range(len(data["fg_segments"])):
        save_data = dict()
        save_data["fg_segments"] = data["fg_segments"][i]
        save_data["value_predictions"] = []
        save_data["adjusted_value_predictions"] = []
        save_data["category_predictions"] = []

        for cat in categories:
            current = data["category_predictions"][cat][i]
            if current > confidence_threshold:
                save_data["category_predictions"].append((cat, current))

        for key in value_predictions_keys:
            current = data["value_predictions"][key][i]
            if current > confidence_threshold:
                save_data["value_predictions"].append((key, current))

        for cat in save_data["category_predictions"]:
            for key in save_data["value_predictions"]:
                pattern = cat[0] + "_" + key[0]
                if pattern in adjusted_value_predictions_keys:
                    current = data["adjusted_value_predictions"][pattern][i]
                    save_data["adjusted_value_predictions"].append((pattern, current))

        output[i] = save_data

    save_json(name + "_analysis", output)


def access_api(output_dir, names, url_list, api_key):
    api_url = "https://pribot.org/api/web/analyzeNewPolicy"
    json_dict = {
        "key": api_key,
    }

    for name, url in zip(names, url_list):
        if not url or type(url) == float:  # empty or N/A in csv
            print("ERROR: {} is missing policy url".format(name), file=sys.stderr)
            continue

        json_dict["url"] = url
        response = requests.request("POST", api_url, json=json_dict)
        try:
            data = response.json()
        except:
            print("ERROR: Bad response for {} | status {}".format(name, response.status_code), file=sys.stderr, end="")
            if response.status_code == 200:
                print(" ({})".format(response.text), file=sys.stderr)
            print(file=sys.stderr)
            time.sleep(sleep_time)
            continue

        file_name = os.path.join(output_dir, get_file_name(name))
        save_json(file_name + "_output", data)

        if data["status"] != "success":
            print("ERROR: Unsuccessful request for {} | status {}".format(name, data["status"]), file=sys.stderr)
        else:
            analyze_api(file_name, data)
            print(file_name)

        time.sleep(sleep_time)


def main(args):
    if not os.path.exists(args.url_list):
        print("ERROR: Invalid path for url file given", file=sys.stderr)
        return

    if not os.path.exists(args.output_dir):
        os.mkdir(args.output_dir)

    if args.url_list[-3:] == "csv":
        infile = pd.read_csv(args.url_list)
        for col in infile.columns:
            if re.search(r'Privacy.Policy', col):
                urls = infile[col]
            # if re.search(r'Package.Name', col):
            #   names = infile[col]
            if re.search(r'App.Title', col):
                names = infile[col]

    if urls.empty or names.empty:
        print("ERROR: Couldn't load names or urls", file=sys.stderr)
    else:
        access_api(args.output_dir, names, urls, args.api_key)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Access Polisis's API for privacy policy links given")
    parser.add_argument("output_dir", help="Output directory", type=str)
    parser.add_argument("url_list", help="Path to url list file", type=str)
    parser.add_argument("api_key", help="Polisis API key", type=str)
    args = parser.parse_args()

    main(args)
