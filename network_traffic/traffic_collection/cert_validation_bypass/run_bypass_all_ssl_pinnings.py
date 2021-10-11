'''
1) This script uses the technique to find hooked function address in universal_libunity_function_search.py.
2) Then it replaces the address in the bypass_ssl_pinning_unity.js with a real address.
3) Finally, it saves it as _bypass_ssl_pinning_unity.js.
'''

from argparse import ArgumentParser
import os
import subprocess
import re
from difflib import get_close_matches

# Path and file name of the Frida script.
FRIDA_SCRIPT_PATH = 'frida_hooks'
FRIDA_SCRIPT_FILE = 'bypass_all_ssl_pinnings.js'
CHANGED_LINE = 'const function_offset = '
ARM_64BIT = 'arm64-v8a'
ARM_32BIT = 'armeabi-v7a'

# From the apk_builder.py script
WORK_DIR = "/tmp/appmon_apk"


def get_address(apk_dir, arch, pre, sig):
    # find the signature within the file
    file_path = os.path.join(apk_dir, 'lib', arch, 'libunity.so')
    offset = open(file_path, 'rb').read().find(bytes.fromhex(pre + sig))
    if offset != -1:
        return hex(offset + 4)

    # return None if signature is not found
    return 0x0


def get_sig(unity_dir, version, arch, function):
    path = os.path.join(unity_dir, version)
    if not os.path.exists(path):
        try:
            version = get_close_matches(version, os.listdir(unity_dir), n = 1)[0]
            path = os.path.join(unity_dir, version)
        except IndexError:
            return None

    # find symbol file for the given unity version
    # Full version
    #file_path = os.path.join(path, 'il2cpp', 'Release', 'Symbols', arch, 'libunity.sym.so')
    # Stripped down version
    file_path = os.path.join(path, 'Symbols', arch, 'libunity.sym.so')
    command = 'nm -a ' + file_path + ' | grep -m 1 ' + function + '; exit 0'
    # look for function address
    output = subprocess.check_output(command, shell = True)
    # the Unity versions that are before 2018 do not have mbedtls symbols (maybe they did not use the mbedtls library before then)
    if not output:
        print("INFO: Unity versions before 2018 do not have mbedtls symbols/do not use the mbedtls library")
        return None, None

    output = re.split(r"\s", output.decode('utf-8'), 1)
    address = re.search(r'[^0].*', output[0])   # strip front 0s
    # we need to get 4 bytes before and 16 bytes after the address
    address = int(address.group(0), 16)
    pre_addr = address - 4

    # look for func signature at the address found 
    # Full version
    #file_path = os.path.join(path, 'il2cpp', 'Release', 'Libs', arch, 'libunity.so')
    # Stripped down version
    file_path = os.path.join(path, 'Libs', arch, 'libunity.so')
    # get the function signature itself
    command = 'xxd -l 16 -g 16 -s ' + str(address) + ' ' + file_path + ' ; exit 0'
    signature = subprocess.check_output(command, shell = True)
    signature = re.split(r"\s", signature.decode('utf-8'))
    # get the 4-byte preamble
    command = 'xxd -l 4 -g 4 -s ' + str(pre_addr) + ' ' + file_path + ' ; exit 0'
    preamble = subprocess.check_output(command, shell = True)
    preamble = re.split(r"\s", preamble.decode('utf-8'))

    # return the unique 4-byte preamble and 20-byte signature
    return preamble[1], signature[1]


def get_arch(apk_dir):
    # arch is found by checking contents of lib folder
    try:
        arch_dirs = os.listdir(os.path.join(apk_dir, 'lib'))
        # if there are two then we have to choose arm64-v8a (i.e., ARM_64BIT)
        if ARM_32BIT in arch_dirs:
            arch = ARM_32BIT
        if ARM_64BIT in arch_dirs:
            arch = ARM_64BIT
        return arch

    except IndexError:
        return None


