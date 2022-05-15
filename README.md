# Python SFDX Toolkit
Python SFDX Toolkit is a CLI program built to execute both *retrieve* and *deploy* operations on Salesforce.

The CLI supports the usage of internal built in methods to retrieve and deploy as well as SFDX retrieve/deploy operations.

- [Python SFDX Toolkit](#python-sfdx-toolkit)
  - [Requirements](#requirements)
  - [Usage](#usage)
  - [Installation](#installation)
  - [Features](#features)
    - [Authenticate to Salesforce](#authenticate-to-salesforce)
    - [Retrieve full metadata from Salesforce based on package.xml](#retrieve-full-metadata-from-salesforce-based-on-packagexml)
    - [Deploy full metadata to Salesforce based on package.xml](#deploy-full-metadata-to-salesforce-based-on-packagexml)
    - [Apply 'standard' plugins](#apply-standard-plugins)
      - [Standard Helpers](#standard-helpers)
      - [Standard Plugins](#standard-plugins)
    - [Build your own plugins](#build-your-own-plugins)
  - [Changelog](#changelog)

## Requirements

- [Python3](https://www.python.org/) at least `3.10`
- [SFDX](https://developer.salesforce.com/tools/sfdxcli) at least `7.149.1`


## Usage

__Python SFDX Toolkit__ is meant to be a CLI interface to perform retrieve and deploy operations on Salesforce.

Type `pydx --help` to see all the available commands. If you would like to have more information about a specific command, type `pydx <command> --help` to have all the available options.

## Installation
To install `pydx` in your local environment, run the following command:
```
pip install Python-SFDX-Toolkit
```

Once installed, go to the root folder of a Salesforce project and type:
```
pydx init
```
which will create a *pydx.json* file in the root folder of your current workspace.

## Features
### Authenticate to Salesforce
To authenticate to Salesforce, in each command available you should includes the username `-u` and the password `-p` options:
```
pydx retrieve -u USERNAME -p PASSWORD
```
If you would like to authenticate to a Sandbox environment (with the url https://test.salesforce.com), you should add the 'sandbox' option `-s`:
```
pydx retrieve -s -u USERNAME -p PASSWORD
```

If you use the `SFDX` wrapper commands (i.e. `retrieve-sfdx` or `deploy-sfdx`) you should authenticate to Salesforce using the actual SFDX CLI and then use `pydx` to login using the org alias option:
```
pydx retrieve-sfdx -o MY_SFDX_ORG_ALIAS
```

### Retrieve full metadata from Salesforce based on package.xml
To retrieve all the metadata you specified inside a "package.xml" file from Salesforce, the command to run is:
```
pydx retrieve
```
This command has the following options that you can use:
- `-u` `--username`: The username used to authenticate to Salesforce. __REQUIRED__
- `-p` `--password`: The password used to authenticate to Salesforce. __REQUIRED__
- `--package`: The path to the package.xml file, default is `<CURRENT_FOLDER>/src/package.xml`.
- `-s` `--sandbox`: Flag used to authenticate towards a Sandbox environment
- `-o` `--output`: Path to the output folder where to unpack the retrieved metadata, default is `<CURRENT_FOLDER>/src`.
- `-se` `--settingFile`: The path to the settings file, default is `<CURRENT_FOLDER>/pydx.json`.

### Deploy full metadata to Salesforce based on package.xml
To deploy all your local metadatas specified inside the "package.xml" to Salesforce, you should run:
```
pydx deploy
```

The deploy command accepts the following options:
- `-u` `--username`: The username used to authenticate to Salesforce. __REQUIRED__
- `-p` `--password`: The password used to authenticate to Salesforce. __REQUIRED__
- `--package`: The path to the package.xml file, default is `<CURRENT_FOLDER>/src/package.xml`.
- `-s` `--sandbox`: Flag used to authenticate towards a Sandbox environment
- `-se` `--settingFile`: The path to the settings file, default is `<CURRENT_FOLDER>/pydx.json`.
- `-t` `--testLevel`: The test level used to permorm the deployment, chosen from:
  - RunAllTests: run all the tests available inside the org (both managed and unmanaged)
  - RunLocalTests: run your tests (only unmanaged tests)
  - RunSpecifiedTests: run a subset of specified tests (they should be specified inside the `-runTests` option)
  - NoTestRun: it doesn't run any tests to perform the deployment. *ONLY FOR __NON PRODUCTION__ ORG*
- `-r` `--runTests`: comma separated test classes to be run when chosen the *RunSpecifiedTests* test level
- `-v` `--validate`: Flag used to perform only a validation (it executes all the operation needed to deploy the metadata but it doesn't persist any modification in the target org)

### Apply 'standard' plugins
`PYDX` not only support retrieve and deploy operation, but also is useful when you would like to alter your metadata before the deployment or the retrieve.  
This can be particularly useful when you would like to use this CLI in a *CI/CD* project to automate your deployment to Salesforce performing various tasks.  

The __Python SFDX Toolkit__ comes with a set of plugins we've seen useful in our projects, like delete some useless folder (such as *resource-bundles*), change the content of some metadatas (i.e. remove some Profile permission which usually breaks the deployment in sanboxes environment) etc...

This pre-implemented functions are divided into 2 main categories:
- helpers: function built to perform generic tasks to alter the metadatas. They are available in all your plugins under the `helpers` variable.
- plugins: callbacks used to perform specific tasks hardcoded inside the plugin itself. They are available in all your plugins importing the `standard_plugin` package.

#### Standard Helpers
| Name                      | Description                                                                            | Usage                                        |
| ------------------------- | -------------------------------------------------------------------------------------- | -------------------------------------------- |
| __editXML__               | Read an XML file and parse it as Dictionary to be modified by the callback function    | `helpers.editXML(path, callback)`            |
| __filterMetadata__        | Remove the metadata (files) specified within the given path                            | `helpers.filterMetadata(path)`               |
| __editRawFile__           | Read a file and parse it as a simple string to be modified by the callback function    | `helpers.editRawFile(path, callback)`        |
| __removeFolders__         | Remove all the folders (and their content) specified within the given path             | `helpers.removeFolders(path)`                |
| __removeStandardLayouts__ | Remove all the layouts for the standard objects __NOT__ specified in the given package | `helpers.removeStandardLayouts(packageFile)` |

#### Standard Plugins
| Name                         | Description                                                                                          | Usage                                                                                 |
| ---------------------------- | ---------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| __enableClassAccessLevel__   | Enable all class accesses to the profiles within the given path                                      | `helpers.editXML('profiles/*.profile', standard_plugins.enableClassAccessLevel)`      |
| __deleteProfilePermissions__ | Remove all user permissions from the profile within the given path                                   | `helpers.editXML('profiles/*.profile', standard_plugins.deleteProfilePermissions)`    |
| __removeOAuthConfig__        | Remove the Consumer Key from the Connected Apps within the given path                                | `helpers.editXML('connectedApps/*.connectedApp', standard_plugins.removeOAuthConfig)` |
| __removeUselessListViews__   | Remove standard list views (inside Task and Event object) that usually mess up during the deployment | `helpers.editXML('objects/Task.object', standard_plugins.removeUselessListViews)`     |

### Build your own plugins

With `PYDX` you can build your own plugins to permform specific tasks in your projects.  
Your plugins can be run before each deployment or after each retrieving from Salesforce.

To specify when you to run your plugin, each `PYDX` needs to have a `pydx.json` file in the root of your project: 
```json
{
  "preDeploy": [],
  "postRetrieve": ["plugins.my_beautiful_plugin"]
}
```
in which you can specify the plugin you would like to run and when you want to run it.

Your plugins should be created inside the folder you will run the CLI (since the importing package is relative to the CLI current folder). For instance, if you run the CLI inside the root folder of a Salesforce project, a possible directory structure could be:
```

Your Salesforce Project/
├─ my_plugins/
│  ├─ __init__.py
│  ├─ my_beautiful_plugin.py
├─ src/
│  ├─ aura/
│  ├─ classes/
│  ├─ other metadatas.../
│  ├─ package.xml
└─ pydx.json
```
As you can see, your plugins are inside a *Python* package and, to let the CLI includes your own plugins, the CLI should be run inside "Your Salesforce Project" folder.

Your plugins should accept 2 parameters: `context` and `helpers`:
```python
def enableClassAccesses(context, helpers):
  pass
```
- `context` contains useful information of the running environment (i.e. you can access all the environment variables of the host system)
- `helpers` contains useful functions to work with metadatas [Standard Helpers](#standard-helpers)

## Changelog

* `0.0.3`: First release with basic features
  * Deploy/Retrieve metadata logging in with username and password
  * Deploy/Retrieve metadata using the SFDX wrapper
  * Simple Plugin Engine to perform various tasks on metadatas