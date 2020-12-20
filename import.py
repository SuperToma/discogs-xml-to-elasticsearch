import argparse
import gzip
import yaml
import asyncio

from clients import ESClient
from parsers import XMLParser
from processors import ElementCounter, ElementImporter


async def main():
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
    await es_client.ping()
    await es_client.prepare_index(args.type, mapping)

    parser = XMLParser(args.type, config["types"][args.type], file_stream)

    # 1/ Count nb elements in the XML file if no nb-objects given (can be long)
    nb_objects = args.nb_objects
    if not nb_objects:
        processor = ElementCounter(parser)
        processor.process()
        nb_objects = parser.get_nb_processed()

    # 2/ Import elements in ES
    processor = ElementImporter(parser, es_client)
    await processor.process(total=nb_objects)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
