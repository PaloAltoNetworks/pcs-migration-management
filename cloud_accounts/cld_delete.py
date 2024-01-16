from sdk.color_print import c_print
from tqdm import tqdm

def delete_accounts(cln_session, accounts, logger):
    deleted = 0
    if accounts:
        logger.info(f'Deleting Cloud Accounts from tenant \'{cln_session.tenant}\'')

        for account in tqdm(accounts, desc='Deleting Cloud Accounts', leave=False):
            cloud_type = ''
            cld_id = ''
            if 'cloudAccount' in account:
                cloud_type = account['cloudAccount']['cloudType']
                cld_id = account['cloudAccount']['accountId']
            else:
                cloud_type = account['cloudType']
                cld_id = account['accountId']
        
            logger.debug('API - Deleting cloud account')
            res = cln_session.request('DELETE', f'/cloud/{cloud_type}/{cld_id}')
            if res.status_code == 200 or res.status_code == 201:
                delted += 1
    else:
        logger.info(f'No Cloud Accounts to delete for tenant \'{cln_session.tenant}\'')

    return deleted