from sdk.color_print import c_print
from user_roles import role_translate_id
from tqdm import tqdm

def add_roles(session, old_session, roles, logger):
    added = 0

    tenant_name = session.tenant
    if roles:
        logger.info(f'Adding User Roles to tenant: \'{tenant_name}\'')

        #Translate Acc Grp IDs
        logger.debug('API - Getting source Account Groups')
        src_acc_grps = old_session.request('GET', '/cloud/group').json()
        logger.debug('API - Getting destination Account Groups')
        dest_acc_grps = session.request('GET', '/cloud/group').json()

        #Translate Resource List IDs
        logger.debug('API - Getting source Resource Lists')
        src_rsc_lists = old_session.request('GET', '/v1/resource_list').json()
        logger.debug('API - Getting destination Resource Lists')
        dest_rsc_lists = session.request('GET', '/v1/resource_list').json()

        for role in tqdm(roles, desc='Adding User Roles', leave=False):
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

            name = role['name']
            logger.debug(f'API - Adding role: {name}')
            res = session.request('POST', '/user/role', json=role)
            if res.status_code == 200 or res.status_code == 201:
                added += 1

    else:
        logger.info(f'No User Roles to add for tenant: \'{tenant_name}\'')

    return added