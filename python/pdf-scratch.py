import sys
import os

from pdfrw import PdfReader, PdfWriter, PageMerge


def makeAllUp(pages):
    result = PageMerge()
    # NOTE: PageMerge() resizes based on content so we now have a (pageCount)*width by height page. 
    #       Ideally we'd then resize the page, but this is fine for now since we can use print to scale in 
    #       print programs.
    for p in pages:
        result.add(p)
        firstPageAdded = len(result) == 1
        if firstPageAdded: continue; 

        addedPage = result[-1]
        secondLastAddedPage = result[-2]
        addedPage.x = secondLastAddedPage.x + secondLastAddedPage.w

    return result.render()

inputPdf = "/temp/input.pdf"
output = '/temp/output.pdf'
pages = PdfReader(inputPdf).pages
PdfWriter(output).addpage(makeAllUp(pages)).write()
