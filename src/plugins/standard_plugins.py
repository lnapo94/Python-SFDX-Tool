def enableClassAccessLevel(fileName, data):
  """Enable all classes to users' profiles"""
  if 'classAccesses' in data['Profile']:
    for classAccess in data['Profile']['classAccesses']:
      classAccess['enabled'] = 'true'

def deleteProfilePermissions(fileName, data):
  """Remove permissions which usually break the deployment"""
  permissionsToRemove = ["ManageSandboxes","ManageTranslation", "EditBillingInfo", "RemoveDirectMessageMembers", "ConsentApiUpdate", "Packaging2PromoteVersion", "ViewFlowUsageAndFlowEventData", "ViewUserPII", "TraceXdsQueries", "AIViewInsightObjects"]

  if 'userPermissions' in data['Profile']:
    for userPermission in data['Profile']['userPermissions']:
      if userPermission['name'] in permissionsToRemove:
        data['Profile']['userPermissions'].remove(userPermission)

def removeOAuthConfigFromConnectedApp(fileName, data):
  """Remove OAuth consumer key from connected apps (it is regenerated automatically in each Salesforce org)"""
  if 'consumerKey' in data['ConnectedApp']['oauthConfig']:
    del data['ConnectedApp']['oauthConfig']['consumerKey']

def removeUselessListViews(fileName, data):
  """Remove Tasks and Events List Views that, I don't know why, Salesforce duplicates everytime it deploys"""
  listViewToRemove = ['CompletedTasks', 'DelegatedTasks', 'RecurringTasks', 'UnscheduledTasks', 'OpenTasks', 'OverdueTasks', 'TodaysTasks', 'MyRecentEvents', 'MyTeamsRecentEvents', 'MyTeamsUpcomingEvents', 'MyUpcomingEvents', 'TodaysAgenda']

  if 'listViews' in data['CustomObject']:
    listViewsToMaintain = []
    for listView in data['CustomObject']['listViews']:
      if listView['fullName'] not in listViewToRemove:
        listViewsToMaintain.append(listView)

    data['CustomObject']['listViews'] = listViewsToMaintain