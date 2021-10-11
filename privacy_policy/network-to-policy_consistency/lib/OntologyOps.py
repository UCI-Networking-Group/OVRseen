#!/usr/bin/env python

import networkx as nx
from functools import lru_cache

def loadOntology(filename):
    return nx.read_gml(filename)

def loadEntityOntology(filename):
    return loadOntology(filename)

def loadDataOntology(filename):
    return loadOntology(filename)

def loadOntologyTerms(filename):
    terms = set()
    tdict = loadOntology(filename)
    for t in tdict:
        terms.add(t)
        for s in tdict[t]:
            terms.add(s)
    return terms

def getAllDescendents(ontology, node):#TODO check if node in ontology...
    if node not in ontology.nodes:
        raise ValueError('Node {} is not in the ontology'.format(node))
    return [ n for n in ontology.nodes if n == node or nx.has_path(ontology, node, n) ] 

def getDirectAncestors(ontology, node):
    return [ src for src,_ in ontology.in_edges(node) ]

@lru_cache(4096)
def isSubsumedInternal(ontology, x, y):
    return x in getAllDescendents(ontology, y)

# X is subsumed under Y
@lru_cache(4096)
def isSubsumedUnder(ontology, x, y):
    return x != y and isSubsumedInternal(ontology, x, y)

# X is subsumed under Y or equal
@lru_cache(4096)
def isSubsumedUnderOrEq(ontology, x, y):
    return x == y or isSubsumedInternal(ontology, x, y)

@lru_cache(4096)
def isSemanticallyEquiv(ontology, x, y):
    return isSubsumedUnderOrEq(ontology, x, y) or isSubsumedUnderOrEq(ontology, y, x)

@lru_cache(4096)
def isSemanticallyApprox(ontology, x, y, root):
    if isSemanticallyEquiv(ontology, x, y):
        return False

    xDescend = getAllDescendents(ontology, x)
    if root in xDescend:
        xDescend.remove(root)
    yDescend = getAllDescendents(ontology, y)
    if root in yDescend:
        yDescend.remove(root)

    return not isSemanticallyEquiv(ontology, x, y) and len(set(xDescend).intersection(set(yDescend))) > 0
