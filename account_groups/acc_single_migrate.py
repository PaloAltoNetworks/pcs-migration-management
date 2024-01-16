from account_groups import acc_get, acc_add

#Used to migrate a single account group based on its UUID
def single_migrate(tenant_sessions, uuid, logger):
    account_groups = acc_get.get_account_groups(tenant_sessions[0], logger)

    acc_to_add = {}
    for acc in account_groups:
        if acc.get('id') == uuid:
            acc_to_add = acc

    if acc_to_add:
        for session in tenant_sessions[1:]:
            acc_add.add_account_groups(session, [acc_to_add], logger)
    else:
        logger.warning(f'Could not find Account Group with UUID \'{uuid}\'')