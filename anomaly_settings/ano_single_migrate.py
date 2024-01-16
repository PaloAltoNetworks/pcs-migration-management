from anomaly_settings import ano_get, ano_update

#Used to migrate a single anomaly setting based on its ID
def single_migrate(tenant_sessions, uuid, logger):
    #Network section===========================================================
    src_network_settings = ano_get.get_all_network_settings(tenant_sessions[0], logger)
    src_network_settings_structured = src_network_settings.items()

    network_to_update = tuple()

    for network in src_network_settings_structured:
        if network[0] == uuid:
            network_to_update = network
            break
    
    if network_to_update:
        for session in tenant_sessions[1:]:
            ano_update.update_setting(session, network_to_update[0], network_to_update[1], logger)
        return


    #UEBA section==============================================================
    src_ueba_settings = ano_get.get_all_ueba_settings(tenant_sessions[0], logger)
    src_ueba_settings_structured = src_ueba_settings.items()

    ueba_to_update = tuple()

    for ueba in src_ueba_settings_structured:
        if ueba[0] == uuid:
            ueba_to_update = ueba
            break

    if ueba_to_update:
        for session in tenant_sessions[1:]:
            ano_update.update_setting(session, ueba_to_update[0], ueba_to_update[1], logger)
        return

    


    #Trusted Lists=============================================================
    src_trusted_lists = ano_get.get_trusted_lists(tenant_sessions[0], logger)

    trusted_to_add = {}

    for trusted in src_trusted_lists:
        if trusted.get('id') == uuid:
            trusted_to_add = trusted
            break

    if trusted_to_add:
        for session in tenant_sessions[1:]:
            ano_update.add_trusted_list(session, trusted_to_add, logger)

        return

    
    logger.info(f'Could not find Anomaly Setting with UUID of \'{uuid}\'')


