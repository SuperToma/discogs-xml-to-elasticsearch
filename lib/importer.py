from tqdm import tqdm
from elasticsearch.helpers import async_streaming_bulk

from .es_client import ESClient
from .xml_parser import XMLParser


class ElementImporter():

    es_client: ESClient
    parser: XMLParser

    def __init__(self, parser: XMLParser, es_client: ESClient):
        self.es_client = es_client
        self.parser = parser
        self.tqdm = tqdm(
            total=self.parser.file_size,
            unit='B',
            unit_scale=True,
            mininterval=1,
            position=0
        )
        self.tqdm_etree = tqdm(
            unit=f" {self.parser.type}",
            mininterval=1,
            position=1
        )

    async def process(self, **kwargs):
        async for ok, result in async_streaming_bulk(
            self.es_client.es, self.get_next_doc()
        ):
            self.tqdm.update(self.parser.file_stream.fileobj.tell() - self.tqdm.n)
            self.tqdm_etree.update()
            action, result = result.popitem()
            if not ok:
                print("failed to %s document %s" % ())

    async def get_next_doc(self):
        start_tag = None

        # 1/ get the next XML element
        for event, element in self.parser.context:
            if event == 'start' and start_tag is None:
                start_tag = element.tag
            if event == 'end' and element.tag == start_tag:
                # 2/ get the XML element as a dict for indexing
                doc = self.parser.get_values_from_tree_element(element)
                element.clear()
                while element.getprevious() is not None:
                    del element.getparent()[0]
                # 3/ add bulk envelop around the dict
                yield self.es_client.get_doc_single_bulk(doc)
                start_tag = None
