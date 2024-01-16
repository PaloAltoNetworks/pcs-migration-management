import json

#Get info from all tenants
#Relate UUIDs from each tenant to a UUID from an other tenant

#Source tenant UUID
#Tenant Name
#Returns the related UUID if it exists

def create_cloud_account_matrix():
    pass

def update_cloud_account_matrix():
    pass


def create_update_account_groups_matrix(tenants_data, tenant_sessions):
    matrix = {}

    try:
        with open('translation_matrix/account_groups_matrix.json', 'r') as f:
            matrix = json.load(f)
    except:
        matrix = {}

    source_data = tenants_data[0]
    source_tenant = tenant_sessions[0]
    
    clone_tenant_data = tenants_data[1:]
    clone_tenant_sessions = tenant_sessions[1:]

    for i in range(len(clone_tenant_data)):
        clone_data =  clone_tenant_data[i]
        clone_session = clone_tenant_sessions[i]

        for cln_element in clone_data:
            if cln_element.get('id'):
                for src_element in source_data:
                    if src_element.get('id'):
                        if src_element['name'] == cln_element['name']:
                            #Create relation between these elements
                            old_val = matrix.get(src_element.get('id'), {})
                            old_val.update({clone_session.tenant: cln_element.get('id')})
                            matrix.update({src_element.get('id'): old_val})

    with open('translation_matrix/account_groups_matrix.json', 'w') as f:
        json.dump(matrix, f)

def update_account_groups_matrix():
    pass


def create_resource_lists_matrix():
    pass

def update_resource_lists_matrix():
    pass


def create_user_roles_matrix():
    pass

def update_user_roles_matrix():
    pass


def create_user_profiles_matrix():
    pass

def update_user_profiles_matrix():
    pass


def create_trusted_ips_matrix():
    pass

def update_trusted_ips_matrix():
    pass


def create_saved_searches_matrix():
    pass

def update_saved_searches_matrix():
    pass


def create_compliance_data_matrix():
    pass

def update_compliance_data_matrix():
    pass


def create_policies_matrix():
    pass

def update_policies_matrix():
    pass


def create_alert_rules_matrix():
    pass

def update_alert_rules_matrix():
    pass


def create_anomaly_settings_matrix():
    pass

def update_anomaly_settings_matrix():
    pass

# data = {
#     'sourceUUID': {
#         'tenantName': 'relatedUUID'
#     }
# }
