#!/usr/bin/python

###
# This file is a part of OVRseen <https://athinagroup.eng.uci.edu/projects/ovrseen/>.
# Copyright (c) 2021 UCI Networking Group.
#
# OVRseen is dual licensed under the MIT License and the GNU General Public
# License version 3 (GPLv3).
#
# See the LICENSE.md file along with OVRseen for more details.
#
# This file incorporates content from AppMon <https://github.com/dpnishant/appmon>.
# Copyright (c) 2016 Nishant Das Patnaik.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# https://github.com/dpnishant/appmon/blob/master/apk_builder/apk_builder.py
###

import os, sys, re, argparse, codecs
import subprocess, pwd, glob, shutil
import time, zipfile, traceback
from termcolor import colored

parser = argparse.ArgumentParser()
parser.add_argument('--apk', action='store', dest='apk_path', help='''(absolute) path to APK''', required=True)
parser.add_argument('--keystore_pw', action='store', dest='keystore_pw',  help='''keystore password for APK signing''', required=True)
parser.add_argument('--device_arch', action='store', dest='device_arch', default='arm64-v8a', help='''Architecture of Device''')
parser.add_argument('--inject_frida', action='store_true', help='''Inject frida-gadget into the APK''')
parser.add_argument('--use_aapt2', action='store_true', help='''Use aapt2 instead of aapt to check the APK''')
parser.add_argument('--downgrade_api', action='store_true', help='''Downgrade the Android API''')
parser.add_argument('--inject_internet_perm', action='store_true', help='''Makes sure the APK has internet access permission''')

parser.add_argument('-v', action='version', version='AppMon APK Builder v0.1, Copyright 2016 Nishant Das Patnaik')

print("""
     ___      .______   .______   .___  ___.   ______   .__   __. 
    /   \     |   _  \  |   _  \  |   \/   |  /  __  \  |  \ |  | 
   /  ^  \    |  |_)  | |  |_)  | |  \  /  | |  |  |  | |   \|  | 
  /  /_\  \   |   ___/  |   ___/  |  |\/|  | |  |  |  | |  . `  | 
 /  _____  \  |  |      |  |      |  |  |  | |  `--'  | |  |\   | 
/__/     \__\ | _|      | _|      |__|  |__|  \______/  |__| \__| 
					    github.com/dpnishant
                                                                  
""")


args = parser.parse_args()
print(args)

apk_path = args.apk_path
keystore_pw = args.keystore_pw
use_aapt2 = args.use_aapt2

new_apk_path = ""
aligned_apk_path = ""
renamed_apk_path = ""

# Change to Android 6.0 and SDK API Level 23
old_android_manifest_header_1 = '<?xml version="1.0" encoding="utf-8" standalone="no"?><manifest xmlns:android="http://schemas.android.com/apk/res/android" android:compileSdkVersion="23" android:compileSdkVersionCodename="6" android:installLocation="auto" package="'
old_android_manifest_header_2 = '" platformBuildVersionCode="23" platformBuildVersionName="6">\n'

if not os.path.isfile(apk_path):
    print("[E] File doesn't exist: %s\n[*] Quitting!" % (apk_path))
    sys.exit(1)

SMALI_DIRECT_METHODS = """    .method static constructor <clinit>()V
    .locals 1
    .prologue
    const-string v0, "frida-gadget"
    invoke-static {v0}, Ljava/lang/System;->loadLibrary(Ljava/lang/String;)V
    return-void
.end method
"""

SMALI_DIRECT_METHODS_INSTRUCTOR_EXISTS = """ 
    .prologue
    const-string v0, "frida-gadget"
    invoke-static {v0}, Ljava/lang/System;->loadLibrary(Ljava/lang/String;)V
"""

SMALI_PROLOGUE = """    const-string v0, "frida-gadget"
    invoke-static {v0}, Ljava/lang/System;->loadLibrary(Ljava/lang/String;)V
"""

WORK_DIR = "/tmp/appmon_apk"
LIB_FILE_PATH = "lib.zip"

