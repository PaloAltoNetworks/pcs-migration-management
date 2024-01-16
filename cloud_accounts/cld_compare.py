def get_accounts_to_update(src_accounts: list, cln_accounts: list, src_session: object, cln_session: object, logger:object):
    '''
    Loops through the given cloud accounts and compares elements based on the type of the cloud account.
    Returns a list of the cloud accouts that have different attributes accross each tenant.
    '''
    #Get account groups from both tenants to translate accountGroup IDs

    res = src_session.request('GET', '/cloud/group')
    data = res.json()
    src_group_data = data

    res = cln_session.request('GET', '/cloud/group')
    data = res.json()
    cln_group_data = data

    accounts_to_update = []
    for index, src_acc in enumerate(src_accounts):
        for index, cln_acc in enumerate(cln_accounts):
            #This function compares the full dictionary of each cloud account.
            #Since the cloud accounts store variables in different locations,
            #it takes extra work to get the id and cloud type
            if 'cloudAccount' in src_acc:
                #Set variables
                src_acc_type = src_acc['cloudAccount']['cloudType']
                src_acc_id = src_acc['cloudAccount']['accountId']
            else:
                #Set variables
                src_acc_type = src_acc['cloudType']
                src_acc_id = src_acc['accountId']

            if 'cloudAccount' in cln_acc:
                #Set variables
                cln_acc_type = cln_acc['cloudAccount']['cloudType']
                cln_acc_id = cln_acc['cloudAccount']['accountId']
            else:
                #Set variables
                cln_acc_type = cln_acc['cloudType']
                cln_acc_id = cln_acc['accountId']
            
            #Only compare the same cloud account to itself accross tenants
            if cln_acc_id == src_acc_id:
                #Compare each attribute
                cln_attributes = {}
                src_attributes = {}
                
                #Compare attributes  based on cloud type                
                if src_acc_type == 'aws':
                    cln_attributes = get_aws_attributes(cln_acc, cln_group_data)
                    src_attributes = get_aws_attributes(src_acc, src_group_data)
                elif cln_acc_type == 'azure':#==============================================================================
                   cln_attributes = get_azure_attributes(cln_acc, cln_group_data)
                   src_attributes = get_azure_attributes(src_acc, src_group_data)
                elif cln_acc_type == 'gcp':#==================================================================================
                    cln_attributes = get_gcp_attributes(cln_acc, cln_group_data)
                    src_attributes = get_gcp_attributes(src_acc, src_group_data)
                elif cln_acc_type == 'alibaba_cloud':#==========================================================================
                    cln_attributes = get_alibaba_attributes(cln_acc, cln_group_data)
                    src_attributes = get_alibaba_attributes(src_acc, src_group_data)
                else:
                    pass
                    
                if cln_attributes != src_attributes:
                    acc = translate_g_ids(src_acc, src_group_data, cln_group_data)
                    accounts_to_update.append(acc)

    return accounts_to_update

#==============================================================================
def translate_g_ids(account, src_group_data, cln_group_data):
    '''
    A Helper functions for translating Account Group IDs since they are differenet accross each
    tenant.
    '''
    groupIds = []
    src_acc_ids = []
    if 'cloudAccount' in account:    
        src_acc_ids = account['cloudAccount']['groupIds']
    else:
        src_acc_ids = account['groupIds']

    for src_grp_id in src_acc_ids:
        if src_grp_id in [el['id'] for el in src_group_data]:
            src_name = [el['name'] for el in src_group_data if el['id'] == src_grp_id][0]
            if src_name in [el['name'] for el in cln_group_data]:
                cln_id = [el['id'] for el in cln_group_data if el['name'] == src_name][0]
                groupIds.append(cln_id)

    if 'cloudAccount' in account:    
        account['cloudAccount'].update(groupIds=groupIds)
    else:
        account.update(groupIds=groupIds)

    return account

#==============================================================================
def get_aws_attributes(account, t_group_data):
    '''
    A Helper function that gets the attributes of an aws account
    that need to be synced accross tenants
    '''
    group_names = []
    for grp in t_group_data:
        if grp['id'] in account['groupIds']:
            group_names.append(grp['name'])
    group_names.sort()
    
    attributes = {
        'cloudType': account['cloudType'],
        'groupIds': group_names,
        'enabled': account['enabled'],
        'externalId': account['externalId'],
        'roleArn': account['roleArn'],
        'storageScanEnabled': account['storageScanEnabled'],
        'storageScanConfig': account.get('storageScanConfig', {}),
        'name': account['name'],
        'ingestionMode': account['ingestionMode'],
        'accountId': account['accountId']
    }
        
    return attributes

