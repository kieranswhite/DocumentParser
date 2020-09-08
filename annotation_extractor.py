import argparse
import fitz



def annotations(doc):
    annotations = []
    pages = []
    for i in range(doc.pageCount):
        page = doc[i]
        pages.append(page)
        for annot in page.annots():
            annotations.append(annot)
    return pages, annotations


def parse(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        anns = list(annotations(doc))
        print(anns)
    finally:
        doc.close()


if __name__ == "__main__":

    argparser = argparse.ArgumentParser(description='Read given PDF file and extract annotation information to JSON format')
    argparser.add_argument('file', nargs=1)
    args = argparser.parse_args()
    file = args.file[0]

    print('Parsing PDF: ' + file + "\n")
    annotation_list = []
    doc = fitz.open(file)
    pgs, anns = annotations(doc)
    for annotation in anns:

        annot_lines = (str(annotation.info["content"])).rstrip().splitlines()
        annot_conf = dict()

        for line in annot_lines:
            key=(line.split(':'))[0]
            value=(line.split(':'))[1]
            annot_conf[key] = value

        r = annotation.rect
        annot_page = annotation.parent
        page_height = annot_page.MediaBox.height

        r.y0 = page_height + (-1 * r.y0)
        r.y1 = page_height + (-1 * r.y1)

        annot_conf['coordinates'] = str(r.x0) + ',' + str(r.y0) + ',' + str(r.x1) + ',' + str(r.y1)

        annotation_list.append(annot_conf)

        print("Annotation Info: \n" + str(annot_conf) + "\n")

    print("PDF annotations parsed")
    doc.close()



