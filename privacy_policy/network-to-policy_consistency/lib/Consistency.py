#!/usr/bin/env python

from . import OntologyOps as ontutils
import networkx as nx

# Input flow=(entity, data object), policies=[(entity, collect/not_collect, data object), ...]

class Entity:
    def __init__(self, entity):
        self.entity = entity

    @staticmethod
    def loadOntology(filename, ontology=None, rootNode='anyone'):
        Entity.ontology = ontutils.loadEntityOntology(filename) if ontology is None else ontology
        Entity.root = rootNode

    @staticmethod
    def loadStaticOntology():
        edges = [
            ('anyone', 'third_party'),
            ('anyone', 'we'),
            ('third_party', 'advertising_network'),
            ('third_party', 'analytic_provider'),
            ('third_party', 'social_network'),
            ('advertising_network', 'google'),
            ('analytic_provider', 'google'),
            ('google', 'crashlytics'),
            ('google', 'google ads'),

            ('analytic_provider', 'appsflyer'),
            ('advertising_network', 'facebook'),
            ('analytic_provider', 'facebook'),
            ('social_network', 'facebook'),
            ('advertising_network', 'verizon'),
            ('analytic_provider', 'verizon'),
            ('verizon', 'flurry'),
            ('analytic_provider', 'branch'),
            ('advertising_network', 'unity'),
            ('analytic_provider', 'unity'),
            ('analytic_provider', 'adjust'),
            ('analytic_provider', 'kochava'),
            ('advertising_network', 'mopub'),
            ('analytic_provider', 'mopub'),
            ('advertising_network', 'ironsource'),
            ('advertising_network', 'adcolony'),
        ]
        Entity.ontology = nx.DiGraph()
        Entity.ontology.add_edges_from(edges)
        Entity.root = 'anyone'

    @staticmethod
    def isOntologyLoaded():
        return hasattr(Entity, 'ontology')

    def getDirectAncestors(self):
        if Entity.isOntologyLoaded():
            return [ Entity(r) for r in ontutils.getDirectAncestors(Entity.ontology, self.entity) ]
        return NotImplemented

    def isRoot(self):
        return self.entity == Entity.root

    def isEquiv(self, other):
        if isinstance(other, Entity) and Entity.isOntologyLoaded():
            return ontutils.isSemanticallyEquiv(Entity.ontology, self.entity, other.entity)
        return NotImplemented       

    def isApprox(self, other):
        if isinstance(other, Entity) and Entity.isOntologyLoaded():
            return ontutils.isSemanticallyApprox(Entity.ontology, self.entity, other.entity, Entity.root)
        return NotImplemented       

    # TODO we can do synonyms here...
    def __hash__(self):
        return hash(self.entity)

    def __eq__(self, other):
        if isinstance(other, Entity):
            return other.entity == self.entity
        return NotImplemented

    def __ne__(self, other):
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result

    def __lt__(self, other):#subsumes
        if isinstance(other, Entity) and Entity.isOntologyLoaded():
            return ontutils.isSubsumedUnder(Entity.ontology, self.entity, other.entity)
        return NotImplemented

    def __le__(self, other):#subsumes
        if isinstance(other, Entity) and  Entity.isOntologyLoaded():
            return ontutils.isSubsumedUnderOrEq(Entity.ontology, self.entity, other.entity)
        return NotImplemented


    def __gt__(self, other):
        if isinstance(other, Entity) and Entity.isOntologyLoaded():
            return ontutils.isSubsumedUnder(Entity.ontology, other.entity, self.entity)
        return NotImplemented


    def __ge__(self, other):
        if isinstance(other, Entity) and  Entity.isOntologyLoaded():
            return ontutils.isSubsumedUnderOrEq(Entity.ontology, other.entity, self.entity)
        return NotImplemented

    def __str__(self):
        return self.entity

