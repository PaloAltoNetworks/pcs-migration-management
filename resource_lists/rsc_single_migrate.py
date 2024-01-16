from resource_lists import rsc_get, rsc_add

def single_migrate(tenant_sessions, uuid, logger):
    resource_lists = rsc_get.get_resource_lists(tenant_sessions[0], logger)

    resource_list_to_add = {}

    for rsc_list in resource_lists:
        if rsc_list.get('id') == uuid:
            resource_list_to_add = rsc_list

    if resource_list_to_add:
        for session in tenant_sessions[1:]:
            rsc_add.add_resource_lists(session, [resource_list_to_add], logger)
    else:
        logger.warning(f'Could not find Resource List with UUID of \'{uuid}\'')