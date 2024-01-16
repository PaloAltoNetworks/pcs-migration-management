from sdk.color_print import c_print
from tqdm import tqdm

def add_account_groups(session, account_groups, logger):
    '''
    Accepts a tenant session and a list of account groups to add.
    Adds all the account groups to the tenant of the supplied session.
    '''
    
    tenant_name = session.tenant

    added = 0

    if account_groups:
        logger.info(f'Adding Account Groups to tenant: \'{tenant_name}\'')
        
        for acc_grp in tqdm(account_groups, desc='Adding Account Groups', leave=False):
            logger.debug('API - Adding Account Group')
            res = session.request('POST', '/cloud/group', json=acc_grp)
            if res.status_code == 200 or res.status_code == 201:
                added += 1
    else:
        logger.info(f'No Account Groups to add for tenant: \'{tenant_name}\'')

    return added