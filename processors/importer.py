from copy import deepcopy
import json
from tqdm import tqdm
from lxml import etree
from lxml.etree import Element, XPath

from processors.processor import Processor

class ElementImporter(Processor):
    conf_fields_xpath: dict
    nb_processed: int
    type: str

    def __init__(self, type: str, conf_fields_xpath: dict, **kwargs):
        self.nb_processed = 0
        self.type = type
        self.conf_fields_xpath = conf_fields_xpath
        self.tqdm = tqdm(
            unit=f" {type}",
            mininterval=1,
            total=kwargs.get("total"),
        )

    def process(self, tree_element: Element):
        self.nb_processed += 1
        self.tqdm.update()
        #print("dump : ")
        #etree.dump(tree_element)
        #print(">>>")
        es_fields_values = self.get_fields_values(
            self,
            tree_element,
            self.conf_fields_xpath
        )
        #toto = json.dumps(es_fields_values, indent=4)
        #print(toto)
        #quit()

    def get_nb_processed(self):
        return self.nb_processed

    @staticmethod
    def get_fields_values(self, tree_element, conf_fields_xpath):
        fields_xpath = {}

        for field_name, xpath in conf_fields_xpath.items():
            if isinstance(xpath, dict):
                children = tree_element.xpath(xpath["xpath"])

                field_value = []
                for child in children:
                    new_xpath = deepcopy(xpath)
                    del new_xpath["xpath"]

                    field_value.append(self.get_fields_values(self, child, new_xpath))

                fields_xpath[field_name] = field_value
                continue

            field_value = tree_element.xpath(xpath)
            fields_xpath[field_name] = field_value
        return fields_xpath

