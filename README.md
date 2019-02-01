# ali
This is a python script to extract some data for Ali. You can use it like so:

```console
$ python extract.py "/path/to/root/of/files"
```

This will generate a file called output.csv with the metadata from the XML files it is able to find in the zips.

For example, with the directories I was able to see you might try `python extract.py "/Volume/Untitled"`

I haven't been able to figure out the connection between the XML files and the PDF files, if you know what it is I can have this script move the files around etc...
