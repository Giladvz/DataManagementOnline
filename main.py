import urllib.parse

from rdflib import *
import lxml.html
import requests
import queue
import re

xpaths = [["//table[contains(@class, 'infobox')]/tbody/tr[th//text()='Population']/following::td[1]/text()[1]","Population"],
               ["//table[contains(@class, 'infobox')]/tbody/tr[th//text()='President']/td//a[1][not(contains(@href,'#cite'))]/text()","President"],
               ["//table[contains(@class, 'infobox')]/tbody/tr[th//text()='Prime Minister']/td/a[1][not(contains(@href,'#cite'))]/text()","Prime_Minister"],
               ["//table[contains(@class, 'infobox')]/tbody/tr[th//text()='Area ']/following::td[1]/text()[1]" ,"Area"],
               ["//table[contains(@class, 'infobox')]/tbody/tr[th//text()='Capital']/td/a[1][not(contains(@href,'#cite'))]/@href","Capital"],
               ["//table[contains(@class, 'infobox')]/tbody/tr[th//text()='Government']/td//a[not(contains(@href,'#cite'))]/@href","Government_Form"]]






##pipi's xpaths
p_birth_date_xpath = "//table[contains(@class, 'infobox')]/tbody/tr[th//text()='Born']//span[@class='bday']//text()"

p_birth_place_xpath = "//table[contains(@class, 'infobox')]/tbody/tr[th//text()='Born']//td[1]//text()"

states = []
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
def get_prim_and_pres(p, g):
    url = prefix + "/wiki/" + p
    doc = lxml.html.fromstring((requests.get(url).content))
    birth_data = doc.xpath(p_birth_place_xpath)
    ret = search_for_country(birth_data)
    if (ret):
        print(Literal(
            str(RDF_URI_PREFIX + "/wiki/"+ret.replace(" ", "_")).strip()) + " is the " + RDF_URI_PREFIX + "Birth_Place" + " of " + RDF_URI_PREFIX + p.replace(
            " ", "_"))
        g.add((URIRef(str(RDF_URI_PREFIX + "/wiki/"+ret.replace(" ", "_")).strip()), URIRef(RDF_URI_PREFIX + "Birth_Place"),
               URIRef(RDF_URI_PREFIX + p.replace(" ", "_"))))
    for elem in doc.xpath(p_birth_date_xpath):
        if (elem):
            print(Literal(str(RDF_URI_PREFIX + elem).strip()) + " is the " + RDF_URI_PREFIX + "Birth_Date" + " of " + RDF_URI_PREFIX + p.replace(" ", "_"))
            g.add((Literal(str(RDF_URI_PREFIX + elem).strip()), URIRef(RDF_URI_PREFIX + "Birth_Date"),
                   URIRef(RDF_URI_PREFIX + p.replace(" ", "_"))))


def search_for_country(elem):
    for country in states:
        if(country in str(elem)):
            return country
    return None




def add_to_ontology(country, xpath, literal, g):
    r = requests.get(prefix + country)
    doc = lxml.html.fromstring(r.content)
    for elem in doc.xpath(xpath):
        if elem == None:
            print(country, literal, " is empty")
            break
        elem = elem.strip()
        elem = elem.replace(" ", "_")
        elem = urllib.parse.quote(elem)
        if (literal in ["Prime_Minister", "President"]):
            get_prim_and_pres(elem, g)
            g.add((URIRef(str(RDF_URI_PREFIX+elem).strip()), URIRef(RDF_URI_PREFIX + literal), URIRef(RDF_URI_PREFIX + country[5:])))
            print(RDF_URI_PREFIX + literal + " of " + RDF_URI_PREFIX + country[5:] + " is " + Literal(str(RDF_URI_PREFIX+elem).strip()))
        elif (literal == "Capital"):
            g.add((URIRef(str(RDF_URI_PREFIX+elem[5:]).strip()), URIRef(RDF_URI_PREFIX + literal), URIRef(RDF_URI_PREFIX + country[5:])))
            print(RDF_URI_PREFIX + literal + " of " + RDF_URI_PREFIX + country[5:] + " is " + Literal(str(RDF_URI_PREFIX+elem[5:]).strip()))
        elif (literal in ["Area", "Population"]):
            elem = urllib.parse.unquote(elem)
            elem = re.match("^(\d+).*",elem)
            print(elem.group(1))
            g.add((Literal(str(elem).strip()), URIRef(RDF_URI_PREFIX + literal), URIRef(RDF_URI_PREFIX + country[5:])))
            print(RDF_URI_PREFIX + literal + " of " + RDF_URI_PREFIX + country[5:] + " is " + Literal(str(elem).strip()))
        else:
            g.add((URIRef(str(RDF_URI_PREFIX+elem[5:]).strip()), URIRef(RDF_URI_PREFIX + literal), URIRef(RDF_URI_PREFIX + country[5:])))
            elem = urllib.parse.unquote(elem)
            print(RDF_URI_PREFIX + literal + " of " + RDF_URI_PREFIX + country[5:] + " is " + Literal(str(RDF_URI_PREFIX+elem).strip()))



def import_countries():
    count = 0
    r = requests.get("https://en.wikipedia.org/wiki/List_of_countries_by_population_(United_Nations)")
    doc = lxml.html.fromstring(r.content)
    for t in doc.xpath('//table[@class="wikitable sortable static-row-numbers plainrowheaders srn-white-background"]//tr/td[1]/span/a[1]/@href |'
                       '//table[@class="wikitable sortable static-row-numbers plainrowheaders srn-white-background"]//tr/td[1]/i/a[1]/@href | '
                       '//table[@class="wikitable sortable static-row-numbers plainrowheaders srn-white-background"]//tr/td[1]/span[@class = "flagicon"]/following-sibling::a[1]/@href'):
        if (t not in states and not t.startswith('#') ):
            count += 1
            states.append(t[6:].replace("_", " "))
            countries_queue.put(t)
            print(count, t)
    print(states)
    ##crawl(countries_queue)


create_ontology()
