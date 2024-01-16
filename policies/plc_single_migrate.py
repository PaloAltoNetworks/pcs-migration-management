from policies import plc_get, plc_update, plc_add

def single_migrate(tenant_sessions, uuid, logger):
    src_plcs = plc_get.api_get_custom(tenant_sessions[0], logger)

    plc_to_add = {}
        
    for plc in src_plcs:
        if plc.get('policyId') == uuid:
            plc_to_add = plc
    
    if plc_to_add:
        for session in tenant_sessions[1:]:
            plc_add.add_custom_policies(session, tenant_sessions[0], [plc_to_add], logger)
    else:
        logger.info(f'Could not find Custom Policy with UUID of \'{uuid}\'')