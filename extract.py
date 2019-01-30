import os
import re
import xml.etree.ElementTree
import zipfile
import csv

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
  record = xml.etree.ElementTree.fromstring(xml_string)
  publication = record.find('Publication')
  contributor = record.find('Contributor')
  return {
    'record_id': record.find('RecordID').text,
    'record_title': record.find('RecordID').text,
    'publication_id': publication.find('PublicationID').text,
    'publication_title': publication.find('Title').text,
    'publication_qualifier': publication.find('Qualifier').text,
    'publisher': record.find('Publisher').text,
    'volume': record.find('Volume').text,
    'issue': record.find('Issue').text,
    'alpha_pub_date': record.find('AlphaPubDate').text,
    'numeric_pub_date': record.find('NumericPubDate').text,
    'source_type': record.find('SourceType').text,
    'object_type': record.find('ObjectType').text,
    'contributor_role': contributor.find('ContribRole').text,
    'contributor_last_name': contributor.find('LastName').text,
    'contributor_first_name': contributor.find('FirstName').text,
    'contributor_person_name': contributor.find('PersonName').text,
    'contributor_original_form': contributor.find('OriginalForm').text,
    'start_page': record.find('StartPage').text,
    'end_page': record.find('EndPage').text,
    'pagination': record.find('Pagination').text,
    'url_doc_view': record.find('URLDocView').text,
  }

def write_dict_array_to_csv(dict_array):
  with open('output.csv', 'wb') as output_file:
    dict_writer = csv.DictWriter(output_file, dict_array[0].keys())
    dict_writer.writeheader()
    dict_writer.writerows(dict_array)

zip_files = find_zip_files()
xml_strings = read_zip_file_xml(zip_files.pop(0))
row = dict_from_xml_string(xml_strings.pop(0))
write_dict_array_to_csv([row])






