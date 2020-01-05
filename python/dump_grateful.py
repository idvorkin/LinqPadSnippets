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
    matches += re.findall("-\\s*(.*)", l)
    return matches


def isSectionStart(l, section):
    return re.match(f"^##.*{section}.*", l) is not None


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


def makeCategoryMap():
    category_map_i = {}
    category_map_data= {"wake":"up early;wake;work",
                "magic":"magic;card;palm",
                "diet":"diet;eating;juice;juicing;weight",
                "exercise": "gym;exercise;ring"
                }
    # todo figure out how to stem
    categories_flat = "anxiety;essential;appreciate;daily;zach;amelia;tori;offer;bike;meditate;interview".split(";")

    for (category,words) in category_map_data.items():
        category_map_i[category] = words.split(";")
    for c in categories_flat: category_map_i[c] = [c]

    # do some super stemming - probably more effiient way
    suffixes="d;ed;s;ing".split(";")
    #print(suffixes)
    for (c,words) in category_map_i.items():
        words = words[:] # force a copy
        #print (words)
        for w in words:
            if w == " " or w == "":continue
            for s in suffixes:
                #print (f"W:{w},s:{s}")
                with_stem = w+s
                #print(f"with_stem:{with_stem}")
                category_map_i[c]+=[with_stem]
        #print(category_map_i[c])



    #print (category_map_i)
    return category_map_i


category_map = makeCategoryMap()
# print (category_map)
categories = category_map.keys()

def lineToCategory(l):
    # NLP tokenizing remove punctuation.
    punctuation="/.,;"
    for p in punctuation:
        l = l.replace(p," ")
    words = l.lower().split()


    for c,words_in_category in category_map.items():
        for w in words:
            # print (f"C:{c},W:{w},L:{l}")
            if w in words_in_category:
                return c
    return None


def groupCategory(reasons_to_be_grateful):
    grateful_by_reason = defaultdict(list)

    for reason in reasons_to_be_grateful:
        if reason == "":
            continue

        category = lineToCategory(reason)
        grateful_by_reason[category] += [reason]

    l3 = sorted(grateful_by_reason.items(), key=lambda x: len(x[1]))
    return l3


def printCategory(grouped):
    for l in grouped:
        if l[0] == None:
            for m in l[1]: print(f"{m}")
            continue

        print(f"{l[0]}")
        for m in l[1]: print(f"   {m}")


# extractGratefulReason("a. hello world")
# m = list(extractListInSection("/home/idvorkin/gits/igor2/750words/2019-11-04.md", "Grateful"))
# print(m)
# r = dumpAll(os.path.expanduser("~/gits/igor2/750words/*md")
# all_reasons_to_be_grateful = extractGratefulFromGlob (os.path.expanduser("~/gits/igor2/750words_new_archive/*md"))


# @click.command()
# @click.argument("glob", default="~/gits/igor2/750words/*md")
# @click.argument("thelist", default="")
def dumpGlob(glob, thelist):
    all_reasons_to_be_grateful = extractListFromGlob(os.path.expanduser(glob), thelist)
    grouped = groupCategory(all_reasons_to_be_grateful)
    printCategory(grouped)


@click.group()
def journal():
    pass


@journal.command()
@click.argument("days", default=7)  # days takes precedent over archive/noarchive
def grateful(days):
    """ What made me grateful """
    return dumpSectionDefaultDirectory("Grateful", days)


@journal.command()
@click.argument("days", default=7)  # days takes precedent over archive/noarchive
def awesome(days):
    """ What made yesterday awesome """
    return dumpSectionDefaultDirectory("Yesterday", days)


@journal.command()
@click.argument("days", default=2)  # days takes precedent over archive/noarchive
def todo(days):
    """ Yesterday's Todos"""
    return dumpSectionDefaultDirectory("if", days)


@journal.command()
@click.argument("weeks", default=4)
@click.argument("section", default="Moments")
def week(weeks, section):
    """ Section of choice for count weeks"""
    return dumpSectionDefaultDirectory(section, weeks, day=False)


# section
def dumpSectionDefaultDirectory(section, days, day=True):
    # assert section in   "Grateful Yesterday if".split()

    print(f"## ----- Section:{section}, days={days} ----- ")

    # Dump both archive and latest.
    listItem = []
    if day:
        files = [
            os.path.expanduser(
                f"~/gits/igor2/750words/{(datetime.now()-timedelta(days=d)).strftime('%Y-%m-%d')}.md"
            )
            for d in range(days)
        ]
        files += [
            os.path.expanduser(
                f"~/gits/igor2/750words_new_archive/{(datetime.now()-timedelta(days=d)).strftime('%Y-%m-%d')}.md"
            )
            for d in range(days)
        ]
        listItem = extractListFromFiles(files, section)
    else:
        # User requesting weeks.
        # Instead of figuring out sundays, just add 'em up.
        files = [
            os.path.expanduser(
                f"~/gits/igor2/week_report/{(datetime.now()-timedelta(days=d)).strftime('%Y-%m-%d')}.md"
            )
            for d in range(days * 8)
        ]
        # print (files)
        listItem = extractListFromFiles(files, section)

    grouped = groupCategory(listItem)
    printCategory(grouped)


if __name__ == "__main__":
    journal()