class Action:
    def __init__(self, action):
        self.action = action
        self.positiveTerm = 'collect'
        self.negativeTerm = 'not_collect'
        self.domain = [self.positiveTerm, self.negativeTerm]

    def isPositiveSentiment(self):
        if self.action not in self.domain:
            raise ValueError('Action ({}) was not in domain {}'.format(self.action, self.domain))
        return True if self.action == self.positiveTerm else False

    def isNegativeSentiment(self):
        if self.action not in self.domain:
            raise ValueError('Action ({}) was not in domain {}'.format(self.action, self.domain))
        return True if self.action == self.negativeTerm else False

    def __hash__(self):
        return hash(self.action)

    def __eq__(self, other):
        if isinstance(other, Action):
            return (self.isPositiveSentiment() and other.isPositiveSentiment()) or (self.isNegativeSentiment() and other.isNegativeSentiment())
        return NotImplemented

    def __lt__(self, other):#subsumes
        return NotImplemented

    def __le__(self, other):#subsumes
        return NotImplemented

    def __ne__(self, other):
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result

    def __gt__(self, other):
        return NotImplemented

    def __ge__(self, other):
        return NotImplemented

    def __str__(self):
        return self.action

class DataObject:
    def __init__(self, data):
        self.data = data
    
    @staticmethod
    def loadOntology(filename, ontology=None, rootNode='information'):
        DataObject.ontology = ontutils.loadDataOntology(filename) if ontology is None else ontology
        DataObject.root = rootNode

    @staticmethod
    def loadStaticOntology():
        edges = [
            ('information', 'pii'),
            ('pii', 'email address'),#pii
            ('pii', 'person name'),#pii
            ('pii', 'phone number'),#pii
            ('pii', 'device information'),#pii
            ('information', 'non-pii'),
            ('non-pii', 'geographical location'),
            ('non-pii', 'geographical location'),
            ('non-pii', 'device information'),#pii
            ('device information', 'identifier'),#pii
            ('identifier', 'device identifier'),#pii
            ('identifier', 'mac address'),#pii
            ('device information', 'router name'),#
            ('device identifier', 'advertising identifier'),#pii
            ('device identifier', 'android identifier'),#pii
            ('device identifier', 'imei'),#pii
            ('device identifier', 'gsfid'),#pii
        ]
        DataObject.ontology = nx.DiGraph()
        DataObject.ontology.add_edges_from(edges)
        DataObject.root = 'information'

    @staticmethod
    def isOntologyLoaded():
        return hasattr(DataObject, 'ontology')

    def getDirectAncestors(self):
        if DataObject.isOntologyLoaded():
            return [ DataObject(r) for r in ontutils.getDirectAncestors(DataObject.ontology, self.data) ]
        return NotImplemented

    def isRoot(self):
        return self.data == DataObject.root

    def isEquiv(self, other):
        if isinstance(other, DataObject) and DataObject.isOntologyLoaded():
            return ontutils.isSemanticallyEquiv(DataObject.ontology, self.data, other.data)
        return NotImplemented       

    def isApprox(self, other):
        if isinstance(other, DataObject) and DataObject.isOntologyLoaded():
            return ontutils.isSemanticallyApprox(DataObject.ontology, self.data, other.data, DataObject.root)
        return NotImplemented

    # TODO we can do synonyms here...
    def __hash__(self):
        return hash(self.data)

    def __eq__(self, other):
        if isinstance(other, DataObject):
            return other.data == self.data
        return NotImplemented

    def __ne__(self, other):
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result

    def __lt__(self, other):#subsumes
        if isinstance(other, DataObject) and DataObject.isOntologyLoaded():
            return ontutils.isSubsumedUnder(DataObject.ontology, self.data, other.data)
        return NotImplemented

    def __le__(self, other):#subsumes
        if isinstance(other, DataObject) and  DataObject.isOntologyLoaded():
            return ontutils.isSubsumedUnderOrEq(DataObject.ontology, self.data, other.data)
        return NotImplemented


    def __gt__(self, other):
        if isinstance(other, DataObject) and DataObject.isOntologyLoaded():
            return ontutils.isSubsumedUnder(DataObject.ontology, other.data, self.data)
        return NotImplemented

    def __ge__(self, other):
        if isinstance(other, DataObject) and  DataObject.isOntologyLoaded():
            return ontutils.isSubsumedUnderOrEq(DataObject.ontology, other.data, self.data)
        return NotImplemented

    def __str__(self):
        return self.data


