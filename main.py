from rdflib import *
import lxml.html
import requests
import queue

xpaths = [{"/html/body/div[3]/div[3]/div[5]/div[1]/table[1]/tbody/tr[th/a/text()='Population']/following-sibling::*[1]/td/text()", True,"Population"},
      {"/html/body/div[3]/div[3]/div[5]/div[1]/table[1]/tbody/tr[th/div/a/text() = 'President']/td/a/text()",False,"President"},
       {"/html/body/div[3]/div[3]/div[5]/div[1]/table[1]/tbody/tr[th/div/a/text() = 'Prime Minister']/td/a/text() ",True,"Prime Minister"},
       {"/html/body/div[3]/div[3]/div[5]/div[1]/table[1]/tbody/tr[th/a/text() ='Area ']/following-sibling::*[1]/td/text() ",True,"Area"},
       {"/html/body/div[3]/div[3]/div[5]/div[1]/table[1]/tbody/tr[th/text() = 'Capital']/td/a/text()",True,"Capital"},
       {"/html/body/div[3]/div[3]/div[5]/div[1]/table[1]/tbody/tr[./th/a[text()='Government']]/td/a/text() | tr[./th/a[text()='Government']]/td/span/a/text() | tr[./th/text()='Government']/td/a/text()",True,"Government Form"}
      ]

r = requests.get("https://en.wikipedia.org/wiki/List_of_countries_by_population_(United_Nations)")
doc = lxml.html.fromstring(r.content)
countries_queue = queue.Queue()
prefix = "http://en.wikipedia.org"
RDF_URI_PREFIX = "http://example.org/"
labels_for_country = ["Prime Minister", "President", "Government", "capital", "Area"]
labels_for_Persons = ["Born"]


def create_ontology():
    g = Graph()
    import_countries()
    while not countries_queue.empty():
        country = countries_queue.get()
        countryname = country[5:]
        country_literal = URIRef(RDF_URI_PREFIX + countryname)
        for xp in xpaths[:5]:
            add_to_ontology(countryname, xp[0], xp[1], xp[2], g)


def add_to_ontology(name, xpath, spaces,literal,g):
    for elem in self.doc.xpath(xpath):
        if spaces:
            g.add((country, URIRef(RDF_URI_PREFIX + literal), Literal(str(elem).replace(" ", ""))))
        else:
            g.add((country, URIRef(RDF_URI_PREFIX + literal), Literal(str(elem))))





def push_to_queue(t, entitype):
#    if (f"{prefix}{t}" not in visited):
        countries_queue.put((entitype, f"{prefix}{t}"))
 #       visited.add(f"{prefix}{t}")








def import_countries():
    count = 0
    states = []
    for t in doc.xpath('//table[@class="wikitable sortable static-row-numbers plainrowheaders srn-white-background"]//tr/td[1]/span/a[1]/@href |'
                       '//table[@class="wikitable sortable static-row-numbers plainrowheaders srn-white-background"]//tr/td[1]/i/a[1]/@href | '
                       '//table[@class="wikitable sortable static-row-numbers plainrowheaders srn-white-background"]//tr/td[1]/span[@class = "flagicon"]/following-sibling::a[1]/@href'):
        if (t not in states and not t.startswith('#') ):
            count += 1
            states.append(t)
            push_to_queue(t,"country")
            print(count, t)
    print(count)
    ##crawl(countries_queue)

print(" Hello World              ".strip())
import_countries()




