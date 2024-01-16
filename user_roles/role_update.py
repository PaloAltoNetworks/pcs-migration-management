from sdk.color_print import c_print
from user_roles import role_translate_id
from tqdm import tqdm

def update_roles(session, old_session, roles, logger):
    updated = 0

    if roles:
        logger.info(f'Updating User Roles for tenant: \'{session.tenant}\'')

        #Translate Acc Grp IDs
        logger.debug('API - Getting source account groups')
        src_acc_grps = old_session.request('GET', '/cloud/group').json()
        logger.debug('API - Getting destination account groups')
        dest_acc_grps = session.request('GET', '/cloud/group').json()

        #Translate Resource List IDs
        logger.debug('API - Getting source resource lists')
        src_rsc_lists = old_session.request('GET', '/v1/resource_list').json()
        logger.debug('API - Getting destination resource lists')
        dest_rsc_lists = session.request('GET', '/v1/resource_list').json()

        for role in tqdm(roles, desc='Updating User Roles', leave=False):
            #Translate Acc Grp IDs
            if 'accountGroupIds' in role:
                new_ids = []
                for index in range(len(role['accountGroupIds'])):
                    old_id = role['accountGroupIds'][index]
                    new_id = role_translate_id.translate_acc_grp_ids(old_id, dest_acc_grps, src_acc_grps)
                    new_ids.append(new_id)
                role.update(accountGroupIds=new_ids)

            #Translate resource List IDS
            if 'resourceListIds' in role:
                new_ids = []
                for index in range(len(role['resourceListIds'])):
                    old_id = role['resourceListIds'][index]
                    new_id = role_translate_id.translate_rsc_list_ids(old_id, dest_rsc_lists, src_rsc_lists)
                    new_ids.append(new_id)
                role.update(resourceListIds=new_ids)

            r_id = role['id']
            name = role['name']
            # print(role)
            
            logger.debug(f'API - Updating role {name}')
            session.request('PUT', f'/user/role/{r_id}', json=role)
            updated += 1

    else:
        logger.info(f'No User Roles to update for tenant: \'{session.tenant}\'')

    return updated 