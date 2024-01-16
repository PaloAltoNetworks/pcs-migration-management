from cloud_accounts import cld_get, cld_add, cld_keys

#Used to migrate a single cloud account based on its ID
def single_migrate(tenant_sessions, uuid, logger):
    account_to_migrate = {}
    cld_account_names = cld_get.get_names(tenant_sessions[0], logger)

    for cld in cld_account_names:
        if cld.get('id') == uuid:
            account_to_migrate = cld
    
    if account_to_migrate:
        pass
        account_to_migrate = cld_get.get_all_info(tenant_sessions[0], account_to_migrate, logger)
        azure_account_keys = cld_keys.get_azure_credentials([account_to_migrate], logger)
        gcp_account_keys = cld_keys.get_gcp_credentials([account_to_migrate], logger)
        for session in tenant_sessions[1:]:
            cld_add.add_accounts(session, [account_to_migrate], azure_account_keys, gcp_account_keys, logger)
    else:
        logger.warning(f'Could not find Cloud Account with ID of \'{uuid}\'')