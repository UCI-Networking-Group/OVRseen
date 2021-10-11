#!/usr/bin/env python

import csv
import os
from pathlib import Path
import pickle
import re
import shlex
import sys

import spacy

import lib.Consistency as con
import lib.ConsistencyDatabase as conDB
from lib.TermPreprocessor2 import TermPreprocessor
spacy.prefer_gpu()

DATA_ROOT = Path(sys.argv[1])
TermPreprocessor.initialize(DATA_ROOT / 'data')


def fixEntityLemma(txt, nlp):
    def getLemma(tok):
        return tok.lemma_ if tok.lemma_ != '-PRON-' else tok.text
    doc = nlp(txt)
    return ' '.join([getLemma(t) for t in doc if t.pos != spacy.symbols.DET ])

def LOG_ERROR(outputfilename, message):
    with open(DATA_ROOT / 'log' / outputfilename, 'a', encoding='utf-8') as logfile:
        print(message, file=logfile)

# dataMap for Oculus Quest2
# TODO: The following list needs to be curated more carefully!
DATA_MAP = {
    'android_id': 'android id',
    'app_name': 'app name',
    'build_version': 'build version',
    'cookie': 'cookie',
    'device_id': 'device id',
    'email': 'email address',
    'flags': 'flags',
    'geographical_location': 'geographical location',
    'hardware_info': 'hardware information',
    'person_name': 'person name',
    'sdk_version': 'sdk version',
    'serial_number': 'serial number',
    'session_info': 'session information',
    'system_version': 'system version',
    'language': 'language',
    'usage_time': 'usage time',
    'user_id': 'user id',
    'vr_field_of_view': 'vr field of view',
    'vr_ipd': 'vr pupillary distance',
    'vr_play_area': 'vr play area',
    'vr_movement': 'vr movement',
    'vr_position': 'vr movement',
    'vr_rotation': 'vr movement',
}

def loadFlowResults(filename, packageName, cdb):
    pNameNoVers = re.sub(r'-[0-9]+$', '', packageName)
    flows = []
    extra_policies = set()

    with open(filename) as fin:
        for row in csv.DictReader(fin):
            row = {k: v if v != 'N/A' else '' for k, v in row.items()}

            package_name = row['app_id']
            if package_name != pNameNoVers:
                continue

            dest_domain = row['hostname'] or row['dst_ip']
            data_type = row['pii_types']
            developer_name = row['creator']
            privacy_policy = row['developer_privacy_policy']

            # extra (platform / SDK / ...) policies to be loaded
            extra_policies.update(row['extra_policies'].split('+'))

            resolvedEntity = TermPreprocessor.resolve_domain(dest_domain, package_name, privacy_policy, developer_name)
            resolvedData = DATA_MAP.get(data_type)

            if resolvedData is None:
                # log and continue
                LOG_ERROR('SkippedDataFlows.log', '{},{}'.format(data_type, packageName))
                continue

            if resolvedData not in con.DataObject.ontology.nodes:
                LOG_ERROR('SkippedDataFlowsOnt.log', '{},{}'.format(data_type, packageName))
                continue

            if resolvedEntity not in con.Entity.ontology.nodes:  # TODO log
                # possibly mark as unknown entity instead of skipping (Hao Cui)
                resolvedEntity = 'unknown entity'

                LOG_ERROR('SkippedEntityFlows.log', '{},{}'.format(dest_domain, packageName))
                #continue

            # TODO Don't put a duplicates...
            dflow = con.DataFlow((resolvedEntity, resolvedData))
            if dflow not in flows:
                flows.append(dflow)
                cdb.insertDataFlow(resolvedEntity, resolvedData)

            cdb.insertAppDataFlow(packageName, resolvedEntity, resolvedData, dest_domain, data_type)

    print('\tLoaded {} flows for {}'.format(len(flows), pNameNoVers))
    return flows, list(extra_policies)


def shouldIgnoreSentence(s):
    mentionsChildRegex = re.compile(r'\b(child(ren)?|kids|from\sminor(s)?|under\s1[0-9]+|under\s(thirteen|fourteen|fifteen|sixteen|seventeen|eighteen)|age(s)?(\sof)?\s1[0-9]+|age(s)?(\sof)?\s(thirteen|fourteen|fifteen|sixteen|seventeen|eighteen))\b', flags=re.IGNORECASE)
    mentionsUserChoiceRegex = re.compile(r'\b(you|user)\s(.*\s)?(choose|do|decide|prefer)\s.*\s(provide|send|share|disclose)\b', flags=re.IGNORECASE)
    mentionsUserChoiceRegex2 = re.compile(r'\b((your\schoice)|(you\sdo\snot\shave\sto\sgive))\b', flags=re.IGNORECASE)
    # TODO remove false positives that discuss "except as discussed in this privacy policy / below"
    mentionsExceptInPrivacyPol1 = re.compile(r'\b(except\sas\s(stated|described|noted))\b', flags=re.IGNORECASE)
    mentionsExceptInPrivacyPol2 = re.compile(r'\b(except\sin(\sthose\slimited)?\s(cases))\b', flags=re.IGNORECASE)

    if mentionsChildRegex.search(s) or mentionsUserChoiceRegex.search(s) or mentionsUserChoiceRegex2.search(s) or mentionsExceptInPrivacyPol1.search(s) or mentionsExceptInPrivacyPol2.search(s):
        return True
    return False


