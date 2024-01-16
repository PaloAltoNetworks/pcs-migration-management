# Tenant Lift and Shift / Tenant Central Management

# Modes of Operation

## Sync Mode

Sync Mode is used to sync changes made to a “main” tenant across one or more “clone” tenants. 

Sync mode was designed to allow for multiple Prisma Cloud tenants to be centrally managed by one main tenant. Sync mode is capable of adding, updating, and deleting (must manually enable) elements from Prisma Cloud tenants to ensure that any change made to the main tenant is propagated to the clone tenants.

## Migrate Mode

Migrate Mode is used to copy tenant data from an existing populated Prisma Cloud tenant to a new empty Prisma Cloud tenant. For example, if you have a test tenant and you want to create a second tenant for production, Migrate Mode can be used to initially configure the new tenant.  To keep the second tenant up to date as you make changes in the dev tenant, you would then use Sync Mode to migrate changes.

## Supported Prisma Cloud Components

The scripts customization menu allows you to do a “full” migration/sync or pick and choose which components you want to migrate/sync. See “Running Script” section for details.

This script supports two primary modes of operation, migrate and sync. The difference between the migrate and sync mode is as follows: Migrate mode assumes the destination tenant is empty or mostly empty. The migrate mode will not do checks/comparisons on nested values of entities. For example, if you are migrating compliance standards to an empty or mostly empty tenant. Migrate mode will only look at the top level compliance standard to determine if the compliance standard and its requirements and sections need to be brought over. In sync mode, the script would look through all of the compliance data and could find and add a single missing compliance section. This means that migrate mode is faster and sync mode is much slower but does a more thorough job. Sync mode also allows for components to be updated and even deleted. Migrate mode will only add components or update default components as that is the only change that can be made to default components on Prisma Cloud.

This script is divided up into modules that each migrate/sync one component of Prisma Cloud. For example, the cloud_migrate module handles the migration of Cloud Accounts.

Many modules rely on other modules being run first due to dependencies that exist within prisma cloud. For example, the Users modules should only be run/migrated after the Roles module. Users belong to Roles and if the Roles do not exist on the tenant when the Users are migrated, the Users will all be placed into the default Role and not into the Roles they should be as the roles do not yet exist.

Prisma Cloud components that can be migrated and synced by this script:

Compliance Data -	    Depends on: None  
Enterprise Settings - Depends on: None  
Resource Lists - 	    Depends on: None  
Trusted IPs - 		    Depends on: None  
Account Groups - 	    Depends on: None  
Saved Searches -	    Depends on: Trusted IPs  
User Roles - 		      Depends on: Account Groups, Resources List  
Users - 		          Depends on: User Roles  
Policies - 		        Depends on: Compliance Data, Saved Searches  
Alert Rules - 		    Depends on: Account Groups, Resource Lists, Policies  
Anomaly Settings - 	  Depends on: Policies

**This script does not make any modifications to the source/main tenant.**

**The destination/clone tenant WILL be modified by the script.**

**In Migrate mode, the clone tenant will only have elements added or updated - no items will be deleted.**

**In Sync mode a deep nested search is performed to find all possible deltas between the tenants involved in the script. There is a setting that allows Sync mode to delete entities that are found on the clone tenant that do not exist on the source tenant. This option is disabled in “full sync” mode. To enable, you must manually select each Prisma Cloud component from the customization menu and by following the prompts, change the allowed operations to include delete mode.**

# Disclaimer

Please report any bugs you encounter so they can be fixed. Please include any relevant error messages, the modes/settings you were running the script in and any other information you believe to be relevant. Log files are now produced with each run so if you encounter any errors please include any associated log files.

## Conditions for Use / Caveats

### Name Changes

In all but a few cases, the name of an entity is its only cross tenant identifier. Changing the name of entities and then running this script in sync mode, will result in that entity from being deleted from the clone tenant, and then added back with the new name. This will disrupt any other entities on the Prisma Cloud tenant that depend on it. Using this script means in most cases you will not be able to change the name of entities that you are trying to sync/update across all the tenants you are managing. A fix to this problem is in the works but for now, please understand this limitation.

### Cloud Accounts

GCP and Azure Cloud Accounts can not be migrated without the user supplying the credentials. For security reasons, the Prisma Cloud API does not return GCP or Azure credentials. To overcome this, please supply the Service Account Key JSON file to the ‘cloud_credentials/gcp’ or the ‘cloud_credentials/azure’ folder and name the terraform file to be the exact same name of the Cloud Accounts name in Prisma Cloud, spaces included. For best results, copy and paste the cloud accounts name into the filename to ensure sameness.

