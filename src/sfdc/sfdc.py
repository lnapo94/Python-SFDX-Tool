import requests
import xml.dom.minidom
from xml.etree import ElementTree as ET
from .exceptions import SalesforceAuthenticationFailed
from .soap_messages import LOGIN_MSG, DEPLOY_MSG, CHECK_DEPLOY_STATUS_MSG, RETRIEVE_MSG, CHECK_RETRIEVE_STATUS_MSG

import click

class Sfdc:

  _XML_NAMESPACES = {
    'soapenv': 'http://schemas.xmlsoap.org/soap/envelope/',
    'mt': 'http://soap.sforce.com/2006/04/metadata'
    }

  def __init__(self, username, password, url):
    """
    Initializes a new SFDC object to work with Salesforce Metadata API.
    """
    self.url = url
    self.username = username
    self.password = password

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
    login_url = f'{self.url}/services/Soap/u/54.0'

    # Make the request
    response = requests.post(url=login_url, data=login_soap_body, headers=login_soap_request_headers)

    if response.status_code == 200:
      # If the request was good, parse it to obtain SessionID and ServerURL
      self.__sessionId = self.__getUniqueElementValueFromXmlString(response.text, 'sessionId')
      self.__serverUrl = self.__getUniqueElementValueFromXmlString(response.text, 'serverUrl')
      print(f'Session ID {self.__sessionId}')
    else:
      # Othewise, throw an exception
      except_code = self.__getUniqueElementValueFromXmlString(response.content, 'sf:exceptionCode')
      except_msg = self.__getUniqueElementValueFromXmlString(response.content, 'sf:exceptionMessage')
      raise SalesforceAuthenticationFailed(response.status_code, except_msg)

  def retrieve(self):
    """
    Submit a retrieve request to SFDC Metadata API.
    """

     # Setup the headers for the request
    retrieve_soap_request_headers = {
      'content-type': 'text/xml',
      'charset': 'UTF-8',
      'SOAPAction': 'retrieve'
    }

    # Get all the Metadata from the specified "package.xml" file
    # TODO To be implemented
    retrieve_package = """<types>
        <members>*</members>
        <name>Group</name>
    </types>"""

    # Get the Retrieve SOAP Message and complete it with additional information
    retrieve_soap_body = RETRIEVE_MSG.format(sessionId=self.__sessionId, apiVersion='54.0', singlePackage=True, unpackaged=retrieve_package)

    # Build the actual Retrieve URL
    retrieve_url = self.__serverUrl.replace('/u/', '/m/')

    # Make the request
    response = requests.post(url=retrieve_url, data=retrieve_soap_body, headers=retrieve_soap_request_headers)

    print(self.__serverUrl)
    print(response.text)

    # Parse response to get Async Id and its Status
    async_process_id = ET.fromstring(response.text).find(
      'soapenv:Body/mt:retrieveResponse/mt:result/mt:id',
      self._XML_NAMESPACES).text
    status = ET.fromstring(response.text).find(
      'soapenv:Body/mt:retrieveResponse/mt:result/mt:state',
      self._XML_NAMESPACES).text

    return async_process_id, status

  def checkRetrieveStatus(self, asyncProcessId):
    """
    Checks the status of a retrieve request.
    TODO: To be implemented
    """
    pass

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