import os
from datetime import datetime
from flask import current_app

from inputs.file_input import FileInput
from parsers.pdf_parser import PDFParser
from outputs.file_writer import FileWriter



def process_document(input_file: str, input_type: str, output_path: str, output_type: str, output_format: str, parse_config: dict):
    current_app.logger.info("Processing Document: " + input_file)

    local_file = read_file(input_file,input_type)

    outputs = parse_file(local_file,parse_config)

    outputs = add_metadata(outputs,parse_config['schema_name'],input_file)

    write_and_output_files(outputs,output_path,output_type,output_format,input_file)

    return True, output_path    




def read_file(input_file, input_type):
    file_input = FileInput()
    if input_type == 's3':
        file_path = file_input.read_s3_file(input_file)
    elif input_type == 'local':
        file_path = file_input.read_local_file(input_file)
    
    return file_path



def parse_file(file_path,parse_config):
    if parse_config['type'] == 'pdf':
            pdf = PDFParser(parse_config,file_path)
            return pdf.parse()
            # outputs is a dict of pandas dataframes which each key being table_$ID, text_$ID, key_$ID.


def write_and_output_files(df_dict,output_path,output_type,output_format,input_filename):
    base_filename = os.path.splitext(os.path.basename(input_filename))[0]

    for key, dataframe in df_dict.items():
        base_output_filename = str(base_filename) + '_' + str(key)


        filewriter = FileWriter(output_type,output_format,output_path,base_output_filename,dataframe)
        written_filename = filewriter.write()

    return False



def add_metadata(dfs: dict,doc_schema,doc_original_filename):
    doc_parsed_datetime = datetime.now()
    
    for key,dataframe in dfs.items():
        dataframe.insert(0,'meta_doc_schema', doc_schema)
        dataframe.insert(0,'meta_doc_original_filename', doc_original_filename)
        dataframe.insert(0,'meta_doc_parsed_datetime', doc_parsed_datetime)

        dfs[key] = dataframe

    return dfs










