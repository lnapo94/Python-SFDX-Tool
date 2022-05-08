import click
import os
import time
import io

from zipfile import ZipFile
import xml.etree.ElementTree as ET

from sfdc import Sfdc
from utils import sfdc_utils

DEFAULT_SRC = os.path.join(os.getcwd(), 'src')

@click.group()
def main():
  """Python SFDX Toolkit"""
  pass

@main.command(name='retrieve')
@click.option('-u', '--username', 'username', required=True, help='Salesforce username')
@click.option('-p', '--password', 'password', required=True, help='Salesforce password')
@click.option('--package', 'packagePath', help='Path to the "package.xml" file', default=DEFAULT_SRC, type=click.Path(exists=True))
@click.option('-s', '--sandbox', 'isSandbox', help='Set SFDC URL to sandbox', is_flag=True, default=False)
def retrieve(username, password, packagePath, isSandbox):
  """Start retrieving the package.xml from SFDC"""

  path = DEFAULT_SRC if not packagePath else packagePath
  sfdcURL = sfdc_utils.sfdc_url(isSandbox)

  packageTree = ET.parse(f'{path}/package.xml')
  packageRoot = packageTree.getroot()

  packageVersion = packageRoot.find('{http://soap.sforce.com/2006/04/metadata}version').text

  package_file = open('{}/package.xml'.format(path), 'r')
  package_text = package_file.read()
  package_file.close()

  package_text = package_text.replace('<?xml version="1.0" encoding="UTF-8"?>', '')
  package_text = package_text.replace('<Package xmlns="http://soap.sforce.com/2006/04/metadata">', '')
  package_text = package_text.replace('<version>{}</version>'.format(packageVersion), '')
  package_text = package_text.replace('</Package>', '')

  print('{:<30}{:<40}'.format(click.style('Package.xml path: ', fg='yellow'), click.style(path, fg='green')))
  print('{:<30}{:<40}'.format(click.style('SFDC URL: ', fg='yellow'), click.style(sfdcURL, fg='green')))
  print('{:<30}{:<40}'.format(click.style('API Version: ', fg='yellow'), click.style(packageVersion, fg='green')))
  print('{:<30}{:<40}'.format(click.style('Username: ', fg='yellow'), click.style(username, fg='green')))
  print('{:<30}{:<40}'.format(click.style('Password: ', fg='yellow'), click.style(password, fg='green')))
  print('\n')

  connection = Sfdc(username, password, sfdcURL, packageVersion)

  print(click.style('Connecting to SFDC...', fg='bright_black'))
  connection.login()
  print('{}{}'.format(click.style('Connected as: ', fg='yellow'), click.style(connection.username, fg='green')))
  
  print(click.style('Submit retrieve request...', fg='bright_black'))
  async_process_id, state = connection.retrieve(package=package_text)
  print('{}{}'.format(click.style('Async ID: ', fg='yellow'), click.style(async_process_id, fg='green')))

  retrieving_start = time.time()
  while not connection.isRetrievingMetadata(async_process_id):
    print(click.style('Retrieve in progress...', fg='bright_black'))
    time.sleep(5)

  print('{} {}'.format(click.style('Retrieve completed 😎', fg='green'), click.style('[Elapsed time: {}s]'.format(int(time.time() - retrieving_start)), fg='bright_black')))

  archive = ZipFile(io.BytesIO(connection.getZipFile()), "r")

  for file in archive.namelist():
    if 'package.xml' not in file:
      archive.extract(file, path=path)

if __name__ == '__main__':
  main()