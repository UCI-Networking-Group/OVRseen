#!/bin/bash

# Unzip the OVRseen_datasets.zip
unzip ../OVRseen_datasets.zip -d ../

# PCAPs
# Copy and extract all PCAP files
unzip ../OVRseen_datasets/pcaps/PCAPs.zip -d ../network_traffic/post-processing/
#unzip "../network_traffic/post-processing/PCAPs/Oculus-Free/*.zip" -d ../network_traffic/post-processing/PCAPs/Oculus-Free/
unzip "../network_traffic/post-processing/PCAPs/Oculus-Paid/*.zip" -d ../network_traffic/post-processing/PCAPs/Oculus-Paid/
#unzip "../network_traffic/post-processing/PCAPs/SideQuest/*.zip" -d ../network_traffic/post-processing/PCAPs/SideQuest/
rm -rf ../network_traffic/post-processing/PCAPs/Oculus-Free/
rm -rf ../network_traffic/post-processing/PCAPs/SideQuest/

# Privacy policies
unzip ../OVRseen_datasets/privacy_policies/privacy_policies.zip -d ../privacy_policy/network-to-policy_consistency/

# Intermediate outputs
mv ../OVRseen_datasets/lists_of_apps/*.csv ../network_traffic/post-processing/
cp ../OVRseen_datasets/intermediate_outputs/all-merged-with-esld-engine-privacy-developer-party.csv ../network_traffic/post-processing/
mv ../OVRseen_datasets/intermediate_outputs/all-merged-with-esld-engine-privacy-developer-party.csv ../privacy_policy/network-to-policy_consistency/
unzip ../OVRseen_datasets/intermediate_outputs/polisis_output.zip -d ../privacy_policy/purpose_extraction/ext/

# Remove OVRseen_datasets.zip to save space
rm ../OVRseen_datasets.zip