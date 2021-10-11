#!/bin/bash

#apktool b -o repackaged.apk apk_output/ -f
#jarsigner -sigalg SHA1withRSA -digestalg SHA1 -keystore custom.keystore -storepass 123456 repackaged.apk mykeyaliasname
#jarsigner -verify repackaged.apk
#zipalign -f 4 repackaged.apk repackaged_new.apk

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

# $1 is the path to OBB files
# $2 is the keystore password
# $3 is the path to APK file
# TODO: Use the following command to have apktool select between aapt and aapt2 (some apps need aapt and some others aapt2).
python3 apk_builder.py --keystore_pw $2 --apk $3 --inject_frida --downgrade_api --inject_internet_perm
#python3 apk_builder.py --keystore_pw $2 --apk $3 --use_aapt2 --inject_frida --downgrade_api --inject_internet_perm

APK_FILE=$(basename $3)
path="_$APK_FILE"
echo $APK_FILE
echo $path
adb -d install $path
# Copy OBB file
PKG_NAME=$(get_package_name $3)
# First argument is the path to all OBB files
if [[ -d $1/$PKG_NAME ]]
then
	adb -d push $1/$PKG_NAME /sdcard/Android/obb/
fi
# Make a file to save the current APK package name
echo $PKG_NAME > ../cert_validation_bypass/current_apk