class DataFlow:
    def __init__(self, flow):
        self.entity = Entity(flow[0])
        self.data = DataObject(flow[1])

    def getTuple(self):
        return (self.entity.entity, self.data.data)

    def __eq__(self, other):
        if isinstance(other, DataFlow):
            return other.data == self.data and other.entity == self.entity
        return NotImplemented

    def __ne__(self, other):
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result

    def __lt__(self, other):
        return NotImplemented

    def __le__(self, other):
        return NotImplemented

    def __gt__(self, other):
        return NotImplemented

    def __ge__(self, other):
        return NotImplemented

    def __str__(self):
        return '({}, {})'.format(self.entity, self.data)


class PolicyStatement:
    def __init__(self, policyStatement):
        self.entity = Entity(policyStatement[0])
        self.action = Action(policyStatement[1])
        self.data = DataObject(policyStatement[2])
    
    def getTuple(self):
        return (self.entity.entity, self.action.action, self.data.data)

    def isDiscussingRootTerms(self):
        return self.data.isRoot() or self.entity.isRoot()

    def isDiscussingAllRootTerms(self):
        return self.data.isRoot() and self.entity.isRoot()

    def isEquiv(self, other):
        if isinstance(other, DataObject):
            return self.data.isEquiv(other)
        elif isinstance(other, Entity):
            return self.entity.isEquiv(other)
        elif isinstance(other, PolicyStatement) or isinstance(other, DataFlow):
            return self.data.isEquiv(other.data) and self.entity.isEquiv(other.entity)  
        return NotImplemented

    def isApprox(self, other):
        if isinstance(other, DataObject):
            return self.data.isApprox(other)
        elif isinstance(other, Entity):
            return self.entity.isApprox(other)
        elif isinstance(other, PolicyStatement) or isinstance(other, DataFlow):
            return self.data.isApprox(other.data) and self.entity.isApprox(other.entity)    
        return NotImplemented

    def __eq__(self, other):
        if isinstance(other, PolicyStatement):
            return other.data == self.data and other.entity == self.entity and other.action == self.action
        return NotImplemented

    def __ne__(self, other):
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result

    def __lt__(self, other):
        return NotImplemented

    def __le__(self, other):
        return NotImplemented

    def __gt__(self, other):
        return NotImplemented

    def __ge__(self, other):
        return NotImplemented

    def __str__(self):
        return '({}, {}, {})'.format(self.entity, self.action, self.data)   


