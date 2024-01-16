from sdk.color_print import c_print
from user_profiles import usr_get, usr_add, usr_compare

def migrate(tenant_sessions: list, logger: object):
    '''
    Accepts a list of tenant session objects.

    Migrates all the User Profiles from the source tenant to the
    clone tenants
    '''

    tenant_users_added = []

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

    #Comapre user profiles
    tenant_users_to_add = []
    cln_tenant_user_roles = tenant_user_roles[1:]
    src_tenant_usr_profiles = tenant_user_profiles[0]
    cln_tenant_usr_profiles = tenant_user_profiles[1:]
    for index in range(len(cln_tenant_usr_profiles)):
        users_to_add = usr_compare.compare_users(src_tenant_usr_profiles, cln_tenant_usr_profiles[index], cln_tenant_user_roles[index])
        tenant_users_to_add.append(users_to_add)

    #Add user profiles
    for index in range(len(tenant_users_to_add)):
        added = usr_add.add_users(tenant_sessions[index + 1], tenant_users_to_add[index], logger)
        tenant_users_added.append(added)

    logger.info('Finished migrating User Profiles')

    return tenant_users_added
    
if __name__ =='__main__':
    from sdk.load_config import load_config_create_sessions

    tenant_sessions = load_config_create_sessions()

    migrate(tenant_sessions)