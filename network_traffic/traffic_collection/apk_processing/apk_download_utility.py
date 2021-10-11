'''
	This script downloads the newly installed apps' APKs from the device:
	1) First, it will save the installed APK information into a file for reference (if such a file doesn't exist yet).
	2) Next, when we use this script to download APKs, it will check the latest installed APK information
	   against the stored file, i.e., see the difference and download the new APKs
'''

from argparse import ArgumentParser
import csv
import datetime
import os
import re
import subprocess


COL_APP_NAME = 'app_name'
COL_PACKAGE_NAME = 'pkg_name'


# Get installed APK info
def get_installed_apk_info():
    # Get the installed APK info
    command = "adb -d shell pm list packages -3 | tr -d '\r' | sed 's/package://g'"
    output = subprocess.check_output(command, shell = True)
    # Don't forget the remove the trailing '\n' with '-1'
    apk_list = re.split(r"\n", output.decode('utf-8').strip())

    return apk_list


# Write installed APK info into a file
def write_installed_apk(info_file):
    # Get installed APK info
    apk_list = get_installed_apk_info()
    # Write the list into a file
    file = open(info_file, 'w')
    for apk in apk_list:
        print(f"[+] Adding {apk} into {info_file}...")
        file.write(apk + '\n')
    file.close()


# Download APK if it is not in the installed APK list yet
def download_new_apk(info_file, apk_dir):
    # Get installed APK info
    apk_list = get_installed_apk_info()
    # Read the list into a file
    installed_apks = set(line.strip() for line in open(info_file))
    # We never need to download AntMonitor
    installed_apks.add("edu.uci.calit2.anteatermo.dev")
    # CSV rows with app data.
    csv_rows = []
    for apk in apk_list:
        # Download the new APKs
        if apk not in installed_apks:
            # Get the APK path on the device
            command = "adb -d shell pm path " + apk + " | tr -d '\r' | sed 's/package://g'"
            output = subprocess.check_output(command, shell = True)
            apk_path = output.decode('utf-8').strip()
            if not os.path.exists(apk_dir):
                # Create the directory if it doesn't exist
                command = "mkdir " + apk_dir
                output = subprocess.check_output(command, shell = True)
                print(f"[+] Created new directory {apk_dir}/...")
            # Use the path to download the APK if the APK hasn't been downloaded yet
            if not os.path.isfile(apk_dir + "/" + apk + ".apk"):
                command = "adb -d pull " + apk_path + " " + apk_dir + "/"
                output = subprocess.check_output(command, shell = True)
                print(f"[+] Downloaded {apk_path}...")
                # Renaming the APK into package name
                command = "mv " + apk_dir + "/base.apk " + apk_dir + "/" + apk + ".apk"
                output = subprocess.check_output(command, shell = True)
                print(f"[+] Renamed APK file into {apk_dir}/{apk}.apk...")
                command = "aapt dump badging " + apk_dir + "/" + apk + ".apk"
                output = subprocess.check_output(command, shell = True)
                app_name = output.decode('utf-8').split("application: label='")[1].split("'")[0].strip("'\"\n\t ")
                csv_row = { COL_APP_NAME:app_name, 
                            COL_PACKAGE_NAME:apk }
                csv_rows.append(csv_row)
                print(f"[+] Saved app {app_name} into CSV file...")
            else:
                print(f"[-] " + apk_dir + "/" + apk + ".apk has previously been downloaded...")
            # Download the OBB file also if it hasn't been downloaded
            if not os.path.exists(apk_dir + "/obb/"):
                 # Create the directory if it doesn't exist
                command = "mkdir " + apk_dir + "/obb/"
                output = subprocess.check_output(command, shell = True)
                print(f"[+] Created new directory {apk_dir}/obb/...")               
            if not os.path.exists(apk_dir + "/obb/" + apk):
                command = "adb -d shell ls /sdcard/Android/obb/"
                output = subprocess.check_output(command, shell = True)
                # Check if this app has OBB
                if output.decode('utf-8').find(apk) != -1:
                    command = "adb -d pull /sdcard/Android/obb/" + apk + " " + apk_dir + "/obb/"
                    output = subprocess.check_output(command, shell = True)
                    print(f"[+] Downloaded OBB file into {apk_dir}/obb/{apk}/...")
                else:
                    print("[-] No OBB file found for " + apk)
            else:
                print(f"[-] " + apk_dir + "/obb/" + apk + " has previously been downloaded...")
            # Uninstall the app from the device
            command = "adb -d uninstall " + apk
            output = subprocess.check_output(command, shell = True)
            print(f"[+] Uninstalled app {apk}...")           
            # New line
            print("\n")
    # Save everything into a CSV file
    save_into_csv(csv_rows)


# Write the app data to a CSV file.
def save_into_csv(csv_rows):
    timestamp_fmt = datetime.datetime.now().strftime('%Y-%m-%d_%H%M')
    with open('./app-list-' + timestamp_fmt + '.csv' , 'w+', newline='') as csvf:
        columns = [COL_APP_NAME, COL_PACKAGE_NAME]
        csv_writer = csv.DictWriter(csvf, fieldnames=columns)
        csv_writer.writeheader()
        for row in csv_rows:
            csv_writer.writerow(row)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("installed_apk_info", type=str, help="path to file that will contain the saved installed APK info")
    parser.add_argument("--apk_dir", type=str, help="path to directory that will contain downloaded APK files")
    args = parser.parse_args()
    info_file = args.installed_apk_info

    # Check if installed_apk_info has already existed (if so, then we will download the new APKs)
    if not os.path.isfile(info_file):
        print("[.] Creating a new installed APK info file...")
        write_installed_apk(info_file)
    else:
        if args.apk_dir != None:
            apk_dir = args.apk_dir
            print("[.] Installed APK info file exists...")
            print("[.] Downloading newly installed APK files now...\n")
            download_new_apk(info_file, apk_dir)
        else:
            print(f"[.] Installed APK info file {info_file} already exists...")
