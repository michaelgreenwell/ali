# ali
This is a python script to extract some data for Ali. You can use it like so:

```console
$ python extract.py "/path/to/root/of/files"
```

This will generate two files:
* `metadata.csv` with the metadata from the XML files it is able to find in the zips.
* `pdfs.csv` with a list of the files and their locations.

For example, with the directories I was able to see you might try `python extract.py "/Volume/Untitled"`