class Consistency:
    @staticmethod
    def flowSubsumedUnderPolicy(flow, pol):
        return flow.data <= pol.data and flow.entity <= pol.entity

    @staticmethod
    def checkPermissive(policyStatements, flow):
        for pol in policyStatements:
            if Consistency.flowSubsumedUnderPolicy(flow, pol) and pol.action.isPositiveSentiment() and not pol.isDiscussingRootTerms():
                return (True, pol, None)
        return (False, None, None)


    @staticmethod
    def checkStrict(policyStatements, flow):
        def getNegativeContradiction(pol, flow, policyStatements):
            for cpol in policyStatements:
                if Consistency.flowSubsumedUnderPolicy(flow, cpol) and cpol.action.isNegativeSentiment() and not cpol.isDiscussingRootTerms():
                    return (True, cpol)
            return (False, None)

        def hasPositiveSentimentStatement(P):
            return len([ p for p in P if p.action.isPositiveSentiment()]) > 0

        def hasNegativeSentimentStatement(P):
            return len([ p for p in P if p.action.isNegativeSentiment()]) > 0


        #Get all relevant policy statements     
        relP = [ p for p in policyStatements if Consistency.flowSubsumedUnderPolicy(flow, p) ] #and not pol.isDiscussingRootTerms()

        if len(relP) == 0: # No justification
            return (False, None, None)

        # Exists a positive sentiment statement, does not exist a negative sentiment
        consistencyResult = hasPositiveSentimentStatement(relP) and not hasNegativeSentimentStatement(relP)

        if consistencyResult:
            return (consistencyResult, relP, None)

        contradictions = []
        for p1 in relP:
            contrResults = []
            #Ensure p1 is positive sentiment or we'll potentially double count...
            if p1.action.isPositiveSentiment():
                for p2 in relP:
                    if not p2.action.isNegativeSentiment():
                        continue
                    for cindex,conmethod in enumerate(contradictionMethods):
                        if conmethod(p1, p2):# If contradiction between policies...
                            contrResults.append((p2, cindex))
            contradictions.append(contrResults if len(contrResults) > 0 else None)
        return (consistencyResult, relP, contradictions)

    @staticmethod
    def getDirectAncestors(cobj):
        result = set()
        for o in cobj:
            for k in o.getDirectAncestors():
                result.add(k)
        return result


    @staticmethod
    def findContradictionsForStatements(policyStatements, pMatches):
        if pMatches is None or len(pMatches) == 0:
            return (False, False, None, None)

        resultDecision = False
        hasNegativeSent = False
        cpols = []
        for p in pMatches:
            if p.action.isNegativeSentiment():
                hasNegativeSent = True
            if p.action.isPositiveSentiment():
                resultDecision = True

            contrResults = []
            for p1 in policyStatements:
                for cindex,conmethod in enumerate(contradictionMethods):
                    if conmethod(p, p1):# If contradiction between policies...
                        # Check number of flows that would have been accepted if we ignored contradiction...
                        contrResults.append(p1)
            cpols.append(contrResults)
        return (False if hasNegativeSent else resultDecision, hasNegativeSent, pMatches, cpols)

    @staticmethod
    def checkNearestEntityMatch(policyStatements, flow):
        def findNearestMatch(policyStatements, flow):
            def findDataMatch(policyStatements, data, entity):
                while len(data) > 0:
                    pMatches = [ p for p in policyStatements if p.data in data and p.entity in entity ]
                    if len(pMatches) > 0:
                        return pMatches
                    data = Consistency.getDirectAncestors(data)
                return None

            #########################
            # Get "nearest" match
            data = set([flow.data])
            entity = set([flow.entity])
            while len(entity) > 0:
                pMatches = findDataMatch(policyStatements, data, entity)
                if pMatches is None:
                    entity = Consistency.getDirectAncestors(entity)
                    continue
                return pMatches
            return None
        #########################
        pMatches = findNearestMatch(policyStatements, flow)
        return Consistency.findContradictionsForStatements(policyStatements, pMatches)

    @staticmethod
    def checkNearestDataMatch(policyStatements, flow):
        def findNearestMatch(policyStatements, flow):
            def findEntityMatch(policyStatements, data, entity):
                while len(entity) > 0:
                    pMatches = [ p for p in policyStatements if p.data in data and p.entity in entity ]
                    if len(pMatches) > 0:
                        return pMatches
                    entity = Consistency.getDirectAncestors(entity)
                return None
            #########################
            # Get "nearest" match
            data = set([flow.data])
            entity = set([flow.entity])
            while len(data) > 0:
                pMatches = findEntityMatch(policyStatements, data, entity)
                if pMatches is None:
                    data = Consistency.getDirectAncestors(data)
                    continue
                return pMatches
            return None
        #########################
        pMatches = findNearestMatch(policyStatements, flow)
        return Consistency.findContradictionsForStatements(policyStatements, pMatches)


    @staticmethod
    def checkIntermediate(policyStatements, flow):
        def isContradicted(pol, cpol):
            return Contradictions.checkContradiction1(pol, cpol) or Contradictions.checkContradiction3(pol, cpol) or \
                Contradictions.checkContradiction4(pol, cpol) or Contradictions.checkContradiction7(pol, cpol) or \
                Contradictions.checkContradiction8(pol, cpol) or Contradictions.checkContradiction9(pol, cpol) or \
                Contradictions.checkContradiction11(pol, cpol) or Contradictions.checkContradiction12(pol, cpol) or \
                Contradictions.checkContradiction13(pol, cpol) or Contradictions.checkContradiction15(pol, cpol) or \
                Contradictions.checkContradiction16(pol, cpol)

        def getNegativeContradiction(pol, policyStatements):
            for cpol in policyStatements:
                if cpol.action.isNegativeSentiment() and Consistency.flowSubsumedUnderPolicy(flow, cpol) and not cpol.isDiscussingRootTerms() and isContradicted(pol, cpol):
                    return (True, cpol)
            return (False, None)

        #################
        hitContr = False
        for pol in policyStatements:
            if Consistency.flowSubsumedUnderPolicy(flow, pol) and pol.action.isPositiveSentiment() and not pol.isDiscussingRootTerms():
                contradictionExists,cpol = getNegativeContradiction(pol, policyStatements)
                if contradictionExists: # TODO Do we really just return here? Is it exists or forall? IS there a difference
                    hitContr = True
                    #return (False, pol, cpol)
                    continue
                return (True, pol, None)
        return (False, None, None)

