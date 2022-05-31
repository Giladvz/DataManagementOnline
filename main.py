import urllib.parse
import sys
from rdflib import *
import lxml.html
import requests
import queue
import re
import time

xpaths = [["//table[contains(@class, 'infobox')][1]/tbody/tr[th//text()='Population']/td/text()[1] | "
           "//table[contains(@class, 'infobox')][1]/tbody/tr[th//text()='Population']/following::td[1]/div/ul/li[1]/text()[1] | "
           "//table[contains(@class, 'infobox')][1]/tbody/tr[th//text()='Population']/following::td[1]/text()[1] | "
           "//table[contains(@class, 'infobox')][1]/tbody/tr[th//text()='Population']/following::td[1]/span/text()[1] | "
           "//table[contains(@class, 'infobox')][1]/tbody/tr[th//text()='Population']/following::td[1]/span/span/text() | "
           "//table[contains(@class, 'infobox')][1]/tbody/tr[th//text()='Population']/following::td[1]/i/text()","Population"],
               ["//table[contains(@class, 'infobox')][1]/tbody/tr[th//text()='President']/td//a[1][not(contains(@href,'#cite'))]/@href","President"],
               ["//table[contains(@class, 'infobox')][1]/tbody/tr[th//text()='Prime Minister']/td/a[1][not(contains(@href,'#cite'))]/@href","Prime_Minister"],
               ["//table[contains(@class, 'infobox')][1]/tbody/tr[th//text()='Area ']/following::td[1]/text()[1] | "
                "//table[contains(@class, 'infobox')][1]/tbody/tr[th//text()='Area']/following::td[1]/text()[1] | "
                "//table[contains(@class, 'infobox')][1]/tbody/tr[th//text()='Area']/td/text()[1]", "Area"],
               ["//table[contains(@class, 'infobox')][1]/tbody/tr[th//text()='Capital']/td//a[1][not(contains(@href,'#cite'))]/@href","Capital"],
               ["//table[contains(@class, 'infobox')][1]/tbody/tr[th//text()='Government']/td//a[not(contains(@href,'#cite'))]/@href","Government_Form"]]

## people's xpaths
p_birth_date_xpath = "//table[contains(@class, 'infobox')][1]/tbody/tr[th//text()='Born']//span[@class='bday']//text()"
p_birth_place_xpath = "//table[contains(@class, 'infobox')][1]/tbody/tr[th//text()='Born']//td[1]//text()"

states = []
countries_queue = queue.Queue()
prefix = "http://en.wikipedia.org/"
RDF_URI_PREFIX = "http://example.org/"
labels_for_country = ["Prime_Minister", "President", "Government_Form", "capital", "Area", "Population"]
labels_for_Persons = ["Born"]
create = "create"
question = "question"
cnt = [["States: ", 0], ["Prim: ", 0], ["Pres: ", 0], ["Gov: ", 0], ["Cap: ", 0], ["Area: ", 0], ["Pop: ", 0], ["Date: ", 0 ], ["Place: ", 0]]

def create_ontology():
    g = Graph()
    import_countries()
    for i in range(0):
        countries_queue.get()
    while not countries_queue.empty():
        country = countries_queue.get()
        cnt[0][1] += 1
        for xp in xpaths:
            add_to_ontology(country, xp[0], xp[1], g)
    for a in cnt:
        print(str(a[0]) + str(a[1]))
    g.serialize(destination='ontology.nt', format='nt', encoding="utf-8", errors="ignore")


def import_countries():
    r = requests.get("https://en.wikipedia.org/wiki/List_of_countries_by_population_(United_Nations)")
    doc = lxml.html.fromstring(r.content)
    for t in doc.xpath('//table[@class="wikitable sortable static-row-numbers plainrowheaders srn-white-background"]//tr/td[1]/span/a[1]/@href |'
                       '//table[@class="wikitable sortable static-row-numbers plainrowheaders srn-white-background"]//tr/td[1]/i/a[1]/@href | '
                       '//table[@class="wikitable sortable static-row-numbers plainrowheaders srn-white-background"]//tr/td[1]/span[@class = "flagicon"]/following-sibling::a[1]/@href'):
        if (t not in states and not t.startswith('#') ):
            states.append(t[6:].replace("_", " "))
            countries_queue.put(t)


