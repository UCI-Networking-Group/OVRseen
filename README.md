[![DOI](https://zenodo.org/badge/411401488.svg)](https://zenodo.org/badge/latestdoi/411401488)
# OVRseen
This is the repository for OVRSeen, a system and framework to perform network traffic and privacy policy analyses on VR apps on Oculus Quest 2. OVRSeen was developed and used in the paper [OVRseen: Auditing Network Traffic and Privacy Policies in Oculus VR](https://www.usenix.org/conference/usenixsecurity22/presentation/trimananda). 

Please read the paper first before using OVRSeen. Please also visit our [OVRseen project page](https://athinagroup.eng.uci.edu/projects/ovrseen/) for more information on the project, including dataset releases.

# Citation
If you create a publication (including web pages, papers published by a third party, and publicly available presentations) using OVRSeen, please cite the corresponding paper as follows:
```
@inproceedings{trimananda2022ovrseen,
  title     = {{OVRseen: Auditing Network Traffic and Privacy Policies in Oculus VR}},
  author    = {Trimananda, Rahmadi and Le, Hieu and Cui, Hao and Tran Ho, Janice and 
               Shuba, Anastasia and Markopoulou, Athina},
  booktitle = {Proceedings of the 31st USENIX Security Symposium (USENIX Security 22)},
  year      = {2022}
}
```
We also encourage you to provide us ([athinagroupreleases@gmail.com](mailto:athinagroupreleases@gmail.com)) with a link to your publication. We use this information in reports to our funding agencies.

# Getting Started
## Downloading OVRseen
One can get started by downloading this repository to a local computer by running the following command.
```
$ git clone https://github.com/UCI-Networking-Group/OVRseen.git
```
## Our Datasets
Please also download [our datasets here](https://athinagroup.eng.uci.edu/projects/ovrseen/ovrseen-datasets/) if one wants to test the entire flow of OVRseen without collecting their own datasets. We will give you access to download these datasets after you fill out the consent form. Then, you can download the zipped file and place it in the `OVRseen` folder on your local machine (after downloading our OVRseen repository); to use `gdown` (as shown in the command below), one has to first activate the Python virtual environment as specified in the [Dependencies section](https://github.com/UCI-Networking-Group/OVRseen#dependencies) below (`gdown` is part of Python libraries). Next, run the `extract_datasets.sh` script to copy the necessary dataset files into the right directories. We can also use the following command to download the zipped file (please replace `<datasets-zipped-file-id>` with the file ID in the download link).
```
OVRseen $ gdown https://drive.google.com/uc?id=<datasets-zipped-file-id> # Downloading our datasets can also be done using a web browser
OVRseen $ cd supplementary_code
OVRseen/supplementary_code $ ./extract_datasets.sh
```
## OVRseen Wiki
Our [Wiki page](https://github.com/UCI-Networking-Group/OVRseen/wiki) contains more information about OVRseen and how to use it (OVRseen has been tested on **Ubuntu 20.04.3 LTS**).

## Virtual Machine
For convenience, please use our [Ubuntu 20.04.3 LTS virtual machine (VM) that can be downloaded here](https://ucirvine.sharepoint.com/:u:/s/athinagroup/ER0CAXmEuNBKtG1soIVsNJYBPsfLnTYK-7wkHtJiLz4JhA?e=ZQFXmV) (login password: `ovrseen`) to run OVRseen; please first download OVRseen (and our datasets) following the above instructions after booting up the VM.

## A Quick Demo: Try OVRseen Yourself
Please note that the VM is set up with 4GB of RAM and 30GB of hard disk capacity. These resources are enough to run the demo of OVRseen as explained in the page [Try OVRseen Yourself](https://github.com/UCI-Networking-Group/OVRseen/wiki/Try-OVRseen-Yourself).

## Running OVRseen on Our Full Datasets
One has to increase the RAM (at least a 20GB RAM is needed) and disk capacity (preferrably around 80-100GB) to run the complete flow of [OVRseen's traffic collection](https://github.com/UCI-Networking-Group/OVRseen/wiki/Traffic-Collection) on our full datasets (e.g., [the entire collection of Unity library files alone consumes around 19GB of disk space](https://github.com/UCI-Networking-Group/OVRseen/wiki/Traffic-Collection#setup)). Please see [this page on how to change the virtual disk size](https://www.howtogeek.com/124622/how-to-enlarge-a-virtual-machines-disk-in-virtualbox-or-vmware/) and [this page on how to use GParted to change the partition size on Ubuntu 20.04.3](https://www.howtogeek.com/114503/how-to-resize-your-ubuntu-partitions/). This is a [short tutorial video on how to use GParted on Ubuntu 20.04.3](https://ucirvine.sharepoint.com/:v:/s/athinagroup/ES4gzefLb7NLrh608-CSEuwBn1OcDB1r_NWyn-q8JaMOYg?e=dXg56r).

# Dependencies
OVRseen depends on other tools and many Python packages. Please check the [list of OVRseen's dependencies on our Wiki page](https://github.com/UCI-Networking-Group/OVRseen/wiki#dependencies) for more information. These dependencies have been installed properly in the provided Ubuntu 20.04.3 LTS virtual machine (VM), but they are yet to be installed on a local machine if the VM is not used. Please note that different machines, OSes, tool versions, Python packages, and setups may not produce the same results (and may even cause runtime errors) even when OVRseen is run on the same dataset.
For Python dependencies, please use the script that creates a new Python virtual environment before executing OVRseen.
```
OVRseen/virtualenv $ ./python3_venv.sh
OVRseen/virtualenv $ source python3_venv/bin/activate
```
We can invoke the `deactivate` command to deactivate the virtual environment when it is no longer needed.

# License
OVRseen is dual-licensed under the [MIT License](https://opensource.org/licenses/MIT) and the [GNU General Public License version 3 (GPLv3)](https://www.gnu.org/licenses/gpl-3.0.en.html) (please see `COPYING-MIT.txt` and `COPYING-GPL3.txt` files in this repository). Please see the file LICENSE.md or visit [this Wiki page](https://github.com/UCI-Networking-Group/OVRseen/wiki/OVRseen-License) to learn more about OVRseen's licensing.

# Disclaimer
We make no warranties that OVRseen is free of errors. Please read the [paper](https://arxiv.org/abs/2106.05407) and [Wiki](https://github.com/UCI-Networking-Group/OVRseen/wiki) so that you understand what OVRseen is supposed to do.

# Contact
Please feel free to contact us for more information at properdata@uci.edu. Bug reports are welcome, and we are happy to hear from our users.
