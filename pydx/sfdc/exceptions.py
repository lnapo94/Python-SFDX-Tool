class SalesforceError(Exception):
  """Base Salesforce API exception"""

  message = 'Unknown error occurred for {url}. Response content: {content}'

  def __init__(self, url, status, resource_name, content):
    self.url = url
    self.status = status
    self.resource_name = resource_name
    self.content = content

  def __str__(self):
    return self.message.format(url=self.url, content=self.content)

  def __unicode__(self):
    return self.__str__()

class SalesforceAuthenticationFailed(SalesforceError):
  """
  Thrown to indicate that authentication with Salesforce failed.
  """

  def __init__(self, code, message):
    self.code = code
    self.message = message

  def __str__(self):
    return '{code}: {message}'.format(code=self.code, message=self.message)