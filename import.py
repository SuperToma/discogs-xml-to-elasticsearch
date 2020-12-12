import argparse
import gzip
import yaml

from clients import ESClient
from parsers import XMLParser
from processors import ElementCounter, ElementImporter


if __name__ == "__main__":
    # Load config
    with open("./config/config.yml", 'r') as yml_stream:
        config = yaml.safe_load(yml_stream)

    # Script arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--date", type=int, required=True)
    parser.add_argument("-n", "--nb-objects", type=int, required=False)
    parser.add_argument(
        "-t", "--type",
        type=str,
        required=True,
        choices=config["types"].keys()
    )
    args = parser.parse_args()

    file_stream = gzip.open(
        f"{config['app']['download_dir']}discogs_{args.date}_{args.type}.xml.gz"
    )

    with open(f"./config/mapping.{args.type}.yml", 'r') as yml_stream:
        mapping = yaml.safe_load(yml_stream)

    es_client = ESClient(config["elasticsearch"])
    es_client.prepare_index(args.type, mapping)

    # 1/ Count nb elements in the XML file if no nb-objects given (can be long)
    nb_objects = args.nb_objects
    if not nb_objects:
        processor = ElementCounter(args.type)
        parser = XMLParser(type=args.type)
        parser.parse(file_stream, processor)
        nb_objects = parser.get_nb_processed()

    # 2/ Import elements in ES
    processor = ElementImporter(
        args.type,
        config["types"][args.type],
        total=nb_objects
    )
    parser = XMLParser(args.type)
    parser.parse(file_stream, processor)
