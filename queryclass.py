import rdflib
import re
from collections import Counter
from elasticsearch import Elasticsearch
from elasticsearch import helpers
# NLTK Stop words
from nltk.corpus import stopwords
# NLTK tokenize
from nltk.tokenize import word_tokenize
# NLTK stemming
from nltk.stem import PorterStemmer


def storeOntology():

    # Connect to the elastic cluster
    es = Elasticsearch([{'host': '172.17.0.2', 'port': 9200}])
    ontoUrl = "to.owl"
    ontoType = 'to'
    g = rdflib.Graph()

    g   .parse(ontoUrl)

    print(len(g))

    # dictionary
    data = {}
    actions = []
    count = 0
    for subj in g.subjects(predicate=None, object=None):
        print('SUJET = '+subj)
        subjLabel = g.label(subj, default='')
        print('SUBJLABEL = '+subjLabel)
        concept = {}
        for p, o in g.predicate_objects(subject=subj):
            predicate = p
            print('PREDICATE = '+p)
            object = o
            print('OBJECT = '+o)
            tabPredicate = predicate.split('#')
            if len(tabPredicate) == 2:
                if object and len(object) > 0:
                    if Counter(tabPredicate[1]) == Counter('id'):
                        concept[tabPredicate[1]] = str(object)
                    elif Counter(tabPredicate[1]) == Counter('comment'):
                        concept[tabPredicate[1]] = str(g.comment(subject=subj, default=''))
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
        #tabConcept.append(concept)
        #data[subj] = concept

        if count <= 10:
            action = {
                "_index": "ontology",
                "_type": "to",
                "_id": count,
                "_source": concept
                }

            actions.append(action)

            #res = es.index(index='ontology', doc_type=ontoType, id=count, body=data)
            #concept.clear()
            #data.clear()
            count = count + 1
        else:
            helpers.bulk(es, actions)
            exit()


def textProcessing(text):
    newText = text.lower()
    newText = re.sub('[0-9]', '', newText)
    newText = re.sub('[^ a-zA-Z0-9]', '', newText)
    # print(newText)

    # tokenize
    word_tokens = word_tokenize(newText)

    # load stop words
    stop_words = stopwords.words('english')
    # print(stop_words)

    # Remove stop words
    filterWords = [word for word in word_tokens if word not in stop_words]
    # print(filterWords)

    # stemming words
    ps = PorterStemmer()
    stemWords = []

    for word in filterWords:
        stemWords.append(ps.stem(word))
    # print(stemWords)
    return stemWords


def queryOntology(text):

    # Connect to the elastic cluster
    es = Elasticsearch([{'host': '172.17.0.2', 'port': 9200}])
    res = es.get(index='ontology',  doc_type='to', id=2)
    print(res)
    res = es.search(index='ontology', body=
                                            {
                                                "query": {
                                                    "bool": {
                                                        "should": [
                                                            {"match": {
                                                                "label": str(text)
                                                            }}
                                                        ]
                                                    }
                                                }
                                            }
                    )
    print(res)
#


def main():
    queryText = textProcessing('shoot')
    print(queryText)
    queryOntology(queryText)
    #storeOntology()


if __name__ == '__main__':

    main()