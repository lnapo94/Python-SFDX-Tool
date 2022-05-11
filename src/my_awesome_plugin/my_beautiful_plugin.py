import click
import plugins

def enableClassAccesses(context, helpers):
  print(click.style('Enabling all classes...', fg='bright_black'))
  helpers.editXML('profiles/*.profile', plugins.enableClassAccessLevel)

def deletePermissions(context, helpers):
  print(click.style('Removing Profile Permissions...', fg='bright_black'))
  helpers.editXML('profiles/*.profile', plugins.deleteProfilePermissions)

def removeOAuthConfig(context, helpers):
  print(click.style('Removing OAuth Config from Connected App...', fg='bright_black'))
  helpers.editXML('connectedApps/*.connectedApp', plugins.removeOAuthConfigFromConnectedApp)

def removeTaskAndEventListViews(context, helpers):
  print(click.style('Removing Useless List Views...', fg='bright_black'))
  helpers.editXML('objects/Task.object', plugins.removeUselessListViews)
  helpers.editXML('objects/Event.object', plugins.removeUselessListViews)

def removeResourceBundles(context, helpers):
  print(click.style('Filtering Metadata...', fg='bright_black'))
  helpers.removeFolders('resource-bundles/')
