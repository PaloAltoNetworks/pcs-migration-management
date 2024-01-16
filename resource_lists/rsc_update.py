from sdk.color_print import c_print
from tqdm import tqdm

def update_resource_lists(session, resource_lists, logger):
    updated = 0
    if resource_lists:
        logger.info(f'Updating Resource Lists for tenant: \'{session.tenant}\'')

        for rsc_list in tqdm(resource_lists, desc='Updating Resource Lists', leave=False):
            rl_id = rsc_list['id']
            status_ignore = [201]
            logger.debug('API - Updating Resource List')
            session.request("PUT", f"/v1/resource_list/{rl_id}", json=rsc_list, status_ignore=status_ignore)
            updated += 1

    else:
        logger.info(f'No Resource Lists to update for tenant: \'{session.tenant}\'')

    return updated