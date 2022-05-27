import rdflib
import lxml.html
import requests
import queue

g = rdflib.Graph()
r = requests.get("https://en.wikipedia.org/wiki/List_of_countries_by_population_(United_Nations)")
doc = lxml.html.fromstring(r.content)
urls_queue = queue.Queue()
prefix = "http://en.wikipedia.org"
labels_for_country = ["Prime Minister","President","Government","capital","Area"]
lables_for_Persons = ["Born"]
visited = set()


def push_to_queue(t, entitype):
    if (f"{prefix}{t}" not in visited):
        urls_queue.put((entitype, f"{prefix}{t}"))
        visited.add(f"{prefix}{t}")

def crawl(queue):




def import_countries():
    count = 1
    states = []
    for t in doc.xpath('//table[@class="wikitable sortable static-row-numbers plainrowheaders srn-white-background"]//tr//td[1]//a[1]/@href'):
        if (t not in states and not t.startswith('#') ):
            states.append(t)
            if (f"{prefix}{t}" not in visited):
                urls_queue.put(("Country", f"{prefix}{t}"))
                visited.add(f"{prefix}{t}")
            print(count, t)
            count += 1
    print(count)
    crawl(urls_queue)



