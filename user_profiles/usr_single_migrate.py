from user_profiles import usr_get, usr_add

def single_migrate(tenant_sessions, uuid, logger):
    profiles = usr_get.get_users(tenant_sessions[0], logger)

    profile_to_add = {}

    for usr in profiles:
       if usr.get('email') == uuid:
           profile_to_add = usr

    if profile_to_add:
        #translate roles
        tenant_user_roles = []
        for session in tenant_sessions:
            data = usr_get.get_user_roles(session, logger)
            tenant_user_roles.append(data)

        for ten_index, session in enumerate(tenant_sessions[1:]):
            clone_roles = tenant_user_roles[ten_index + 1]
            for index in range(len(profile_to_add['roles'])):
                cur_id = profile_to_add['roles'][index].get('id')
                for cln_role in clone_roles:
                    if profile_to_add['roles'][index].get('name') == cln_role.get('name'):
                        profile_to_add['roles'][index].update(id=cln_role.get('id'))
                        profile_to_add['roleIds'][index] = cln_role.get('id')
                        #Update Default Role
                        if profile_to_add['defaultRoleId'] == cur_id:
                            profile_to_add.update(defaultRoleId=cln_role.get('id'))
            
            usr_add.add_users(session, [profile_to_add], logger)
    else:
        logger.warning(f'Could not find User Profile with email \'{uuid}\'')