import rdflib
from collections import Counter

g = rdflib.Graph()
g.parse("http://purl.obolibrary.org/obo/go.owl")

print(len(g))
f = open('ontologies.txt', 'a+')
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
                    f.write(tabPredicate[1] + '=' + object + ', ')
                elif Counter(tabPredicate[1]) == Counter('comment'):
                    f.write(tabPredicate[1] + '=' + g.comment(subject=subj, default='') + ', ')
                else:
                    tabObject = object.split('#')
                    if len(tabObject) == 2:
                        f.write(tabPredicate[1] + '=' + tabObject[1] + ', ')
                    else:
                        f.write(tabPredicate[1] + '=' + object + ', ')
            else:
                f.write(tabPredicate[1]+'='+'None, ')

f.close()





