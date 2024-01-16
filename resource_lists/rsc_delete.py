from sdk.color_print import c_print
from tqdm import tqdm

def delete_resource_lists(session, resource_lists, logger):
    deleted = 0

    if resource_lists:
        logger.info(f'Deleteing resource lists from tenant: \'{session.tenant}\'')

        for rsc_list in tqdm(resource_lists, desc='Deleting Resource Lists', leave=False):
            rl_id = rsc_list['id']
            status_ignore = [201, 204]
            logger.debug('API - Deleting Resource List')
            session.request("DELETE", f"/v1/resource_list/{rl_id}", status_ignore=status_ignore)
            delted += 1

    else:
        logger.info(f'No Resource Lists to delete for tenant: \'{session.tenant}\'')

    return deleted