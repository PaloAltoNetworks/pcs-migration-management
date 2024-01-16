from sdk.color_print import c_print
from tqdm import tqdm

def update_account_groups(session, account_groups, logger):
    added = 0
    if account_groups:
        logger.info(f'Updating Account Groups for tenant: \'{session.tenant}\'')
        for acc in tqdm(account_groups, desc="Updating Account Groups", leave=False):
            payload = {
                'name': acc.get('name'),
                'description': acc.get('description', ''),
                'accountIds': acc.get('accountIds', [])#,
                #'nonOnboardedCloudAccountIds': acc.get('nonOnboardedCloudAccountIds', []) 
            }
            grp_id = acc.get('id')
            logger.debug('API - Updating Account Group')
            session.request('PUT', f"/cloud/group/{grp_id}", json=payload)
            added =+ 1

    else:
        logger.info(f'No Account Groups to update for tenant: \'{session.tenant}\'')

    return added