def get_lists_to_add(trusted_lists: list):
    #Define lists
    original_tenant = trusted_lists[0]
    clone_tenants = trusted_lists[1:]

    #Compare the original tenant to the other clone tenants
    clone_tenant_lists_delta = []
    for tenant in clone_tenants:
        lists_delta = []
        for o_list in original_tenant:
            if o_list['name'] not in [t_list['name'] for t_list in tenant]:
                lists_delta.append(o_list)

        clone_tenant_lists_delta.append(lists_delta)

    return clone_tenant_lists_delta


def get_lists_to_update(trusted_lists):
    #Define lists
    source_tenant = trusted_lists[0]
    clone_tenants = trusted_lists[1:]

    #Compare the original tenant to the other clone tenants
    clone_tenant_lists_delta = []
    for cln_tenant in clone_tenants:
        lists_delta = []
        for src_list in source_tenant:
            for cln_list in cln_tenant:
                if cln_list['name'] == src_list['name']:
                    #compare attributes
                    if cln_list['description'] != src_list['description']:
                        #update the ID
                        src_list.update(id=cln_list['id'])
                        lists_delta.append(src_list)
                        break
                    if not compare_lists(cln_list['trustedListEntries'], src_list['trustedListEntries']):
                        #update the ID
                        src_list.update(id=cln_list['id'])
                        lists_delta.append(src_list)
                        break
                    if not compare_lists(cln_list['applicablePolicies'], src_list['applicablePolicies']):
                        #update the ID
                        src_list.update(id=cln_list['id'])
                        lists_delta.append(src_list)
                        break
                    pass

        clone_tenant_lists_delta.append(lists_delta)

    return clone_tenant_lists_delta

def get_lists_to_delete(trusted_lists):
    #Define lists
    original_tenant = trusted_lists[0]
    clone_tenants = trusted_lists[1:]

    #Compare the original tenant to the other clone tenants
    clone_tenant_lists_delta = []
    for tenant in clone_tenants:
        lists_delta = []
        for cln_list in tenant:
            if cln_list['name'] not in [t_list['name'] for t_list in original_tenant]:
                lists_delta.append(cln_list)

        clone_tenant_lists_delta.append(lists_delta)

    return clone_tenant_lists_delta

def compare_settings(network_settings_list):
    source_settings_dict = network_settings_list[0]
    clone_network_settings = network_settings_list[1:]

    tenant_settings_to_update = []
    for cln_settings_dict in clone_network_settings:
        settings_to_update = []
        cln_settings = cln_settings_dict.items()
        for cln_setting in cln_settings:
            src_settings = source_settings_dict.items()
            for src_setting in src_settings:
                if src_setting[1].get('policyName','-0') == cln_setting[1].get('policyName','-1'):
                    if src_setting[1].get('alertDisposition') != cln_setting[1].get('alertDisposition'):
                        settings_to_update.append(src_setting)
                        break
                    if 'trainingModelThreshold' in src_setting[1]:
                        if src_setting[1].get('trainingModelThreshold') != cln_setting[1].get('trainingModelThreshold'):
                            settings_to_update.append(src_setting)
                            break
                    
        tenant_settings_to_update.append(settings_to_update)

    return tenant_settings_to_update


def compare_lists(list1, list2) -> bool:
    for el1 in list1:
        found = False
        for el2 in list2:
            if el1 == el2:
                found = True
                break
        #if even one element is missing, the lists are not equal
        if found == False:
            return False

    return True
        
    
