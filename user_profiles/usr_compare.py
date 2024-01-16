#compares the tenants to find the missing user/s
def compare_users(source_users: list, clone_users: list, clone_roles: list):
    users_to_add = []
    for src_usr in source_users:
        # check whether if the key 'email' values are in both src_user and dst_user
        if src_usr['email'] not in [cln_user['email'] for cln_user in clone_users]:
            
            #Translate the UUIDs of the roles
            for index in range(len(src_usr['roles'])):
                cur_id = src_usr['roles'][index].get('id')
                for cln_role in clone_roles:
                    if src_usr['roles'][index].get('name') == cln_role.get('name'):
                        src_usr['roles'][index].update(id=cln_role.get('id'))
                        src_usr['roleIds'][index] = cln_role.get('id')
                        
                        #Update Default Role
                        if src_usr['defaultRoleId'] == cur_id:
                            src_usr.update(defaultRoleId=cln_role.get('id'))

            users_to_add.append(src_usr)

    return users_to_add


def get_users_to_update(source_users: list, clone_users: list, clone_roles: list):
    '''
    Accepts a source tenant user list, a clone tenant user list, and a roles list from that same clone tenant.

    Returns a list of user profiles that need to be updated with properly translated role IDs.
    '''

    users_to_update = []
    for src_usr in source_users:
        for cln_usr in clone_users:
            if src_usr['email'] == cln_usr['email']:
                #Get default role name
                src_def_name = ''
                src_def_role_id = src_usr.get('defaultRoleId')
                src_def_role_name = [role['name'] for role in src_usr['roles'] if role['id'] == src_def_role_id]
                if src_def_role_name:
                    src_def_name = src_def_role_name[0]

                #Get role names and sort
                src_role_names = [role['name'] for role in src_usr.get('roles')]
                src_role_names.sort()

                src_data = {
                    'firstName': src_usr['firstName'],
                    'lastName': src_usr['lastName'],
                    'timeZone': src_usr['timeZone'],
                    'enabled': src_usr['enabled'],
                    'roles': src_role_names,
                    'defaultRole': src_def_name
                }

                #Get default role name
                cln_def_name = ''
                cln_def_role_id = cln_usr.get('defaultRoleId')
                cln_def_role_name = [role['name'] for role in cln_usr['roles'] if role['id'] == cln_def_role_id]
                if cln_def_role_name:
                    cln_def_name = cln_def_role_name[0]

                #Get Role names and sort    
                cln_role_names = [role['name'] for role in cln_usr.get('roles')]
                cln_role_names.sort()
                cln_data = {
                    'firstName': cln_usr['firstName'],
                    'lastName': cln_usr['lastName'],
                    'timeZone': cln_usr['timeZone'],
                    'enabled': cln_usr['enabled'],
                    'roles': cln_role_names,
                    'defaultRole': cln_def_name
                }

                if src_data != cln_data:
                    #Translate the Default Role
                    def_role_id = src_usr.get('defaultRoleId')
                    def_role_name = [role['name'] for role in src_usr['roles'] if role['id'] == def_role_id]
                    if def_role_name:
                        name = def_role_name[0]
                        new_def_role_id = [role['id'] for role in clone_roles if role['name'] == name]
                        if new_def_role_id:
                            src_usr.update(defaultRoleId=new_def_role_id[0])

                    #Translate role IDs
                    new_role_ids = []
                    for name in src_role_names:
                        cln_role_id = [role['id'] for role in clone_roles if role['name'] == name]
                        if cln_role_id:
                            new_role_ids.append(cln_role_id[0])

                    src_usr.update(roleIds=new_role_ids)

                    #Add user to list
                    users_to_update.append(src_usr)

    return users_to_update


def get_users_to_delete(source_users: list, clone_users: list):
    '''
    Accepts a list of source tenant user profiles and a clone tenant user profiles.

    Returns the list of user profiles found in the clone tenant not found in the source tenant.
    '''
    
    user_to_delete = []
    for cln_usr in clone_users:
        if cln_usr['email'] not in [src_usr['email'] for src_usr in source_users]:
            user_to_delete.append(cln_usr)

    return user_to_delete

