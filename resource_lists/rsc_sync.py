from resource_lists import rsc_get, rsc_compare, rsc_add, rsc_update, rsc_delete
import resource_lists
from sdk.color_print import c_print

def sync(tenant_sessions: list, addMode: bool, upMode: bool, delMode: bool, logger):
    '''
    Accepts a list of tenant session objects.
    
    Syncs resource lists by adding updating and deleting
    resource lists from the clone tenant.
    '''

    added_resource_lists = []
    updated_resource_lists = []
    deleted_resource_lists = []
    
    #Get all resource lists
    tenant_resource_lists = []
    for session in tenant_sessions:
        data = rsc_get.get_resource_lists(session, logger)
        tenant_resource_lists.append(data)

    src_rsc_lists = tenant_resource_lists[0]
    cln_tenant_rsc_lists = tenant_resource_lists[1:]

    if addMode:
        #Get resource lists to add
        cln_tenant_rsc_lists_to_add = []
        for cln_rsc_lists in cln_tenant_rsc_lists:
            rsc_to_add = rsc_compare.compare_resource_lists(src_rsc_lists, cln_rsc_lists)
            cln_tenant_rsc_lists_to_add.append(rsc_to_add)

        #Add resource lists
        for index, cln_rsc_lists in enumerate(cln_tenant_rsc_lists_to_add):
            added = rsc_add.add_resource_lists(tenant_sessions[index + 1], cln_rsc_lists, logger)
            added_resource_lists.append(added)
    
    if upMode:
        #Get resource lists to update
        cln_tenant_rsc_list_to_update = []
        for cln_rsc_lists in cln_tenant_rsc_lists:
            rsc_to_update = rsc_compare.get_resource_lists_to_update(src_rsc_lists, cln_rsc_lists)
            cln_tenant_rsc_list_to_update.append(rsc_to_update)
        
        #Update resource lists
        for index, rsc_lists in enumerate(cln_tenant_rsc_list_to_update):
            updated = rsc_update.update_resource_lists(tenant_sessions[index + 1], rsc_lists, logger)
            updated_resource_lists.append(updated)

    if delMode:
        #Get resource lists to delete
        cln_tenant_rsc_lists_to_delete = []
        for cln_rsc_lists in cln_tenant_rsc_lists:
            rsc_to_delete = rsc_compare.get_rsc_lists_to_delete(src_rsc_lists, cln_rsc_lists)
            cln_tenant_rsc_lists_to_delete.append(rsc_to_delete)
        
        #Delete resource lists
        for index, rsc_lists in enumerate(cln_tenant_rsc_lists_to_delete):
            deleted = rsc_delete.delete_resource_lists(tenant_sessions[index + 1], rsc_lists, logger)
            deleted_resource_lists.append(deleted)
    else:
        for index in tenant_sessions[1:]:
            deleted_resource_lists.append(0)

    logger.info('Finished migrateding Resource Lists')

    return added_resource_lists, updated_resource_lists, deleted_resource_lists, {}

if __name__ =='__main__':
    from sdk.load_config import load_config_create_sessions

    tenant_sessions = load_config_create_sessions()

    sync(tenant_sessions, True, True, True)
    