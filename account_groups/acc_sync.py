from account_groups import acc_get, acc_compare, acc_add, acc_update, acc_delete
from sdk.color_print import c_print

def sync(tenant_sessions: list, addMode: bool, upMode: bool, delMode: bool, logger):
    '''
    Accepts a list of tenant sessions objects.

    Adds, Updates, and Deletes account group to sync changes accross all tenants supplied.
    '''

    added_account = []
    updated_account = []
    deleted_account = []

    #Get all account groups
    tenant_acc_grps = []
    for session in tenant_sessions:
        data = acc_get.get_account_groups(session, logger)
        tenant_acc_grps.append(data)

    src_acc_grps = tenant_acc_grps[0]
    cln_tenant_acc_grps = tenant_acc_grps[1:]

    if addMode:
        #Get account groups to add
        cln_tenant_acc_grps_to_add = []
        for cln_acc_grps in cln_tenant_acc_grps:
            acc_grps = acc_compare.compare_account_groups(src_acc_grps, cln_acc_grps)
            cln_tenant_acc_grps_to_add.append(acc_grps)

        #Add account groups
        for index, cln_acc_grps in enumerate(cln_tenant_acc_grps_to_add):
            session = tenant_sessions[index + 1]
            added = acc_add.add_account_groups(session, cln_acc_grps, logger)
            added_account.append(added)

    if upMode:
        #Get account groups to update
        cln_tenant_acc_grps_to_update = []
        for cln_acc_grps in cln_tenant_acc_grps:
            acc_grps = acc_compare.get_account_groups_to_update(src_acc_grps, cln_acc_grps)
            cln_tenant_acc_grps_to_update.append(acc_grps)

        for index, cln_acc_grps in enumerate(cln_tenant_acc_grps_to_update):
            session = tenant_sessions[index + 1]
            updated = acc_update.update_account_groups(session, cln_acc_grps, logger)
            updated_account.append(updated)

    if delMode:
        cln_tenant_acc_grps_to_delete = []
        for cln_acc_grps in cln_tenant_acc_grps:
            acc_grps = acc_compare.get_account_groups_to_delete(src_acc_grps, cln_acc_grps)
            cln_tenant_acc_grps_to_delete.append(acc_grps)

        for index, cln_acc_grps in enumerate(cln_tenant_acc_grps_to_delete):
            session = tenant_sessions[index + 1]
            deleted = acc_delete.delete_account_groups(session, cln_acc_grps, logger)
            deleted_account.append(deleted)
    else:
        for index in tenant_sessions[1:]:
            deleted_account.append(0)
        

    logger.info('Finished syncing Account Groups')

    return added_account, updated_account, deleted_account, {}

if __name__ =='__main__':
    from sdk.load_config import load_config_create_sessions

    tenant_session = load_config_create_sessions()

    sync(tenant_session, True, True, True)
    
