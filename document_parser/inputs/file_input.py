import os
import pathlib
import boto3
from urllib.parse import urlparse
from shutil import copyfile
from flask import current_app


class FileInput(object):

    def __init__(self):
        self.local_dir = pathlib.Path("./tmp_files/")
        if not os.path.exists(self.local_dir):
            os.makedirs(self.local_dir)


    def read_local_file(self,local_path):

        current_app.logger.debug("Read Local File Path: " + local_path)
        input_folder = pathlib.Path("./input_files/")
        file_location = pathlib.Path(local_path)
        file_path = input_folder.joinpath(file_location)
        new_file_location = self.local_dir.joinpath(file_location)
        current_app.logger.debug("New File Path: " + str(new_file_location))
        copyfile(file_path, new_file_location)
        current_app.logger.debug("Local file copied")

        return new_file_location


    def read_s3_file(self,s3_path):
        region_name = os.environ['region_name']

        current_app.logger.debug("Read S3 File Path: " + s3_path)

        url = urlparse(s3_path)
        bucket_name = url.netloc
        key = url.path.strip("/")
        file_name = os.path.basename(key)

        new_file_location = self.local_dir.joinpath(file_name)
        current_app.logger.debug("New File Path: " + str(new_file_location))

        s3 = boto3.client('s3',region_name=region_name)

        s3.download_file(bucket_name, key, str(new_file_location))
        current_app.logger.debug("S3 file copied")
        return new_file_location


    def read_local_files(self,local_path):
        return None

    
    def read_s3_files(self,s3_prefix):
        return None


