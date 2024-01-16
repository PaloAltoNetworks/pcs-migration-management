from ip_allow_lists import ip_get, ip_add

#Used to migrate a single IP allow list based on its UUID
def single_migrate(tenant_sessions, uuid, logger):
    source_networks = ip_get.get_trusted_networks(tenant_sessions[0], logger)

    network_to_add = {}
    for network in source_networks:
        if network.get('uuid') == uuid:
            network_to_add = network

    if network_to_add:
        for session in tenant_sessions[1:]:
            ip_add.add_networks(session, [network_to_add], logger)
        pass
    else:
        logger.warning(f'Could not find Trusted IP Network with UUID \'{uuid}\'')