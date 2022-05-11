import json
import os
import sys
from inspect import getmembers, isfunction

from .helpers import Helper

import os

class PluginEngine:

  def __init__(self, settingFile, outputFolder):
    f = open(settingFile)
    data = json.load(f)
    
    self.outputFolder = outputFolder

    self.preDeployScripts = data['preDeploy']
    self.postRetrieveScripts = data['postRetrieve']

    # Build context
    self.context = {}
    self.context['ENVIRONMENT'] = os.environ

  def preDeploy(self):
    self.__run(self.preDeployScripts)

  def postRetrieve(self):
    self.__run(self.postRetrieveScripts)

  def __run(self, scripts):

    helper = Helper(self.outputFolder)
    
    for script in scripts:
      module = __import__(script)
      for funcName, func in getmembers(module, isfunction):
        print('Running {}...'.format(funcName))
        func(os.environ, helper)
        print('{} finished'.format(funcName))
    

if __name__ == '__main__':
  test = PluginEngine()
  test.postRetrieve()