from tqdm import tqdm

from processors.processor import Processor

class ElementCounter(Processor):
    nb_processed: int
    type: str

    def __init__(self, type: str):
        self.nb_processed = 0
        self.type = type
        self.tqdm = tqdm(
            unit=f" {type}",
            mininterval=1
        )

    def process(self, item: dict):
        self.nb_processed += 1
        self.tqdm.update()

    def get_nb_processed():
        return self.nb_processed
