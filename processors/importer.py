from tqdm import tqdm
from elasticsearch.helpers import async_streaming_bulk

from clients import ESClient
from parsers import XMLParser


class ElementImporter():

    es_client: ESClient
    parser: XMLParser

    def __init__(self, parser: XMLParser, es_client: ESClient):
        self.es_client = es_client
        self.parser = parser
        self.tqdm = tqdm(unit=f" {self.parser.type}", mininterval=1)

    async def process(self, **kwargs):
        self.tqdm.total = kwargs.get("total")

        async for ok, result in async_streaming_bulk(
            self.es_client.es, self.get_next_doc()
        ):
            self.tqdm.update()
            action, result = result.popitem()
            if not ok:
                print("failed to %s document %s" % ())

    async def get_next_doc(self):
        # 1/ get the next XML element
        for event, element in self.parser.context:
            # 2/ get the XML element as a dict for indexing
            doc = self.parser.get_values_from_tree_element(element, self.parser.xpaths_config)
            # 3/ add bulk envelop around the dict
            yield self.es_client.get_doc_single_bulk(doc)
            element.clear()