class Contradictions:
    @staticmethod
    def checkContradiction1(p1, p2):
        return p1.data == p2.data and p1.entity == p2.entity and p1.action != p2.action

    @staticmethod
    def checkContradiction2(p1, p2):
        return p1.data < p2.data and p1.entity == p2.entity and p1.action.isPositiveSentiment() and p2.action.isNegativeSentiment()
    
    @staticmethod
    def checkContradiction3(p1, p2):
        return p1.data > p2.data and p1.entity == p2.entity and p1.action.isPositiveSentiment() and p2.action.isNegativeSentiment()
    
    @staticmethod
    def checkContradiction4(p1, p2):
        return p1.data.isApprox(p2.data) and p1.entity == p2.entity and p1.action.isPositiveSentiment() and p2.action.isNegativeSentiment()
    
    @staticmethod
    def checkContradiction5(p1, p2):
        return p1.data == p2.data and p1.entity < p2.entity and p1.action.isPositiveSentiment() and p2.action.isNegativeSentiment()
    
    @staticmethod
    def checkContradiction6(p1, p2):
        return p1.data < p2.data and p1.entity < p2.entity and p1.action.isPositiveSentiment() and p2.action.isNegativeSentiment()
    
    @staticmethod
    def checkContradiction7(p1, p2):
        return p1.data > p2.data and p1.entity < p2.entity and p1.action.isPositiveSentiment() and p2.action.isNegativeSentiment()
    
    @staticmethod
    def checkContradiction8(p1, p2):
        return p1.data.isApprox(p2.data) and p1.entity < p2.entity and p1.action.isPositiveSentiment() and p2.action.isNegativeSentiment()
    
    @staticmethod
    def checkContradiction9(p1, p2):
        return p1.data == p2.data and p1.entity > p2.entity and p1.action.isPositiveSentiment() and p2.action.isNegativeSentiment()
    
    @staticmethod
    def checkContradiction10(p1, p2):
        return p1.data < p2.data and p1.entity > p2.entity and p1.action.isPositiveSentiment() and p2.action.isNegativeSentiment()
    
    @staticmethod
    def checkContradiction11(p1, p2):
        return p1.data > p2.data and p1.entity > p2.entity and p1.action.isPositiveSentiment() and p2.action.isNegativeSentiment()
    
    @staticmethod
    def checkContradiction12(p1, p2):
        return  p1.data.isApprox(p2.data) and p1.entity > p2.entity and p1.action.isPositiveSentiment() and p2.action.isNegativeSentiment() 
    @staticmethod
    def checkContradiction13(p1, p2):
        return  p1.data == p2.data and p1.entity.isApprox(p2.entity) and p1.action.isPositiveSentiment() and p2.action.isNegativeSentiment()

    @staticmethod
    def checkContradiction14(p1, p2):
        return  p1.data < p2.data and p1.entity.isApprox(p2.entity) and p1.action.isPositiveSentiment() and p2.action.isNegativeSentiment()

    @staticmethod
    def checkContradiction15(p1, p2):
        return  p1.data > p2.data and p1.entity.isApprox(p2.entity) and p1.action.isPositiveSentiment() and p2.action.isNegativeSentiment()

    @staticmethod
    def checkContradiction16(p1, p2):
        return  p1.data.isApprox(p2.data) and p1.entity.isApprox(p2.entity) and p1.action.isPositiveSentiment() and p2.action.isNegativeSentiment()


contradictionMethods = [
                Contradictions.checkContradiction1, Contradictions.checkContradiction2,
                Contradictions.checkContradiction3, Contradictions.checkContradiction4,
                Contradictions.checkContradiction5, Contradictions.checkContradiction6,
                Contradictions.checkContradiction7, Contradictions.checkContradiction8,
                Contradictions.checkContradiction9, Contradictions.checkContradiction10,
                Contradictions.checkContradiction11, Contradictions.checkContradiction12,
                Contradictions.checkContradiction13, Contradictions.checkContradiction14,
                Contradictions.checkContradiction15, Contradictions.checkContradiction16,
            ]

