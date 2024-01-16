from resource_lists import rsc_get, rsc_compare, rsc_add
from sdk.color_print import c_print

def migrate(tenant_sessions: list, logger):
    '''
    Accepts a list of tenant session objects.
    
    Migrates all resource lists from the first tenant, (source tenant)
    to all other tenants (clone tenants).
    '''

    tenant_resource_added = []
    
    #Get all resource lists
    tenant_resource_lists = []
    for session in tenant_sessions:
        data = rsc_get.get_resource_lists(session, logger)
        tenant_resource_lists.append(data)

    #Get resource lists to add
    cln_tenant_rsc_lists_to_add = []
    src_tenant_rsc_lists = tenant_resource_lists[0]
    cln_tenant_rsc_lists = tenant_resource_lists[1:]
    for cln_rsc_lists in cln_tenant_rsc_lists:
        rsc_to_add = rsc_compare.compare_resource_lists(src_tenant_rsc_lists, cln_rsc_lists)
        cln_tenant_rsc_lists_to_add.append(rsc_to_add)

    #Add resource lists
    for index, cln_rsc_lists in enumerate(cln_tenant_rsc_lists_to_add):
        added = rsc_add.add_resource_lists(tenant_sessions[index + 1], cln_rsc_lists, logger)
        tenant_resource_added.append(added)

    logger.info('Finished migrateding Resource Lists')

    return tenant_resource_added




if __name__ =='__main__':
    from sdk.load_config import load_config_create_sessions

    tenant_sessions = load_config_create_sessions()
    
    migrate(tenant_sessions)