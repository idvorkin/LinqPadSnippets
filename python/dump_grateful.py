from collections import *
import re
import glob
import os
# Open all md files
# read till hit line grateful
# skip all lines that don't start with d.
# copy all lines till hit  ## affirmations
def extractGratefulFromList(l):
    matches = re.findall("\d\.\s*(.*)",l)
    return matches

def extractGratefulFromDailyFile(f):
    startMark = "## Grateful for:"
    isInGratefulList = False
    endMark = "## Day awesome if:"
    reasonsGrateful=[]
    fp = open (f)
    for i,l in enumerate(fp.readlines()):
        if startMark in l:
            isInGratefulList = True
            continue
        if endMark in l:
            isInGratefulList = False
            continue
        if not isInGratefulList:
            continue
        reasonsGrateful+=extractGratefulFromList(l)
    return reasonsGrateful
def dumpAll(directory):
    results = []
    for f in glob.glob(directory):
        results += extractGratefulFromDailyFile(f)
    return results

#extractGratefulReason("a. hello world")
# extractGratefulFromDailyFile("/home/idvorkin/gits/igor2/750words/2019-11-04.md")
#r = dumpAll("/home/idvorkin/gits/igor2/750words/*md")
r = dumpAll("/home/idvorkin/gits/igor2/750words_new_archive/*md")
# TODO: Consider adding a date index.
grateful = defaultdict(int)
for l in r:
    grateful[l.lower()]+=1

l2 =  [(grateful[k], k) for k in grateful]
l3 = sorted(l2,key=lambda x:x[0])
for l in l3:
    print (f"{l[0]}:{l[1]}")

