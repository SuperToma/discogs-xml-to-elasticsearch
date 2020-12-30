from datetime import datetime
import hashlib
import os.path
import requests
from tqdm import tqdm

class Downloader():

    def __init__(self, type: str, date: int, config: dict):
        self.type = type
        self.date = date
        self.file_path = config["app"]["file_path"].format(year=self.date[0:4])
        self.file_name = config["app"]["file_name"]
        self.download_dir = config["app"]["download_dir"]
        self.checksums = self.get_checksums()

    def start(self):
        file_name = self.file_name.format(
            date=self.date,
            type=self.type,
            extension="xml.gz"
        )

        if os.path.isfile(f"{self.download_dir}{file_name}"):
            print(f"File {file_name} already downloaded")
        else:
            self.download_file(file_name)

        self.check_file(file_name)

    def get_checksums(self):
        file_name = self.file_name.format(
            date=self.date, type="CHECKSUM", extension="txt"
        )
        response = requests.get(f"{self.file_path}{file_name}")
        open(f"{self.download_dir}{file_name}", "wb").write(response.content)

        file = open(f"{self.download_dir}{file_name}", "r")

        checksums_infos = {}
        for line in file.readlines():
            hash, filename = line.split(" ", 1)
            checksums_infos[filename.strip()] = hash

        return checksums_infos

    def download_file(self, file_name: str):
        print(f"Downloading file {self.file_path}{file_name}")
        response = requests.get(f"{self.file_path}{file_name}", stream=True)

        if response.status_code is not 200:
            response.close()
            raise DownloadError(
                f"File {self.file_path}{file_name} does not exists.\n"
                f"Please specify a correct date with --date or -d option"
            )

        total_size= int(response.headers.get('content-length', 0))
        progress_bar = tqdm(
            total=total_size, unit='iB', unit_scale=True, mininterval=1
        )

        with open(f"{self.download_dir}{file_name}", "wb") as file:
            for data in response.iter_content(1024):
                progress_bar.update(len(data))
                file.write(data)
        progress_bar.close()

    def check_file(self, file_name: str):
        sha256_hash = hashlib.sha256()
        with tqdm(
            total=os.path.getsize(f"{self.download_dir}{file_name}"),
            unit='B',
            unit_scale=True,
            desc=f"Checking file {file_name}",
        ) as t:
            with open(f"{self.download_dir}{file_name}", "rb") as f:
                for chunk in iter(lambda: f.read(4096),b""):
                    sha256_hash.update(chunk)
                    t.update(len(chunk))

        if sha256_hash.hexdigest() == self.checksums[file_name]:
            print("Checksum OK")
        else:
            print(f"Wrong checksum for file {file_name}")
            print(f"Discogs checksum: \n{self.checksums[file_name]}")
            print(f"Downloaded file checksum: \n{sha256_hash.hexdigest()}")
            exit(1)


class DownloadError(Exception):
    def __init__(self, message):
        self.message = message
