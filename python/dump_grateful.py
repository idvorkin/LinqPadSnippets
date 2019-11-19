#!python3
from collections import defaultdict, namedtuple
import re
import glob
import os
import click
from datetime import datetime, timedelta

# Open all md files
# read till hit line grateful
# skip all lines that don't start with d.
# copy all lines till hit  ## affirmations


def extractListItem(l):
    matches = re.findall("\\d\\.\\s*(.*)", l)
    return matches


def isSectionStart(l, section):
    return re.match(f"^##.*{section}.*", l) != None


def extractListInSection(f, section):
    fp = open(f)
    inSection = False
    for l in fp.readlines():
        if inSection:
            isSectionEnd = l.startswith("#")
            if isSectionEnd:
                return

        if isSectionStart(l, section):
            inSection = True

        if not inSection:
            continue

        yield from extractListItem(l)

    return


def extractListFromGlob(directory, section):
    files = [f for f in glob.glob(directory)]
    yield from extractListFromFiles(files, section)


def extractListFromFiles(files, section):
    for f in files:
        if not os.path.exists(f):
            continue
        yield from extractListInSection(f, section)


categories = "up early;magic;up early;diet;essential;appreciate;daily;zach;amelia;tori ".split(
    ";"
)


def groupGrateful(reasons_to_be_grateful):
    grateful_by_reason = defaultdict(list)

    for reason in reasons_to_be_grateful:
        if reason == "":
            continue

        normalized_reason = reason.lower()
        foundCategories = [
            category for category in categories if category in normalized_reason
        ]

        isCategory = len(foundCategories) == 1

        key = foundCategories[0] if isCategory else normalized_reason
        grateful_by_reason[key] += [reason]

    l3 = sorted(grateful_by_reason.items(), key=lambda x: len(x[1]))
    return l3


def printGrateful(grouped):
    for l in grouped:
        print(f"{l[0]}")
        isList = len(l[1]) > 1
        isCategory = any([c in l for c in categories])

        if isList or isCategory:
            for m in l[1]:
                print(f"   {m}")


# extractGratefulReason("a. hello world")
# m = list(extractListInSection("/home/idvorkin/gits/igor2/750words/2019-11-04.md", "Grateful"))
# print(m)
# r = dumpAll(os.path.expanduser("~/gits/igor2/750words/*md")
# all_reasons_to_be_grateful = extractGratefulFromGlob (os.path.expanduser("~/gits/igor2/750words_new_archive/*md"))


@click.command()
@click.argument("glob", default="~/gits/igor2/750words/*md")
@click.argument("thelist", default="")
def dumpGlob(glob, thelist):
    all_reasons_to_be_grateful = extractListFromGlob(os.path.expanduser(glob), thelist)
    grouped = groupGrateful(all_reasons_to_be_grateful)
    printGrateful(grouped)


@click.command()
@click.argument("days", default=0)  # days takes precedent over archive/noarchive
@click.option("--archive/--noarchive", default="False")
@click.option("--grateful/--awesome", default="True")
def dumpDefaults(archive, grateful, days):
    section = "Grateful" if grateful else "Yesterday"

    print(f"----- Section:{section}, days={days}, archive={archive} ----- ")

    listItem = []
    if days > 0:
        files = [
            os.path.expanduser(
                f"~/gits/igor2/750words/{(datetime.now()-timedelta(days=d)).strftime('%Y-%m-%d')}.md"
            )
            for d in range(days)
        ]
        listItem = extractListFromFiles(files, section)
    else:
        glob = (
            "~/gits/igor2/750words/*md"
            if not archive
            else "~/gits/igor2/750words_new_archive/*md"
        )
        listItem = extractListFromGlob(os.path.expanduser(glob), section)

    grouped = groupGrateful(listItem)
    printGrateful(grouped)


if __name__ == "__main__":
    dumpDefaults()
