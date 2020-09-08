import os
import pathlib
import shutil
from urllib.parse import urlparse

import pandas as pd
import boto3

from flask import current_app



class FileWriter(object):

    filename = ''
    output_type = ''

    output_filename = ''

    dataframe = pd.DataFrame()

    def __init__(self, output_type, output_format, output_path, filename, dataframe):
        self.output_type = output_type
        self.output_format = output_format
        self.filename = filename
        self.dataframe = dataframe
        self.output_path = output_path
        self.internal_output_dir = pathlib.Path("./tmp_output_files/")

        # make internal output dir if it doesn't exist
        if not os.path.exists(self.internal_output_dir):
            os.makedirs(self.internal_output_dir)
        # set output filename


    def write(self):
        region_name = os.environ['region_name']

        if self.output_format == 'json':

            self.filename = self.filename + '.json'
            written_file = self.write_json()

        elif self.output_format == 'parquet':

            written_file =  self.write_parquet()

        if self.output_type == 'local':
            # make output dir if it doesn't exist
            if not os.path.exists(self.output_path):
                os.makedirs(self.output_path)

            target_file = os.path.join(self.output_path,self.filename)
            shutil.copyfile(written_file,target_file)
            os.remove(written_file)
            current_app.logger.debug("File written to: " + str(target_file))


        elif self.output_type == 's3':

            s3 = boto3.resource('s3',region_name=region_name)
            o = urlparse(os.path.join(self.output_path,self.filename))
            bucket = str(o.netloc)
            key = str(o.path).strip("/")
            s3.meta.client.upload_file(str(written_file),bucket,key)
            current_app.logger.debug("File written to bucket: " + bucket + ' key: ' + key)
            os.remove(written_file)
            current_app.logger.debug("tmp file: " + written_file + ' removed')




    def write_json(self):
        suffix = '.pdf'
        final_filename = os.path.join(self.internal_output_dir, self.filename)
        self.dataframe.to_json(final_filename,orient = 'records', lines = True)
        current_app.logger.debug("tmp JSON written to: " + final_filename)
        return final_filename



    def write_parquet(self):
        return False





