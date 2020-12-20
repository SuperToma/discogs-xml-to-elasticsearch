# discogs-xml-to-elasticsearch

### Rewrite in Python3.6+ of the NodeJS discogs importer
More than 2 times faster with Python.

Many problems with NodeJS:
 - slower: can't unserialize only some specific XML fields
 - more stable: NodeJS core crashes
 - simpler importer & more readable in Python

```
pip3 install -r requirements.txt
python3.7 import.py -d 20201101 -t releases
````

The number of XML elements can be long,
you can specify the number to parser to avoir calculation:
```
python3.7 import.py -d 20201101 -t releases -n 13203624
```
