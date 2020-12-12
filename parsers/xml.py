from lxml import etree
from processors import Processor

class XMLParser():
    type: str
    element_name: str

    def __init__(self, type: str):
        self.type = type
        self.element_name = type[:-1]

    def parse(self, file_stream, processor):
        context = etree.iterparse(file_stream, events=('end',), tag=self.element_name)

        for event, element in context:
            # etree.dump(element)
            processor.process(element)
            element.clear()
