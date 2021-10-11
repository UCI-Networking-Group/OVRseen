#!/usr/bin/python

"""
Use this script to merge encrypted/decrypted PCAP files into one
USAGE:
$ python merge_cap.py [-dec | -enc] PATH_TO_PCAP_DIRECTORY
"""

import os, sys

from subprocess import call
from subprocess import check_call


def merge_in_dir(encdec, dir_path):
    dir_path = os.path.abspath(dir_path)

    if not os.path.isdir(dir_path):
        print("ERROR: " + dir_path + " is not a directory!")
        sys.exit(-1)

    try:
        os.chdir(dir_path)
    except (WindowsError, OSError):
        print("Could not change directory to " + dir_path)

    files_to_merge = []
    for fn in os.listdir(dir_path):
        if encdec == '-enc' and fn.startswith("COMPLETED") and \
            fn.find("DECRYPTED") == -1:
            files_to_merge.append(fn)
        elif encdec == '-dec' and fn.startswith("COMPLETED_DECRYPTED"):
            files_to_merge.append(fn)

    baseDir = os.path.basename(os.path.realpath(dir_path))
    if encdec == '-enc':
        outFile = baseDir + "-ENC-out.pcapng"
    else:
        outFile = baseDir + "-DEC-out.pcapng"
    cmd = ["mergecap", "-w", outFile]
    cmd += files_to_merge

    call(cmd)
    print("Merged " + str(len(files_to_merge)) + " files into " + outFile)

    if encdec == '-enc':
        jsonFile = baseDir + "-ENC-out.json"
    else:
        jsonFile = baseDir + "-DEC-out.json"

    cmd = ["tshark",
           "-o", "tcp.analyze_sequence_numbers:TRUE",
           "-o", "tcp.desegment_tcp_streams:TRUE",
           "-o", "http.desegment_body:TRUE",
           "-r", outFile, "-T", "json"]

    with open(jsonFile, "wb") as jf:
        check_call(cmd, stdout=jf)

    print("Saved " + jsonFile)


if __name__ == '__main__':
    if len(sys.argv) != 3 or not (sys.argv[1] == '-dec' or sys.argv[1] == '-enc'):
        print("ERROR: incorrect number of arguments or wrong arguments. Correct usage:")
        print("\t$ python merge_cap.py [-dec | -enc] PATH_TO_PCAP_DIRECTORY")
        sys.exit(1)

    merge_in_dir(sys.argv[1], sys.argv[2])
