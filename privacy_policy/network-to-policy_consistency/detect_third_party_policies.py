#!/usr/bin/env python3

from collections import defaultdict
import csv
import os
from pathlib import Path
import re
import shutil
import sys
from urllib.parse import urlsplit

import bs4

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(SCRIPT_DIR, '..', 'code'))
from lib.TermPreprocessor2 import TermPreprocessor as tprep


DATA_ROOT = Path(sys.argv[1])
try:
    append_mode = sys.argv[2] == 'append'
except IndexError:
    append_mode = False

tprep.initialize(DATA_ROOT / 'data')
URL_MAPPING = {
    # the first one of each entity is actually used
    '//unity3d.com/legal/privacy-policy': 'unity',

    '//www.oculus.com/legal/privacy-policy': 'oculus',
    '//www.facebook.com/policy.php': 'facebook',
    '//www.facebook.com/about/privacy': 'facebook',

    '//www.epicgames.com/site/en-US/privacypolicy': 'epic',

    '//amplitude.com/privacy': 'amplitude',
    '//amplitude.com/amplitude-security-and-privacy/privacy': 'amplitude',

    '//playfab.com/terms': 'playfab',

    '//policies.google.com/privacy': 'google',
    '//www.google.com/policies/privacy': 'google',
    '//www.google.com/intl/en/policies': 'google',
    '//www.google.com/intl/en-GB/policies/privacy': 'google',
    '//www.gstatic.com/policies/privacy/pdf': 'google',
    '//readalong.google/intl/en_US/privacy': 'google',

    '//mixpanel.com/legal/privacy-policy': 'mixpanel',
    '//mixpanel.com/legal/privacy-overview': 'mixpanel',
}

policy_urls = dict()
with open(DATA_ROOT / 'data' / 'policheck_flows.csv', newline='') as fin:
    reader = csv.DictReader(fin)
    csv_fields = reader.fieldnames
    all_csv_rows = []

    for row in reader:
        all_csv_rows.append(row)
        package_name = row['app_id']
        policy_urls[package_name] = row['developer_privacy_policy']

app_policies = defaultdict(set)
for filepath in (DATA_ROOT / 'html_policies').iterdir():
    package_name, _ = os.path.splitext(filepath.name)
    if package_name.startswith('@extra'):
        continue

    with filepath.open() as fin:
        soup = bs4.BeautifulSoup(fin, 'lxml')

    url_set = set()

    # check HTML links
    for item in soup("a", href=True):
        parsed = urlsplit(item["href"])
        if parsed.scheme in ['http', 'https']:
            url_set.add(parsed._replace(scheme="", query="", fragment="").geturl())

    # check URL-like string in the text as well
    for string in soup.body.strings:
        for url in re.findall(r'(https?://[^\s]+)', string):
            # remove trailing periods/brackets
            url = re.sub(r'[.)\]]+$', '', url)
            parsed = urlsplit(url)
            if parsed.scheme in ['http', 'https']:
                url_set.add(parsed._replace(scheme="", query="", fragment="").geturl())

    for url in url_set:
        for url_prefix in URL_MAPPING:
            if url.startswith(url_prefix):
                app_policies[package_name].add(URL_MAPPING[url_prefix])
                break
        else:
            # print unknown but possible policy URLs
            if re.search(r'(policy|policies|privacy|term)', url) \
                    and not re.search(r'(generator|template)', url):
                entity = tprep.resolve_domain(urlsplit(url).hostname, package_name,
                                              policy_urls.get(package_name, ''), '')
                if entity != 'we':
                    print(package_name, url, entity)

with open(DATA_ROOT / 'data' / 'policheck_flows_new.csv', 'w', newline='') as fout:
    writer = csv.DictWriter(fout, csv_fields)
    writer.writeheader()

    for row in all_csv_rows:
        package_name = row['app_id']
        policy_set = set(app_policies[package_name])
        if append_mode:
            policy_set.update(row['extra_policies'].split('+'))
        row['extra_policies'] = '+'.join(policy_set)
        writer.writerow(row)

shutil.move(
    DATA_ROOT / 'data' / 'policheck_flows_new.csv',
    DATA_ROOT / 'data' / 'policheck_flows.csv')
