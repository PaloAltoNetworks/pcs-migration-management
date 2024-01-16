from sdk import load_config, color_print
from policies import plc_get, plc_compare, plc_add, plc_update, plc_migrate_default, plc_delete

def sync(tenant_sessions: list, addMode: bool, upMode: bool, delMode: bool, logger):
    '''
    Adds, updates, and deletes policies from clone tenants until the clone tenants match the source tenant.
    '''

    added_policies = []
    updated_policies = []
    deleted_policies = []
    updated_default_policies = []

    #Get all custom policies from all tenants
    tenant_custom_policies = []
    for tenant_session in tenant_sessions:
        tenant_custom_policies.append(plc_get.api_get_custom(tenant_session, logger))
    
    clone_tenant_sessions = tenant_sessions[1:]

    if addMode:
        #Get policies to add
        #Get delta from original tenant policies and clone tenant policies
        policies_to_add = plc_compare.compare_original_to_clones(tenant_sessions, tenant_custom_policies, logger)

        #Upload policies to clone tenants
        for index, policies in enumerate(policies_to_add):
            tenant_session = clone_tenant_sessions[index]
            added = plc_add.add_custom_policies(tenant_session, tenant_sessions[0], policies, logger)
            added_policies.append(added)

    if upMode: 
        #Get policies to update
        policies_to_update = plc_compare.get_policies_to_update(tenant_sessions, tenant_custom_policies, logger)
        
        updated = 0
        #Update policies
        for index, policies in enumerate(policies_to_update):
            session = clone_tenant_sessions[index]
            updated = plc_update.update_custom_policies(session, tenant_sessions[0], policies, logger)
            updated_policies.append(updated)

    if delMode:
        #Get policies to delete
        policies_to_delete = plc_compare.get_policies_to_delete(tenant_custom_policies)

        deleted = 0
        #Delete polices
        for index, policies in enumerate(policies_to_delete):
            session = clone_tenant_sessions[index]
            deleted = plc_delete.delete_policies(session, policies, logger)
            deleted_policies.append(deleted)
    else:
        for index in tenant_custom_policies[1:]:
            deleted_policies.append(0)

    if upMode:
        #Sync default policy
        updated_default_policies = plc_migrate_default.migrate_builtin_policies(tenant_sessions, logger)

    logger.info('Finished syncing Policies')

    return added_policies, updated_policies, deleted_policies, updated_default_policies, {}

if __name__ == '__main__':
    tenant_sessions = load_config.load_config_create_sessions()

    sync(tenant_sessions, True, True, True)
