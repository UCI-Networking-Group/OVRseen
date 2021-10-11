#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re

from lxml import etree
import tldextract
import yaml


def loadAnnotations(filename='synonyms.xml'):
    def getTerm(node):
        return node.get('term')

    def loadAnnotInternal(node, ignoreList, synAnnot):
        if node.tag == 'node':
            term = getTerm(node)
            if term not in synAnnot:
                synAnnot[term] = term
            for child in node:
                if child.tag == 'synonym':
                    childTerm = getTerm(child)
                    if childTerm not in synAnnot:
                        synAnnot[childTerm] = term
                elif child.tag in ['node', 'ignore']:
                    loadAnnotInternal(child, ignoreList, synAnnot)
        elif node.tag == 'ignore':
            term = getTerm(node)
            ignoreList.append(term)
        elif node.tag == 'annotations':
            for child in node:
                loadAnnotInternal(child, ignoreList, synAnnot)

    ignoreList = []
    synonyms = {}
    tree = etree.parse(filename)
    root = tree.getroot()
    loadAnnotInternal(root, ignoreList, synonyms)
    return synonyms


class TermPreprocessor:
    entity_map = None
    data_map = None
    domain_map = None
    initialized = False

    @classmethod
    def initialize(cls, ont_root):
        def rmap(d):
            ret = dict()
            for name, li in d.items():
                for synonym in (li or []):
                    ret[synonym] = name
            return ret

        try:
            with open(os.path.join(ont_root, "entity_synonyms.yml")) as fin:
                d = yaml.safe_load(fin)
                cls.entity_map = rmap(d)

            with open(os.path.join(ont_root, "data_synonyms.yml")) as fin:
                d = yaml.safe_load(fin)
                cls.data_map = rmap(d)

            with open(os.path.join(ont_root, "domains.yml")) as fin:
                d = yaml.safe_load(fin)
                cls.domain_map = rmap(d)
        except FileNotFoundError:
            rd = loadAnnotations(os.path.join(ont_root, "synonyms.xml"))
            cls.entity_map = cls.data_map = cls.domain_map = rd

        cls.initialized = True

    @classmethod
    def __verify_initialization(cls):
        if not cls.initialized:
            raise RuntimeError("TermPreprocessor has not been initialized")

    @classmethod
    def __get_synonym(cls, term, synonym_dict):
        cls.__verify_initialization()
        term = preprocess_term(term)

        if term in synonym_dict:
            return synonym_dict[term]
        else:
            # Strip apostrophe and quotes
            term = re.sub(r'("|\'(\s*s)?)', '', term)
            return synonym_dict.get(term, term)

    @classmethod
    def map_entity(cls, term):
        return cls.__get_synonym(term, cls.entity_map)

    @classmethod
    def map_data(cls, term):
        return cls.__get_synonym(term, cls.data_map)

    @classmethod
    def resolve_domain(cls, domain, packageName, policyUrl, developerName):
        cls.__verify_initialization()
        domain = domain.lower()

        if isFirstParty(packageName, domain, policyUrl, developerName):
            return 'we'

        while '.' in domain:
            try:
                entity = cls.domain_map[domain]

                if packageName == entity:
                    return 'we'
                else:
                    return entity
            except KeyError:
                domain = domain.split('.', 1)[1]

        return None


#####
def isSafeSubstitution(term): #Don't sub if there's a chance there are multiple terms in a noun phrase
    return False if re.search(r'\b(and|or)\b', term) or re.search(r'(,|;)', term) else True

def isSimpleUsageInfoTerm(term):
    if not isSafeSubstitution(term):
        return False
    return True if re.search(r'^(information|data|datum|record|detail)\s+(about|regard|of|relate\sto)(\s+how)?\s+(you(r)?\s+)?(usage|use|uses|utilzation|activity)\s+(of|on|our)\s+.*$', term) else False

def isSimpleNonPersonalInfoTerm(term):
    if not isSafeSubstitution(term):
        return False
    if re.search(r'^(non-(pii|personally(\-|\s)identif(y|iable)\s(information|data|datum|detail)))$', term):
        return True
    return True if re.search(r'\b((information|data|datum|detail)\s.*\snot\sidentify\s(you|user|person|individual))\b', term) else False