def get_version(apk_dir):
    # find all files in unzipped_apk/assets/bin/Data/
    path = os.path.join(apk_dir, 'assets', 'bin', 'Data')
    files = (file for file in os.listdir(path) if os.path.isfile(os.path.join(path, file)))
    # iterate over the files and find the Unity version
    for file in files:
        # find the unity version, stated within file
        command = 'xxd ' + os.path.join(apk_dir, 'assets', 'bin', 'Data', file) + '; exit 0'
        output = subprocess.check_output(command, shell = True)
        lines = re.split(r"\n", output.decode('utf-8'), 2)
        # version is within bytes [18, 27], which is usually shown in second line of output
        # has format 20xx.x.xxx
        for line in lines:
            result = re.search(r"20[\w]{2}\.[\w]+\.[\w]+f[\w]+", line)
            if result:
                return result.group(0).strip()

    return None


def get_existing_unzipped_apk(apk_dir):
    # check if we need to get the existing unzipped APK left by the apk_builder.py script
    if apk_dir.find(".apk") != -1:
        # if this is the original apk file then we need to get the existing unzipped APK
        return True

    return False


def is_apk(lib_name, apk_dir):
    # check if we need to get the existing unzipped APK left by the apk_builder.py script
    lib = os.path.join(apk_dir, 'lib')
    arch = os.listdir(lib)[0]
    path_to_so = os.path.join(lib, arch)
    # find libunity.so
    for so_file in os.listdir(path_to_so):
        if so_file == lib_name:
            return True

    return False


def main(apk_dir, unity_dir, function):
    if get_existing_unzipped_apk(apk_dir):
        # this generator will always return one result, i.e., the unzipped APK directory
        dir_gen = (item for item in os.listdir(WORK_DIR) if not os.path.isfile(os.path.join(WORK_DIR, item)))
        apk_dir = os.path.join(WORK_DIR, next(dir_gen))

    if not os.path.exists(apk_dir):
        print("ERROR: Invalid apk path given")
        return 0x0

    if not os.path.exists(unity_dir):
        print("ERROR: Invalid unity path given")
        return 0x0

    # Check if this is really a Unity APK
    if not is_apk('libunity.so', apk_dir):
        if is_apk('libUE4.so', apk_dir):
            # Check if this is an Unreal APK instead
            return 0x1
        else:
            # If neither then return 0x0
            return 0x0

    version = get_version(apk_dir)
    if not version: 
        print("ERROR: Couldn't find unity version")
        return 0x0
    print("Unity version: " + version)

    arch = get_arch(apk_dir)
    print("Architecture: " + arch)
    if not arch: 
        print("ERROR: Couldn't find unity architecture")
        return 0x0

    pre, sig = get_sig(unity_dir, version, arch, function)
    if not pre or not sig:
        print("ERROR: Couldn't find signature")
        return 0x0

    func_addr = get_address(apk_dir, arch, pre, sig)
    if func_addr != 0x0:
        print(f"{function} is found at address {func_addr}...")
    else:
        print(f"{function} is not found... returning address 0x0...")

    return func_addr


# replace the address in bypass_ssl_pinning_unity.js with the address found
def replace_addr(func_addr):
    # original Frida script
    file = os.path.join(FRIDA_SCRIPT_PATH, FRIDA_SCRIPT_FILE)
    frida_script = open(file, 'r')
    # new Frida script with the actual function address
    newfile_name = "_" + FRIDA_SCRIPT_FILE
    newfile = os.path.join(FRIDA_SCRIPT_PATH, newfile_name)
    frida_newscript = open(newfile, 'w')
    # read and replace the function address
    lines = frida_script.readlines()
    for line in lines:
        if line.find(CHANGED_LINE) != -1:
            line = CHANGED_LINE + str(func_addr)
        frida_newscript.write(line)

    frida_script.close()
    frida_newscript.close()

    print(f"Rewriting {FRIDA_SCRIPT_FILE} into {newfile_name}...")


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("apk_dir", type=str, help="absolute path to unzipped apk")
    parser.add_argument("unity_dir", type=str, help="path to unity directory containing version dirs")
    parser.add_argument("function", type=str, help="searched function name")
    args = parser.parse_args()

    # find function address
    func_addr = main(args.apk_dir, args.unity_dir, args.function)
    # replace the function address and write to a new file
    if func_addr == 0x1:
        print("INFO: Not looking for function address... This is an Unreal APK...")
    elif func_addr == 0x0:
        print("INFO: Function was not found, or this is neither a Unity nor Unreal APK...")
    else:
        print("INFO: Function was found... This is a Unity APK...")

    replace_addr(func_addr)
