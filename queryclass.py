from rdflib import Graph
from rdflib.namespace import RDFS, RDF, SKOS
from pyjarowinkler import distance

g = Graph()
g.parse("data.owl")
print(len(g))
# n is a subclass name and its class name is good-behaviour
# which i want to be the result
#n = "pity"


#for subj, obj in g.subject_objects(predicate=RDFS.subClassOf):
#   print(g.label(subj))

#for s in g.subjects(predicate=None,object=None):
#    print(g.label(s))

for subj in g.subjects(predicate=None, object=None):
    subjLabel = g.preferredLabel(subj,lang='en',default=None, labelProperties=(SKOS.prefLabel, RDFS.label))
    if subjLabel:
        getLabel = subjLabel.pop(0)[1]
        if 'known' in getLabel:
            print('Lablel '+getLabel+' similarity = %d   URI = %s',float(distance.get_jaro_distance(getLabel, 'known', winkler=True, scaling=0.1)), subj)