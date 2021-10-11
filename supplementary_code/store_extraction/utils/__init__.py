import json
import re
import unicodedata
import os

def save_json(name, data, replace_dups = False):	
	file_name = name + ".json"
	if os.path.exists(file_name) and not replace_dups:
		file_name = name + "_dup.json"

	with open(file_name, "w") as outfile:
		json.dump(data, outfile)

def get_file_name(raw_name):
	name = re.sub("[><:\"\\\/|?*]", " ", raw_name)
	return normalize_text(name)

def normalize_text(raw):
	return unicodedata.normalize('NFKD', raw).encode('ascii', 'ignore').decode("utf-8")

def string_to_val(str_val):
	THOUSAND = 1000
	MILLION = 1000000

	if str_val == 'No':
		return 0
	elif str_val[-1] == 'k':
		return float(str_val[:-1]) * THOUSAND
	elif str_val[-1] == 'M':
		return float(str_val[:-1]) * MILLION
	else:
		return int(str_val)

def find_numeric_entries(entries_list):
	splits = []
	for i, s in enumerate(entries_list):
		if re.search(r'[\d]', s):
			splits.append(i)

	return splits

def format_key_string(raw):
	words = [w.capitalize() for w in re.split(r'[\s]+', raw)]
	return "_".join(words)