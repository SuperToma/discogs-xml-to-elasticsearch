# discogs-xml-to-elasticsearch
## A discogs XMLs importer into Elasticsearch

Written in Python 3.6+
```sh
pip3 install -r requirements.txt
python3 import.py
````

The process will:
1. Download the file of the current month discogs_YYYYMM01.xml.gz on Discogs [https://data.discogs.com](https://data.discogs.com/?prefix=data/2020/)
2. Check the file with the related checksum
3. Create an Elasticsearch index _type__YYYYMMDD_HHMMSS
4. Import the XML data in the created index
5. Create/switch the alias _type_ on the new index

No need to extract the .gz file
With progress bar & ETA

### Parameters

- `--type / -t`: will import only the specified type.
Valid values: (artists|masters|releases)

- `--date / -d`: will import the specified date (writen in [Discogs's XML file](https://data.discogs.com/?prefix=data/2020/))
Format: YYYYMMDD

### Performance infos

On a home basic configuration with a mini-pc:
 - Intel 4415U 2.30GHz / 8Gb ram / hdd mSATA
 - Elasticsearch running on same PC, Apache, ...

 (with the fields selected in config.yml)

| Type | Nb imported | Duration | Average |
| --- | --- | --- | --- |
| artists | 7 259 634 | 18:13 | 6641/s |
| masters | 1 796 961 | 09:55 | 3020/s |
| release | n/a | n/a | n/a |

Memory consuming: between 35MB & 55MB

### Performance tuning

The XML unserialization is the most time consuming.

In the configuration file, comment the fields that
you don't need to import:
[config/config.yml](config/config.yml)

### Versions

This is a complete re-write of my NodeJS discogs importer

Many disadvantages with NodeJS:
 - slower: more than 2 times faster in Python even reading the gzip file without extract
 - slow unserialization: NodeJS unserialize all the XML element, can't unserialize only some specific XML fields
 - more stable: NodeJS core crashes
 - simpler, more readable, less lines, no callbacks hell & pyramid of Doom

### Todo
 - Labels import is not implemented