#==============================================================================
def get_azure_attributes(account, t_group_data):
    '''
    A helper function that gets the attributes of an azure account
    that need to be synced accross tenants.
    '''
    group_names = []
    for grp in t_group_data:
        if grp['id'] in account['cloudAccount']['groupIds']:
            group_names.append(grp['name'])
    group_names.sort()

    attributes = {
        'flowLogStorageBucket': account['flowLogStorageBucket'],
        'dataflowEnabledProject': account['dataflowEnabledProject'],
        'cloudAccount': {
            'cloudType': account['cloudAccount']['cloudType'],
            'name': account['cloudAccount']['name'],
            'storageScanEnabled': account['cloudAccount'].get('storageScanEnabled', False),
            'groupIds': group_names,
            'enabled': account['cloudAccount']['enabled'],
            'ingestionMode': account['cloudAccount']['ingestionMode'],
            'accountId': account['cloudAccount']['accountId']
        }
    }

    return attributes

#==============================================================================
def get_gcp_attributes(account, t_group_data):
    '''
    A helper functions that gets the attributes of a gcp account
    that need to be synced accross tenants
    '''
    group_names = []
    for g_id in account['cloudAccount']['groupIds']:
        if g_id in [el['id'] for el in t_group_data]:
            grp_name = [el['name'] for el in t_group_data if el['id'] == g_id]
            group_names.append(grp_name)
    
    group_names.sort()

    #FlowLog is sometimes '' and sometimes None
    if account['flowLogStorageBucket'] == None:
        account.update(flowLogStorageBucket='')

    attributes = {
        'flowLogStorageBucket': account['flowLogStorageBucket'],
        'compressionEnabled': account['compressionEnabled'],
        'dataflowEnabledProject': account['dataflowEnabledProject'],
        'cloudAccount': {
            'cloudType': account['cloudAccount']['cloudType'],
            'enabled': account['cloudAccount']['enabled'],
            'ingestionMode': account['cloudAccount']['ingestionMode'],
            'name': account['cloudAccount']['name'],
            'storageScanEnabled': account['cloudAccount']['storageScanEnabled'],
            'groupIds': group_names,
            'accountId': account['cloudAccount']['accountId']
        }
    }

    return attributes

#==============================================================================
def get_alibaba_attributes(account, t_group_data):
    '''
    A helper function that gets the attributes of an alibaba account
    that need to be synced accross tenants
    '''
    group_names = []
    for grp in t_group_data:
        if grp['id'] in account['groupIds']:
            group_names.append(grp['name'])
    group_names.sort()
    
    attributes = {
        'cloudType': account['cloudType'],
        'groupIds': group_names,
        'enabled': account['enabled'],
        'externalId': account['externalId'],
        'storageScanEnabled': account['storageScanEnabled'],
        'storageScanConfig': account['storageScanConfig'],
        'name': account['name'],
        'ingestionMode': account['ingestionMode'],
        'ramArn': account['ramArn'],
        'accountId': account['accountId']
    }

    return attributes

def get_oci_attributes(account):
    attributes = {}
    return attributes

#==============================================================================
def get_accounts_to_delete(src_accounts, cln_accounts):
    '''
    Loops through the cloud accounts lists and if there is a cloud account
    on a cln tenant that is not on the source tenant, it is added to the list
    of accounts that need to be delted.
    '''
    accounts_to_delete = []
    src_acc_ids = []
    for acc in src_accounts:
        if 'cloudAccount' in acc:
            src_acc_ids.append(acc['cloudAccount']['accountId'])
        else:
            src_acc_ids.append(acc['accountId'])
    
    for cln_acc in cln_accounts:
        cln_acc_id = ''
        if 'cloudAccount' in cln_acc:
            cln_acc_id = cln_acc['cloudAccount']['accountId']
        else:
            cln_acc_id = cln_acc['accountId']

        if cln_acc_id not in src_acc_ids:
            accounts_to_delete.append(cln_acc)

    return accounts_to_delete

#==============================================================================
def get_accounts_to_add(tenant_sessions: object, cloud_accounts: list, logger:object) -> list:
    '''
    Returns a list of the cloud accounts that need to be added to each tenant.
    The first element in the list is the tenant where cloud accounts are
    being moved from. The other elemtents in the list are the tenants where
    the cloud accounts are being migrated too.

    Keyward Arguments:
    cloud_accounts -- List of cloud accounts from the names API for each tenant. Needs at least 2 tenants.

    Returns:
    List of clone tenants and the cloud accounts that need to be added to each one.
    '''
    
    original_tenant = cloud_accounts[0]
    clone_tenants = cloud_accounts[1:]

    #Compare the original tenant to the other clone tenants
    clone_tenants_cloud_accounts_delta = []
    for tenant in clone_tenants:
        cloud_accounts_delta = []
        for o_cloud_account in original_tenant:
            if o_cloud_account['id'] not in [cloud_account['id'] for cloud_account in tenant]:
                cloud_accounts_delta.append(o_cloud_account)
        clone_tenants_cloud_accounts_delta.append(cloud_accounts_delta)

    #Logging output
    for enum in enumerate(clone_tenants_cloud_accounts_delta):
        logger.info(f'Found {len(enum[1])} cloud accounts missing from tenant: {tenant_sessions[enum[0]+1].tenant}.')

    return clone_tenants_cloud_accounts_delta