lib_dir = ""
marker = 0
method_start = 0
method_end = 0
constructor_start = 0
constructor_end = 0
prologue_start = 0
header_range = range(0, 0)
footer_range = range(0, 0)
header_block = ""
footer_block = ""

try:
	
	if os.path.isdir(WORK_DIR):
		print("[I] Preparing work directory...")
		shutil.rmtree(WORK_DIR)
	os.makedirs(WORK_DIR)

	print("[I] Expanding APK...")

	if use_aapt2:
		apk_dump = subprocess.check_output(["aapt2", "dump", "badging", apk_path]).decode('utf-8')
	else:
		apk_dump = subprocess.check_output(["aapt", "dump", "badging", apk_path]).decode('utf-8')
	#uncomment the follwing when installing a VR apk. 
	apk_xml_tree = subprocess.check_output(["aapt", "dump", "xmltree", apk_path, "AndroidManifest.xml"]).decode('utf-8')
	apk_permissions = subprocess.check_output(["aapt", "dump", "permissions", apk_path]).decode('utf-8')
	package_name = apk_dump.split("package: name=")[1].split(" ")[0].strip("'\"\n\t ")
	app_name = apk_dump.split("application: label='")[1].split("'")[0].strip("'\"\n\t ")
	manifest_file_path = os.path.join(WORK_DIR, package_name, "AndroidManifest.xml")

	new_apk_path = WORK_DIR + "/" + package_name + ".apk"
	print("New Apk Path:" + new_apk_path)

	subprocess.call(["cp", apk_path, new_apk_path])
	subprocess.call(["apktool", "-f", "--quiet", "decode", new_apk_path])
	subprocess.call(["mv", package_name, WORK_DIR])

	# Find the right architecture info from the folder lib
	# There is usually just one architecture in the lib directory for Oculus VR...
	# We need to also handle a case where we have both architectures
	arcs = next(os.walk(WORK_DIR + os.sep + package_name + os.sep + "lib"))[1]
	# Write app name, package name, and game type (Unity or Unreal) into a file
	csv_file = open('./apps-under-test.csv' , 'a+')
	apk_type = 'Others'
	# Check the type of platform (Unity vs. Unreal) from the first lib subfolder seen
	if os.path.exists(os.path.join(WORK_DIR, package_name, 'lib', arcs[0], 'libunity.so')):
		apk_type = 'Unity'
	elif os.path.exists(os.path.join(WORK_DIR, package_name, 'lib', arcs[0], 'libUE4.so')):
		apk_type = 'Unreal'
	csv_file.write(app_name + ', ' + package_name + ', ' + apk_type + '\n')
	csv_file.close()

	if args.inject_internet_perm:
		if not "uses-permission: name='android.permission.INTERNET'" in apk_permissions:
			print("[I] APK needs INTERNET permission")
			with codecs.open(manifest_file_path, 'r', 'utf-8') as f:
				manifest_file_contents = f.readlines()

			for line_num in range(0, len(manifest_file_contents)):
				print(manifest_file_contents[line_num])
				if "android.permission.INTERNET" in manifest_file_contents[line_num]:
					manifest_file_contents.insert(line_num, "    <uses-permission android:name=\"android.permission.INTERNET\"/>\n")
					with codecs.open(manifest_file_path, 'w', 'utf-8') as f:
						manifest_file_contents = "".join(manifest_file_contents)
						f.write(manifest_file_contents)
						print("\tSuccess: Added Internet Permission into APK")
					break
		else:
			print("\tAlready have internet permission")
	
	if args.downgrade_api:
		#print("\n\n\n\nDEBUG: ORIGINAL ANDROID MANIFEST!")
		#with codecs.open(manifest_file_path, 'r', 'utf-8') as f:
		#	manifest_file_contents = f.readlines()
		#for line_num in range(0, len(manifest_file_contents)):
		#	print(manifest_file_contents[line_num])
		
		print("[I] Change AndroidManifest header to Android 6.0 and API Level 23 to allow it to use mitmproxy certificate")
		with codecs.open(manifest_file_path, 'r', 'utf-8') as f:
			manifest_file_contents = f.readlines()
		#print(manifest_file_contents[0])
		# NOTE: The following lines cause a bug when dealing with apps created with Godot Engine. 
		# A different package name, other than the actual APK name, will be generated, e.g., com.godot.game.
		# We have to skip 9 characters, namely 'package="'
		#package_name_start = manifest_file_contents[0].find('package="') + 9
		#package_name_end = manifest_file_contents[0].find('"', package_name_start)
		#package_name = manifest_file_contents[0][package_name_start:package_name_end]
		manifest_file_contents[0] = old_android_manifest_header_1 + package_name + old_android_manifest_header_2
		with codecs.open(manifest_file_path, 'w', 'utf-8') as f:
			manifest_file_contents = "".join(manifest_file_contents)
			f.write(manifest_file_contents)
			print("\tSuccess: AndroidManifest header to Android 6.0 and API Level 23")

		#print("\n\n\n\nDEBUG: CHANGED ANDROID MANIFEST!")
		#with codecs.open(manifest_file_path, 'r', 'utf-8') as f:
		#	manifest_file_contents = f.readlines()
		#for line_num in range(0, len(manifest_file_contents)):
		#	print(manifest_file_contents[line_num])

	
	if args.inject_frida:
		print("[I] Attempting to inject frida-gadget")
		try:
			#uncomment the follwing when installing a VR apk
			launchable_activity = apk_xml_tree.split("E: application")[1].split("E: activity")[1].split("A: android:name")[1].split("\"")[1].strip("'\"\n\t ")
			
			#comment the follwing line when installing a VR apk. 
			#launchable_activity = apk_dump.split("launchable-activity: name=")[1].split(" ")[0].strip("'\"\n\t ")
			print("\tLaunchable Activity:" + launchable_activity)

		except IndexError:
			print("No launchable activity found")
			sys.exit(1)

		launchable_activity_path = os.path.join(WORK_DIR, package_name, "smali", launchable_activity.replace(".", os.sep) + ".smali")

		if not os.path.isfile(launchable_activity_path):
			print("\tCould not find .smali file at %s" % launchable_activity_path)
			smali_file_name = launchable_activity_path.split(os.sep)[-1]
			tmp_apk_path = os.path.join(WORK_DIR, package_name)
			print("\tSearching in apk directory %s for file %s: " % (tmp_apk_path, smali_file_name))
			for root, dirs, files in os.walk(tmp_apk_path):
				for tmp_file in files:
					if tmp_file == smali_file_name:
						launchable_activity_path = os.path.join(root, tmp_file)
						print("\tFound .smali file at %s" % launchable_activity_path)

		print("\t[I] Searching .smali")
		with codecs.open(launchable_activity_path, 'r', 'utf-8') as f:
			file_contents = f.readlines()
		
		for line in range(0, len(file_contents)):
			if "# direct methods" in file_contents[line]:
				method_start = line
			if "# virtual methods" in file_contents[line]:
				method_end = line

		marker = method_start + 1

		if (method_end - method_start) > 1:
			for cursor in range(marker, method_end):
				if ".method static constructor <clinit>()V" in file_contents[cursor]:
					constructor_start = cursor
					marker = constructor_start + 1
					break
			for cursor in range(marker, method_end):
				if ".end method" in file_contents[cursor]:
					constructor_end = cursor + 1
					break
			for cursor in range(marker, constructor_end):
				if ".prologue" in file_contents[cursor]:
					prologue_start = cursor
					marker = cursor + 1
		
		header_range = range(0, marker)
		footer_range = range(marker, len(file_contents))

		for line_num in header_range:
			header_block += file_contents[line_num]
		for line_num in footer_range:
			footer_block += file_contents[line_num]

		if prologue_start > 1:
			renegerated_smali = header_block + SMALI_PROLOGUE + footer_block
		elif constructor_start > 1:
			renegerated_smali = header_block + SMALI_DIRECT_METHODS_INSTRUCTOR_EXISTS + footer_block
		else:
			renegerated_smali = header_block + SMALI_DIRECT_METHODS + footer_block

		print("\t[I] Patching .smali")
		with codecs.open(launchable_activity_path, 'w', 'utf-8') as f:
			#print renegerated_smali
			f.write(renegerated_smali)
			print("\tSuccess: patched smali file " + launchable_activity_path + " for frida-gadget" )


		# Fix for issue #15 (app starting bug)
		# Architecture is determined automatically, so update the library file path 
		# 	with the name "lib-" + arc, e.g., lib-arm64-v8a, lib-armeabi-v7a
		for arc in arcs:
			lib_dir = os.path.join(WORK_DIR, package_name, "lib" + os.sep + arc)
			if not os.path.isdir(lib_dir):
				os.makedirs(lib_dir)
			unzip_output = subprocess.check_output(["unzip", "lib-" + arc, "-d", lib_dir])
			print("\tSuccess: Injected libs for frida-gadget with arch " + arc)

	print("[I] Building APK")
	#shutil.rmtree(os.path.join(WORK_DIR, package_name, "original/META-INF"))

	# Bug fix: apktool uses aapt and it seems that for one APK, aapt throws an error.
	# In this situation, we can tell apktool to use aapt2.
	# See https://stackoverflow.com/questions/57441409/how-fix-brut-androlib-androlibexception-brut-common-brutexception-could-not-ex
	if use_aapt2:
		build_apk_output = subprocess.check_output(["apktool", "build", "--use-aapt2", os.path.join(WORK_DIR, package_name)])
	else:
		build_apk_output = subprocess.check_output(["apktool", "build", os.path.join(WORK_DIR, package_name)])

	new_apk_path = "%s/%s.apk" % (os.path.join(WORK_DIR, package_name, "dist"), package_name)
	aligned_apk_path = "%s/%s-zipaligned.apk" % (os.path.join(WORK_DIR, package_name, "dist"), package_name)
	signed_apk_path = "%s/%s-zipaligned-signed.apk" % (os.path.join(WORK_DIR, package_name, "dist"), package_name)
	#renamed_apk_path = "%s/%s.apk" % (os.path.join(WORK_DIR, package_name, "dist"), os.path.basename(apk_path).split(".apk")[0] + "-appmon")
	renamed_apk_path = "%s/%s" % (os.path.join(WORK_DIR, package_name, "dist"), "_" + os.path.basename(apk_path))
	appmon_apk_path = os.path.join(os.getcwd(), "_" + os.path.basename(apk_path))

	print("\t" + new_apk_path)
	print("\t" + aligned_apk_path)
	print("\t" + appmon_apk_path)
	print("\t" + renamed_apk_path)

	print("[I] Aligning APK")
	subprocess.check_output(["zipalign", "-v", "-p", "4", new_apk_path, aligned_apk_path])

	align_verify = subprocess.check_output(["zipalign", "-v", "-c", "4", aligned_apk_path]).decode('utf-8')
	align_verify.strip(" \r\n\t")
	if not "Verification successful" in align_verify:
		print("\t[E] alignment verification failed")
	else:
		print("\t[I] APK alignment verified")

	# 
	print("[I] Signing APK")
	sign_status = subprocess.check_output(["apksigner", "sign", "--verbose", "--ks", "appmon.keystore", "--ks-pass", \
		"pass:" + keystore_pw, "--out", signed_apk_path, aligned_apk_path]).decode('utf-8')
	print("\t" + str(sign_status))
	if not "Signed" in sign_status:
		print("\t[E] APK signing error %s" % (sign_status))

	
	sign_verify = subprocess.check_output(["apksigner", "verify", "--verbose", signed_apk_path]).decode('utf-8')
	print(sign_verify)
	if not "Verified using v1 scheme (JAR signing): true" in sign_verify \
		and not "Verified using v2 scheme (APK Signature Scheme v2): true" in sign_verify:
		print(sign_verify)
	else:
		print("[I] APK signature verified")

	print("[I] Housekeeping")
	subprocess.call(["mv", signed_apk_path, renamed_apk_path])
	subprocess.call(["mv", renamed_apk_path, os.getcwd()])
	subprocess.call(["rm", new_apk_path, aligned_apk_path])


	if os.path.isfile(appmon_apk_path):
		print("[I] Ready: %s" % (appmon_apk_path))

except Exception as e:
	traceback.print_exc()
	sys.exit(1)
