from bs4 import BeautifulSoup
import zipfile
from io import BytesIO
import os

from base64 import b64encode


def sfdc_url(sandbox=False):
  if sandbox:
    return 'https://test.salesforce.com'
  else:
    return 'https://login.salesforce.com'

def package_creator(path):

  packageFile = open(path, 'r')
  contents = packageFile.read()
  soup = BeautifulSoup(contents, 'xml')

  packageVersion = soup.find('version').text
  types = soup.Package.find_all('types')

  packageText = ''

  for metadata in types:
    packageText += str(metadata)

  return packageVersion, packageText

def zipDirectory(path):
  mem_zip = BytesIO()

  zf = zipfile.ZipFile(mem_zip, "w")

  for dirname, subdirs, files in os.walk(path):
    zf.write(dirname)
    for filename in files:
      zipPath = os.path.join(dirname, filename)
      zf.write(zipPath, zipPath.replace(path, ''))

  return b64encode(mem_zip.getvalue()).decode()