def getRawContradictionStats(policies, flows):
    results = []
    for index0,p0 in enumerate(policies):
        if p0.isDiscussingRootTerms():
            continue
        for index1,p1 in enumerate(policies):
            if index0 == index1 or p1.isDiscussingRootTerms():
                continue
            for cindex,conmethod in enumerate(contradictionMethods):
                if conmethod(p0, p1):# If contradiction between policies...
                    # Check number of flows that would have been accepted if we ignored contradiction...
                    conImpact = [ f for f in flows if Consistency.flowSubsumedUnderPolicy(f, p0) and Consistency.flowSubsumedUnderPolicy(f, p1) ]
                    results.append(((p0, p1), cindex, conImpact))
    return results

def checkConsistency(policies, flows):
    return [ { 'flow' : f, 'consistency' : Consistency.checkStrict(policies, f) } for f in flows ]

#def checkConsistency(policies, flows, packageName, calcRawStats=False):
#   results = []
#   for f in flows:
        #TODO integrate raw stats calculation here...
#       pRes = Consistency.checkPermissive(policies, f)
#       iRes = Consistency.checkIntermediate(policies, f)
#       sRes = Consistency.checkStrict(policies, f)
#       results.append({'permissive' : pRes, 'intermediate' : iRes, 'strict' : sRes})
#   return (results, getRawContradictionStats(policies, flows)) if calcRawStats else results


def getContradictions(policies, packageName, calcRawStats=False):
    results = []
    for index0,p0 in enumerate(policies):
        if p0.isDiscussingRootTerms():
            continue
        for index1,p1 in enumerate(policies):
            if index0 == index1 or p1.isDiscussingRootTerms():
                continue
            for cindex,conmethod in enumerate(contradictionMethods):
                if conmethod(p0, p1):# If contradiction between policies...
                    results.append(((p0, p1), cindex))
    return results

def init(dataOntologyFilename, entityOntologyFilename):
    Entity.loadOntology(entityOntologyFilename)
    DataObject.loadOntology(dataOntologyFilename)

def init_static():
    Entity.loadStaticOntology()
    DataObject.loadStaticOntology()

########################################################
def createDummyEntityOntology():
    edges = [
                ('public', 'first party'),
                ('public', 'third party'),
                ('third party', 'third party provider'),
                ('third party provider', 'advertiser'),
                ('third party provider', 'analytic provider'),
                ('advertiser', 'companyX'),
                ('advertiser', 'google admob'),
                ('analytic provider', 'companyX'),
                ('analytic provider', 'google analytics'),
            ]
    ontology = nx.DiGraph()
    ontology.add_edges_from(edges)
    return ontology

def createDummyDataOntology():
    edges = [
                ('information', 'personal information'),
                ('personal information', 'account credential'),
                ('personal information', 'medical treatment information'),
                ('account credential', 'biometric information'),
                ('biometric information', 'fingerprint'),
                ('biometric information', 'heart rate'),
                ('account credential', 'username'),
                ('medical treatment information', 'medical_health information'),
                ('medical_health information', 'blood glucose'),
                ('medical_health information', 'heart rate'),
            ]
    ontology = nx.DiGraph()
    ontology.add_edges_from(edges)
    return ontology

