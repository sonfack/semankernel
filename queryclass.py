from rdflib import Graph
from rdflib.namespace import RDFS, RDF, SKOS

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

for s in g.subjects(predicate=None, object=None):
    print(g.preferredLabel(s,lang='en',default=None, labelProperties=(SKOS.prefLabel, RDFS.label)))