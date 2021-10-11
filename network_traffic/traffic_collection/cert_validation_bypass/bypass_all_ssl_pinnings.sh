#!/bin/bash

# Function to print usage
print_usage()
{
	echo ""
	echo "A utility script to bypass SSL pinnings."
	echo -e  "Usage:\tbypass_all_ssl_pinnings.sh [options]"
	echo ""
	echo -e "\t-h\t(print this usage info)"
	echo ""
	echo -e "\t-l\t<path-to-libunity>\t-a\t<path-to-apk>\t[-u]\t<unzip-if-this-option-used>"
	echo ""
	exit 1
}


# Execute SSL pinning bypass
execute_ssl_pinning_bypass()
{
	# First argument is the path to the Unity
	UNITY_PATH=$1
	# Second argument is the path to the APK
	# We first take the package name from current_apk created by frida_automate
	if [ ! -f current_apk ]; then
		echo "ERROR: The file current_apk is not found!"
		exit 1
	fi
	PKG_NAME=$(cat current_apk)
	APK_PATH=$2/$PKG_NAME.apk
	# Third argument specifies whether we need to unzip or not
	NEED_UNZIP=$3

	# Set this to default value
	UNZIPPED_APK=$APK_PATH
	# Unzip the APK first
	if [[ $NEED_UNZIP == '-u' ]]
	then
		echo "==> Unzipping APK file: $APK_PATH"
		UNZIPPED_APK=${APK_PATH%.*}
		unzip $APK_PATH -d $UNZIPPED_APK
	else
		echo "==> Using existing unzipped APK file..."
	fi
	
	# Clear adb logcat
	echo "==> Clearing adb logcat first..."
	adb logcat -c

	# Run run_bypass_all_ssl_pinnings.py
	echo "==> Extracting the address of function mbedtls_x509_crt_verify_with_profile for the current app..."
	python3 run_bypass_all_ssl_pinnings.py $UNZIPPED_APK $UNITY_PATH mbedtls_x509_crt_verify_with_profile

	# Run Frida script
	echo -e "==> Running Frida script to perform SSL pinning bypass..."
	#frida -U Gadget -l frida_hooks/_bypass_all_ssl_pinnings.
	# Frida 14.2.14 uses package name instead of 'Gadget'
	#frida -U $PKG_NAME -l frida_hooks/_bypass_all_ssl_pinnings.js
	# Moving to Frida 15.0.8 and it is using 'Gadget' again.
	frida -U Gadget -l frida_hooks/_bypass_all_ssl_pinnings.js
}


###
# Main body of script
###
# Get input argument and execute the right function
if [[ $1 == '-l' ]] && [[ $3 == '-a' ]]
then
	execute_ssl_pinning_bypass $2 $4 $5
else
	# Print usage info if there is any mistake
	print_usage
fi