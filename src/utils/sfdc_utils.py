def sfdc_url(sandbox=False):
  if sandbox:
    return 'https://test.salesforce.com'
  else:
    return 'https://login.salesforce.com'