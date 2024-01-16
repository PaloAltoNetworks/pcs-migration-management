def get_names(session: object, logger: object):
    '''
    Gets a list of all the cloud accounts and their names on a tenant.
    '''

    querystring = {'excludeAccountGroupDetails': 0 }

    logger.debug(f'API - Gettings cloud account names from tenant: {session.tenant}.')
    response = session.request('GET', '/cloud/name', params=querystring)

    data = response.json()

    accounts_found = len(data)

    logger.info(f'Got {accounts_found} accounts from tenant: {session.tenant}.')

    return data

def get_info(session: object, account: dict, logger: object) -> dict:
    '''
    Gets all cloud account info for all cloud accounts that are NOT children of organizations.
    The endpoint that returns all cloud accounts does not return enough details about
    each cloud account to onboard it to a new tenant.
    '''

    #Does this only Ignore GCP Child accounts?

    #Ignore GCP Child accounts
    if 'parentAccountName' in account:
        if account.get('name') != account.get('parentAccountName'):
            return ""

    #Gets all details for a specific cloud accounts
    cloud_type = account.get('cloudType')
    account_id = account.get('id')
    name = account.get('name')
    endpoint_url = f"/cloud/{cloud_type}/{account_id}"

    querystring = {"includeGroupInfo":1}

    logger.debug(f'API - Getting {cloud_type} cloud account info for \'{name}\' - \'{account_id}\'')
    response = session.request("GET", endpoint_url, params=querystring)
    
    if response.status_code == 200:
        return response.json()
    else:
        return ""

def get_all_info(session: object, account: dict, logger: object) -> dict:
    '''
    Gets all cloud account info for all cloud accounts that are NOT children of organizations.
    The endpoint that returns all cloud accounts does not return enough details about
    each cloud account to onboard it to a new tenant.
    '''

    #Gets all details for a specific cloud accounts
    cloud_type = account.get('cloudType')
    account_id = account.get('id')
    name = account.get('name')
    endpoint_url = f"/cloud/{cloud_type}/{account_id}"

    querystring = {"includeGroupInfo":1}

    logger.debug(f'API - Getting {cloud_type} cloud account info for \'{name}\' - \'{account_id}\'')
    response = session.request("GET", endpoint_url, params=querystring)
    
    if response.status_code == 200:
        return response.json()
    else:
        return ""