Oracle Cloud (OCI) Accounts are not supported by this script at this time.

### Alert Rules

Integrations can not be migrated by this script. All Alert Rules that rely on external integrations will be migrated but will not be configured to use the external integrations. These alert rules will be migrated and disabled. The user will have to manually configure these alert rules to use the integrations.

### Modules

Currently, module configuration migration/sync is not supported (Data Security & Cloud Code Security.. You are able to migrate/sync IAM Policies and Saved Searches as well as Cloud Accounts that use Data Security. However other modules and module functionality are not supported at this time. For example, if you try to migrate a custom policy or saved search from a module like Microsegmentation, you will encounter errors.  Fortunately, module support is on the roadmap for this tool.

### Trusted Login IPs

The script will not automatically enable the trusted Login IPs to ensure the machine running the script does not get blocked from the tenant. After the migration or sync process is done, someone will have to manually enable them.

## Setup/Installation

This script was written in Python3 and should be run with Python3.10 or greater

Clone this project from github onto the machine of your choice. This script requires a reliable internet connection and may run into trouble if it is being run on a machine connected to a VPN that does TLS Interception.

This script relies on 4 external Python libraries:  
Requests - An installation guide can be found here: https://docs.python-requests.org/en/master/  
PyYAML - An installation guide can be found here: https://pyyaml.org/  
Loguru - An installation guide can be found here: https://github.com/Delgan/loguru  
tqdm - An installation guide can be found here: https://github.com/tqdm/tqdm

You can also install the dependencies quickly by using Python’s package manager and the supplied requirements file.

`python3 -m pip install -r requirements.txt`

## Running the script 

Get your Prisma Cloud Access Key, Secret Key and App URL ready. The script will ask you for them during setup.

This script includes a text based menu that allows you to customize the way the script runs. This is the recommended way to interact with this script. Please note that for the sake of user choice, the script allows you to migrate/sync components of a Prisma Cloud tenant without first migrating the components dependencies. For a full list of components and their dependencies see the Overview section. 

Run the main menu script using Python3 after all required Python3 libraries have been installed.

`python3 main.py`

You will be prompted to run the script in Migrate or Sync mode.

Once you have selected a mode you will be prompted to do a full migration or a full sync. If you select YES then all Prisma Cloud components that are supported by this script will be migrated or synced across the tenants the script has access too. If you select NO then you will be asked to pick and choose what Prisma Cloud components will be migrated or synced with this script. You will also be able to selectively enable Add, Update, and Delete operations for sync mode through this customization menu.

There are also four command line arguments that can be used. -yaml, -creds, -uuid, and -quiet.

-yaml Allows YAML config files to be created that allow this script to be run without any user input being required after the script as started. You have to supply the name of the config file you want to store your script runtime settings in as a command line argument following the -yaml flag. If you supply a file that does not exist, the script will create the file and ask you the necessary setup questions. If you supply an existing valid config file, the script will run with your customized settings without any further user input. This feature enables this script to be run as a cron job.

`python3 main.py -yaml my_sync_settings.yml`  

--no-file Disables plain text files from being created with tenant credentials. By default, when you do this for the first time, the script will walk you through a set up process and a tenant_credentials.yml file will be created. The next time the script is run, this file will be read from and the tenants will be loaded in automatically. If you need to make a change to this file to update the tenants that are being managed by the script, you can manually edit tenant_credentials.yml or delete it and run the script to re-do the setup process.  

`python3 main.py -creds`  

-uuid Allows for specifying a single entity's ID that will be migrated.

`python3 main.py -uuid`

You can of course combine run options for convenience.

`python3 main.py -uuid -yaml my_uuid_migrate.yml`

-quiet Hides the logging output and only shows progress bars in the terminal output.  

`python3 main.py -quiet -yaml my_sync_settings.yml`


## Example Use Cases
Many users only want to sync one or two entities accross multiple Tenants. This can be accomplished by only choosing the desired module during the scripts setup process.

For example, to only move policies from one tenant to an other, respond with 'yes' to the Policies module, Compliance Data module, and the Saved Search Module. Policies rely on Compliance Data and Saved searches so that is why these have to be enabled along with the Policy module.

![Migrate Policies Example](https://github.com/PaloAltoNetworks/pcs-migration-management/blob/main/images/policy_migrate.png) 

Once you have finished answering the questions, the script will start the migration process. The last question asked is "Do you want to migrate Enterprise Settings? (Y/N):" an then the script will begin with the settings you have just configured. 

