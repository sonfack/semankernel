import os.path
import re
import rdflib

from collections import Counter
from elasticsearch import helpers
from pyjarowinkler import distance
from src.common import database


class Ontology(object):

    def __init__(self):
        self.buckets = {}
        self.types = []
        self.ontoGraph = rdflib.Graph()

        allindex = self.noIndexQuery()
        total = allindex['_shards']
        print(total['total'])

        if total['total'] > 0:
            aggregations = allindex['aggregations']
            typeAgg = aggregations['typesAgg']
            buckets = typeAgg['buckets']
            self.buckets = buckets
            #self.types = []
            for index in self.buckets:
                indexVal = index['key']
                alltype = self.indexQuery(indexVal)
                aggType = alltype['aggregations']
                typeAggType = aggType['typesAgg']

                self.types.append(typeAggType['buckets'])


    def getDocumentById(self, indexName, id):
        # Connect to the elastic cluster
        storage = database.Database()
        es = storage.es
        res = es.search(index=indexName, body={
                                  "query": {
                                    "term": {
                                      "_id": id
                                    }
                                  }
                                }
                        )
        return res


    def getTypeOfIndex(self, index):
        for index in self.buckets:
            indexVal = index['key']
            if indexVal == index:
                alltype = self.indexQuery(indexVal)
                aggType = alltype['aggregations']
                typeAggType = aggType['typesAgg']
                return  typeAggType['buckets']


    def personalOntology(self, words, urlOnto):
        # parsing the ontology
        self.ontoGraph.parse(urlOnto)
        print('personal')
        data = []
        count = 0
        for subj in self.ontoGraph.subjects(predicate=None, object=None):
            subjLabel = self.ontoGraph.label(subj, default='')
            print(str(subjLabel))
            persList = []
            for word in words:
                if ((len(subjLabel) > 0) and word in str(subjLabel)) and str(subj) not in persList:
                    concept = {}
                    for p, o in self.ontoGraph.predicate_objects(subject=subj):
                        predicate = p
                        print('PREDICATE = ' + predicate)
                        object = o
                        print('OBJECT = ' + object)
                        tabPredicate = predicate.split('#')
                        if len(tabPredicate) == 2:
                            if object and len(object) > 0:
                                if Counter(tabPredicate[1]) == Counter('id'):
                                    concept[tabPredicate[1]] = str(object)
                                elif Counter(tabPredicate[1]) == Counter('comment'):
                                    concept[tabPredicate[1]] = str(self.ontoGraph.comment(subject=subj, default=''))
                                else:
                                    tabObject = object.split('#')
                                    if len(tabObject) == 2:
                                        concept[tabPredicate[1]] = str(tabObject[1])
                                    else:
                                        concept[tabPredicate[1]] = str(object)
                            else:
                                concept[tabPredicate[1]] = 'None'
                    print('-------   -------------')
                    concept['subject'] = str(subj)
                    concept['similarity'] = float(distance.get_jaro_distance(subjLabel, " ".join(words), winkler=True, scaling=0.1))
                    print(concept)
                    #    tabConcept.append(concept)
                    data.append(concept)
                    print('--------------------')
                    persList.append(str(subj))

        return data


    # this function takes a list of word and create and or contatenation for elasticsearch string query
    def createOrStringQuery(self, listWords):
        ourQuery = "*"
        count = 0
        for word in listWords:
            count = count + 1
            if count < len(listWords):
                ourQuery = ourQuery + str(word) + "* OR *"
            elif count == len(listWords):
                ourQuery = ourQuery + str(word) + "*"
        return ourQuery

    def urlValidator(self, url):
        regex = re.compile(
            r'^(?:http|ftp)s?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)

        if re.match(regex, str(url)):
            return True
        else:
            return False


    # file contains the path to file
    # the url of the given ontology
    # this method stores an ontology in a elasticsearch database with each concept as a document
    def storeOntology(self, ontology, type, index='ontology'):

        if ontology:
            if self.urlValidator(ontology) or os.path.isfile(ontology):
                if type:
                    storage = database.Database()
                    es = storage.es
                    self.ontoGraph.parse(ontology)
                    actions = []
                    count = 0
                    for subj in self.ontoGraph.subjects(predicate=None, object=None):
                        print('SUJET = ' + subj)
                        subjLabel = self.ontoGraph.label(subj, default='')
                        print('SUBJLABEL = ' + subjLabel)
                        concept = {}
                        for p, o in self.ontoGraph.predicate_objects(subject=subj):
                            predicate = p
                            print('PREDICATE = ' + p)
                            object = o
                            print('OBJECT = ' + o)
                            tabPredicate = predicate.split('#')
                            if len(tabPredicate) == 2:
                                if object and len(object) > 0:
                                    if Counter(tabPredicate[1]) == Counter('id'):
                                        concept[tabPredicate[1]] = str(object)
                                    elif Counter(tabPredicate[1]) == Counter('comment'):
                                        concept[tabPredicate[1]] = str(self.ontoGraph.comment(subject=subj, default=''))
                                    else:
                                        tabObject = object.split('#')
                                        if len(tabObject) == 2:
                                            concept[tabPredicate[1]] = str(tabObject[1])
                                        else:
                                            concept[tabPredicate[1]] = str(object)
                                else:
                                    concept[tabPredicate[1]] = ''

                        concept["subject"] = subj

                        print(concept)
                        action = {
                            "_index": str(index),
                            "_type": str(type),
                            "_id": count,
                            "_source": concept
                        }

                        actions.append(action)
                        count = count + 1
                        helpers.bulk(es, actions, request_timeout=90000)
                    return True
                else:
                    return False

            else:
                return False
        else:
            return False


    '''
    this function will query and ontology looking for similar words 
    from the list in the label,synonym, namespace of each class
    listwords is the given list on which the similarity will be done
    '''
    def noIndexQuery(self):

        # Connect to the elastic cluster
        storage = database.Database()
        es = storage.es
        res = es.search(body=
                                {
                                    "aggs": {
                                        "typesAgg": {
                                            "terms": {
                                                "field": "_index",
                                                "size": 20
                                            }
                                        }
                                    },
                                    "size": 0
                                }, request_timeout=300
                        )
        return res


    def indexQuery(self, indexValue=None):
        # Connect to the elastic cluster
        if not indexValue is None:
            storage = database.Database()
            es = storage.es
            res = es.search(index=indexValue, body=
                                                    {
                                                        "aggs": {
                                                            "typesAgg": {
                                                                "terms": {
                                                                    "field": "_type",
                                                                    "size": 20
                                                                }
                                                            }
                                                        },
                                                        "size": 0
                                                    }, request_timeout=300
                        )
            return res
        else:
            return None


    def getConceptById(self, id, indexValue=None):
        # Connect to the elastic cluster
        storage = database.Database()
        es = storage.es
        if id:
            if not indexValue is None:
                res = es.search(index=indexValue, body=
                                                        {
                                                            "query": {
                                                                "bool": {
                                                                    "must": [
                                                                        {
                                                                            "match": {
                                                                                "id": id
                                                                            }
                                                                        }
                                                                    ]
                                                                }

                                                            }
                                                        }, request_timeout=300
                            )
                return res
            else:
                res = es.search(body=
                                    {
                                        "query": {
                                            "bool": {
                                                "must": [
                                                    {
                                                        "match": {
                                                            "id": id
                                                        }
                                                    }
                                                ]
                                            }

                                        }
                                    }, request_timeout=300
                            )
                return res



    def queryOntology(self, listWords, typeValue=None, indexValue=None):
        # Connect to the elastic cluster
        print('database connection')
        storage = database.Database()
        es = storage.es
        if isinstance(listWords, list) and len(listWords) > 0:
            print('condition isinstance(listsWords, list) and len(listWords) > 0')
            ourQuery = self.createOrStringQuery(listWords)
            print('query '+ourQuery)
            if not typeValue is None and not indexValue is None:
                print('condition not typeValue is None and not indexValue is None')
                print('indexValue ')
                print(indexValue)
                print('typeValue ')
                print(typeValue)
                res = es.search(index=indexValue, doc_type=typeValue, body=
                                                                            {   "size":  50,
                                                                                "query": {
                                                                                    "query_string": {
                                                                                        "fields": ["label", "*Synonym", "*Namespace", "comment"],
                                                                                        "query": ourQuery
                                                                                    }
                                                                                }
                                                                            }, request_timeout=300
                                )
                print('result query')
                print(res)
                return res
            elif typeValue is None and not indexValue is None:
                print('condition typeValue is None and not indexValue is None')
                print('indexValue')
                print(indexValue)
                res = es.search(index=indexValue, body=
                                                        {   "size":  50,
                                                            "query": {
                                                                "query_string": {
                                                                    "fields": ["label", "*Synonym", "*Namespace", "comment"],
                                                                    "query": ourQuery
                                                                }
                                                            },
                                                            "sort":
                                                                {"_score": {"order": "desc"}}
                                                        }, request_timeout=300
                            )
                print('result query')
                print(res)
                return res
            elif typeValue is None and indexValue is None:
                print('condition typeValue is None and  indexValue None')
                res = es.search(body=
                                    {   "size":  200,
                                        "query": {
                                            "query_string": {
                                                "fields": ["label", "*Synonym", "*Namespace", "comment"],
                                                "query": ourQuery
                                            }
                                        },
                                        "sort":
                                            {"_score": {"order": "desc"}}
                                    }, request_timeout=300
                                )
                print('result query')
                print(res)
                return res



    def getAllConceptsOfOntology(self, indexName, begin=None, size=None):
        # Connect to the elastic cluster
        storage = database.Database()
        es = storage.es
        if not size is None:
            if begin is None:
                begin = 0
            res = es.search(index=indexName, body={
                                                    "from": begin, "size": size,
                                                    "query": {
                                                        "match_all": {}
                                                    }
                                                }
                         )
            return res
        elif size is None:
            size = 100
            if begin is None:
                begin = 0
            res = es.search(index=indexName, body={
                                                        "from": begin, "size":size,
                                                        "query": {
                                                            "match_all": {}
                                                        }
                                                    }
                            )
            return res