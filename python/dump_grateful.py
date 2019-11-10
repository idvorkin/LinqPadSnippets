from collections import defaultdict, namedtuple
import re
import glob
import os

# Open all md files
# read till hit line grateful
# skip all lines that don't start with d.
# copy all lines till hit  ## affirmations
def extractGratefulFromList(l):
    matches = re.findall("\d\.\s*(.*)", l)
    return matches


def extractGratefulFromDailyFile(f):
    startMark = "## Grateful for:"
    isInGratefulList = False
    endMark = "## Day awesome if:"
    reasonsGrateful = []
    fp = open(f)
    for i, l in enumerate(fp.readlines()):
        if startMark in l:
            isInGratefulList = True
            continue
        if endMark in l:
            isInGratefulList = False
            continue
        if not isInGratefulList:
            continue
        reasonsGrateful += extractGratefulFromList(l)
    return reasonsGrateful


def extractGratefulFromGlob(directory):
    results = []
    for f in glob.glob(directory):
        results += extractGratefulFromDailyFile(f)
    return results


def groupGrateful(reasons_to_be_grateful):
    grateful_by_reason = defaultdict(list)
    categories = "up early;magic;up early;diet;essential;appreciate;daily;zach;amelia;tori ".split(';')

    for reason in all_reasons_to_be_grateful:
        if reason == "":
            continue

        normalized_reason = reason.lower()
        key = normalized_reason

        # if it's a category then
        for category in categories:
            if category in normalized_reason:
                key = category
                break

        grateful_by_reason[key] += [reason]

    l2 = [(k, grateful_by_reason[k]) for k in grateful_by_reason]
    l3 = sorted(l2, key=lambda x: len(x[1]))
    return l3

# extractGratefulReason("a. hello world")
# extractGratefulFromDailyFile("/home/idvorkin/gits/igor2/750words/2019-11-04.md"
# r = dumpAll(os.path.expanduser("~/gits/igor2/750words/*md")
#all_reasons_to_be_grateful = extractGratefulFromGlob (os.path.expanduser("~/gits/igor2/750words_new_archive/*md"))
all_reasons_to_be_grateful = extractGratefulFromGlob (os.path.expanduser("~/gits/igor2/750words/*md"))
grouped = groupGrateful(all_reasons_to_be_grateful)

# TODO: Consider adding a date index.
for l in grouped:
    print(f"{l[0]}")
    isList = len(l[1]) > 1
    if isList:
        for m in l[1]:
            print(f"   {m}")