def runTestCases():#FIXME test cases are broken since returning contradicting policies!
    def testContradictions(pol, flow, expContradictions, expIntermediate, expPermissive, expStrict=None):
        assert(len(contradictionMethods) == len(expContradictions))
        assert(len(pol) == 2)

        for index,conmethod in enumerate(contradictionMethods):
            assert(conmethod(pol[0], pol[1]) == expContradictions[index]), 'Contradiction failed for case {} and policies ({}, {})'.format(index, pol[0], pol[1])


        message = 'Failed {} check for ({}, {}) and flow ({}). Expected = {}, Result = {}'
        pRes = Consistency.checkPermissive(pol, flow)
        assert(pRes == expPermissive), message.format('permissive', pol[0], pol[1], flow, expPermissive, pRes)
        iRes = Consistency.checkIntermediate(pol, flow)
        assert(iRes == expIntermediate), message.format('intermediate', pol[0], pol[1], flow, expIntermediate, iRes)
        sRes = Consistency.checkStrict(pol, flow)
        assert(sRes == expStrict), message.format('strict', pol[0], pol[1], flow, expStrict, sRes)


    def createBoolArr(inverseValueIndex=None, defaultValue=False, length=16):
        arr = [ defaultValue ] * length
        if inverseValueIndex is not None:
            arr[inverseValueIndex] = not arr[inverseValueIndex]
        return arr

    Entity.loadOntology(ontology=createDummyEntityOntology())
    DataObject.loadOntology(ontology=createDummyDataOntology())

    flow1 = DataFlow(('companyX', 'heart rate'))
    flow2 = DataFlow(('companyX', 'blood glucose'))

    p0 = [PolicyStatement(('companyX', 'collect', 'heart rate')),
        PolicyStatement(('companyX', 'not_collect', 'heart rate'))]
    p0ExpCon = createBoolArr(0)
    testContradictions(p0, flow1, p0ExpCon, None, p0[0], None)
    testContradictions(p0, flow2, p0ExpCon, None, None, None)

    p1 = [PolicyStatement(('companyX', 'collect', 'heart rate')),
        PolicyStatement(('companyX', 'not_collect', 'medical_health information'))]
    p1ExpCon = createBoolArr(1)

    testContradictions(p1, flow1, p1ExpCon, p1[0], p1[0], None)
    testContradictions(p1, flow2, p1ExpCon, None, None, None)

    p2 = [PolicyStatement(('companyX', 'collect', 'medical_health information')),
        PolicyStatement(('companyX', 'not_collect', 'heart rate'))]
    p2ExpCon = createBoolArr(2)
    testContradictions(p2, flow1, p2ExpCon, None, p2[0], None)
    testContradictions(p2, flow2, p2ExpCon, p2[0], p2[0], p2[0])

    p3 = [PolicyStatement(('companyX', 'collect', 'medical_health information')),
        PolicyStatement(('companyX', 'not_collect', 'biometric information'))]
    p3ExpCon = createBoolArr(3)
    testContradictions(p3, flow1, p3ExpCon, None, p3[0], None)
    testContradictions(p3, flow2, p3ExpCon, p3[0], p3[0], p3[0])

    p4 = [PolicyStatement(('companyX', 'collect', 'heart rate')),
        PolicyStatement(('advertiser', 'not_collect', 'heart rate'))]
    p4ExpCon = createBoolArr(4)
    testContradictions(p4, flow1, p4ExpCon, p4[0], p4[0], None)
    testContradictions(p4, flow2, p4ExpCon, None, None, None)

    p5 = [PolicyStatement(('companyX', 'collect', 'heart rate')),
        PolicyStatement(('advertiser', 'not_collect', 'medical_health information'))]
    p5ExpCon = createBoolArr(5)
    testContradictions(p5, flow1, p5ExpCon, p5[0], p5[0], None)
    testContradictions(p5, flow2, p5ExpCon, None, None, None)

    p6 = [PolicyStatement(('companyX', 'collect', 'medical_health information')),
        PolicyStatement(('advertiser', 'not_collect', 'heart rate'))]
    p6ExpCon = createBoolArr(6)
    testContradictions(p6, flow1, p6ExpCon, None, p6[0], None)
    testContradictions(p6, flow2, p6ExpCon, p6[0], p6[0], p6[0])

    p7 = [PolicyStatement(('companyX', 'collect', 'medical_health information')),
        PolicyStatement(('advertiser', 'not_collect', 'biometric information'))]
    p7ExpCon = createBoolArr(7)
    testContradictions(p7, flow1, p7ExpCon, None, p7[0], None)
    testContradictions(p7, flow2, p7ExpCon, p7[0], p7[0], p7[0])

    p8 = [PolicyStatement(('advertiser', 'collect', 'heart rate')),
        PolicyStatement(('companyX', 'not_collect', 'heart rate'))]
    p8ExpCon = createBoolArr(8)
    testContradictions(p8, flow1, p8ExpCon, None, p8[0], None)
    testContradictions(p8, flow2, p8ExpCon, None, None, None)

    p9 = [PolicyStatement(('advertiser', 'collect', 'heart rate')),
        PolicyStatement(('companyX', 'not_collect', 'medical_health information'))]
    p9ExpCon = createBoolArr(9)
    testContradictions(p9, flow1, p9ExpCon, p9[0], p9[0], None)
    testContradictions(p9, flow2, p9ExpCon, None, None, None)

    p10 = [PolicyStatement(('advertiser', 'collect', 'medical_health information')),
        PolicyStatement(('companyX', 'not_collect', 'heart rate'))]
    p10ExpCon = createBoolArr(10)
    testContradictions(p10, flow1, p10ExpCon, None, p10[0], None)
    testContradictions(p10, flow2, p10ExpCon, p10[0], p10[0], p10[0])

    p11 = [PolicyStatement(('advertiser', 'collect', 'medical_health information')),
        PolicyStatement(('companyX', 'not_collect', 'biometric information'))]
    p11ExpCon = createBoolArr(11)
    testContradictions(p11, flow1, p11ExpCon, None, p11[0], None)
    testContradictions(p11, flow2, p11ExpCon, p11[0], p11[0], p11[0])

    p12 = [PolicyStatement(('analytic provider', 'collect', 'heart rate')),
        PolicyStatement(('advertiser', 'not_collect', 'heart rate'))]
    p12ExpCon = createBoolArr(12)
    testContradictions(p12, flow1, p12ExpCon, None, p12[0], None)
    testContradictions(p12, flow2, p12ExpCon, None, None, None)

    p13 = [PolicyStatement(('analytic provider', 'collect', 'heart rate')),
        PolicyStatement(('advertiser', 'not_collect', 'medical_health information'))]
    p13ExpCon = createBoolArr(13)
    testContradictions(p13, flow1, p13ExpCon, p13[0], p13[0], None)
    testContradictions(p13, flow2, p13ExpCon, None, None, None)

    p14 = [PolicyStatement(('analytic provider', 'collect', 'medical_health information')),
        PolicyStatement(('advertiser', 'not_collect', 'heart rate'))]
    p14ExpCon = createBoolArr(14)
    testContradictions(p14, flow1, p14ExpCon, None, p14[0], None)
    testContradictions(p14, flow2, p14ExpCon, p14[0], p14[0], p14[0])

    p15 = [PolicyStatement(('analytic provider', 'collect', 'medical_health information')),
        PolicyStatement(('advertiser', 'not_collect', 'biometric information'))]
    p15ExpCon = createBoolArr(15)
    testContradictions(p15, flow1, p15ExpCon, None, p15[0], None)
    testContradictions(p15, flow2, p15ExpCon, p15[0], p15[0], p15[0])

    p17 = [PolicyStatement(('companyX', 'collect', 'heart rate')),
        PolicyStatement(('companyX', 'not_collect', 'blood glucose'))]
    p17ExpCon = createBoolArr()
    testContradictions(p17, flow1, p17ExpCon, p17[0], p17[0], p17[0])
    testContradictions(p17, flow2, p17ExpCon, None, None, None)

    p18 = [PolicyStatement(('companyX', 'collect', 'information')),
        PolicyStatement(('companyX', 'not_collect', 'personal information'))]
    p18ExpCon = createBoolArr(2)
    testContradictions(p18, flow1, p18ExpCon, None, None, None)
    testContradictions(p18, flow2, p18ExpCon, None, None, None)

    p19 = [PolicyStatement(('companyX', 'collect', 'personal information')),
        PolicyStatement(('companyX', 'not_collect', 'information'))]
    p19ExpCon = createBoolArr(1)
    testContradictions(p19, flow1, p19ExpCon, p19[0], p19[0], None)
    testContradictions(p19, flow2, p19ExpCon, p19[0], p19[0], None)

    p20 = [PolicyStatement(('companyX', 'collect', 'personal information')),
        PolicyStatement(('companyX', 'collect', 'medical_health information'))]
    p20ExpCon = createBoolArr()
    testContradictions(p20, flow1, p20ExpCon, p20[0], p20[0], p20[0])
    testContradictions(p20, flow2, p20ExpCon, p20[0], p20[0], p20[0])

    p21 = [PolicyStatement(('companyX', 'not_collect', 'personal information')),
        PolicyStatement(('companyX', 'not_collect', 'medical_health information'))]
    p21ExpCon = createBoolArr()
    testContradictions(p21, flow1, p21ExpCon, None, None, None)
    testContradictions(p21, flow2, p21ExpCon, None, None, None)

if __name__ == '__main__':
    runTestCases()