def loadPrivacyPolicyResults(filename, packageName, cdb, nlp, firstPartyNames, extraPolicyRules):
    if not os.path.isfile(filename):
        return []
    policy = []

    it = pickle.load(open(filename, 'rb'))
    for e, c, d, s in processPrivacyPolicyResults(it, packageName, nlp, firstPartyNames):
        cdb.insertPolicy(e, c, d)
        cdb.insertAppPolicySentence(s, (e, c, d), packageName)
        policy.append((e, c, d, s))

    for e, c, d, s in extraPolicyRules:
        cdb.insertPolicy(e, c, d)
        cdb.insertAppPolicySentence(s, (e, c, d), packageName)
        policy.append((e, c, d, s))

    return policy


def processPrivacyPolicyResults(it, packageName, nlp, firstPartyNames):
    for e, c, d, s, aLemma in it:

        if c == 'not_collect' and shouldIgnoreSentence(s):
            continue

        eproc = TermPreprocessor.map_entity(fixEntityLemma(e, nlp))
        if eproc.strip() == '' or eproc == 'IGNORE':
            continue

        if eproc in ['user', 'you', 'person', 'consumer', 'participant']:
            continue

        #TODO Should we try to resolve company name or ignore entity all together?
        # u'we_implicit'
        if eproc in ['we', 'i', 'us', 'me'] or eproc in ['app', 'mobile application', 'mobile app', 'application', 'service', 'website', 'web site', 'site'] or (e.startswith('our') and eproc in ['app', 'mobile application', 'mobile app', 'application', 'service', 'company', 'business', 'web site', 'website', 'site']):
            eproc = 'we'

        if eproc == 'third_party_implicit' or eproc == 'we_implicit' or eproc == 'anyone':
            continue

        # if eproc == u'third_party_implicit':
        #     eproc = u'third party'

        # fix non-pronoun first party names
        for name in e, eproc:  # try `e` as well in case words in `eproc` are lemmatized
            tokens = re.split(r'\W+', name.strip().lower())
            if tokens and tokens[-1].strip('.') in ['inc', 'llc', 'ltd']:
                tokens.pop()
            test_name = " ".join(tokens).strip()

            for fp_name in firstPartyNames:
                test_fp_name = " ".join(re.split(r'\W+', fp_name.lower())).strip()

                if test_fp_name.startswith(test_name) or test_name.startswith(test_fp_name):
                    eproc = 'we'
                    break

        dproc = TermPreprocessor.map_data(d)
        if dproc.strip() == '' or dproc == 'IGNORE':
            continue

        ents = []
        if eproc not in con.Entity.ontology.nodes:
            res = re.sub(r'\b(and|or|and/or|\/|&)\b', '\n', eproc)
            for e in res.split('\n'):
                e = e.strip()
                if e == '' or e == 'third_party_implicit' or e == 'we_implicit' or e == 'anyone':
                    continue

                e = TermPreprocessor.map_entity(fixEntityLemma(e, nlp))
                if e not in con.Entity.ontology.nodes:#This should really never happen...
                    LOG_ERROR('SkippedPolicyEntities.log',
                              ' '.join(shlex.quote(arg) for arg in [packageName, e, c, d, s]))
                    continue
                ents.append(e)
        else:
            ents = [eproc]

        if len(ents) == 0:
            LOG_ERROR('SkippedPolicyEntities.log',
                      ' '.join(shlex.quote(arg) for arg in [packageName, eproc, c, d, s]))
            continue

        if dproc in con.DataObject.ontology.nodes:
            if dproc in con.DataObject.ontology.nodes and dproc != con.DataObject.root:
                for e in ents:
                    yield e, c, dproc, s
        else:
            res = re.sub(r'\b(and|or|and/or|\/|&)\b', '\n', dproc)
            for d in res.split('\n'):
                d = d.strip()
                d = TermPreprocessor.map_data(fixEntityLemma(d, nlp))
                if d not in con.DataObject.ontology.nodes or d == con.DataObject.root:#This should really never happen...
                    LOG_ERROR('SkippedPolicyDataObjects.log',
                              ' '.join(shlex.quote(arg) for arg in [packageName, eproc, c, d, s]))
                    continue
                for e in ents:
                    if e == con.Entity.root:
                        continue
                    yield e, c, d, s


