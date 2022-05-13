import xmltodict
import shutil
import glob
import os
import click
class Helper:

  def __init__(self, outputDir):
    self.outputDir = outputDir

  def removeFolders(self, path):
    srcPath = f'{self.outputDir}/{path}'
    try:
      shutil.rmtree(srcPath)
    except:
      print(click.style(f"Error while deleting folder : {srcPath}", fg='red'))

  def filterMetadata(self, path):
    srcPath = f'{self.outputDir}/{path}'
    for filePath in glob.glob(srcPath):
      try:
        os.remove(filePath)
      except:
        print(click.style(f"Error while deleting file : {filePath}", fg='red'))

  def editXML(self, path, callback):
    srcPath = f'{self.outputDir}/{path}'

    for fileName in glob.glob(srcPath):
      doc = None

      fr = open(fileName, 'r')
      doc = xmltodict.parse(fr.read())

      callback(fileName, doc)

      fw = open(fileName, 'w')
      fw.write(xmltodict.unparse(doc, pretty=True))

  def editRawFile(self, path, callback):
    srcPath = f'{self.outputDir}/{path}'

    for fileName in glob.glob(srcPath):
      doc = None

      fr = open(fileName, 'r')
      doc = fr.read()

      callback(fileName, doc)

      fw = open(fileName, 'w')
      fw.write(doc)

  def removeStandardLayouts(self, packageFile):
    srcPath = f'{self.outputDir}/layouts/*.layout'

    package = open(f'{self.outputDir}/{packageFile}', 'r')

    doc = xmltodict.parse(package.read())

    members = []
    try:
      for type in doc['Package']['types']:
        if type['name'] == 'CustomObject':
          members = list(filter(lambda member: member != '*' and '__c' not in member, type['members']))

      for filePath in glob.glob(srcPath):
        fileName = os.path.basename(filePath).partition('-')[0]
        if fileName not in members:
          if fileName == 'PersonAccount' and 'Account' in members:
            pass
          elif (fileName == 'CaseClose' or fileName == 'CaseInteraction') and 'Case' in members:
            pass
          elif '__c' not in fileName and '__mdt' not in fileName:
            os.remove(filePath)
    except:
      print(click.style(f"Error while removing standard layouts", fg='red'))