import asyncio
from datetime import datetime

from elasticsearch import AsyncElasticsearch


class ESClient():
    es: AsyncElasticsearch
    indexes_settings: dict
    index_name: str
    type: str

    def __init__(self, config: dict):
        self.es = AsyncElasticsearch(
            config["host"],
            scheme=config["scheme"],
            port=config["port"]
        )
        self.indexes_settings=config["indexes"]["settings"]

    async def ping(self):
        # Check conf with ping
        result = await self.es.ping()
        if not result:
            print("ERROR: Elasticsearch is not reachable: ", self.es)
            quit()

    async def prepare_index(self, type: str, mapping: dict):
        now = datetime.now()
        self.type=type
        self.index_name=f"{type}_{now:%Y%m%d_%H%M%S}"

        await self.es.indices.create(
            self.index_name,
            body={
                "settings": self.indexes_settings,
                "mappings": mapping
            }
        )

    def get_doc_single_bulk(self, doc: dict) -> dict:
        return {
            '_index': self.index_name,
            '_source': doc
        }
