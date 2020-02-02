# I like to know what movies are available on yts.ag, it publishes an RSS feed, but it's
# got a bunch of duplicates in it. I'd like to create an RSS feed that is uniq. This
# will be a lambda which will A) Download RSS feed, uniq and publish.

import xml.etree.ElementTree as ET
import requests as requests
import concurrent.futures as futures

def download_and_get_all_titles():
    with futures.ThreadPoolExecutor(max_workers=100) as executor:
        #get_title_jobs = executor.map(download_and_get_all_title, range(10))
        #for t in get_title_jobs:
            #yield from t
        tasks = [executor.submit(download_and_get_all_title, t) for t in range(100)]
        for task in futures.as_completed(tasks):
            yield from task.result()

def download_and_get_all_title(page_index):
    print(f"{page_index}: Download++")
    response = requests.get(f"https://yts.mx/rss/{page_index}/1080p/all/0")
    root = ET.fromstring(response.content)
    titles = [elem.text for elem in root.findall("*/item/title")]
    yield from titles
    print(f"{page_index}: Download--")

movies = list(download_and_get_all_titles())
print (len(movies))
print (len(set(movies)))
