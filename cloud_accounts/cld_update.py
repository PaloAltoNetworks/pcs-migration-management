from tqdm import tqdm

def update_accounts(cln_session, accounts_to_update, logger):
    '''
    Updates the details of cloud accounts on the clone tenant
    '''
    updated = 0

    if accounts_to_update:
        logger.info(f'Updating Cloud Accounts for tenant \'{cln_session.tenant}\'')

        for account in tqdm(accounts_to_update, desc='Updating Cloud Accounts', leave=False):
            cloud_type = ''
            cld_id = ''

            if 'cloudAccount' in account:
                cloud_type = account['cloudAccount']['cloudType']
                cld_id = account['cloudAccount']['accountId']
            else:
                cloud_type = account['cloudType']
                cld_id = account['accountId']

            #Patch children of orgs
            if 'cloudAccount' in account:
                if 'parentId' in account['cloudAccount']:
                    if account['cloudAccount']['parentId'] != None:
                        patch = {
                            "groupIds": account['cloudAccount']['groupIds']
                        }
                        status = account['cloudAccount']['enabled']
                        if status == True:
                            status = 'true'
                        if status == False:
                            status = 'false'

                        logger.debug('API - Patching child account')
                        res1 = cln_session.request('PATCH', f'/cloud/{cloud_type}/{cld_id}', json=patch)
                        res2 = cln_session.request('PATCH', f'/cloud/{cld_id}/status/{status}', redlock_ignore=['cloud_account_already_disabled'])
                        if res1.status_code == 200 or res1.status_code == 201:
                            updated +=1
                        elif res2.status_code == 200 or res2.status_code == 201:
                            updated +=1
                    else:
                        #Update cloud account
                        logger.debug('API - Updating cloud account')
                        res = cln_session.request('PUT', f'/cloud/{cloud_type}/{cld_id}', json=account)
                        if res.status_code == 200 or res.status_code == 201:
                            updated += 1
                else:
                    #Update cloud account
                    logger.debug('API - Updating cloud account')
                    res = cln_session.request('PUT', f'/cloud/{cloud_type}/{cld_id}', json=account)
                    if res.status_code == 200 or res.status_code == 201:
                        updated += 1
            else:
                #Update cloud account
                logger.debug('API - Updating cloud account')
                res = cln_session.request('PUT', f'/cloud/{cloud_type}/{cld_id}', json=account)
                if res.status_code == 200 or res.status_code == 201:
                    updated += 1
    else:
        logger.info(f'No Cloud Accounts to update for tenant \'{cln_session.tenant}\'')

    return updated