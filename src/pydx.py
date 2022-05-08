import click
import os

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

  print('{:<30}{:<40}'.format(click.style('Package.xml path: ', fg='yellow'), click.style(path, fg='green')))
  print('{:<30}{:<40}'.format(click.style('SFDC URL: ', fg='yellow'), click.style(sfdcURL, fg='green')))
  print('{:<30}{:<40}'.format(click.style('Username: ', fg='yellow'), click.style(username, fg='green')))
  print('{:<30}{:<40}'.format(click.style('Password: ', fg='yellow'), click.style(password, fg='green')))
  print('\n')


  connection = Sfdc(username, password, sfdcURL)

  print(click.style('Connecting to SFDC...', fg='yellow'))
  connection.login()
  print('{}{}'.format(click.style('Connected as: ', fg='yellow'), click.style(connection.username, fg='green')))

  print(click.style('Submit retrieve request...', fg='yellow'))
  async_process_id, state = connection.retrieve()
  print('{}{}'.format(click.style('Async ID: ', fg='yellow'), click.style(async_process_id, fg='green')))

if __name__ == '__main__':
  main()