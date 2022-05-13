import click
import os
import time
import io
import sys
from distutils import dir_util

import subprocess

from datetime import timedelta

from yaspin import yaspin

from zipfile import ZipFile

from .sfdc import Sfdc

from .engine.plugin_engine import PluginEngine
from .utils import sfdc_utils

DEFAULT_SRC = os.path.join(os.getcwd(), 'src')
PWD = os.getcwd()

@click.group()
def main():
  """PYDX: A revisited Salesforce SFDX CLI Toolkit"""
  pass

@main.command(name='retrieve')
@click.option('-u', '--username', 'username', required=True, help='Salesforce username')
@click.option('-p', '--password', 'password', required=True, help='Salesforce password')
@click.option('--package', 'packageFile', help='Path to the "package.xml" file', default=f'{DEFAULT_SRC}/package.xml', type=click.Path(exists=True, file_okay=True, dir_okay=False))
@click.option('-s', '--sandbox', 'isSandbox', help='Set SFDC URL to sandbox', is_flag=True, default=False)
@click.option('-o', '--output', 'outputPath', help='Output directory', default=DEFAULT_SRC, type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option('-se', '--settingFile', 'settingFile', help='Setting file', default=f'{PWD}/pydx.json', type=click.Path(exists=True, file_okay=True, dir_okay=False))
def retrieve(username, password, packageFile, isSandbox, outputPath, settingFile):
  """Retrieve metadatas specified inside the "package.xml" from Salesforce"""

  sfdcURL = sfdc_utils.sfdc_url(isSandbox)

  packageVersion, packageText = sfdc_utils.package_creator(packageFile)

  print('{:<30}{:<40}'.format(click.style('SFDC URL: ', fg='yellow'), click.style(sfdcURL, fg='green')))
  print('{:<30}{:<40}'.format(click.style('Username: ', fg='yellow'), click.style(username, fg='green')))
  print('{:<30}{:<40}'.format(click.style('Password: ', fg='yellow'), click.style(password, fg='green')))
  print('{:<30}{:<40}'.format(click.style('Package.xml file: ', fg='yellow'), click.style(packageFile, fg='green')))
  print('{:<30}{:<40}'.format(click.style('API Version: ', fg='yellow'), click.style(packageVersion, fg='green')))
  print('{:<30}{:<40}'.format(click.style('Output directory: ', fg='yellow'), click.style(outputPath, fg='green')))
  print('{:<30}{:<40}'.format(click.style('Setting File: ', fg='yellow'), click.style(settingFile, fg='green')))

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

  pe = PluginEngine(settingFile=settingFile, outputFolder=outputPath)

  pe.postRetrieve()


@main.command(name='deploy')
@click.option('-u', '--username', 'username', required=True, help='Salesforce username')
@click.option('-p', '--password', 'password', required=True, help='Salesforce password')
@click.option('--package', 'packageFile', help='Path to the "package.xml" file', default=f'{DEFAULT_SRC}/package.xml', type=click.Path(exists=True, file_okay=True, dir_okay=False))
@click.option('-s', '--sandbox', 'isSandbox', help='Set SFDC URL to sandbox', is_flag=True, default=False)
@click.option('-t', '--testLevel', 'testLevel', help='Test level', default='NoTestRun', type=click.Choice(['RunAllTests', 'RunSpecifiedTests', 'RunLocalTests', 'NoTestRun']))
@click.option('-r', '--runTests', 'runTests', help='Test to be run if selected "RunSpecifiedTests"', default=[])
@click.option('-v', '--validate', 'validate', help='Perform only a validation', is_flag=True, default=False)
@click.option('-se', '--settingFile', 'settingFile', help='Setting file', default=f'{PWD}/pydx.json', type=click.Path(exists=True, file_okay=True, dir_okay=False))
def deploy(username, password, packageFile, isSandbox, testLevel, runTests, validate, settingFile):
  """Initiate a validation/deployment process on Salesforce"""
  sfdcURL = sfdc_utils.sfdc_url(isSandbox)

  packageVersion, _ = sfdc_utils.package_creator(packageFile)

  print('{:<30}{:<40}'.format(click.style('SFDC URL: ', fg='yellow'), click.style(sfdcURL, fg='green')))
  print('{:<30}{:<40}'.format(click.style('Username: ', fg='yellow'), click.style(username, fg='green')))
  print('{:<30}{:<40}'.format(click.style('Password: ', fg='yellow'), click.style(password, fg='green')))
  print('{:<30}{:<40}'.format(click.style('Package.xml file: ', fg='yellow'), click.style(packageFile, fg='green')))
  print('{:<30}{:<40}'.format(click.style('API Version: ', fg='yellow'), click.style(packageVersion, fg='green')))
  print('\n{:<30}{:<40}\n'.format(click.style('Validate or Deploy: ', fg='yellow'), click.style('Validate' if validate else 'Deploy', fg='green')))

  pe = PluginEngine(settingFile=settingFile, outputFolder=packageFile.rpartition('/')[0])

  pe.preDeploy()

  if not isSandbox and testLevel == 'NoTestRun':
    print(click.style("Since you're {} in PROD, tests must be run\n".format('deploying' if not validate else 'validating'), fg='yellow'))
    testLevel = 'RunLocalTests'

  connection = Sfdc(username, password, sfdcURL, packageVersion)

  print(click.style('Connecting to SFDC...', fg='bright_black'))
  connection.login()
  print('{}{}'.format(click.style('Connected as: ', fg='yellow'), click.style(connection.username, fg='green')))

  zipFile = sfdc_utils.zipDirectory(packageFile.rpartition('/')[0])

  print(click.style('Submitting {} request...'.format('deploy' if not validate else 'validation'), fg='bright_black'))
  connection.deploy(zipFile, testLevel=testLevel, runTests=runTests, validateOnly=validate)
  print('{}{}'.format(click.style('Async ID: ', fg='yellow'), click.style(connection.asyncProcessId, fg='green')))

  spinner = yaspin(text=click.style('Waiting for {} to start...'.format('deployment' if not validate else 'validation'), fg='bright_black'), color="green")
  spinner.start()
  deploy_start = time.time()

  deployFinished, deployResult = connection.isDeploying()

  while not deployFinished:
    if deployResult['numberComponentsTotal'] + deployResult['numberTestsTotal'] > 0:
      spinner.stop()
      progress(deployResult['componentsDone'] + deployResult['testsDone'], deployResult['numberComponentsTotal'] + deployResult['numberTestsTotal'], suffix='[{}/{}]'.format(deployResult['componentsDone'] + deployResult['testsDone'], deployResult['numberComponentsTotal'] + deployResult['numberTestsTotal']))
    time.sleep(1)
    deployFinished, deployResult = connection.isDeploying()

  if deployResult['status'] == 'Failed':
    spinner.text = '{} {}'.format(click.style('{} Failed'.format('Deployment' if not validate else 'Validation'), fg='red'), click.style('[Elapsed time: {}]'.format(timedelta(seconds=int(time.time() - deploy_start))), fg='bright_black'))
    spinner.fail("❌")
    click.echo(click.style('Broken components: {}, Broken tests: {}'.format(deployResult['numberComponentErrors'], deployResult['numberTestErrors']), fg='red'))
  elif deployResult['status'] == 'Canceled':
    spinner.text = '{} {}'.format(click.style('{} Canceled'.format('Deployment' if not validate else 'Validation'), fg='bright_black'), click.style('[Elapsed time: {}]'.format(timedelta(seconds=int(time.time() - deploy_start))), fg='bright_black'))
    spinner.fail("🚫")
  else:
    spinner.text = '{} {}'.format(click.style('{} Completed'.format('Deployment' if not validate else 'Validation'), fg='green'), click.style('[Elapsed time: {}]'.format(timedelta(seconds=int(time.time() - deploy_start))), fg='bright_black'))
    spinner.ok("✅")

def progress(count, total, bar_len=60, suffix=''):
  filled_len = int(round(bar_len * count / float(total)))

  percents = round(100.0 * count / float(total), 1)
  bar = '=' * filled_len + '-' * (bar_len - filled_len)

  sys.stdout.write(click.style('[%s] %s%s %s\r' % (bar, percents, '%', suffix), fg='yellow'))
  sys.stdout.flush()


@main.command(name='retrieve-sfdx')
@click.option('-f', '--folder', 'folder', required=True, help='Where to unpack the retrieved metadatas', default=DEFAULT_SRC, type=click.Path(exists=True))
@click.option('-o', '--orgalias', 'orgAlias', required=True, help='The organization alias')
@click.option('-p', '--packageFile', 'packageFile', required=True, help='Path to package.xml file', default=f'{DEFAULT_SRC}/package.xml', type=click.Path(exists=True, file_okay=True, dir_okay=False))
@click.option('-se', '--settingFile', 'settingFile', help='Setting file', default=f'{PWD}/pydx.json', type=click.Path(exists=True, file_okay=True, dir_okay=False))
def retrieveSFDX(folder, orgAlias, packageFile, settingFile):
  """Using the standard SFDX Salesforce CLI, performs a retrieve operation"""
  click.echo('Retrieve SFDX')

  result = subprocess.run(['sfdx', 'force:mdapi:retrieve', '-r', folder, '-u', orgAlias, '-k', packageFile])

  archive = ZipFile(f'{folder}/unpackaged.zip', "r")

  for file in archive.namelist():
    archive.extract(file, path=folder)

  dir_util.copy_tree(f'{folder}/unpackaged/', folder)

  os.remove(f'{folder}/unpackaged.zip')
  dir_util.remove_tree(f'{folder}/unpackaged')

  pe = PluginEngine(settingFile=settingFile, outputFolder=folder)

  pe.postRetrieve()

@main.command(name='deploy-sfdx')
@click.option('-f', '--folder', 'folder', required=True, help='Where metadata and package.xml are', default=DEFAULT_SRC, type=click.Path(exists=True))
@click.option('-o', '--orgalias', 'orgAlias', required=True, help='The organization alias')
@click.option('-v', '--validate', 'validate', help='Perform only a validation', is_flag=True, default=False)
@click.option('-l', '--runLocalTests', 'runLocalTests', help='Run also Local Tests for this deploy', is_flag=True, default=False)
@click.option('-se', '--settingFile', 'settingFile', help='Setting file', default=f'{PWD}/pydx.json', type=click.Path(exists=True, file_okay=True, dir_okay=False))
def deploySFDX(folder, orgAlias, validate, runLocalTests, settingFile):
  """Using the standard SFDX Salesforce CLI, performs a deploy operation"""
  click.echo('Deploy SFDX')

  command = ['sfdx', 'force:mdapi:deploy', '-d', folder, '-u', orgAlias, '-w', '10']

  if validate:
    command.append('-c')

  if runLocalTests:
    command.append('-l')

  pe = PluginEngine(settingFile=settingFile, outputFolder=folder)

  pe.preDeploy()

  result = subprocess.run(command)
  
if __name__ == '__main__':
  main()