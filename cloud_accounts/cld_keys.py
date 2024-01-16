import json
from os import path

def get_gcp_credentials(cloud_accounts: list, logger:object):
    #Read Terraform JSON and get credentials
    #The Terraform JSON must be named as the same as the cloud_account
    info = dict()
    for account in cloud_accounts:
        if account['cloudType'] == 'gcp':
            if 'parentAccountName' in account:
                if account['name'] != account['parentAccountName']: #Ignore child accounts
                    continue
            cld_name = account['name']            
            try:
                f_path = path.join('cloud_credentials','gcp',cld_name) + '.json'
                with open(f_path, 'r') as f:
                    terraform = json.load(f)
                    account_id = account['id']
                    info.update({
                        account_id:{
                            'private_key_id':terraform['private_key_id'],
                            'private_key':terraform['private_key'],
                            }
                        })
            except:
                logger.error(f'ERROR. Terraform JSON not found for GCP account: \'{cld_name}\'')
    return info

def get_azure_credentials(cloud_accounts: list, logger:object):
    #Read Terraform JSON and get credentials
    #The Terraform JSON must be named as the same as the cloud_account
    info = dict()
    for account in cloud_accounts:
        if account['cloudType'] == 'azure':
            if 'parentAccountName' in account:
                if account['name'] != account['parentAccountName']: #Ignore child accounts
                    continue
            cld_name = account['name']            
            try:
                f_path = path.join('cloud_credentials','azure',cld_name) + '.json'
                with open(f_path, 'r') as f:
                    terraform = json.load(f)
                    account_id = account['id']
                    info.update({
                        account_id:{
                            'key':terraform['key']
                            }
                        })
            except:
                logger.error(f'ERROR. Terraform JSON not found for Azure account: \'{cld_name}\'')
    return info