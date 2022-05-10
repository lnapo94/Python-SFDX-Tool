import requests
from bs4 import BeautifulSoup
from base64 import b64decode
from .exceptions import SalesforceAuthenticationFailed
from .soap_messages import LOGIN_MSG, DEPLOY_MSG, CHECK_DEPLOY_STATUS_MSG, RETRIEVE_MSG, CHECK_RETRIEVE_STATUS_MSG

class Sfdc:

  def __init__(self, username, password, url, apiVersion):
    """
    Initializes a new SFDC object to work with Salesforce Metadata API.
    """
    self.url = url
    self.username = username
    self.password = password
    self.apiVersion = apiVersion
    self.sessionId = None
    self.serverUrl = None
    self.metadataUrl = None
    self.asyncProcessId = None

    self.retrieveResult = None

  def login(self):
    """
    Login into SFDC Metadata API and retrieve SessionID and ServerURL.
    """

    # Setup the headers for the request
    login_soap_request_headers = {
      'content-type': 'text/xml',
      'charset': 'UTF-8',
      'SOAPAction': 'login'
    }

    # Get the Login SOAP Message and complete it with additional information
    login_soap_body = LOGIN_MSG.format(username=self.username, password=self.password)

    # Build the actual Login URL
    login_url = f'{self.url}/services/Soap/u/{self.apiVersion}'

    # Make the request
    response = requests.post(url=login_url, data=login_soap_body, headers=login_soap_request_headers)
    soup = BeautifulSoup(response.text, 'xml')

    if response.status_code == 200:
      # If the request was good, parse it to obtain SessionID and ServerURL
      self.sessionId = soup.find('sessionId').text
      self.serverUrl = soup.find('serverUrl').text
      self.metadataUrl = soup.find('serverUrl').text.replace('/u/', '/m/')
    else:
      # Othewise, throw an exception
      except_code = soup.find('sf:exceptionCode').text
      except_msg = soup.find('sf:exceptionMessage').text
      raise SalesforceAuthenticationFailed(except_code, except_msg)

  def retrieve(self, package):
    """
    Submit a retrieve request to SFDC Metadata API.
    """

     # Setup the headers for the request
    retrieve_soap_request_headers = {
      'content-type': 'text/xml',
      'charset': 'UTF-8',
      'SOAPAction': 'retrieve'
    }

    # Get the Retrieve SOAP Message and complete it with additional information
    retrieve_soap_body = RETRIEVE_MSG.format(sessionId=self.sessionId, apiVersion=self.apiVersion, singlePackage=True, unpackaged=package)

    # Make the request
    response = requests.post(url=self.metadataUrl, data=retrieve_soap_body, headers=retrieve_soap_request_headers)

    # Parse response to get Async Id
    soup = BeautifulSoup(response.text, 'xml')
    self.asyncProcessId = soup.Envelope.Body.retrieveResponse.result.id.text

  def isRetrievingMetadata(self):
    """
    Checks the status of a retrieve request.
    """

    # Setup the headers for the request
    retrieve_status_soap_request_headers = {
      'content-type': 'text/xml',
      'charset': 'UTF-8',
      'SOAPAction': 'checkRetrieveStatus'
    }

    # Get the Retrieve SOAP Message and complete it with additional information
    retrieve_status_soap_body = CHECK_RETRIEVE_STATUS_MSG.format(sessionId=self.sessionId, asyncProcessId=self.asyncProcessId, includeZip=True)

    # Make the request
    response = requests.post(url=self.metadataUrl, data=retrieve_status_soap_body, headers=retrieve_status_soap_request_headers)

    # Parse response to check retrieving status
    soup = BeautifulSoup(response.text, 'xml')
    result = soup.Body.checkRetrieveStatusResponse.result.done

    if result is None:
      raise Exception(f'Result node could not be found: {response.text}')
    elif result.text == 'true':
      self.retrieveResult = response.text
      return True
    else:
      return False

  def getZipFile(self):
    if self.retrieveResult is not None:
      soup = BeautifulSoup(self.retrieveResult, 'xml')
      zipfile_base64 = soup.Body.checkRetrieveStatusResponse.result.zipFile.text
      return b64decode(zipfile_base64)

  def deploy(self, zipFile, testLevel: str, runTests=[], validateOnly=False):
    """
    Submit a deploy request to SFDC Metadata API.
    """
    attributes = {
      'sessionId': self.sessionId,
      'ZipFile': zipFile,
      'allowMissingFiles': False,
      'autoUpdatePackage': False,
      'checkOnly': validateOnly,
      'ignoreWarnings': False,
      'performRetrieve': False,
      'purgeOnDelete': False,
      'rollbackOnError': True,
      'singlePackage': True
    }

    if testLevel:
      attributes['testLevel'] = '<met:testLevel>{}</met:testLevel>'.format(testLevel)
    
    testsTag = ''
    if runTests and str(testLevel).lower() == 'runspecifiedtests':
      for test in runTests:
        testsTag += '<met:runTests>{}</met:runTests>'.format(test)
    attributes['tests'] = testsTag

    # Setup the headers for the request
    deploy_soap_request_headers = {
      'content-type': 'text/xml',
      'charset': 'UTF-8',
      'SOAPAction': 'deploy'
    }

    # Get the Retrieve SOAP Message and complete it with additional information
    deploy_soap_body = DEPLOY_MSG.format(**attributes)

    # Make the request
    response = requests.post(url=self.metadataUrl, data=deploy_soap_body, headers=deploy_soap_request_headers)

    # Parse response to get Async Id
    soup = BeautifulSoup(response.text, 'xml')
    self.asyncProcessId = soup.Envelope.Body.deployResponse.result.id.text


  def isDeploying(self):
    """
    Checks the status of a Deploy request.
    """
     # Setup the headers for the request
    deploy_status_soap_request_headers = {
      'content-type': 'text/xml',
      'charset': 'UTF-8',
      'SOAPAction': 'checkDeployStatus'
    }

    # Get the Deploy SOAP Message and complete it with additional information
    deploy_status_soap_body = CHECK_DEPLOY_STATUS_MSG.format(sessionId=self.sessionId, asyncProcessId=self.asyncProcessId, includeDetails=True)

    # Make the request
    response = requests.post(url=self.metadataUrl, data=deploy_status_soap_body, headers=deploy_status_soap_request_headers)

    # Parse response to check retrieving status
    soup = BeautifulSoup(response.text, 'xml')
    result = soup.Body.checkDeployStatusResponse.result.done

    numberComponentsDeployed = soup.Body.checkDeployStatusResponse.result.numberComponentsDeployed.text
    numberComponentErrors = soup.Body.checkDeployStatusResponse.result.numberComponentErrors.text
    numberComponentsTotal = soup.Body.checkDeployStatusResponse.result.numberComponentsTotal.text

    numberTestsCompleted = soup.Body.checkDeployStatusResponse.result.numberTestsCompleted.text
    numberTestErrors = soup.Body.checkDeployStatusResponse.result.numberTestErrors.text
    numberTestsTotal = soup.Body.checkDeployStatusResponse.result.numberTestsTotal.text

    stateDetail = soup.Body.checkDeployStatusResponse.result.stateDetail

    status = soup.Body.checkDeployStatusResponse.result.status.text

    print('Status: {}'.format(status))

    print('Deployment: {} / {} [Errors: {}]'.format(numberComponentsDeployed, numberComponentsTotal, numberComponentErrors))
    print('Tests: {} / {} [Errors: {}]'.format(numberTestsCompleted, numberTestsTotal, numberTestErrors))

    if stateDetail:
      print('State Detail: {}'.format(stateDetail.text))

    if result is None:
      raise Exception(f'Result node could not be found: {response.text}')
    elif result.text == 'true':
      self.retrieveResult = response.text
      return True
    else:
      return False