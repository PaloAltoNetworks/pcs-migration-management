from sdk.color_print import c_print

def compare_added_roles(roles_list):
    #Define lists
    original_tenant = roles_list[0]
    clone_tenants = roles_list[1:]

    #Compare the original tenant to the other clone tenants
    clone_tenant_roles_delta = []
    for tenant in clone_tenants:
        roles_delta = []
        for o_role in original_tenant:
            if o_role['name'] not in [role['name'] for role in tenant]:
                roles_delta.append(o_role)

        clone_tenant_roles_delta.append(roles_delta)

    return clone_tenant_roles_delta


def compare_deleted_roles(roles_list):
    #Define lists
    original_tenant = roles_list[0]
    clone_tenants = roles_list[1:]

    #Compare the current tenant to the original tenant
    clone_tenant_roles_delta = []
    for tenant in clone_tenants:
        roles_delta = []
        for role in tenant:
            #If there is a role on the current tenant that does not exist on the 
            # source/original tenant, add it to the list of games that need to be deleted
            if role['name'] not in [o_role['name'] for o_role in original_tenant]:
                roles_delta.append(role)

        clone_tenant_roles_delta.append(roles_delta)

    return clone_tenant_roles_delta

def compare_each_role(roles_list, tenant_sessions=None):
    #Define lists
    original_tenant = roles_list[0]
    clone_tenants = roles_list[1:]

    #Compare the current tenant to the original tenant
    clone_tenant_roles_delta = []
    for index, tenant in enumerate(clone_tenants):
        roles_delta = []
        for cln_role in tenant:
            if cln_role['name'] in [o_role['name'] for o_role in original_tenant]:
                #Get the source role
                src_role = [o_role for o_role in original_tenant if o_role['name'] == cln_role['name']][0]

                acc_grps = [grp['name'] for grp in src_role.get('accountGroups')]
                acc_grps.sort()
                rsc_lists = [rsc['name'] for rsc in src_role.get('resourceLists')]
                rsc_lists.sort()
                src_data = {
                    'roleType': src_role.get('roleType'),
                    'accountGroup': acc_grps,
                    'resourceLists': rsc_lists
                }

                acc_grps = [grp['name'] for grp in cln_role.get('accountGroups')]
                acc_grps.sort()
                rsc_lists = [rsc['name'] for rsc in cln_role.get('resourceLists')]
                rsc_lists.sort()
                cln_data = {
                    'roleType': cln_role.get('roleType'),
                    'accountGroup': acc_grps,
                    'resourceLists': rsc_lists
                }

                #Add the role to the list if there is a difference
                if src_data != cln_data:
                    #update ID to the role id on the tenant
                    src_role.update(id=cln_role['id'])
                    roles_delta.append(src_role)

        clone_tenant_roles_delta.append(roles_delta)

    return clone_tenant_roles_delta


def name_change(role, original_tenant):
    role_desc = role['description']
    role_acc_grp_names = [grp['name'] for grp in role['accountGroups']]
    role_resource_names = [rsc['name'] for rsc in role['resourceLists']]
    role_permission = role['roleType']
    role_dismiss = role['restrictDismissalAccess']
    role_attributes = role['additionalAttributes']

    #If the only attribute that is different is the name, then it is likely the name changed

    for o_role in original_tenant:
        o_role_desc = o_role['description']
        o_role_acc_grp_names = [grp['name'] for grp in o_role['accountGroups']]
        o_role_resource_names = [rsc['name'] for rsc in o_role['resourceLists']]
        o_role_permission = o_role['roleType']
        o_role_dismiss = o_role['restrictDismissalAccess']
        o_role_attributes = role['additionalAttributes']

        if o_role_desc == role_desc and o_role_acc_grp_names == role_acc_grp_names and o_role_resource_names == role_resource_names and o_role_permission == role_permission and o_role_dismiss == role_dismiss and o_role_attributes == role_attributes:
            #Only difference is name, name change event.
            print('Found Name Change Event')
            print()
            return True, o_role['name']
    
    return False