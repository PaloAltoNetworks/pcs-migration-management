

from tqdm import tqdm

def add_accounts(session: object, accounts: list, azure_account_keys: dict,
                    gcp_account_keys: dict, logger: object) -> bool:

    accounts_added = 0

    #List of redlock errors to manually handle and have ignored by session.request
    redlock_ignore = ['not_account_owner', 'project_id_credential_mismatch', 'data_security_not_enabled_for_tenant', 'organization_viewer_permission_required', 'project_viewer_permission_required']

    tenant_name = session.tenant

    if accounts:
        logger.info(f'Adding Cloud Accounts to tenant: \'{session.tenant}\'')
        for account in tqdm(accounts, desc='Adding Cloud Accounts', leave=False):
            res = object()
            cloud_type = ''
            account_type = ''
            account_name = ''
            account_id = ''

            #Correctly set variables
            if 'cloudAccount' in account:
                if account['cloudAccount']['parentId'] != None: #Skip children of org accounts
                    continue
                #Set variables
                cloud_type = account['cloudAccount']['cloudType']
                account_name = account['cloudAccount']['name']
                account_id = account['cloudAccount']['accountId']
            else:
                #Set variables
                cloud_type = account['cloudType']
                account_type = account['accountType']
                account_name = account['name']
                account_id = account['accountId']
            res = 'BAD'
            if cloud_type == 'aws':
                res = add_aws(session, account, logger, redlock_ignore)
            if cloud_type == 'azure':
                res = add_azure(session, account, azure_account_keys, logger, redlock_ignore)
            if cloud_type == 'gcp':
                res = add_gcp(session, account, gcp_account_keys, logger, redlock_ignore)
            if cloud_type== 'alibaba_cloud':
                res = add_alibaba(session, account, logger, redlock_ignore)

            if res != 'BAD':
                try:
                    if res.status_code != 200:
                        if 'x-redlock-status' in res.headers:
                            if  redlock_ignore[0] in res.headers['x-redlock-status']:
                                logger.error('FAILED')
                                logger.warning(f'{cloud_type} cloud account \'{account_name}\'::\'{account_id}\' already onboarded to application stack.')
                                logger.error('not_account_owner')
                            if redlock_ignore[1] in res.headers['x-redlock-status']:
                                logger.error('FAILED')
                                logger.warning(f'Incorrect or invalid credentials for {cloud_type} account {account_name}::{account_id}.')
                                logger.error('project_id_credential_mismatch')
                            if redlock_ignore[2] in res.headers['x-redlock-status']:
                                logger.error('FAILED')
                                logger.warning('Data security not enabled on this tenant')
                                logger.error('data_security_not_enabled_for_tenant')
                            if redlock_ignore[3] in res.headers['x-redlock-status']:
                                logger.error('FAILED')
                                logger.warning('Problem with GCP Organization Key - No viewer permission')
                                logger.error('organization_viewer_permission_required')
                            if redlock_ignore[4] in res.headers['x-redlock-status']:
                                logger.error('FAILED')
                                logger.warning('Problem with GCP Project Key - No viewer permission')
                                logger.error('organization_viewer_permission_required')

                        logger.error(f'Cloud Account \'{account_name}\'::\'{account_id}\' failed to onboard.')
                    else:
                        accounts_added += 1
                except:
                    logger.critical('No responce from Prisma Cloud')
    else:
        logger.info(f'No Cloud Accounts to add for tenant: \'{session.tenant}\'')

    return accounts_added
        

#==============================================================================

def add_aws(session: object, account: dict, logger:object, redlock_ignore: list=None) -> bool:
    endpoint_url = "/cloud/aws"

    querystring = {"skipStatusChecks":1}

    #Account Groups are not specified here as they do not exists yet.
    if 'groupIds' in account:
        account.update(groupIds=[])
    if 'accountGroupInfos' in account:
        account.update(accountGroupInfos=[])
    if 'defaultAccountGroupId' in account:
        account.pop('defaultAccountGroupId')


    logger.debug('API - Add AWS account ', account['name'], '::', account['accountId'])
    response = session.request('POST', endpoint_url, json=account, params=querystring, redlock_ignore=redlock_ignore)

    return response

#==============================================================================

def add_azure(session: object, account: dict, azure_keys: dict, logger:object, redlock_ignore: list=None) -> bool:
    acc_name = account.get('cloudAccount', {}).get('name')
    
    
    if account['cloudAccount']['accountId'] in azure_keys:
        account.update(key=azure_keys[account['cloudAccount']['accountId']]['key'])

    if '***' in account.get('key'):
        logger.warning(f'No Keys for Azure account \'{acc_name}\'')
        logger.warning('Not onboarding account')
        return 'BAD'

    account['cloudAccount'].update(groupIds=[])

    #Account Groups are not specified here as they do not exists yet.
    if 'groupIds' in account['cloudAccount']:
        account['cloudAccount'].update(groupIds=[])
    if 'accountGroupInfos' in account['cloudAccount']:
        account['cloudAccount'].update(accountGroupInfos=[])
    if 'defaultAccountGroupId' in account:
        account.pop('defaultAccountGroupId')

    
    querystring = {"skipStatusChecks":1}

    logger.debug('API - Add Azure Account: ', acc_name, '::', account['cloudAccount']['accountId'])
    response = session.request("POST", '/cloud/azure', json=account, params=querystring, redlock_ignore=redlock_ignore)
    
    return response

#==============================================================================

def add_gcp(session: object, account: dict, gcp_keys: dict, logger:object, redlock_ignore: list=None):
    endpoint_url = "/cloud/gcp"

    querystring = {"skipStatusChecks":1}

    accountId = account['cloudAccount']['accountId']

    if accountId in gcp_keys:
        account['credentials'].update(private_key=gcp_keys[accountId]['private_key']) 
        account['credentials'].update(private_key_id=gcp_keys[accountId]['private_key_id'])

    # account['cloudAccount'].update(enabled=False)

    #Account Groups are not specified here as they do not exists yet.
    if 'groupIds' in account['cloudAccount']:
        account['cloudAccount'].update(groupIds=[])
    if 'accountGroupInfos' in account['cloudAccount']:
        account['cloudAccount'].update(accountGroupInfos=[])
    if 'defaultAccountGroupId' in account:
        account.pop('defaultAccountGroupId')
    
    logger.debug('API - Add GCP Account: ', account['cloudAccount']['name'], '::', account['cloudAccount']['accountId'])
    response = session.request("POST", endpoint_url, json=account, params=querystring, redlock_ignore=redlock_ignore)

    return response

#==============================================================================

def add_alibaba(session: object, account: dict, logger:object, redlock_ignore: list=None) -> bool:
    endpoint_url = "/cloud/alibaba_cloud"

    querystring = {"skipStatusChecks":1}

    account.update(groupIds=[])

    logger.debug('API - Add Alibaba Account: ', account['name'], '::', account['accountId'])
    response = session.request('POST', endpoint_url, params=querystring, json=account, redlock_ignore=redlock_ignore)

    return response

#==============================================================================

def add_oci(token: str, api_url, account: dict, redlock_ignore: list=None) -> bool:
    pass
