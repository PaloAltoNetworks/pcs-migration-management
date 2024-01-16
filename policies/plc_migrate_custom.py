from sdk.color_print import c_print
from policies import plc_compare, plc_get, plc_add

def migrate_custom_policies(tenant_sessions: list, logger):
    '''
    Adds all custom policies from the source tenant that are missing from the clone tenants.
    This proccess cannot be completed without first migrating over all compliance standards.
    In the proccess of migrating policies, saved searched/rql queries will be migrated over
    as well since they are associated with policies.
    '''

    tenant_added_policies = []

    #Get all custom policies from all tenants
    tenant_custom_policies = []
    for tenant_session in tenant_sessions:
        tenant_custom_policies.append(plc_get.api_get_custom(tenant_session, logger))
    
    #Get delta from original tenant policies and clone tenant policies
    clone_tenant_policies_delta = plc_compare.compare_original_to_clones(tenant_sessions, tenant_custom_policies, logger)

    #Upload policies to clone tenants
    clone_tenant_sessions = tenant_sessions[1:]
    for index, policies in enumerate(clone_tenant_policies_delta):
        tenant_session = clone_tenant_sessions[index]
        added = plc_add.add_custom_policies(tenant_session, tenant_sessions[0], policies, logger)
        tenant_added_policies.append(added)

    logger.info('Finished migrating custom policies')

    return tenant_added_policies

if __name__ == '__main__':
    from sdk import load_config
    tenant_sessions = load_config.load_config_create_sessions()

    migrate_custom_policies(tenant_sessions)