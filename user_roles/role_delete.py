from sdk.color_print import c_print
from tqdm import tqdm

def delete_roles(session, roles, logger):
    if roles:
        logger.info(f'Deleting User Roles from tenant: \'{session.tenant}\'')


        for role in tqdm(roles, desc='Deleting User Roles', leave=False):
            r_id = role['id']
            name = role['name']
            logger.debug(f'API - Deleting role {name}')
            session.request('DELETE', f'/user/role/{r_id}', json=role)

    else:
        logger.info(f'No User Roles to delete for tenant: \'{session.tenant}\'')
