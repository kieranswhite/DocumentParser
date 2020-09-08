import json

class BaseParser(object):


    document_path = ""
    config = {}
    doc = ""
    output_dict = {}


    def __init__(self,doc_config,document_path):
        self.config = doc_config
        self.document_path = document_path



class ParsingException(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return 'ParsingError, {0} '.format(self.message)
        else:
            return 'ParsingError has occured'


class ConfigException(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return 'ConfigError, {0} '.format(self.message)
        else:
            return 'ConfigError has occured'