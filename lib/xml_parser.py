from copy import deepcopy
import gzip
import io
from lxml import etree
from lxml.etree import Element, XPath
import os.path
import struct


class XMLParser():
    tag: str
    type: str
    context: etree.iterparse

    def __init__(self, type: str, date: str, config: dict):
        self.type = type
        self.tag = type[:-1]

        self.xpaths_config = config["types"][type]
        self.compiled_xpaths = self.compile_xpaths(self.xpaths_config)

        filename = config["app"]["file_name"].format(
            date=date, type=type, extension="xml.gz"
        )
        file_path = f"{config['app']['download_dir']}{filename}"
        self.file_size = os.path.getsize(file_path)

        self.file_stream = gzip.open(file_path)
        self.context = etree.iterparse(self.file_stream, events=("start", "end"), tag=self.tag)

    def compile_xpaths(self, conf: dict) -> dict:
        compiled_conf = {}

        for key in conf:
            value = conf[key]

            if isinstance(value, str):
                compiled_conf[value] = XPath(value)
            elif isinstance(value, dict):
                compiled_conf.update(self.compile_xpaths(value))

        return compiled_conf

    def get_values_from_tree_element(self, tree_element, xpaths_config=None):
        if xpaths_config is None:
            xpaths_config = self.xpaths_config

        fields_xpath = {}

        for field_name, xpath in xpaths_config.items():
            if isinstance(xpath, dict): # Sub-elements
                children = self.compiled_xpaths[xpath["xpath"]](tree_element)
                field_value = []
                for child in children:
                    new_xpath = deepcopy(xpath)
                    del new_xpath["xpath"]
                    field_value.append(self.get_values_from_tree_element(child, new_xpath))

                fields_xpath[field_name] = field_value
            else:
                field_value = self.compiled_xpaths[xpath](tree_element)

            fields_xpath[field_name] = field_value

        return fields_xpath
