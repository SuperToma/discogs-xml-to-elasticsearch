from tqdm import tqdm

from parsers import XMLParser


class ElementCounter():
    nb_processed: int
    type: str

    def __init__(self, parser: XMLParser):
        self.nb_processed = 0
        self.parser = parser
        self.tqdm = tqdm(
            unit=f" {self.parser.type}",
            mininterval=1
        )

    def process(self):
        for event, element in self.parser.context:
            self.nb_processed += 1
            self.tqdm.update()

    def get_nb_processed():
        return self.nb_processed
