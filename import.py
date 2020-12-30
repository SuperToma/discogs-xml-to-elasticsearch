from datetime import datetime
import argparse
import asyncio
import yaml

from lib import (
    Downloader, DownloadError,
    ESClient,
    XMLParser,
    ElementImporter
)


async def main():
    # Load config
    with open("./config/config.yml", 'r') as yml_stream:
        config = yaml.safe_load(yml_stream)

    valid_types = config["types"].keys()

    # Script arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--date", type=int, required=False)
    parser.add_argument(
        "-t", "--type", type=str, required=False, choices=valid_types
    )
    args = parser.parse_args()

    types = [args.type] if args.type else valid_types
    if args.date:
        date = str(args.date)
    else:
        date = datetime.today().strftime('%Y%m01')
        print(
        f"No date option specified (--date or -d), "
        f"using the first day of current month: {date}")

    download_dir = config['app']['download_dir']

    for type in types:
        # 1/ Create index
        global es_client # global for removing index if script crashes
        es_client = ESClient(type, config)
        await es_client.ping()
        await es_client.prepare_index()

        # 2/ Download file
        downloader = Downloader(type, date, config)
        downloader.start()

        # 3/ Import elements in ES
        parser = XMLParser(type, date, config)
        processor = ElementImporter(parser, es_client)
        await processor.process()

        # 4/ Last steps
        await es_client.refresh_index()
        await es_client.switch_alias()

    print("Import finished.")
    await es_client.close()

loop = asyncio.get_event_loop()

try:
    loop.run_until_complete(main())
except (DownloadError, KeyboardInterrupt) as e:
    print(str(e))
    loop.run_until_complete(es_client.remove_index())
except Exception as e:
    print("Exception catched, removing not completed index.")
    loop.run_until_complete(es_client.remove_index())
    raise e
finally:
    loop.run_until_complete(es_client.close())
    loop.close()
