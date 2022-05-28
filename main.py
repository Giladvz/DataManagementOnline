from rdflib import *
import lxml.html
import requests
import queue

xpaths = [["//table[contains(@class, 'infobox')]/tbody/tr[th//text()='Population']/td//a[1]/text()","Population"],
               ["//table[contains(@class, 'infobox')]/tbody/tr[th//text()='President']/td//a[1]/text()","President"],
               ["//table[contains(@class, 'infobox')]/tbody/tr[th//text()='Prime Minister']/td//a[1]/text()","Prime_Minister"],
               ["//table[contains(@class, 'infobox')]/tbody/tr[th//text()='Area']/td//a[1]/text()","Area"],
               ["//table[contains(@class, 'infobox')]/tbody/tr[th//text()='Capital']/td//a[1]/text()","Capital"],
               ["//table[contains(@class, 'infobox')]/tbody/tr[th//text()='Government']/td//a[not(contains(@href,'#cite'))]/text()","Government_Form"]]






##pipi's xpaths
p_birth_date_xpath = "//table[contains(@class, 'infobox')]/tbody/tr[th//text()='Born']//span[@class='bday']//text()"

p_birth_place_xpath = "//table[contains(@class, 'infobox')]/tbody/tr[th//text()='Born']//td[1]//text()"

countries_queue = queue.Queue()
prefix = "http://en.wikipedia.org/"
RDF_URI_PREFIX = "http://example.org/"
labels_for_country = ["Prime_Minister", "President", "Government_Form", "capital", "Area", "Population"]
labels_for_Persons = ["Born"]


def create_ontology():
    g = Graph()
    import_countries()
    while not countries_queue.empty():
        country = countries_queue.get()
        for xp in xpaths:
            add_to_ontology(country, xp[0], xp[1], g)
    g.serialize(destination='ontology.nt', format='nt')



##Adding pipi's info to the Ontology
def get_prim_and_pres(p,g):
    print(p)
    url = prefix + p.replace(" ", "_")
    doc = lxml.html.fromstring((requests.get(url)).content)
    #print(doc)
    for elem in doc.xpath(p_birth_date_xpath):
        if(elem):
            g.add(Literal(str(elem).strip()),URIRef(RDF_URI_PREFIX + "birth_date"), URIRef(RDF_URI_PREFIX + p))
    #######
    for elem in doc.xpath(p_birth_place_xpath):
        #print(elem)
        #elem = birth_data[-1]
        #print(elem + "--------------------------")
        ########
        g.add(Literal(str(elem).strip()),URIRef(RDF_URI_PREFIX + "birth_location"), URIRef(RDF_URI_PREFIX + p))



def add_to_ontology(country, xpath, literal, g):
    r = requests.get(prefix + country)
    doc = lxml.html.fromstring(r.content)
    for elem in doc.xpath(xpath):
        if (literal in ["Prime_Minister", "President"]):
            get_prim_and_pres(elem, g)
        print(literal+ " of " + country + " is "+ elem)
        g.add((Literal(str(elem).strip()), URIRef(RDF_URI_PREFIX + literal), URIRef(RDF_URI_PREFIX + country[5:])))



def push_to_queue(t):
#    if (f"{prefix}{t}" not in visited):
        countries_queue.put(t)
 #       visited.add(f"{prefix}{t}")


def import_countries():
    count = 0
    states = []
    r = requests.get("https://en.wikipedia.org/wiki/List_of_countries_by_population_(United_Nations)")
    doc = lxml.html.fromstring(r.content)
    for t in doc.xpath('//table[@class="wikitable sortable static-row-numbers plainrowheaders srn-white-background"]//tr/td[1]/span/a[1]/@href |'
                       '//table[@class="wikitable sortable static-row-numbers plainrowheaders srn-white-background"]//tr/td[1]/i/a[1]/@href | '
                       '//table[@class="wikitable sortable static-row-numbers plainrowheaders srn-white-background"]//tr/td[1]/span[@class = "flagicon"]/following-sibling::a[1]/@href'):
        if (t not in states and not t.startswith('#') ):
            count += 1
            states.append(t)
            push_to_queue(t)
            print(count, t)
    ##crawl(countries_queue)

print(" Hello World              ".strip())
create_ontology()