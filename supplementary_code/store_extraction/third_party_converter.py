from argparse import ArgumentParser
import json 
import csv 
import os
import unicodedata

def get_all_headers(input_dir, variable_headers):
    headers = []

    for filename in os.listdir(input_dir):
        full_path = os.path.join(input_dir, filename) 
        data = json.load(open(full_path, 'r'))
        for key in data.keys():
            if key not in headers:
                headers.append(key)

        if not variable_headers:
            break

    headers.sort()
    return headers

def merge_data(input_dir, outfile, headers):
    count = 0
    with open(outfile, 'w', newline='') as data_file:
        csv_writer = csv.DictWriter(data_file, fieldnames=headers)    # create the csv writer object 

        csv_writer.writeheader()    # write header 
        for filename in os.listdir(input_dir):
            if not filename.endswith(".json"):
                print("Skipping ", filename)
            else:
                full_path = os.path.join(input_dir, filename)
                data = json.load(open(full_path, 'r', encoding='utf-8'))

                for k, v in data.items():
                    if isinstance(v, str):
                        data[k] = unicodedata.normalize('NFKD', v).encode('ascii', 'ignore').decode("utf-8")
                    elif isinstance(v, list):
                        
                        for i in range(len(v)):
                            if isinstance(v[i], str):
                                v[i] = unicodedata.normalize('NFKD', v[i]).encode('ascii', 'ignore').decode("utf-8")

                try:
                    csv_writer.writerow(data)    # Writing data of CSV file 
                except ValueError as err:
                    print(filename, "has error", err)

                count += 1

    # data_file.close() 
    return count

def main(input_dir, outfile, variable_headers):
    if not os.path.exists(input_dir):
        print("ERROR: Invalid input directory path given")
        return

    headers = get_all_headers(input_dir, variable_headers)
    count = merge_data(input_dir, outfile, headers)
    print("Combined", count, "files into", outfile)

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("input_dir", type=str, help="path to folder that holds input files")
    parser.add_argument("outfile", type=str, help="name of excel output file")
    parser.add_argument("--variable_headers", help = "Flag if json files don't all have same keys", action="store_true", default=False)

    args = parser.parse_args()
    main(args.input_dir, args.outfile, args.variable_headers)

