from pdfrw import PdfReader, PdfWriter, PageMerge


def make_all_up(pages):
    result = PageMerge()
    # note: pagemerge() resizes based on content so we now have a
    # (pagecount)*width by height page.  Ideally we'd then resize the page, but
    # this is fine for now since we can use print to scale in print programs.
    for page in pages:
        # p.scale(0.5)
        result.add(page)
        first_page_added = len(result) == 1
        if first_page_added:
            continue

        added_page = result[-1]
        second_last_page_added = result[-2]
        added_page.x = second_last_page_added.x + second_last_page_added.w

    return result.render()


def main():
    input_pdf = "/temp/input.pdf"
    output_pdf = '/temp/output.pdf'
    pages = PdfReader(input_pdf).pages
    PdfWriter(output_pdf).addpage(make_all_up(pages)).write()


main()
