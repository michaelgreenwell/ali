import os
import re
import xml.etree.ElementTree
import zipfile
import csv
import sys
import copy

# This will look for files paths under the provided root directory that match the provided regular expression recursively
def find_files_by_regex(root, regex):
  zip_files = []
  for path, _, files in os.walk(root):
    for file in files:
      filepath = path + "/" + file
      if re.compile(regex).match(filepath):
        print filepath
        zip_files.append(filepath)
  return zip_files

# This will open those zip files and pull out the XML
def read_xml_zip_file(filepath):
  xml_strings = []
  zfile = zipfile.ZipFile(filepath)
  for finfo in zfile.infolist():
    if re.compile('(.*xml$)').match(finfo.filename):
      ifile = zfile.open(finfo)
      content = ifile.read()
      xml_strings.append(content)
  return xml_strings

# This will open zip files and create a dict of where PDF files are located
def read_pdf_zip_file(filepath):
  pdf_paths = {}
  zfile = zipfile.ZipFile(filepath)
  for finfo in zfile.infolist():
    if re.compile('(.*pdf$)').match(finfo.filename):
      pdf_paths[os.path.basename(finfo.filename)] = {
        'zipfile_path': filepath,
        'zipped_pdf_path': finfo.filename
      }
  return pdf_paths

# This is used to wrap fields that may not appear in the XML
def text_or_none(find_result):
  return None if find_result is None else find_result.text

# This will read an XML file in with the expected format and create a Dictionary
def dict_from_xml_string(xml_string, pdf_paths):
  record = xml.etree.ElementTree.fromstring(xml_string)

  publication = record.find('Publication')
  publication_dict = {}
  if publication is not None:
    publication_dict = {
      'publication_id': text_or_none(publication.find('PublicationID')),
      'publication_title': text_or_none(publication.find('Title')),
      'publication_qualifier': text_or_none(publication.find('Qualifier')),
    }

  contributor = record.find('Contributor')
  contributor_dict = {}
  if contributor is not None:
    contributor_dict = {
      'contributor_role': text_or_none(contributor.find('ContribRole')),
      'contributor_last_name': text_or_none(contributor.find('LastName')),
      'contributor_first_name': text_or_none(contributor.find('FirstName')),
      'contributor_person_name': text_or_none(contributor.find('PersonName')),
      'contributor_original_form': text_or_none(contributor.find('OriginalForm')),
    }

  main_dict = {
    'record_id': text_or_none(record.find('RecordID')),
    'record_title': text_or_none(record.find('RecordID')),
    'publisher': text_or_none(record.find('Publisher')),
    'volume': text_or_none(record.find('Volume')),
    'issue': text_or_none(record.find('Issue')),
    'alpha_pub_date': text_or_none(record.find('AlphaPubDate')),
    'numeric_pub_date': text_or_none(record.find('NumericPubDate')),
    'source_type': text_or_none(record.find('SourceType')),
    'object_type': text_or_none(record.find('ObjectType')),
    'start_page': text_or_none(record.find('StartPage')),
    'end_page': text_or_none(record.find('EndPage')),
    'pagination': text_or_none(record.find('Pagination')),
    'url_doc_view': text_or_none(record.find('URLDocView')),
  }

  main_dict.update(publication_dict)
  main_dict.update(contributor_dict)



  def merge_product_id(product_element):
    md = copy.deepcopy(main_dict)
    md.update({'product_id': text_or_none(product_element.find('ProductID'))})
    md.update({'file_name': '_'.join([md['publication_id'], md['numeric_pub_date'], md['product_id']]) + '.pdf'})
    return md

  # This will pull all of the ProductIDs and write them into a copy of the row
  product_elements = record.find('Products').findall('Product')
  products = map(merge_product_id, product_elements)

  for product in products:
    pdf_path = pdf_paths.get('file_name', None)
    if pdf_path is not None:
      product.update(pdf_path)
    else:
      product.update({
        'zipfile_path': None,
        'zipped_pdf_path': None
      })
  return products

def write_dict_array_to_csv(dict_array):
  with open('output.csv', 'wb') as output_file:
    dict_writer = csv.DictWriter(output_file, dict_array[0].keys())
    dict_writer.writeheader()
    dict_writer.writerows(dict_array)


root = sys.argv[1]
PDF_ZIP_FILE_REGEX = '.*/(PDF)/(.*zip$)' # This regular expression identifies file paths for XML zips
XML_ZIP_FILE_REGEX = '.*/(xml|XML)/(.*zip$)' # This regular expression identifies file paths for XML zips

pdf_zip_files = find_files_by_regex(root, PDF_ZIP_FILE_REGEX)
pdf_paths = {}
for zip_file in pdf_zip_files:
  pdf_paths.update(read_pdf_zip_file(zip_file))

xml_zip_files = find_files_by_regex(root, XML_ZIP_FILE_REGEX)
xml_strings = []
for zip_file in xml_zip_files:
  xml_strings = xml_strings + read_xml_zip_file(zip_file)

rows = []
for xml_string in xml_strings:
  dicts = dict_from_xml_string(xml_string, pdf_paths)
  rows = rows + dicts

write_dict_array_to_csv(rows)






