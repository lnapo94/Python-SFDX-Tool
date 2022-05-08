import requests
import xml.dom.minidom
from base64 import b64encode, b64decode
from xml.etree import ElementTree as ET
from .exceptions import SalesforceAuthenticationFailed
from .soap_messages import LOGIN_MSG, DEPLOY_MSG, CHECK_DEPLOY_STATUS_MSG, RETRIEVE_MSG, CHECK_RETRIEVE_STATUS_MSG

import click

class Sfdc:

  _XML_NAMESPACES = {
    'soapenv': 'http://schemas.xmlsoap.org/soap/envelope/',
    'mt': 'http://soap.sforce.com/2006/04/metadata'
    }

  def __init__(self, username, password, url, apiVersion):
    """
    Initializes a new SFDC object to work with Salesforce Metadata API.
    """
    self.url = url
    self.username = username
    self.password = password
    self.apiVersion = apiVersion

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

    if response.status_code == 200:
      # If the request was good, parse it to obtain SessionID and ServerURL
      self.__sessionId = self.__getUniqueElementValueFromXmlString(response.text, 'sessionId')
      self.__serverUrl = self.__getUniqueElementValueFromXmlString(response.text, 'serverUrl')
    else:
      # Othewise, throw an exception
      except_code = self.__getUniqueElementValueFromXmlString(response.content, 'sf:exceptionCode')
      except_msg = self.__getUniqueElementValueFromXmlString(response.content, 'sf:exceptionMessage')
      raise SalesforceAuthenticationFailed(response.status_code, except_msg)

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
    retrieve_soap_body = RETRIEVE_MSG.format(sessionId=self.__sessionId, apiVersion=self.apiVersion, singlePackage=True, unpackaged=package)

    # Build the actual Retrieve URL
    retrieve_url = self.__serverUrl.replace('/u/', '/m/')

    # Make the request
    response = requests.post(url=retrieve_url, data=retrieve_soap_body, headers=retrieve_soap_request_headers)

    # Parse response to get Async Id and its Status
    async_process_id = ET.fromstring(response.text).find(
      'soapenv:Body/mt:retrieveResponse/mt:result/mt:id',
      self._XML_NAMESPACES).text
    status = ET.fromstring(response.text).find(
      'soapenv:Body/mt:retrieveResponse/mt:result/mt:state',
      self._XML_NAMESPACES).text

    return async_process_id, status

  def isRetrievingMetadata(self, asyncProcessId):
    """
    Checks the status of a retrieve request.
    TODO: To be implemented
    """

    # Setup the headers for the request
    retrieve_status_soap_request_headers = {
      'content-type': 'text/xml',
      'charset': 'UTF-8',
      'SOAPAction': 'checkRetrieveStatus'
    }

    # Get the Retrieve SOAP Message and complete it with additional information
    retrieve_status_soap_body = CHECK_RETRIEVE_STATUS_MSG.format(sessionId=self.__sessionId, asyncProcessId=asyncProcessId, includeZip=True)

    # Build the actual Retrieve URL
    retrieve_status_url = self.__serverUrl.replace('/u/', '/m/')

    # Make the request
    response = requests.post(url=retrieve_status_url, data=retrieve_status_soap_body, headers=retrieve_status_soap_request_headers)

    # Parse response to check retrieving status
    root = ET.fromstring(response.text)
    result = root.find('soapenv:Body/mt:checkRetrieveStatusResponse/mt:result/mt:done', self._XML_NAMESPACES)

    if result is None:
      raise Exception(f'Result node could not be found: {response.text}')
    elif result.text == 'true':
      self.__retrieveResult = response.text
      return True
    else:
      return False

  def getZipFile(self):
    if self.__retrieveResult is not None:
      root = ET.fromstring(self.__retrieveResult)
      result = root.find('soapenv:Body/mt:checkRetrieveStatusResponse/mt:result', self._XML_NAMESPACES)
      zipfile_base64 = result.find('mt:zipFile', self._XML_NAMESPACES).text
      return b64decode(zipfile_base64)

  def deploy(self):
    """
    Submit a deploy request to SFDC Metadata API.
    TODO: To be implemented
    """
    pass

  def checkDeployStatus(self, asyncProcessId):
    """
    Checks the status of a Deploy request.
    TODO: To be implemented
    """
    pass

  def __getUniqueElementValueFromXmlString(self, xmlString, elementName):
    """
    Extracts an element value from an XML string.
    For example, invoking
    getUniqueElementValueFromXmlString(
        '<?xml version="1.0" encoding="UTF-8"?><foo>bar</foo>', 'foo')
    should return the value 'bar'.
    """
    xmlStringAsDom = xml.dom.minidom.parseString(xmlString)
    elementsByName = xmlStringAsDom.getElementsByTagName(elementName)
    elementValue = None
    if len(elementsByName) > 0:
      elementValue = (
        elementsByName[0]
        .toxml()
        .replace('<' + elementName + '>', '')
        .replace('</' + elementName + '>', '')
      )
    return elementValue