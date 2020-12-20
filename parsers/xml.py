from copy import deepcopy
from io import BufferedReader
from lxml import etree
from lxml.etree import Element, XPath

class XMLParser():
    tag: str
    type: str
    context: etree.iterparse

    def __init__(self, type: str, xpaths_config: dict, file_stream: BufferedReader):
        self.type = type
        self.tag = type[:-1]

        self.xpaths_config = xpaths_config
        self.xpaths_compiled = {}
        self.compiled_xpaths = self.compile_xpaths(xpaths_config)

        self.context = etree.iterparse(file_stream, events=('end',), tag=self.tag)

    def compile_xpaths(self, conf: dict) -> dict:
        compiled_conf = {}

        for key in conf:
            value = conf[key]

            if isinstance(value, str):
                compiled_conf[value] = XPath(value)
            elif isinstance(value, dict):
                compiled_conf.update(self.compile_xpaths(value))

        return compiled_conf

    def get_values_from_tree_element(self, tree_element, xpaths_config):
        fields_xpath = {}

        for field_name, xpath in self.xpaths_config.items():
            if isinstance(xpath, dict): # Sub-elements
                children = self.compiled_xpaths[xpath["xpath"]](tree_element)

                field_value = []
                for child in children:
                    new_xpath = deepcopy(xpath)
                    del new_xpath["xpath"]

                    field_value.append(self.get_values_from_tree_element(child, new_xpath))

                fields_xpath[field_name] = field_value
                continue

            field_value = self.compiled_xpaths[xpath](tree_element)
            fields_xpath[field_name] = field_value

        return fields_xpath
