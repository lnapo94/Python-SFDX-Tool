""" Salesforce API message templates """

LOGIN_MSG = \
  """<?xml version="1.0" encoding="utf-8" ?>
      <soapenv:Envelope
              xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
              xmlns:urn="urn:partner.soap.sforce.com">
          <soapenv:Header>
              <urn:CallOptions>
                  <urn:defaultNamespace>sf</urn:defaultNamespace>
              </urn:CallOptions>
          </soapenv:Header>
          <soapenv:Body>
              <urn:login>
                  <urn:username>{username}</urn:username>
                  <urn:password>{password}</urn:password>
              </urn:login>
          </soapenv:Body>
      </soapenv:Envelope>"""

DEPLOY_MSG = \
    """<soapenv:Envelope
        xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
        xmlns:met="http://soap.sforce.com/2006/04/metadata">
   <soapenv:Header>
      <met:SessionHeader>
         <met:sessionId>{sessionId}</met:sessionId>
      </met:SessionHeader>
   </soapenv:Header>
   <soapenv:Body>
      <met:deploy>
         <met:ZipFile>{ZipFile}</met:ZipFile>
         <met:DeployOptions>
            <met:allowMissingFiles>{allowMissingFiles}</met:allowMissingFiles>
            <met:autoUpdatePackage>{autoUpdatePackage}</met:autoUpdatePackage>
            <met:checkOnly>{checkOnly}</met:checkOnly>
            <met:ignoreWarnings>{ignoreWarnings}</met:ignoreWarnings>
            <met:performRetrieve>{performRetrieve}</met:performRetrieve>
            <met:purgeOnDelete>{purgeOnDelete}</met:purgeOnDelete>
            <met:rollbackOnError>{rollbackOnError}</met:rollbackOnError>
            <met:singlePackage>{singlePackage}</met:singlePackage>
            {testLevel}
            {tests}
         </met:DeployOptions>
      </met:deploy>
   </soapenv:Body>
</soapenv:Envelope>"""

CHECK_DEPLOY_STATUS_MSG = \
    """<soapenv:Envelope
xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
xmlns:met="http://soap.sforce.com/2006/04/metadata">
   <soapenv:Header>
      <met:SessionHeader>
         <met:sessionId>{sessionId}</met:sessionId>
      </met:SessionHeader>
   </soapenv:Header>
   <soapenv:Body>
      <met:checkDeployStatus>
         <met:asyncProcessId>{asyncProcessId}</met:asyncProcessId>
         <met:includeDetails>{includeDetails}</met:includeDetails>
      </met:checkDeployStatus>
   </soapenv:Body>
</soapenv:Envelope>"""

RETRIEVE_MSG = \
    """<soapenv:Envelope
xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
xmlns:met="http://soap.sforce.com/2006/04/metadata">
   <soapenv:Header>
      <met:SessionHeader>
         <met:sessionId>{sessionId}</met:sessionId>
      </met:SessionHeader>
   </soapenv:Header>
   <soapenv:Body>
      <met:retrieve>
         <met:retrieveRequest>
            <met:apiVersion>{apiVersion}</met:apiVersion>
            <met:singlePackage>{singlePackage}</met:singlePackage>
            <met:unpackaged>{unpackaged}</met:unpackaged>
         </met:retrieveRequest>
      </met:retrieve>
   </soapenv:Body>
</soapenv:Envelope>"""

CHECK_RETRIEVE_STATUS_MSG = \
    """<soapenv:Envelope
xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
xmlns:met="http://soap.sforce.com/2006/04/metadata">
   <soapenv:Header>
      <met:SessionHeader>
         <met:sessionId>{sessionId}</met:sessionId>
      </met:SessionHeader>
   </soapenv:Header>
   <soapenv:Body>
      <met:checkRetrieveStatus>
         <met:asyncProcessId>{asyncProcessId}</met:asyncProcessId>
         <met:includeZip>{includeZip}</met:includeZip>
      </met:checkRetrieveStatus>
   </soapenv:Body>
</soapenv:Envelope>"""