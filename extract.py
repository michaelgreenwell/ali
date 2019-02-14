import os
import re
import xml.etree.ElementTree
import zipfile
import csv
import sys
import copy
import codecs
import collections
import cStringIO

# This is the template for each row
ROW_TEMPLATE = collections.OrderedDict({
  'publication_id': None,
  'publication_title': None,
  'publication_qualifier': None,
  'contributor_role': None,
  'contributor_last_name': None,
  'contributor_first_name': None,
  'contributor_person_name': None,
  'contributor_original_form': None,
  'record_id': None,
  'record_title': None,
  'publisher': None,
  'volume': None,
  'issue': None,
  'alpha_pub_date': None,
  'numeric_pub_date': None,
  'source_type': None,
  'object_type': None,
  'start_page': None,
  'end_page': None,
  'pagination': None,
  'url_doc_view': None,
  'file_name': None,
  'zipfile_path': None,
  'zipped_pdf_path': None
})

# This will look for files paths under the provided root directory that match the provided regular expression recursively
def find_files_by_regex(root, regex):
  zip_files = []
  for path, _, files in os.walk(root):
    for file in files:
      filepath = path + "/" + file
      if re.compile(regex, re.IGNORECASE).match(filepath):
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
def dicts_from_xml_string(xml_string, pdf_paths):
  record = xml.etree.ElementTree.fromstring(xml_string)
  main_dict = copy.deepcopy(ROW_TEMPLATE)

  publication = record.find('Publication')
  if publication is not None:
    main_dict.update({
      'publication_id': text_or_none(publication.find('PublicationID')),
      'publication_title': text_or_none(publication.find('Title')),
      'publication_qualifier': text_or_none(publication.find('Qualifier')),
    })

  contributor = record.find('Contributor')
  if contributor is not None:
    main_dict.update({
      'contributor_role': text_or_none(contributor.find('ContribRole')),
      'contributor_last_name': text_or_none(contributor.find('LastName')),
      'contributor_first_name': text_or_none(contributor.find('FirstName')),
      'contributor_person_name': text_or_none(contributor.find('PersonName')),
      'contributor_original_form': text_or_none(contributor.find('OriginalForm')),
    })

  main_dict.update({
    'record_id': text_or_none(record.find('RecordID')),
    'record_title': text_or_none(record.find('RecordTitle')),
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
  })

  main_dict.update(
    {'file_name': '_'.join([main_dict['publication_id'], main_dict['numeric_pub_date'], main_dict['record_id']]) + '.pdf'}
  )

  pdf_path = {
    'zipfile_path': None,
    'zipped_pdf_path': None
  }
  pdf_path.update(pdf_paths.get('file_name', {}))
  main_dict.update(pdf_path)

  return [main_dict]

class UnicodeWriter:
  def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
    # Redirect output to a queue
    self.queue = cStringIO.StringIO()
    self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
    self.stream = f
    self.encoder = codecs.getincrementalencoder(encoding)()

  def writerow(self, row):
    self.writer.writerow([s.encode("utf-8") for s in row])
    # Fetch UTF-8 output from the queue ...
    data = self.queue.getvalue()
    data = data.decode("utf-8")
    # ... and reencode it into the target encoding
    data = self.encoder.encode(data)
    # write to the target stream
    self.stream.write(data)
    # empty queue
    self.queue.truncate(0)

ROOT = sys.argv[1]
PDF_ZIP_FILE_REGEX = '.*/(pdf)/(.*zip$)' # This regular expression identifies file paths for XML zips
XML_ZIP_FILE_REGEX = '.*/(xml)/(.*zip$)' # This regular expression identifies file paths for XML zips

pdf_zip_files = find_files_by_regex(ROOT, PDF_ZIP_FILE_REGEX)
pdf_paths = {}
for zip_file in pdf_zip_files:
  pdf_paths.update(read_pdf_zip_file(zip_file))

with codecs.open('pdfs.csv', 'w', 'utf-8') as fp:
  writer = csv.writer(fp)
  for key, value in pdf_paths.iteritems():
    writer.writerow([key] + value.values())

with codecs.open('metadata.csv', 'w', 'utf-8') as fp:
  writer = UnicodeWriter(fp)
  writer.writerow(ROW_TEMPLATE.keys())
  xml_zip_files = find_files_by_regex(ROOT, XML_ZIP_FILE_REGEX)
  for zip_file in xml_zip_files:
    xml_strings = read_xml_zip_file(zip_file)
    for xml_string in xml_strings:
      for row in dicts_from_xml_string(xml_string, pdf_paths):
        writer.writerow([(s or u'') for s in row.values()])
