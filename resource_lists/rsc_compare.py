import resource_lists


def compare_resource_lists(source_resource_lists: list, clone_resource_lists: list):
    '''
    Compare the resource lists between the source tenants and a clone tenant.

    Returns a list of the resource lists that are missing from the clone tenant.
    '''
    
    resource_lists_to_add = []
    for src_rsc in source_resource_lists:
        if src_rsc['name'] not in [cln_rsc['name'] for cln_rsc in clone_resource_lists]:
            resource_lists_to_add.append(src_rsc)

    return resource_lists_to_add


def get_resource_lists_to_update(source_resource_lists: list, clone_resource_lists: list):
    '''
    Compares the resource lists between the source tenant and a clone tenant.

    Returns a list of the resource lists that need to be updated.
    '''
    resource_lists_to_update = []
    for src_list in source_resource_lists:
        for cln_list in clone_resource_lists:
            if src_list['name'] == cln_list['name']:
                src_data = {
                    'description': src_list.get('description', ''),
                    'members': src_list.get('members', [])
                }
                cln_data = {
                    'description': cln_list.get('description', ''),
                    'members': cln_list.get('members', [])
                }

                if src_data != cln_data:
                    src_list.update(id=cln_list.get('id'))
                    resource_lists_to_update.append(src_list)

    return resource_lists_to_update

def get_rsc_lists_to_delete(source_resource_lists, clone_resource_lists):
    '''
    Returns a list of resource lists found in the clone tenant that are not found 
    in the source tenant.
    '''
    resource_lists_to_delete = []
    for cln_rsc in clone_resource_lists:
        if cln_rsc['name'] not in [src_rsc['name'] for src_rsc in source_resource_lists]:
            resource_lists_to_delete.append(cln_rsc)

    return resource_lists_to_delete