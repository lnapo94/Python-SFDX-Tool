def removeExpose(fileName, data):
  print(fileName)
  del data['LightningComponentBundle']['isExposed']
  data['LightningComponentBundle']['apiVersion'] = '100.0'

def func1(context, helpers):
  print('Run Func 1')

  helpers.filterMetadata('lwc/*/**.xml')
