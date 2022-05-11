import xmltodict
import json
import glob
import os
import click

class Helper:

  def __init__(self, outputDir):
    self.outputDir = outputDir

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