def add_to_ontology(country, xpath, literal, g):
    r = requests.get(prefix + country)
    doc = lxml.html.fromstring(r.content)
    # If doc.xpath(xpath) is empty, doesn't go in
    for elem in doc.xpath(xpath):
        elem = elem.strip()
        elem = elem.replace(" ", "_")
        elem = urllib.parse.quote(elem)
        if (literal in ["Prime_Minister", "President"]):
            if (literal == "Prime_Minister"):
                cnt[1][1] += 1
            else:
                cnt[2][1] += 1
            get_prim_and_pres(elem, g)
            g.add((URIRef(str(RDF_URI_PREFIX+elem[6:]).strip()), URIRef(RDF_URI_PREFIX + literal), URIRef(RDF_URI_PREFIX + country[6:])))
            #print(RDF_URI_PREFIX + literal + " of " + RDF_URI_PREFIX + country[5:] + " is " + Literal(str(RDF_URI_PREFIX+elem).strip()))
        elif (literal == "Capital"):
            cnt[4][1] += 1
            g.add((URIRef(str(RDF_URI_PREFIX+elem[6:]).strip()), URIRef(RDF_URI_PREFIX + literal), URIRef(RDF_URI_PREFIX + country[6:])))
            #print(RDF_URI_PREFIX + literal + " of " + RDF_URI_PREFIX + country[5:] + " is " + Literal(str(RDF_URI_PREFIX+elem[5:]).strip()))
            break
        elif (literal in ["Area", "Population"]):
            elem = urllib.parse.unquote(elem)
            if elem == "" or elem == " " or elem == " (" or elem == "(":
                continue
            if (literal == "Area"):
                cnt[5][1] += 1
            else:
                cnt[6][1] += 1
            elem = re.match("^([-0-9,\.–]+).*",elem)
            elem = elem.group(1)
            g.add((URIRef(RDF_URI_PREFIX + country[6:]), URIRef(RDF_URI_PREFIX + literal), Literal(str(elem).strip())))
            #print(RDF_URI_PREFIX + literal + " of " + RDF_URI_PREFIX + country[5:] + " is " + Literal(str(elem).strip()))
            break
        else:
            cnt[3][1] += 1
            g.add((URIRef(str(RDF_URI_PREFIX+elem[6:]).strip()), URIRef(RDF_URI_PREFIX + literal), URIRef(RDF_URI_PREFIX + country[6:])))
            elem = urllib.parse.unquote(elem)
            #print(URIRef(str(RDF_URI_PREFIX+elem[6:]).strip()), URIRef(RDF_URI_PREFIX + literal), URIRef(RDF_URI_PREFIX + country[6:]))


##Adding people's info to the Ontology
def get_prim_and_pres(p, g):
    p = urllib.parse.unquote(p)
    url = prefix + p
    doc = lxml.html.fromstring((requests.get(url).content))
    birth_data = doc.xpath(p_birth_place_xpath)
    ret = search_for_country(birth_data)
    if (ret):
        #print(Literal(
         #   str(RDF_URI_PREFIX + "/wiki/"+ret.replace(" ", "_")).strip()) + " is the " + RDF_URI_PREFIX + "Birth_Place" + " of " + RDF_URI_PREFIX + p.replace(
          #  " ", "_"))
        cnt[8][1] += 1
        g.add((URIRef(str(RDF_URI_PREFIX + "/wiki/"+ret.replace(" ", "_")).strip()), URIRef(RDF_URI_PREFIX + "Birth_Place"),
               URIRef(RDF_URI_PREFIX + p[6:])))
    for elem in doc.xpath(p_birth_date_xpath):
        if (elem):
            cnt[7][1] += 1
            #print(URIRef(str(RDF_URI_PREFIX + elem.strip())),p)
            #print(str(RDF_URI_PREFIX + elem).strip() + " is the " + RDF_URI_PREFIX + "Birth_Date" + " of " + RDF_URI_PREFIX + p.replace(" ", "_"))
            g.add((URIRef(str(RDF_URI_PREFIX + elem).strip()), URIRef(RDF_URI_PREFIX + "Birth_Date"),
                   URIRef(RDF_URI_PREFIX + p[6:])))

def search_for_country(elem):
    for i in range(len(elem)):
        el = elem[i].replace("(","").replace(")","")
        el = el.split(",")
        for j in range(len(el)):
            el[j] = el[j].strip()
        for country in states:
            #if(country in str(elem).split(",")[-1].strip()):
            if(country in el):
                return country
    return None


def get_answer(question):
    g = Graph().parse("ontology.nt")
    query = create_sparql_query(urllib.parse.quote(question))
    answer = g.query(query)
    for i in range(len(list(answer))):
        row = list(answer)[i]  # get row i from query list result.
        entity_with_uri = str(row[0])
        print(entity_with_uri)
        entity_with_uri = entity_with_uri.split("/")
        entity_without_uri = entity_with_uri[-1]
        # the next 3 code lines are to strip excessive spaces in the names.
        entity_without_uri = entity_without_uri.replace("_", " ")
        entity_without_uri = entity_without_uri.strip()
        entity_without_uri = entity_without_uri.replace(" ", "_")
        print(entity_without_uri)
           
