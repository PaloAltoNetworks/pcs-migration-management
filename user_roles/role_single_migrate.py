from user_roles import role_get, role_add

def single_migrate(tenant_sessions, uuid, logger):
    roles = role_get.get_roles(tenant_sessions[0], logger)

    role_to_add = {}
    for role in roles:
        if role.get('id') == uuid:
            role_to_add = role
    
    if role_to_add:
        for session in tenant_sessions[1:]:
            role_add.add_roles(session, tenant_sessions[0], [role_to_add], logger)
    else:
        logger.warning(f'Could not find User Role with UUID of \'{uuid}\'')