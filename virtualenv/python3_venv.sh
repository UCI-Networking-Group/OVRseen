#!/bin/bash

set -e
pip3 install virtualenv

# Create a new virtual environment if it hasn't been created or use the existing one
if [[ ! -d python3_venv ]]; then
	echo ""
	echo "[+] Creating a new python3_venv virtual environment..."
	echo ""
	virtualenv -p python3 python3_venv
	# Alternative command below
	#python3 -m venv python3_venv
	source python3_venv/bin/activate
	# Traffic collection
	pip3 install unicodecsv==0.14.1
	pip3 install termcolor==1.1.0
	pip3 install tldextract==3.1.2
	pip3 install frida-tools==10.3.0
	pip3 install frida==15.1.3
	pip3 install utils==1.0.1
	pip3 install selenium==3.141.0
	# Post-processing
	pip3 install pandas==1.3.3
	pip3 install pandasql==0.7.3
	pip3 install adblockparser==0.7
	pip3 install urllib3==1.26.7
	# Network-to-policy consistency and purpose extraction
	pip3 install spacy==2.0.18
	pip3 install msgpack==0.5.6
	pip3 install beautifulsoup4==4.10.0
	pip3 install pdfminer.six==20201018
	pip3 install lxml==4.6.3
	pip3 install html2text==2020.1.16
	pip3 install langdetect==1.0.9
	pip3 install roman==3.3
	pip3 install networkx==2.6.3
	pip3 install tldextract==3.1.2
	pip3 install pyyaml==5.4.1
	pip3 install matplotlib==3.4.3
	pip3 install seaborn==0.11.2
	pip3 install gdown==4.0.1
else
	echo "[+] Found an existing python3_venv virtual environment... Reusing it!"
	echo "[!] Please remove the existing python3_venv and rerun this script if the existing one is broken!"
	echo ""
	source python3_venv/bin/activate
fi
