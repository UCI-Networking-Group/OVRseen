#!/bin/bash

VERSION="latest"
#VERSION="tag/14.0.8"
#VERSION="tag/15.0.2"
#VERSION="tag/14.2.18"

mkdir all_libs
cd all_libs
#wget -qO - https://github.com/frida/frida/releases/latest | grep -o "\/frida\/frida\/releases\/download\/.*\/frida-gadget-.*-android-.*\.so\.xz" | sed 's/\/frida\/frida/https:\/\/github\.com\/frida\/frida/g' | sed 's/%0A/\n/g' > list.txt
wget -qO - https://github.com/frida/frida/releases/$VERSION | grep -o "\/frida\/frida\/releases\/download\/.*\/frida-gadget-.*-android-.*\.so\.xz" | sed 's/\/frida\/frida/https:\/\/github\.com\/frida\/frida/g' | sed 's/%0A/\n/g' > list.txt
wget -i list.txt
unxz *.xz
mkdir arm64 arm64-v8a armeabi armeabi-v7a x86 x86_64
# arm64
cp *-arm64.so arm64
mv arm64/*.so arm64/libfrida-gadget.so
cd arm64/; zip -r lib-arm64.zip libfrida-gadget.so; cd ..
mv arm64/lib-arm64.zip ..
# arm64-v8a
cp *-arm64.so arm64-v8a
mv arm64-v8a/*.so arm64-v8a/libfrida-gadget.so
cd arm64-v8a/; zip -r lib-arm64-v8a.zip libfrida-gadget.so; cd ..
mv arm64-v8a/lib-arm64-v8a.zip ..
# armeabi
cp *-arm.so armeabi
mv armeabi/*.so armeabi/libfrida-gadget.so
cd armeabi/; zip -r lib-armeabi.zip libfrida-gadget.so; cd ..
mv armeabi/lib-armeabi.zip ..
# armeabi-v7a
cp *-arm.so armeabi-v7a
mv armeabi-v7a/*.so armeabi-v7a/libfrida-gadget.so
cd armeabi-v7a/; zip -r lib-armeabi-v7a.zip libfrida-gadget.so; cd ..
mv armeabi-v7a/lib-armeabi-v7a.zip ..
# x86
cp *-x86.so x86
mv x86/*.so x86/libfrida-gadget.so
cd x86/; zip -r lib-x86.zip libfrida-gadget.so; cd ..
mv x86/lib-x86.zip ..
# x86-64
cp *-x86_64.so x86_64
mv x86_64/*.so x86_64/libfrida-gadget.so
cd x86_64/; zip -r lib-x86_64.zip libfrida-gadget.so; cd ..
mv x86_64/lib-x86_64.zip ..
find . -name ".DS_*" -type f -delete
find . -name "*~*" -type f -delete
rm -rf *.so
rm -rf list.txt
#zip -r ../all_all_libslib.zip *
cd ..
#rm -rf all_libs/
