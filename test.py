import rdflib

g = rdflib.Graph()
result = g.parse("http://www.w3.org/People/Berners-Lee/card")

print("Graphe has %s statements." % len(g))

q = "select ?title  where { <https://www.w3.org/People/Berners-Lee/card#i> <'http://xmlns.com/foaf/0.1/title'> ?title }"
x = g.query(q)

for row in x:
    print("%s knows %s" % row)