def isSimplePersonallyIdentifiableInfoTerm(term):
    if not isSafeSubstitution(term):
        return False
#   if re.search(r'^((information|data|datum|detail)\sabout\syou)$', term):
#       return True
    if re.search(r'^(pii|personally(\-|\s)identif(y|iable)\s(information|data|datum|detail))$', term):
        return True
    return True if re.search(r'\b((information|data|datum|detail)\s.*\sidentify\s(you(rself)?|user|person|individual))\b', term) else False

def isSimpleIpAddr(term):
    if not isSafeSubstitution(term):
        return False
    return True if re.search(r'\b((ip|internet(\sprotocol)?)\saddress(es)?)\b', term) else False

def simpleSynonymSub(term):
    if not isSafeSubstitution(term):
        return term

    if isSimpleNonPersonalInfoTerm(term):
        term = 'non-personally identifiable information'
#       term = u'non-personally identifiable information'
    elif isSimplePersonallyIdentifiableInfoTerm(term):
        term = 'personally identifiable information'
#       term = u'personally identifiable information'
    elif isSimpleIpAddr(term):
        term = 'ip address'
    elif isSimpleUsageInfoTerm(term):
        term = 'usage information'
    return term

#####

def fixWhitespace(text):
    text = re.sub(r'^\s+', '', text)
    text = re.sub(r'\s+$', '', text)
    return re.sub(r'\s+', ' ', text)


def commonTermSubstitutions(term):
    # third-party --> third party
    term = re.sub(r'\b(third\-party)\b', 'third party', term)
    term = re.sub(r'\b(app(s)?|applications)\b', 'application', term)
    term = re.sub(r'\b(wi\-fi)\b', 'wifi', term)
    term = re.sub(r'\b(e\-\s*mail)\b', 'email', term)
    return fixWhitespace(term)

def stripIrrelevantTerms(term):
    pronRegex = re.compile(r'^(your|our|their|its|his|her|his(/|\s(or|and)\s)her)\b')
    irrevRegex = re.compile(r'^(additional|also|available|when\snecessary|obviously|technically|typically|basic|especially|collectively|certain|general(ly)?|follow(ing)?|important|limit(ed)?(\s(set|amount)\sof)?|more|most|necessary|only|optional|other|particular(ly)?|perhaps|possibl(e|y)|potential(ly)?|relate(d)?|relevant|require(d)?|select|similar|some(times)?|specific|variety\sof|various(\s(type|kind)(s)\sof)?)\b(\s*,\s*)?')
    while pronRegex.search(term) or irrevRegex.search(term):
        term = fixWhitespace(pronRegex.sub('', term))
        term = fixWhitespace(irrevRegex.sub('', term))
    return fixWhitespace(term)

def stripEtc(term):
    term = re.sub(r'\b(etc)(\.)?$', '', term)
    return fixWhitespace(term)

def subInformation(text):
    text = re.sub(r'\b(info|datum|data)\b', 'information', text)
    #this can happen when subbing data for information
    return fixWhitespace(re.sub(r'\b(information(\s+information)+)\b', 'information', text))


IGNORE_PACKAGE_TOKENS = ["com", "android", "free", "paid", "co"]
CLOUD_PROVIDER_DOMAINS = ["amazonaws.com", "digitaloceanspaces.com"]
DEVELOPER_FIRST_PARTY_TOKENS = ["oculus", "facebook", "unity"]

