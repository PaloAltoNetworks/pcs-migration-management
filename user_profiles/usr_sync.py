from sdk.color_print import c_print
from user_profiles import usr_get, usr_add, usr_compare, usr_delete, usr_update

def sync(tenant_sessions: list, addMode: bool, upMode: bool, delMode: bool, logger):
    '''
    Accepts a list of tenant session objects.

    Adds Updates, and Deletes User Profiles from the clone tenants until they
    match the source tenant.
    '''

    added_profiles = []
    updated_profiles = []
    deleted_profiles = []

    #Get all user profiles
    tenant_user_profiles = []
    for session in tenant_sessions:
        data = usr_get.get_users(session, logger)
        tenant_user_profiles.append(data)

    #Get all roles for role ID translation
    tenant_user_roles = []
    for session in tenant_sessions:
        data = usr_get.get_user_roles(session, logger)
        tenant_user_roles.append(data)

    cln_tenant_user_roles = tenant_user_roles[1:]
    src_tenant_usr_profiles = tenant_user_profiles[0]
    cln_tenant_usr_profiles = tenant_user_profiles[1:]

    if addMode:
        #Comapre user profiles to add
        tenant_users_to_add = []
        for index in range(len(cln_tenant_usr_profiles)):
            users_to_add = usr_compare.compare_users(src_tenant_usr_profiles, cln_tenant_usr_profiles[index], cln_tenant_user_roles[index])
            tenant_users_to_add.append(users_to_add)

        #Add user profiles
        for index in range(len(tenant_users_to_add)):
            added = usr_add.add_users(tenant_sessions[index + 1], tenant_users_to_add[index], logger)
            added_profiles.append(added)
    
    if upMode:
        #Get User Profiles to update
        tenant_users_to_update = []
        for index in range(len(cln_tenant_usr_profiles)):
            users_to_update = usr_compare.get_users_to_update(src_tenant_usr_profiles, cln_tenant_usr_profiles[index], cln_tenant_user_roles[index])
            tenant_users_to_update.append(users_to_update)

            #Add user profiles
            for index, users in enumerate(tenant_users_to_update):
                updated = usr_update.update_user_profiles(tenant_sessions[index + 1], users, logger)
                updated_profiles.append(updated)

    
    if delMode:
        #Get user profiles to delete
        tenant_users_to_delete = []
        for index in range(len(cln_tenant_usr_profiles)):
            users_to_delete = usr_compare.get_users_to_delete(src_tenant_usr_profiles, cln_tenant_usr_profiles[index])
            tenant_users_to_delete.append(users_to_delete)

        #Delete user profiles
        for index, users in enumerate(tenant_users_to_delete):
            deleted = usr_delete.delete_user_profiles(tenant_sessions[index + 1], users, logger)
            deleted_profiles.append(deleted)
    else:
        for index in tenant_sessions[1:]:
            deleted_profiles.append(0)

    logger.info('Finished syncing User Profiles')

    return added_profiles, updated_profiles, deleted_profiles, {}
    
if __name__ =='__main__':
    from sdk.load_config import load_config_create_sessions

    tenant_sessions = load_config_create_sessions()

    sync(tenant_sessions, True, True, True)