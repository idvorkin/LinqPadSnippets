import concurrent.futures as futures
import urllib.request
import time
import sys 
from bs4 import BeautifulSoup

start = time.time()
urls = ["http://www.google.com", "http://www.techbargains.com", "http://www.slashdot.org", "http://www.apple.com"]

def url_to_title(url):
    title = ""
    try:
     page = urllib.request.urlopen(url)
     soup = BeautifulSoup(page,"html.parser")
     title = soup.title.string
     print (f"{url} t:{time.time() -start}")
    except: 
        e = sys.exc_info()[0]
        title = f"failed to load {url} {str(e)}"
    return title

with futures.ThreadPoolExecutor(max_workers=5) as executor:
    pages = executor.map(url_to_title, urls)

# pages is a generator of futures (in ordered return. Need to convert to list to access each element.
print (list(pages))
