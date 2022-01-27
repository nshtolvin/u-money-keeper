# region Import
from contextlib import closing
from libs import logger_lib
import json
# endregion


# Метод считывания параметров конфигурации из json-файла
def read_settings(conf_filename):
    try:
        with closing(open(conf_filename, "r")) as json_file:
            dict_settings = json.load(json_file)
        return dict_settings
    except Exception as err:
        logger_lib.error(conf_filename, err)


# Class for configuration,
# read configuration from json file
# and save configuration to json file
class Config:
    # default constructor
    def __init__(self, conf_filename):
        self.filename = conf_filename
        self.settings = {}
        self.read_settings()

    # read parameters from file
    def read_settings(self):
        try:
            with closing(open(self.filename, "r")) as json_file:
                self.settings = json.load(json_file)
        except Exception as err:
            logger_lib.error(self.filename, err)

    # write parameters to file
    def write_settings(self):
        try:
            with closing(open(self.filename, "w")) as json_file:
                json.dump(self.settings, json_file)
        except Exception as err:
            logger_lib.error(self.filename, err)
