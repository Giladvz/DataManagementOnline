import rdflib
import lxml.html
import requests
import queue

g = rdflib.Graph()
r = requests.get("https://en.wikipedia.org/wiki/List_of_countries_by_population_(United_Nations)")
doc = lxml.html.fromstring(r.content)
countries_queue = queue.Queue()
prime_Pres_queue = queue.Queue()
prefix = "http://en.wikipedia.org"
RDF_URI_PREFIX = "http://example.org/"
labels_for_country = ["Prime Minister","President","Government","capital","Area"]
lables_for_Persons = ["Born"]
visited = set()


def push_to_queue(t, entitype):
    if (f"{prefix}{t}" not in visited):
        countries_queue.put((entitype, f"{prefix}{t}"))
        visited.add(f"{prefix}{t}")

def create_ontology(que):
    g =  rdflib.Graph()
    while not que.empty():
        country = que.pop()
        countryname = country[5:]
        country_literal = rdflib.URIRef(RDF_URI_PREFIX + countryname)




def import_countries():
    count = 1
    states = []
    for t in doc.xpath('//table[@class="wikitable sortable static-row-numbers plainrowheaders srn-white-background"]//tr//td[1]//a[1]/@href'):
        if (t not in states and not t.startswith('#') ):
            states.append(t)
            if (f"{prefix}{t}" not in visited):
                countries_queue.put(("Country", f"{prefix}{t}"))
                visited.add(f"{prefix}{t}")
            print(count, t)
            count += 1
    for t in doc.xpath('//table[@class="wikitable sortable static-row-numbers plainrowheaders srn-white-background"]//tr/td[1]/a[1]/@href'):
        states.append(t)
        print(t)
    count = 1
    for t in doc.xpath('//table[@class="wikitable sortable static-row-numbers plainrowheaders srn-white-background"]//tr/td[1]/span/a[1]/@href'):
        states.append(t)
        print(count, t)
        count+=1

    print(count)
    print("/wiki/French_Fifth_Republic" in states)
    ##crawl(countries_queue)


import_countries()




