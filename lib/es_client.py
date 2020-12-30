import asyncio
from datetime import datetime
from elasticsearch import AsyncElasticsearch
import yaml


class ESClient():
    def __init__(self, type: str, config: dict):
        self.es = AsyncElasticsearch(
            config["elasticsearch"]["host"],
            scheme=config["elasticsearch"]["scheme"],
            port=config["elasticsearch"]["port"]
        )
        self.indexes_settings=config["elasticsearch"]["indexes"]["settings"]
        self.type = type
        self.mapping_file = config["app"]["mapping_file"].format(type=type)

        now = datetime.now()
        self.index_name=f"{type}_{now:%Y%m%d_%H%M%S}"

    async def ping(self):
        # Check conf with ping
        result = await self.es.ping()
        if not result:
            print("ERROR: Elasticsearch is not reachable: ", self.es)
            quit()

    async def prepare_index(self):
        with open(self.mapping_file, "r") as yml_stream:
            mapping = yaml.safe_load(yml_stream)

        await self.es.indices.create(
            self.index_name,
            body={
                "settings": self.indexes_settings,
                "mappings": mapping
            }
        )
        print(f"Index {self.index_name} created")

        await self.es.indices.put_settings(
            index=self.index_name,
            body= {"index": {"refresh_interval": -1}}
        )

    def get_doc_single_bulk(self, doc: dict) -> dict:
        return {
            "_index": self.index_name,
            "_source": doc
        }

    async def refresh_index(self):
        return await self.es.indices.refresh(index=self.index_name)

    async def switch_alias(self):
        if await self.es.indices.exists_alias(self.type):
            await self.es.indices.delete_alias("_all", self.type)

        print(f"Setting alias {self.type} on index {self.index_name}")
        return await self.es.indices.put_alias(self.index_name, self.type)

    async def remove_index(self):
        print(f"Removing index {self.index_name}")
        return await self.es.indices.delete(index=self.index_name)

    async def close(self):
        await self.es.close()
