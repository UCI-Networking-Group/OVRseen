import csv
import os
from pathlib import Path
import re
import shlex
import sys

import spacy
import spacy.lang.en
spacy.prefer_gpu()

IGNORE_ENTITY_NAMES = set(spacy.lang.en.stop_words.STOP_WORDS)
IGNORE_ENTITY_NAMES.update({"com", "android", "free", "paid", "co"})
IGNORE_ENTITY_NAMES.update({"provider", "company", "website", "inc", "llc", "vr"})


def is_entity_valid(ent):
    flag = ent.label_ in {'PERSON', 'ORG'}
    flag = flag and ent.text.lower() not in IGNORE_ENTITY_NAMES
    flag = flag and re.search('[A-Z]', ent.text)
    return flag


def check_file(fin, nlp):
    for line in fin:
        line = line.strip()
        # Fix "xxx LLC" entity name
        line = line.replace("LLC", "Inc")

        if 'all rights reserved' in line.lower():
            # case 1: copyright <company name> all rights reserved
            doc = nlp(line)

            for sentence in doc.sents:
                if 'all rights reserved' in sentence.text.lower():
                    for ent in doc.ents:
                        if is_entity_valid(ent):
                            yield re.sub(r'(?:copyright\s*)?20[12]\d\W*', '', ent.text, flags=re.I)
        elif re.search(r"([\"'])(?:we|us|our)[^\W]*\1", line, re.I):
            # case 2: company name ("we"/"us"/"other names")
            doc = nlp(line)

            for sentence in doc.sents:
                bra_pairs = []
                bra_stack = []

                for idx, tok in enumerate(sentence):
                    if tok.text == '(':
                        bra_stack.append(idx)
                    elif tok.text == ')' and len(bra_stack) > 0:
                        left_idx = bra_stack.pop()

                        if len(bra_stack) == 0:
                            bra_text = sentence[left_idx + 1: idx].text

                            if re.search(r"([\"'])(?:we|us|our)[^\W]*\1", bra_text, re.I):
                                bra_pairs.append((left_idx, idx))

                for left_idx, right_idx in bra_pairs:
                    for ent in sentence.ents:
                        if (left_idx >= ent.end and re.search(r'\w', sentence[ent.end:left_idx].text) is None) \
                           or (ent.start >= left_idx and ent.end < right_idx):
                            if is_entity_valid(ent):
                                yield ent.text
        elif line.endswith("Privacy Policy") or line.endswith("PRIVACY POLICY"):
            # case 3: extract company/app name from title ("XXX GAME PRIVACY POLICY")
            doc = nlp(line)

            if len(list(doc.sents)) > 1 or len(doc.ents) != 1:
                continue

            if is_entity_valid(doc.ents[0]):
                yield doc.ents[0].text


def check_package_name(package_name):
    for item in package_name.split('.'):
        if item.lower() in IGNORE_ENTITY_NAMES or len(item) == 0:
            continue

        # ref: https://stackoverflow.com/questions/7593969
        tokens = re.split(r'(?<=[a-z])(?=[A-Z])', item)
        if len(tokens) > 1 or tokens[0][0].isupper():
            yield ' '.join(tokens)


def check_creator_name(creator):
    creator = creator.replace("LLC", "Inc")

    for e in re.split('[,()/]', creator):
        yield e


def trim_entity(e):
    e = re.sub(r'\W+(ltd|llc|inc)[^\w]*$', '', e, flags=re.I)
    e = re.sub(r'^\W+', '', e)
    e = re.sub(r'\W+$', '', e)
    return e


def main():
    DATA_ROOT = Path(sys.argv[1])
    OUTPUT_ROOT = DATA_ROOT / 'output'

    app_creators = dict()

    with open(DATA_ROOT / 'data' / 'policheck_flows.csv') as fin:
        for row in csv.DictReader(fin):
            app_creators[row['app_id']] = row['creator']

    os.makedirs(OUTPUT_ROOT, exist_ok=True)
    nlp = spacy.load(DATA_ROOT / 'NlpFinalModel')

    with (OUTPUT_ROOT / 'first_party_names.list').open("w") as fout:
        for filepath in (DATA_ROOT / 'plaintext_policies').iterdir():
            package_name, _ = os.path.splitext(filepath.name)
            if package_name.startswith('@'):
                continue

            entities = set()
            entities.update(check_package_name(package_name))

            if package_name in app_creators:
                entities.update(check_creator_name(app_creators[package_name]))

            with filepath.open() as fin:
                entities.update(check_file(fin, nlp))

            fixed_entities = set()
            for raw_e in entities:
                for item in raw_e, trim_entity(raw_e):
                    doc = nlp(item.strip() + ' will collect your identifier.')
                    for ent in doc.ents:
                        if is_entity_valid(ent) and ent.text != 'identifier':
                            fixed_entities.add(ent.text)
                            fixed_entities.add(trim_entity(ent.text))

            print(shlex.quote(package_name),
                  *[shlex.quote(n) for n in fixed_entities],
                  file=fout)


if __name__ == '__main__':
    main()
