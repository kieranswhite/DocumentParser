import re
from fitz import fitz
from itertools import groupby
import pandas as pd
import camelot

from utils import calculate_pages
from flask import current_app
from .base_parser import *

class PDFParser(BaseParser):

    num_pages = ""

    parsed_tables = {}
    parsed_texts = {}
    parsed_fields = {}

    def __init__(self,doc_config,document_path):
        super().__init__(doc_config,document_path)


    def parse(self):

        current_app.logger.debug("Parsing PDF")
        # Open the PDF and set the number of pages
        self.doc = fitz.open(self.document_path)
        self.num_pages = self.doc.pageCount

        ## check for table, text and fields and then call the parse methods accordingly
        if 'tables' in self.config:
            self.parse_tables(self.config['tables'])

        if 'text' in self.config:
            self.parse_texts(self.config['text'])

        if 'fields' in self.config:
            self.parse_fields(self.config['fields'])


        # combine dataframes into one dictionary of dataframes each with a unique key
        for table_id, table in self.parsed_tables.items():
            self.output_dict['table_'+ table_id] = table

        for text_id, text in self.parsed_texts.items():
            self.output_dict['text_' + text_id] = text

        for field_id, field in self.parsed_fields.items():
            self.output_dict['field_'+ field_id] = field

        # return the dictionary of dataframes from the PDF
        return self.output_dict


    # For each table in the config parse it
    def parse_tables(self,tables_config):
        for table in tables_config:
            self.parsed_tables[table['id']] = self.parse_table(table)
        return True


    def parse_table(self,table_config):
        dfs = []
        for section in table_config['sections']:
            page_list = calculate_pages(section['pages'],self.num_pages)

            for page in page_list:

                if 'strip_text' in section:
                    strip_text = section['strip_text']
                else:
                    strip_text = None

                camelot_tables = camelot.read_pdf(str(self.document_path),table_regions=[section['table_region']],pages=str(page),flavor=table_config['type'],strip_text=strip_text)

                if camelot_tables.n != 1:
                    raise ParsingException("error! table: " + table_config['id'] + " not parsed on page: " + page)

                else:
                    section_df = camelot_tables[0].df
                    
                    if section['header'] == 'Y':
                        section_df = section_df.iloc[1:]

                    if len(table_config['fields']) != len(section_df.columns):
                        raise ParsingException('Table Config specified: ' + str(len(table_config['fields'])) + ' fields, but table:' + str(table_config['id']) + ' has: ' + str(len(section_df.columns)) + ' fields')
                    else:
                        section_df.columns = table_config['fields']

                    dfs.append(section_df)
        #combine all section dfs
        table_df = pd.concat(dfs, axis=0, ignore_index=True)

        if len(table_config['fields']) != len(table_df.columns):
            raise ParsingException('Table Config specified: ' + str(len(table_config['fields'])) + ' fields, but table: ' + str(table_config['id']) + ' has: ' + str(len(table_df.columns)) + ' fields' )
        else:
            table_df.columns = table_config['fields']

        return table_df



    def parse_texts(self,texts_config):
        for text in texts_config:
            self.parsed_texts[text['id']] = self.parse_text(text)
        return True


# TODO add functionality to parse all text out of a document rather than sections as a new text type
    def parse_text(self,text_config):
        # list of dataframes to return
        dfs = []

        # open the PDF
        pdf = fitz.open(str(self.document_path))

        # for each section in the text config parse text
        for section in text_config['sections']:
            # Calculate the set of pages based off of the pages syntax for this tool
            page_list = calculate_pages(section['pages'], self.num_pages)

            for page in page_list:
                # PyMuPDF is 0 indexed so change page numbers and select the correct page
                page = page-1
                pdf_page = pdf[page]

                # Set rectangle PDF coordinate based on config
                rect_coords = section['text_region'].split(",")

                # Establish the height of the page
                page_height = pdf_page.MediaBox.height

                # use fitz to create a rectangle and then convert y coordinates from PDF coordinates to PyMuPDF coordinates
                r = fitz.Rect(rect_coords)
                r.y0 = page_height + (-1 * r.y0)
                r.y1 = page_height + (-1 * r.y1)

                # Extract all words from the page
                page_words = pdf_page.getText("words")

                # Sort all words, select words that intersect with the coordinates and group by line
                page_words.sort(key=lambda w: (w[3], w[0]))
                rect_words = [w for w in page_words if fitz.Rect(w[:4]).intersects(r)]
                group = groupby(rect_words, key=lambda w: w[3])

                # Create a list of lines from each grouped set of words
                lines = []
                for y1, words in group:
                    line = (" ".join(w[4] for w in words))
                    lines.append(line)

                #convert lines to a dataframe
                section_df = pd.DataFrame(lines, columns =['text'])
                dfs.append(section_df)

        # Combine all dataframes for that section into one
        text_df = pd.concat(dfs, axis=0, ignore_index=True)
        # TODO other text types?
        return text_df



    def parse_fields(self,fields_config):
        for field in fields_config:
            self.parsed_fields[field['id']] = self.parse_field(field)
        return True

    def parse_field(self,field_config):
        # Read entire document and use regex for look for a field?
        # list of dataframes to return
        dfs = []
        matches = ""

        # open the PDF
        pdf = fitz.open(str(self.document_path))

        # for each section in the text config parse text
        for section in field_config['sections']:
            # Calculate the set of pages based off of the pages syntax for this tool
            page_list = calculate_pages(section['pages'], self.num_pages)

            try:
                regex = re.compile(section['regex'])
            except:
                raise ParsingException(
                    'Field: '+  str(field_config['id']) + ' regex : ' + str(section['regex'])  + ' failed to compile!. Please review the regex syntax')

            # loop through each page in the section and parse the field
            for page in page_list:

                if matches == 1:
                    break

                page = page - 1
                pdf_page = pdf[page]

                # Extract all words from the page
                page_words = pdf_page.getText("words")

                page_words.sort(key=lambda w: (w[3], w[0]))
                group = groupby(page_words, key=lambda w: w[3])

                page_text = ''
                for y1, words in group:
                    line = (" ".join(w[4] for w in words) + '\n')
                    page_text+=line

                # Extract matches based on the number of matches requested
                if section['matches'] == '1':
                    field_list = [regex.findall(page_text)[0]]
                    if len(field_list) == 0:
                        break
                    elif len(field_list) == 1:
                        matches = 1
                elif section['matches'] == 'all':
                    field_list = regex.findall(page_text)
                else:
                    raise ConfigException('Section matches is: ' + str(section['matches']) + ' and should either be "1" or "all" Please review the syntax')
                page_df = pd.DataFrame(field_list, columns=[str(field_config['id'])])
                dfs.append(page_df)

        field_df = pd.concat(dfs, axis=0, ignore_index=True)
        # TODO other text types?
        return field_df
        # fields per page / section?