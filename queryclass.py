import rdflib
import json
from collections import Counter
from rdflib import Graph, plugin
from rdflib.serializer import Serializer

g = rdflib.Graph()
g.parse("http://purl.obolibrary.org/obo/go.owl")

print(len(g))
f = open('ontologies.txt', 'a+')
f.write('{ \n')
for subj in g.subjects(predicate=None, object=None):
    print('SUJET = '+subj)
    subjLabel = g.label(subj, default='')
    print('SUBJLABEL = '+subjLabel)
    f.write('\n\n')
    for p, o in g.predicate_objects(subject=subj):
        predicate = p
        print('PREDICATE = '+p)
        object = o
        print('OBJECT = '+o)
        tabPredicate = predicate.split('#')
        if len(tabPredicate) == 2:
            if object and len(object) > 0:
                if Counter(tabPredicate[1]) == Counter('id'):
                    f.write(tabPredicate[1] + ':' + object + ', \n' )
                elif Counter(tabPredicate[1]) == Counter('comment'):
                    f.write(tabPredicate[1] + ':' + g.comment(subject=subj, default='') + ', \n')
                else:
                    tabObject = object.split('#')
                    if len(tabObject) == 2:
                        f.write(tabPredicate[1] + ':' + tabObject[1] + ', \n')
                    else:
                        f.write(tabPredicate[1] + ':' + object + ', \n')
            else:
                f.write(tabPredicate[1]+':'+'None, \n')
f.write('\n }')
f.close()





