from datetime import datetime
from elasticsearch import Elasticsearch


class ESClient():
    es: Elasticsearch
    indexes_settings: dict
    index_date: str
    type: str

    def __init__(self, config: dict):
        self.es = Elasticsearch(
            config["host"],
            scheme=config["scheme"],
            port=config["port"]
        )
        self.indexes_settings=config["indexes"]["settings"]
        self.index_date=datetime.now().strftime("%Y%m%d_%H%M%S")

        # Check conf with ping
        result = self.es.ping()
        if not result:
            print("ERROR: Elasticsearch is not reachable: ", self.es)
            quit()

    def prepare_index(self, type: str, mapping: dict):
        self.type=type
        self.es.indices.create(
            f"{self.type}_{self.index_date}",
            body={
                "settings": self.indexes_settings,
                "mappings": mapping
            }
        )
