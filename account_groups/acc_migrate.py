from account_groups import acc_get, acc_compare, acc_add
from sdk.color_print import c_print

def migrate(tenant_sessions: list, logger):
    '''
    Accepts a list of tenant sessions objects.

    Migrates all account groups from the first tenant, (source tenant)
    to all other tenants (clone tenants).
    '''

    tenant_groups_added = []

    #Get all account groups
    tenant_acc_grps = []
    for session in tenant_sessions:
        data = acc_get.get_account_groups(session, logger)
        tenant_acc_grps.append(data)

    #Get account groups to add
    cln_tenant_acc_grps_to_add = []
    src_acc_grps = tenant_acc_grps[0]
    cln_tenant_acc_grps = tenant_acc_grps[1:]
    for cln_acc_grps in cln_tenant_acc_grps:
        acc_grps = acc_compare.compare_account_groups(src_acc_grps, cln_acc_grps)
        cln_tenant_acc_grps_to_add.append(acc_grps)

    #Add account groups
    for index, cln_acc_groups in enumerate(cln_tenant_acc_grps_to_add):
        session = tenant_sessions[index + 1]
        added = acc_add.add_account_groups(session, cln_acc_groups, logger)
        tenant_groups_added.append(added)

    logger.info('Finished migrating Account Groups')

    return tenant_groups_added

if __name__ =='__main__':
    from sdk.load_config import load_config_create_sessions

    tenant_session = load_config_create_sessions()

    migrate(tenant_session)
    