def isFirstParty(package_name, dest_domain, privacy_policy, developer_name):
    # tokenize package_name
    package_name_tokens = package_name.split(".")
    package_name_tokens = [x.lower() for x in package_name_tokens if x.lower() not in IGNORE_PACKAGE_TOKENS and len(x.strip()) > 2]

    dest_domain_parsed = tldextract.extract(dest_domain)

    # extract the eSLD for comparison
    # if it's hosted on a cloud service, take the subdomain instead
    if dest_domain_parsed.registered_domain in CLOUD_PROVIDER_DOMAINS:
        domain_cmp = dest_domain_parsed.subdomain
    else:
        domain_cmp = dest_domain_parsed.registered_domain

    # check privacy policy url first
    if privacy_policy and privacy_policy != "N/A":
        policy_domain_parsed = tldextract.extract(privacy_policy)
        if policy_domain_parsed.registered_domain == domain_cmp:
            return True

    # we double check if developer has FIRST_PARTY_TOKENS in it. If so, then we allow it.
    for developer_key in DEVELOPER_FIRST_PARTY_TOKENS:
        if developer_key in package_name_tokens and developer_key not in developer_name.lower():
            package_name_tokens.remove(developer_key)

    # check tokens in package name
    for token in package_name_tokens:
        if token in domain_cmp:
            return True

    return False


def preprocess_term(term):
    def subOrdinals(term):
        term = re.sub(r'\b(1st)\b', 'first', term)
        term = re.sub(r'\b(3rd)\b', 'third', term)
        return fixWhitespace(term)

    def stripQuotes(term):
        return fixWhitespace(re.sub(r'"', '', term))

    def stripBeginOrEndPunct(term):
        punctRegex = re.compile(r'((^\s*(;|,|_|\'|\.|:|\-|\[|/)\s*)|((;|,|_|\.|:|\-|\[|/)\s*$))')
        andOrRegex = re.compile(r'^(and|or)\b')
        while punctRegex.search(term) or andOrRegex.search(term):
            term = fixWhitespace(punctRegex.sub('', term))
            term = fixWhitespace(andOrRegex.sub('', term))
        return term

    ##############

    # term = cleanupUnicodeErrors(term)  NOTE: Already fixed in the preprocessor (Hao Cui)

    # Strip unbalanced parentheses
    if not re.search(r'\)', term):
        term = re.sub(r'\(', '', term)
    if not re.search(r'\(', term):
        term = re.sub(r'\)', '', term)

    term = stripBeginOrEndPunct(term)
    term = stripEtc(term)
    term = stripBeginOrEndPunct(term)#Do this twice since stripping etc may result in ending with punctuation...
    term = subOrdinals(term)
    term = stripQuotes(term)
    term = commonTermSubstitutions(term)
    term = stripIrrelevantTerms(term)

    term = fixWhitespace(term)
    term = simpleSynonymSub(term)
    term = subInformation(term)

    return term


