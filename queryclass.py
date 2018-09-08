import rdflib
import json
from rdflib import Graph
from rdflib.namespace import RDFS, RDF, SKOS
from pyjarowinkler import distance
from  collections import Counter



#g = Graph()
#g.parse("data.owl")
g = rdflib.Graph()
g.parse("http://purl.obolibrary.org/obo/go.owl")

f = open('ontologies.json', 'a+')
firstLine = f.readline()
if Counter(firstLine) != Counter('ID, URI, TYPE, LABEL'):
    f.write('ID, URI, TYPE, LABEL')
f.close()

print(len(g))
# n is a subclass name and its class name is good-behaviour
# which i want to be the result
#n = "pity"

#for subj, obj in g.subject_objects(predicate=RDFS.subClassOf):
#   print(g.label(subj))

#for s in g.subjects(predicate=None,object=None):
#    print(g.label(s))
searchLabel = 'obsolete neurotransmitter'
for subj in g.subjects(predicate=None, object=None):

#    print(pred)
#subjLabel = g.preferredLabel(subj,lang='en',default=None, labelProperties=(SKOS.prefLabel, RDFS.label))
    subjLabel = g.label(subj, default='')
#    print(subjLabel+'  len='+str(len(subjLabel))+'\n')
    if ((len(subjLabel) > 0) and (searchLabel in subjLabel)):
#        getLabel = subjLabel.pop(0)[1]
#        print(subjLabel)
#        if searchLabel in getLabel:
#        print(subj)

        for p, o in g.predicate_objects(subject=subj):
#            print('predicate = ' + p)
            predidate = p
#            print('object = ' + o)
            object = o
            tabPredicate = predidate.split('#')
            if len(tabPredicate) == 2:
                if Counter(tabPredicate[1]) == Counter('id'):
                    tabObject = object.split('#')
                    with open('ontologies.json', 'a+') as f:
                        if len(tabObject) == 2:
                            f.write(tabObject[1]+', ')
                        else:
                            f.write('None')
                        f.write(subj+', ')
                    f.close()

                if Counter(tabPredicate[1]) == Counter('type'):
                    tabObject = object.split('#')
                    with open('ontologies.json', 'a+') as f:
                        if len(tabObject) == 2:
                            f.write(tabObject[1]+', ')
                        else:
                            f.write('None')
                    f.close()
                if Counter(tabPredicate[1]) == Counter('label'):
                    tabObject = object.split('#')
                    with open('ontologies.json', 'a+') as f:
                        if len(tabObject) == 2:
                            f.write(tabObject[1]+'\n')
                        else:
                            f.write('None')
                            f.write('\n')
                    f.close()

#        print('Lablel='+subjLabel+'   similarity=%.2f  comment=%s \n'%(float(distance.get_jaro_distance(subjLabel, searchLabel, winkler=True, scaling=0.1)), g.comment(subject=subj, default='')))





