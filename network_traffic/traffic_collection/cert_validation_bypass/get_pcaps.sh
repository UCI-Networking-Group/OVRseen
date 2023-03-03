#!/bin/bash

# Function to print usage
print_usage()
{
	echo ""
	echo "A utility script to pull the captured PCAP files from the device."
	echo -e  "Usage:\tget_pcaps.sh [options]"
	echo ""
	echo -e "\t-h\t(print this usage info)"
	echo ""
	echo -e "\t-d\t<destination-directory>"
	echo ""
	exit 1
}


# Get index of substring from a longer string/text
get_substring_index()
{
	# First argument is the main text
	TEXT=$1
	# Second argument is the searched string
	SUBSTR=$2
	# Get the subtext of the text before the position of SUBSTR
	SUBTEXT="${TEXT%%$SUBSTR*}"
	# Return/print the index of the SUBSTR
	[[ "$SUBTEXT" = "$TEXT" ]] && echo -1 || echo "${#SUBTEXT}"
}


# Get package name
# NOTE: The following function is not used in the current version (kept here for documentation)
get_package_name()
{
	# First argument is APK path
	APK_PATH=$1
	# Get APK info
	APP_INFO=$(aapt dump badging $APK_PATH)
	#echo $APP_INFO
	# We skip the first string: "package: name= '"
	START_IND=15
	# Find the second marker string: "' versionCode=""
	END_IND=$(get_substring_index "$APP_INFO" "' versionCode")
	# Find the length of substring
	LENGTH=$(expr $END_IND - $START_IND)
	echo ${APP_INFO:$START_IND:$LENGTH}
}


# Get PCAP files
get_pcap_files()
{
	# First argument is the destination directory
	DEST_DIR=$1
	# Second argument is the path to APK file
	# We first take the package name from current_apk created by frida_automate
	if [ ! -f current_apk ]; then
		echo "ERROR: The file current_apk is not found!"
		exit 1
	fi
	PKG_NAME=$(cat current_apk)
	# Get PCAP files from the device
	echo "==> Pulling captured PCAP files..."
	if [[ ! -d $DEST_DIR ]]
	then
		mkdir $DEST_DIR
	fi
	# Pull per directory
	adb -d pull /sdcard/antmonitor
	# Rename the directory
	echo -e "==> PCAP files are stored in $DEST_DIR/$PKG_NAME..."
	# Move per directory
	rm -rf $DEST_DIR/$PKG_NAME
	mv antmonitor $DEST_DIR/$PKG_NAME
	# Delete the PCAP files on the device
	adb -d shell 'rm -rf /sdcard/antmonitor/*'
	# Save the logcat_output.log file
	echo -e "==> Saving logcat output into $DEST_DIR/$PKG_NAME..."
	adb -d logcat -d > $DEST_DIR/$PKG_NAME/logcat_output.log

	# Uninstall the app
	echo -e "==> Uninstalling $PKG_NAME..."
	adb -d uninstall $PKG_NAME
}


###
# Main body of script
###
# Get input argument and execute the right function
if [[ $1 == '-d' ]]
then
	# Send intent to AntWall to stop the network traffic capture
	#adb -d shell am broadcast \
	#	-a edu.uci.calit2.anteater.client.android.vpn.STOPBACKGROUND \
	#	-n edu.uci.calit2.anteatermo.dev/edu.uci.calit2.anteater.client.android.device.DeviceBootListener
	# Sleep for a bit
	#sleep 3
	get_pcap_files $2
else
	# Print usage info if there is any mistake
	print_usage
fi
