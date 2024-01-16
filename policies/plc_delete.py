from sdk.color_print import c_print
from tqdm import tqdm

def delete_policies(session, policies, logger):
    deleted = 0
    if policies:
        logger.info(f'Deleteing Policies from tenant \'{session.tenant}\'')

        for policy in tqdm(policies, desc='Deleting Policies', leave=False):
            plc_id = policy['policyId']
            name = policy['name']
            logger.debug(f'API - Deleting policy \'{name}\'')
            session.request('DELETE', f'/policy/{plc_id}', status_ignore=[204])
            deleted += 1
    else:
        logger.debug(f'No Policies to delete from tenant \'{session.tenant}\'')

    return deleted
