import rdflib
from collections import Counter
from elasticsearch import Elasticsearch

# Connect to the elastic cluster
es=Elasticsearch([{'host':'172.17.0.2','port':9200}])

ontoUrl = "to.owl"
ontoType = 'to'
g = rdflib.Graph()

g.parse(ontoUrl)

print(len(g))

# dictionary
data = {}

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
    print(concept)
#    tabConcept.append(concept)
    data[subj] = concept
    count = count + 1
    if count < 5:
        res = es.index(index='ontology',doc_type= ontoType ,id = count, body=data)
        concept.clear()
        data.clear()
#        with open('ontology.json', 'a+') as f:
#           simplejson.dump(data, f)
#        f.close()
    else:
        exit()