# FIXME: dead code (Hao Cui)
r"""
def cleanupUnicodeErrors(term):
    # Cleanup from mistakes before... this should really be fixed during the intial parsing of the document...
    t = re.sub('\ufffc', ' ', term)
    t = re.sub('â€œ', '', t)
    t = re.sub('â€\u009d', '', t)
    t = re.sub('â\u0080\u0094', '', t)
    t = re.sub('â\u0080\u009d', '', t)
    t = re.sub('â\u0080\u009c', '', t)
    t = re.sub('â\u0080\u0099', '', t)
    t = re.sub('â€', '', t)
    t = re.sub('äë', '', t)
    t = re.sub('ä', '', t)
    t = re.sub('\u0093', '', t)
    t = re.sub('\u0092', '', t)
    t = re.sub('\u0094', '', t)
    t = re.sub('\u00a7', '', t)#Section symbol
    t = re.sub('\u25cf', '', t)#bullet point symbol
    t = re.sub('´', '\'', t)
    t = re.sub('\u00ac', '', t)
    t = re.sub('\u00ad', '-', t)
    t = re.sub('\u2211', '', t)
    t = re.sub('\ufb01', 'fi', t)
    t = re.sub('\uff0c', ', ', t)
    t = re.sub('\uf0b7', '', t)
    t = re.sub('\u037e', ';', t)
    return t

def startsWithLetter(term):
    return True if re.search(r'^[a-z]', term) else False

def ignorePhrases(term):
    if re.search(r'\b(act(s)?|advantage|allegation|aspect|because|breach|change|condition(s)?|conduct|confidentiality|copyright|damage|destruction|disclosure|disposition|effectiveness|encryption|enforce(ment|ability)|example|exploitation|failure|freedom|functionality|handling|harm|illegal\sconduct|impact|impossibility|improvement|integrity|lack|law|(legal|sole)\sresponsibility|liability|limitation|loss|malfunction|misuse|(non)?infringement|privacy|policy|practice|protection|removal|right|risk(s)?|safety|sample|security|secrecy|statement|term(s)?|trademark|transfer|(unauthorized|fraudulent|illicit)\suse|violation|warranty)\s(of)\b', term):
        return True
    if re.search(r'\b(privacy(\s(policy|law(s)?|practice|statement|right|act))?|collected\sinformation|security\spractice|intellectual\sproperty(\s(right))?|information\s(handling|gathering)|encrypt(ion)?)\b', term):
        return True
    return False

def ignoreTerms(term):
    return True if re.search(r'^\s*(n\.\s*a(\.)?|et\sal|eula|etc|possible|us|includ(e|ing)|herein|llc|example|button|transfer|policy|factor|mean|agreement|widget|share|item|disclosure|jurisdiction|offering|way|warranty|violation|thing|implied|firewall|encryption|inc(\.)?|thereto|trade(\-)?\s*mark|copyright|td|wrongdoing|hereto|hereinafter|liability)\s*$', term) else False

def ignoreNltkStopwords(term):
    return True if re.search(r'^\s*(i|me|my|myself|we|our|ours|ourselves|you|youre|youve|youll|youd|your|yours|yourself|yourselves|he|him|his|himself|she|shes|her|hers|herself|it|its|its|itself|they|them|their|theirs|themselves|what|which|who|whom|this|that|thatll|these|those|am|is|are|was|were|be|been|being|have|has|had|having|do|does|did|doing|a|an|the|and|but|if|or|because|as|until|while|of|at|by|for|with|about|against|between|into|through|during|before|after|above|below|to|from|up|down|in|out|on|off|over|under|again|further|then|once|here|there|when|where|why|how|all|any|both|each|few|more|most|other|some|such|no|nor|not|only|own|same|so|than|too|very|s|t|can|will|just|don|dont|should|shouldve|now|d|ll|m|o|re|ve|y|ain|aren|arent|couldn|couldnt|didn|didnt|doesn|doesnt|hadn|hadnt|hasn|hasnt|haven|havent|isn|isnt|ma|mightn|mightnt|mustn|mustnt|needn|neednt|shan|shant|shouldn|shouldnt|wasn|wasnt|weren|werent|won|wont|wouldn|wouldnt)\s*$', term) else False

def ignoreWebsiteUrlLink(term):
    return True if re.search(r'\b(website_url_lnk)\b', term) else False

def isSingleLetterTerm(term):
    return True if re.search(r'^\s*[a-z]\s*$', term) else False

def startsWithOrEndsWithPrep(term):
    return True if re.search(r'^\s*(of|at|in|with|by|on|as|if|to|for)\s', term) or re.search('\s(of|at|in|on|with|by|as|if|to|for)\s*$', term) else False

def checkOntIgnoreList(term, negativeTermRegex, generalIgnoreRegex):
    if negativeTermRegex.search(term):
        return True
    return True if generalIgnoreRegex.search(term) else False

def startsWithCoref(term):
    return True if re.search(r'^\s*(this|that|such)\b', term) else False

def potentialConjunction(term):
    if re.search(r',', term): # If it contains a comma, it could be two words together.
        return True
    if re.search(r'/', term):
        return True
    return True if re.search(r'\b(and|or)\b', term) else False

def shouldIgnoreTerm(term, generalIgnoreRegex = None, ontIgnoreRegex=None, preprocessFlag=True):
    if preprocessFlag:
        term = preprocess(term)
    if len(term) <= 1 or potentialConjunction(term) or startsWithCoref(term) or checkOntIgnoreList(term, ontIgnoreRegex, generalIgnoreRegex) or ignoreNltkStopwords(term) or isSingleLetterTerm(term) or ignoreWebsiteUrlLink(term) or not startsWithLetter(term) or ignorePhrases(term) or ignoreTerms(term) or startsWithOrEndsWithPrep(term):
        return True
    return False
"""
