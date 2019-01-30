import os
import re
import xml.etree.ElementTree
import zipfile

root = "/Users/michael/ali/data"
regex = re.compile('(.*xml$)')

xml_files = []
for path, _, files in os.walk(root):
  for file in files:
    if regex.match(file):
       xml_files.append(path + "/" + file)

file = xml_files.pop(0)
rec = xml.etree.ElementTree.parse(file).getroot()

publication = rec.find('Publication')
row = {
    'record_id': rec.find('RecordID').text,
    'record_title': rec.find('RecordID').text,
    'publication_id': publication.find('PublicationID').text,
}

print row






