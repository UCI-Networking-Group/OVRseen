#!/usr/bin/python

# This file is a part of OVRseen <https://athinagroup.eng.uci.edu/projects/ovrseen/>.
# Copyright (c) 2021 UCI Networking Group.
#
# This file incorporates content from NoMoAds <http://athinagroup.eng.uci.edu/projects/nomoads/>.
# Copyright (C) 2018 Anastasia Shuba, University of California, Irvine.
#
# OVRseen is dual licensed under the MIT License and the GNU General Public
# License version 3 (GPLv3). This file is covered by the GPLv3. If this file
# get used, GPLv3 applies to all of OVRseen.
#
# See the LICENSE.md file along with OVRseen for more details.

import os
import math

# Global variables used by other scripts
GENERAL_FILE_NAME = 'general.json'

# Classification labels
LABEL_POSITIVE = 1
LABEL_NEGATIVE = 0

# JSON keys
json_key_type = "type"
json_key_rule = 'rule'
json_key_tk_flag = 'tk_flag' # whether the packet is ad-related or not
json_key_ad_label = 'ad' # whether the packet is ad-related or not
json_key_ad_pkg = "package_responsible" # which app is responsible for the ad
json_key_package_name = 'package_name' # which app generated the packet
json_key_version = "package_version"
json_key_pii_types = 'pii_types'    # a list
json_key_predicted_types = 'predict_piiTypes'
json_key_domain = 'domain'
json_key_host = 'host'
json_key_uri = 'uri'
json_key_headers = 'headers'
json_key_dst_port = "dst_port"
json_key_dst_ip = 'dst_ip'

# Headers for CSV files
hAdLibs = 'ad_libraries'
hPkgName = 'package'

# when reading in a list of directories, use this delimiter
DIR_DELIMITER = ";;"


def readable_dir(prospective_dir):
    if not os.path.isdir(prospective_dir):
        raise Exception("readable_dir:{0} is not a valid path".format(prospective_dir))
    if os.access(prospective_dir, os.R_OK):
        return prospective_dir
    else:
        raise Exception("readable_dir:{0} is not a readable dir".format(prospective_dir))


def readable_dirs(prospective_dirs):
    existing_dirs = []
    split_dirs = prospective_dirs.split(DIR_DELIMITER)
    for dir in split_dirs:
        if not os.path.isdir(dir):
            print("WARNING: readable_dirs:{0} is not a valid path".format(dir))
        else:
            existing_dirs.append(dir)

    if len(existing_dirs) == 0:
        raise Exception("No valid directories found in %s", prospective_dirs)

    return existing_dirs