def getPackageName(policyFilename):
    fname,_ = os.path.splitext(os.path.basename(policyFilename))
    return fname

def doFilesExist(filelist):
    return all(os.path.exists(f) for f in filelist)

def main():
    consistency_database_path = DATA_ROOT / 'output' / 'consistency_results.db'
    cdb = conDB.ConsistencyDB(consistency_database_path)
    con.init(
        dataOntologyFilename=DATA_ROOT / 'data' / 'data_ontology.gml',
        entityOntologyFilename=DATA_ROOT / 'data' / 'entity_ontology.gml')
    # con.init_static()
    nlp = spacy.load(DATA_ROOT / 'NlpFinalModel')
    cdb.createTables()

    first_party_names = dict()
    with open(DATA_ROOT / 'output' / 'first_party_names.list') as fin:
        for line in fin:
            packageName, *alterNames = shlex.split(line.strip())
            first_party_names[packageName] = alterNames

    # load extra third-party (SDK / platform) policies
    extraPolicyRuleDB = dict()
    for fullpath in (DATA_ROOT / 'output' / 'policy').iterdir():
        packageName = getPackageName(fullpath.name)
        if packageName.startswith("@extra."):
            _, actualEntity = packageName.split(".", 1)
            extraPolicyRuleDB[actualEntity] = []

            for e, c, d, s in loadPrivacyPolicyResults(fullpath, packageName, cdb, nlp, [], []):
                s = "@%s: %s" % (actualEntity, s)
                # only include policies bound to this this entity
                # traslate 'we' to the actual entity
                if e == 'we' or e.lower() == actualEntity.lower():
                    # add a prefix so we easily know the sentence is not from the developer policy
                    extraPolicyRuleDB[actualEntity].append((actualEntity, c, d, s))

                    # apply oculus policy to facebook flows as well (TODO: better implementation)
                    if actualEntity == 'oculus':
                        extraPolicyRuleDB[actualEntity].append(('facebook', c, d, s))
                else:
                    extraPolicyRuleDB[actualEntity].append((e, c, d, s))

    # Let's walk the policy directory now...
    for fullpath in (DATA_ROOT / 'output' / 'policy').iterdir():
        polPath = fullpath.name
        packageName = getPackageName(polPath)
        if packageName.startswith("@extra."):
            continue

        print('Starting', polPath)
        flows, extraPolicies = loadFlowResults(DATA_ROOT / 'data' / 'policheck_flows.csv', packageName, cdb)

        # load extra third-party (SDK / platform) policies
        extraPolicyRules = []
        for e in extraPolicies:
            extraPolicyRules.extend(extraPolicyRuleDB.get(e, []))

        policy = loadPrivacyPolicyResults(
            fullpath, packageName, cdb, nlp,
            first_party_names[packageName],
            extraPolicyRules
        )
        policy = [con.PolicyStatement(p) for p in set(policy)]

        print('\tLoaded {} policy statements for {}'.format(len(policy), packageName))

        #PolicyLint Analysis...
        policyContradictions = con.getContradictions(policy, packageName)
        for (p0, p1), contradictionIndex in policyContradictions:
            print(p0,p1,contradictionIndex, packageName)
            print(cdb.insertContradiction(contradictionIndex, packageName, p0.getTuple(), p1.getTuple()))       

        #PoliCheck Analysis...
        if len(flows) == 0:
            LOG_ERROR('SkippedAppsNoFlows.log', packageName)
            continue

        consistencyResults = con.checkConsistency(policy, flows)
        for cres in consistencyResults:
            flow = cres['flow']
            isConsistent,policies,contradictions = cres['consistency']

            cdb.insertConsistencyResult(flow.entity.entity, flow.data.data, packageName, isConsistent)

            numContradictions = 0
            if policies is not None:
                for i,p in enumerate(policies):
                    pTuple = (p.entity.entity, p.action.action, p.data.data)
                    if contradictions is not None and contradictions[i] is not None:
                        for c,cnum in contradictions[i]:
                            numContradictions += 1
                            cTuple = (c.entity.entity, c.action.action, c.data.data)
                            cdb.insertConsistencyData(flow.entity.entity, flow.data.data, packageName, pTuple, cTuple, cnum)
                    else:
                        cdb.insertConsistencyData(flow.entity.entity, flow.data.data, packageName, pTuple, None, -1)

            numPolicies = len(policies) if policies is not None else 0
            print('\tFlow: {}\n\t\tIs Consistent: {}\n\t\tNum Policies: {}\n\t\tNum Contradictions: {}\n'.format(flow, isConsistent, numPolicies, numContradictions))

        print('Ending', polPath)


if __name__ == '__main__':
    main()
