import click
import os
import time
import io
from distutils import dir_util

import subprocess

from datetime import timedelta

from yaspin import yaspin

from zipfile import ZipFile

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
@click.option('--package', 'packageFile', help='Path to the "package.xml" file', default=f'{DEFAULT_SRC}/package.xml', type=click.Path(exists=True, file_okay=True, dir_okay=False))
@click.option('-s', '--sandbox', 'isSandbox', help='Set SFDC URL to sandbox', is_flag=True, default=False)
@click.option('-o', '--output', 'outputPath', help='Output directory', default=DEFAULT_SRC, type=click.Path(exists=True, file_okay=False, dir_okay=True))
def retrieve(username, password, packageFile, isSandbox, outputPath):
  """Retrieve metadatas specified inside the "package.xml" from Salesforce"""

  sfdcURL = sfdc_utils.sfdc_url(isSandbox)

  packageVersion, packageText = sfdc_utils.package_creator(packageFile)

  print('{:<30}{:<40}'.format(click.style('SFDC URL: ', fg='yellow'), click.style(sfdcURL, fg='green')))
  print('{:<30}{:<40}'.format(click.style('Username: ', fg='yellow'), click.style(username, fg='green')))
  print('{:<30}{:<40}'.format(click.style('Password: ', fg='yellow'), click.style(password, fg='green')))
  print('{:<30}{:<40}'.format(click.style('Package.xml file: ', fg='yellow'), click.style(packageFile, fg='green')))
  print('{:<30}{:<40}'.format(click.style('API Version: ', fg='yellow'), click.style(packageVersion, fg='green')))
  print('{:<30}{:<40}'.format(click.style('Output directory: ', fg='yellow'), click.style(outputPath, fg='green')))

  connection = Sfdc(username, password, sfdcURL, packageVersion)

  print(click.style('Connecting to SFDC...', fg='bright_black'))
  connection.login()
  print('{}{}'.format(click.style('Connected as: ', fg='yellow'), click.style(connection.username, fg='green')))
  
  print(click.style('Submit retrieve request...', fg='bright_black'))
  connection.retrieve(package=packageText)
  print('{}{}'.format(click.style('Async ID: ', fg='yellow'), click.style(connection.asyncProcessId, fg='green')))

  retrieving_start = time.time()

  with yaspin(text=click.style('Retrieving...', fg='bright_black'), color="green") as spinner:
    while not connection.isRetrievingMetadata():
      time.sleep(5)
    spinner.text = '{} {}'.format(click.style('Retrieve completed', fg='green'), click.style('[Elapsed time: {}]'.format(timedelta(seconds=int(time.time() - retrieving_start))), fg='bright_black'))
    spinner.ok("✅")

  archive = ZipFile(io.BytesIO(connection.getZipFile()), "r")

  for file in archive.namelist():
    archive.extract(file, path=outputPath)


@main.command(name='deploy')
@click.option('-u', '--username', 'username', required=True, help='Salesforce username')
@click.option('-p', '--password', 'password', required=True, help='Salesforce password')
@click.option('--package', 'packageFile', help='Path to the "package.xml" file', default=f'{DEFAULT_SRC}/package.xml', type=click.Path(exists=True, file_okay=True, dir_okay=False))
@click.option('-s', '--sandbox', 'isSandbox', help='Set SFDC URL to sandbox', is_flag=True, default=False)
@click.option('-t', '--testLevel', 'testLevel', help='Test level', default='NoTestRun', type=click.Choice(['RunAllTests', 'RunSpecifiedTests', 'RunLocalTests', 'NoTestRun']))
@click.option('-r', '--runTests', 'runTests', help='Test to be run if selected "RunSpecifiedTests"', default=[])
@click.option('-v', '--validate', 'validate', help='Perform only a validation', is_flag=True, default=False)
def deploy(username, password, packageFile, isSandbox, testLevel, runTests, validate):
  """Initiate a validation/deployment process on Salesforce"""
  sfdcURL = sfdc_utils.sfdc_url(isSandbox)

  packageVersion, _ = sfdc_utils.package_creator(packageFile)

  print('{:<30}{:<40}'.format(click.style('SFDC URL: ', fg='yellow'), click.style(sfdcURL, fg='green')))
  print('{:<30}{:<40}'.format(click.style('Username: ', fg='yellow'), click.style(username, fg='green')))
  print('{:<30}{:<40}'.format(click.style('Password: ', fg='yellow'), click.style(password, fg='green')))
  print('{:<30}{:<40}'.format(click.style('Package.xml file: ', fg='yellow'), click.style(packageFile, fg='green')))
  print('{:<30}{:<40}'.format(click.style('API Version: ', fg='yellow'), click.style(packageVersion, fg='green')))
  print('\n{:<30}{:<40}\n'.format(click.style('Validate or Deploy: ', fg='yellow'), click.style('Validate' if validate else 'Deploy', fg='green')))

  connection = Sfdc(username, password, sfdcURL, packageVersion)

  print(click.style('Connecting to SFDC...', fg='bright_black'))
  connection.login()
  print('{}{}'.format(click.style('Connected as: ', fg='yellow'), click.style(connection.username, fg='green')))

  zipFile = sfdc_utils.zipDirectory(packageFile.rpartition('/')[0])

  print(click.style('Submit {} request...'.format('deploy' if not validate else 'validation'), fg='bright_black'))
  connection.deploy(zipFile, testLevel=testLevel, runTests=runTests, validateOnly=validate)

  deploy_start = time.time()

  while not connection.isDeploying():
    time.sleep(5)


@main.command(name='retrieve-sfdx')
@click.option('-f', '--folder', 'folder', required=True, help='Where to unpack the retrieved metadatas', default=DEFAULT_SRC, type=click.Path(exists=True))
@click.option('-o', '--orgalias', 'orgAlias', required=True, help='The organization alias')
@click.option('-p', '--packageFile', 'packageFile', required=True, help='Path to package.xml file', default=DEFAULT_SRC, type=click.Path(exists=True))
def retrieveSFDX(folder, orgAlias, packageFile):
  """Using the standard SFDX Salesforce CLI, performs a retrieve operation"""
  click.echo('Retrieve SFDX')

  result = subprocess.run(['sfdx', 'force:mdapi:retrieve', '-r', folder, '-u', orgAlias, '-k', packageFile])

  archive = ZipFile(f'{folder}/unpackaged.zip', "r")

  for file in archive.namelist():
    archive.extract(file, path=folder)

  dir_util.copy_tree(f'{folder}/unpackaged/', folder)

  os.remove(f'{folder}/unpackaged.zip')
  dir_util.remove_tree(f'{folder}/unpackaged')
  
if __name__ == '__main__':
  main()