#==============================================================================
def compare_each_account(src_tenant_acc, dst_tenant_acc):
    accounts_to_update = []
    for index, dst_account in enumerate(dst_tenant_acc):
        for index, src_account in enumerate(src_tenant_acc):
            #This function compares the full dictionary of each cloud account.
            #Since the cloud accounts store variables in different locations,
            #it takes extra work to get the id and cloud type
            if 'cloudAccount' in dst_account:
                #Set variables
                dst_account_type = dst_account['cloudAccount']['cloudType']
                dst_account_id = dst_account['cloudAccount']['accountId']
            else:
                #Set variables
                dst_account_type = dst_account['cloudType']
                dst_account_id = dst_account['accountId']

            if 'cloudAccount' in src_account:
                #Set variables
                src_account_type = src_account['cloudAccount']['cloudType']
                src_account_id = src_account['cloudAccount']['accountId']
            else:
                #Set variables
                src_account_type = src_account['cloudType']
                src_account_id = src_account['accountId']
            
            if dst_account_id == src_account_id:
                #Compare each attribute
                dst_attributes = {}
                src_attributes = {}
                
                #Compare attributes  based on cloud type                
                if dst_account_type == 'aws':#==============================================================================
                    #Destination
                    dst_accountGroupInfos = dst_account['accountGroupInfos']#The ids will always be different
                    for el in dst_accountGroupInfos:
                        el.pop('id')
                    dst_attributes = {
                        'enabled': dst_account['enabled']#,
                        # 'accountGroupInfos': dst_accountGroupInfos,
                        # 'name': dst_account['name'],
                        #ROLE ARN
                        #External ID
                    }
                    
                    #Source
                    src_accountGroupInfos = src_account['accountGroupInfos']#The ids will always be different
                    for el in src_accountGroupInfos:
                        el.pop('id')
                    src_attributes = {
                        'enabled': src_account['enabled']#,
                        # 'accountGroupInfos': src_accountGroupInfos,
                        # 'name': dst_account['name'],
                        # 'storageScanEnabled': dst_account['storageScanEnabled'],
                        # 'protectionMode': dst_account['protectionMode']
                    }
                elif dst_account_type == 'azure':#==============================================================================
                    #Destination
                    dst_accountGroupInfos = dst_account['cloudAccount']['accountGroupInfos']#The ids will always be different
                    for el in dst_accountGroupInfos:
                        el.pop('id')
                    
                    dst_attributes = {
                        'enabled': dst_account['enabled']#,
                        # 'accountGroupInfos': dst_accountGroupInfos
                    }

                    #Source
                    src_accountGroupInfos = src_account['cloudAccount']['accountGroupInfos']#The ids will always be different
                    for el in src_accountGroupInfos:
                        el.pop('id')
                    src_attributes = {
                        'enabled': src_account['enabled']#,
                        #'accountGroupInfos': src_accountGroupInfos
                    }

                elif dst_account_type == 'gcp':#==================================================================================
                    #Destination
                    dst_accountGroupInfos = dst_account['cloudAccount']['accountGroupInfos']#The ids will always be different
                    for el in dst_accountGroupInfos:
                        el.pop('id')
                    
                    dst_attributes = {
                        'enabled': dst_account['enabled']#,
                        #'accountGroupInfos': dst_accountGroupInfos
                    }

                    #Source
                    src_accountGroupInfos = src_account['cloudAccount']['accountGroupInfos']#The ids will always be different
                    for el in src_accountGroupInfos:
                        el.pop('id')
                    src_attributes = {
                        'enabled': src_account['enabled']#,
                        #'accountGroupInfos': src_accountGroupInfos
                    }
                elif dst_account_type == 'alibaba_cloud':#==========================================================================
                    #Destination
                    dst_accountGroupInfos = dst_account['accountGroupInfos']#The ids will always be different
                    for el in dst_accountGroupInfos:
                        el.pop('id')
                    dst_attributes = {
                        'enabled': dst_account['enabled']#,
                        #'accountGroupInfos': dst_accountGroupInfos
                    }
                    
                    #Source
                    src_accountGroupInfos = src_account['accountGroupInfos']#The ids will always be different
                    for el in src_accountGroupInfos:
                        el.pop('id')
                    src_attributes = {
                        'enabled': src_account['enabled']#,
                        #'accountGroupInfos': src_accountGroupInfos
                    }
                else:
                    pass
                    
            if dst_attributes != src_attributes:
                accounts_to_update.append(src_account)

    return accounts_to_update