##### queries ------------------------
def create_sparql_query(input_question):

    lstq = input_question.split()
    length=len(lstq)
    if(lstq[0] == "Who" and lstq[1] == "is"):
        if(lstq[3] != "the"):
            #who_is_query(retrive_from_lst_by_len(lstq,3,length)) ##q11
                return "select ?x where {?x <http://example.org/President> ?y} UNION {select ?x where {?x <http://example.org/Prime_Minister> ?y}"
        else:
            country = retrive_from_lst_by_len(lstq,5,length)
            #who_is_the_query(country,lstq[3]) ##q1, q2
            if lstq == "president":
                return "select ?x where {?x <http://example.org/President> <http://example.org/"+retrive_from_lst_by_len(lstq,6,length)+">}"
            else:
                return "select ?x where {?x <http://example.org/Prim_Minister> <http://example.org/"+retrive_from_lst_by_len(lstq,7,length)+">}"

           
    elif(lstq[0] == "What" and lstq[1] == "is" and lstq[2] == "the"):
        if(lstq[3] == "form"):
            #what_is_form_query(retrive_from_lst_by_len(lstq,7,length),(lstq[5]+" "+lstq[3])) ##q5
            #return "select ?a where {<http://example.org/"+lstq[5]+"> <http://example.org/"+lstq[3]+"> ?a.} "
            print("A")
        else:
            print("A")
            #what_is_query(retrive_from_lst_by_len(lstq,5,length),lstq[3]) ##q3,q4,q6
    elif(lstq[0] == "When" and lstq[1] == "was" and lstq[2] == "the"):
        if(lstq[3] == "president"):
            #when_was_president_query(retrive_from_lst_by_len(lstq,5,length),lst[3]) ##q7
            print("Todo")
        else:
            #when_was_prime_query(retrive_from_lst_by_len(lstq,6,length),(lst[3]+" "+lst[4])) ##q9
            print("Todo")
    elif(lstq[0] == "Where" and lstq[1] == "was" and lstq[2] == "the"):
        if(lstq[3] == "president"):
            #where_was_president_query(retrive_from_lst_by_len(lstq,5,length),lst[3]) ##q8
            print("Todo")
        else:
            #where_was_prime_query(retrive_from_lst_by_len(lstq,6,length),(lst[3]+" "+lst[4])) ##q10
            print("Todo")
    elif(lstq[0] == "How" and lstq[1] == "many"):
        if(lstq[2] == "presidents" and lstq[length-1] == "born"):
            #how_many_presidents_born_query(retrive_from_lst_by_len(lstq,6,length)) ##q14
            print("Todo")
        elif(lstq[length-1] == "country"):
            #how_many_presidents_self_born_query() ##personal
            print("Todo")
        else:
            gov1 = retrive_from_lst_by_str(lstq,2,"are")
            i = get_index(lstq,"also")
            gov2 = retrive_from_lst_by_len(lstq,i+1,length)
            #how_many_governmnet_form_query(gov1,gov2) ##q12
    elif(lstq[0] == "List" and lstq[1] == "all"):
        #list_all_query(retrive_from_lst_by_len(lstq,10,length)) ##q13
        print("Todo")


def retrive_from_lst_by_len(lst,i,j):
    ret = ""
    for k in range(i,j):
        if(ret != ""):
            ret += "_"
        ret += lst[k]
    if(j == len(lst)):
        ret = ret[:len(lst)-1]
    return ret

def retrive_from_lst_by_str(lst,i,st):
    ret = ""
    while(lst[i] != st):
        if(ret != ""):
            ret += "_"
        ret += lst[i]
        i += 1
    return ret

def get_index(lst,st):
    i = 0
    while(lst[i] != st):
        i+=1
    return i

### queries-------------------------------------------------------


def who_is_query():
    g = Graph().parse("ontology.nt")
    query_list_result = g.query("select ?x where {?x <http://example.org/President> <http://example.org/France>}")
    for i in range(len(list(query_list_result))):
        row = list(query_list_result)[i]  # get row i from query list result.
        entity_with_uri = str(row[0])
        print(entity_with_uri)
        entity_with_uri = entity_with_uri.split("/")
        entity_without_uri = entity_with_uri[-1]
        # the next 3 code lines are to strip excessive spaces in the names.
        entity_without_uri = entity_without_uri.replace("_", " ")
        entity_without_uri = entity_without_uri.strip()
        entity_without_uri = entity_without_uri.replace(" ", "_")
        print(entity_without_uri)
        #res_string += entity_without_uri + " "  # get the entity name without the uri.
    #g.query("select ?x,?y where {
    #?x <prefix + ?y> .
    #?x < r2 > ?y}")


if __name__ == '__main__':
    if sys.argv[1] == create:
        start = time.time()
        create_ontology()
        end = time.time()
        print("time: ", end - start)
    elif sys.argv[1] == question:
        get_answer(sys.argv[2])







