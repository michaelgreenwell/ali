import os
import re
import xml.etree.ElementTree
import zipfile

ROOT = "/Users/michael/ali/data"

# This will look for zip files that contain XML
def find_zip_files():
  zip_files = []
  for path, _, files in os.walk(ROOT):
    for file in files:
      filepath = path + "/" + file
      if re.compile('(.*zip$)').match(filepath):
        print filepath
        zip_files.append(filepath)
  return zip_files


# This will open those zip files and pull out the XML
def read_zip_file_xml(filepath):
  xml_strings = []
  zfile = zipfile.ZipFile(filepath)
  for finfo in zfile.infolist():
    if re.compile('(.*xml$)').match(finfo.filename):
      ifile = zfile.open(finfo)
      content = ifile.read()
      xml_strings.append(content)
  return xml_strings

# This will read an XML file in with the expected format and create a Dictionary
def dict_from_xml_string(xml_string):
  rec = xml.etree.ElementTree.fromstring(xml_string)
  publication = rec.find('Publication')
  return {
    'record_id': rec.find('RecordID').text,
    'record_title': rec.find('RecordID').text,
    'publication_id': publication.find('PublicationID').text,
  }

zip_files = find_zip_files()
xml_strings = read_zip_file_xml(zip_files.pop(0))
row = dict_from_xml_string(xml_strings.pop(0))
print row





