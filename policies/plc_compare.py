def compare_original_to_clones(tenant_sessions: list, policies_list: list, logger) -> list:
    '''
    Returns a list of the policies that need to be added to each tenant.
    The first element in the list is the tenant where policies are
    being moved from. The other elemtents in the list are the tenants where
    the policies are being migrated too.

    Keyward Arguments:
    tenant_sessions -- List of tenant sessions to pull tenant names from


    Returns:
    List of clone tenants and the cloud accounts that need to be added to each one.
    '''
    #Define lists
    original_tenant = policies_list[0]
    clone_tenants = policies_list[1:]

    #Compare the original tenant to the other clone tenants
    clone_tenants_policies_delta = []
    for tenant in clone_tenants:
        policies_delta = []
        for o_policy in original_tenant:
            if o_policy['name'] not in [policy['name'] for policy in tenant]:
                policies_delta.append(o_policy)
        clone_tenants_policies_delta.append(policies_delta)

    #Logging output
    for index, policies in enumerate(clone_tenants_policies_delta):
        logger.info(f'Found {len(policies)} policies missing from tenant: {tenant_sessions[index+1].tenant}.')

    return clone_tenants_policies_delta

def get_policies_to_update(tenant_sessions: list, policies_list: list, logger) -> list:
    source_tenant = policies_list[0]
    clone_tenants = policies_list[1:]
    src_session = tenant_sessions[0]
    clone_sessions = tenant_sessions[1:]

    #Get src saved searches for criteria lookup
    logger.debug('API - Getting source saved search for criteria lookup')
    src_saved_search = src_session.request('GET', '/search/history', params={"filter":"saved"}).json()

    tenants_to_update = []
    for index, cln_tenant in enumerate(clone_tenants):
        #Get cln saved searches for critera lookup
        cln_session = clone_sessions[index]
        logger.debug('API - Getting clone saved search for criteria lookup')
        cln_saved_search = cln_session.request('GET', '/search/history', params={"filter":"saved"}).json()

        policies_to_update = []
        for src_policy in source_tenant:
            for cln_policy in cln_tenant:
                if src_policy['name'] == cln_policy['name']:
                    #Compare policy subtypes---------------------------------------
                    if src_policy['policySubTypes'].sort() != cln_policy['policySubTypes'].sort():
                        src_policy.update(policyId=cln_policy['policyId'])
                        policies_to_update.append(src_policy)
                        break

                    #Compare description-------------------------------------------
                    if src_policy['description'] != cln_policy['description']:
                        src_policy.update(policyId=cln_policy['policyId'])
                        policies_to_update.append(src_policy)
                        break

                    #Compare severity
                    if src_policy['severity'] != cln_policy['severity']:
                        src_policy.update(policyId=cln_policy['policyId'])
                        policies_to_update.append(src_policy)
                        break

                    #Compare rule--------------------------------------------------
                    #Comapre run rule
                    if 'criteria' in src_policy['rule']:
                        if 'criteria' in cln_policy['rule']:
                            if src_policy['rule']['criteria'] != cln_policy['rule']['criteria']:
                                #lookup compare criteria
                                if compare_criteria(src_saved_search, cln_saved_search, src_policy['rule']['criteria'], cln_policy['rule']['criteria']):
                                    src_policy.update(policyId=cln_policy['policyId'])
                                    policies_to_update.append(src_policy)
                                    break
                        else:
                            src_policy.update(policyId=cln_policy['policyId'])
                            policies_to_update.append(src_policy)
                            break
                    #Compare build rule
                    if 'build' in src_policy['policySubTypes']:
                        if 'children' in cln_policy['rule']:
                            if src_policy['rule']['children'] != cln_policy['rule']['children']:
                                src_policy.update(policyId=cln_policy['policyId'])
                                policies_to_update.append(src_policy)
                                break
                        else:
                            src_policy.update(policyId=cln_policy['policyId'])
                            policies_to_update.append(src_policy)
                            break

                    #Compare recommendation----------------------------------------
                    if src_policy['recommendation'] != cln_policy['recommendation']:
                        src_policy.update(policyId=cln_policy['policyId'])
                        policies_to_update.append(src_policy)
                        break

                    #Compare compliance metadata-----------------------------------
                    src_complianceMetadata = []
                    if 'complianceMetadata' in src_policy:
                        src_complianceMetadata = src_policy['complianceMetadata']
                    cln_complianceMetadata = []
                    if 'complianceMetadata' in cln_policy:
                        cln_complianceMetadata = cln_policy['complianceMetadata']
                    compFlag = False
                    for el in src_complianceMetadata:
                        name = el['standardName']
                        if name not in [cmp['standardName'] for cmp in cln_complianceMetadata]:
                            compFlag = True
                            break
                        req_id = el['requirementId']
                        if req_id not in [cmp['requirementId'] for cmp in cln_complianceMetadata]:
                            compFlag = True
                            break
                        sec_id = el['sectionId']
                        if sec_id not in [cmp['sectionId'] for cmp in cln_complianceMetadata]:
                            compFlag = True
                            break
                    if compFlag:
                        src_policy.update(policyId=cln_policy['policyId'])
                        policies_to_update.append(src_policy)
                        break
                    
                    #Compare labels------------------------------------------------
                    src_labels = src_policy['labels']
                    cln_labels = cln_policy['labels']
                    src_labels.sort()
                    cln_labels.sort()
                    if src_labels != cln_labels:
                        src_policy.update(policyId=cln_policy['policyId'])
                        policies_to_update.append(src_policy)
                        break

                    #Compare enabled-----------------------------------------------
                    if src_policy['enabled'] != cln_policy['enabled']:
                        src_policy.update(policyId=cln_policy['policyId'])
                        policies_to_update.append(src_policy)
                        break
                    
                    #Compare remediable----------------------------------------
                    if src_policy['remediable'] != cln_policy['remediable']:
                        src_policy.update(policyId=cln_policy['policyId'])
                        policies_to_update.append(src_policy)
                        break
        tenants_to_update.append(policies_to_update)
    return tenants_to_update


def compare_criteria(src_searches, cln_searches, src_criteria, cln_criteria):
    #detect rql vs ID
    if 'config' in src_criteria or 'network' in src_criteria or 'event' in src_criteria:
        #search id is an rql statement, cant be updated anymore
        return False

    src_rql = ''
    for el in src_searches:
        if el['id'] == src_criteria:
            src_rql = el['query']
    cln_rql = ''
    for el in cln_searches:
        if el['id'] == cln_criteria:
            cln_rql = el['query']

    if cln_rql != src_rql:
        return True

    return False

def get_policies_to_delete(policies_list):
    #Define lists
    original_tenant = policies_list[0]
    clone_tenants = policies_list[1:]

    tenants_to_delete_from = []
    for tenant in clone_tenants:
        policies_to_delete = []
        for cln_policy in tenant:
            if cln_policy['name'] not in [plc['name'] for plc in original_tenant]:
                #Policy is in clone tenant but not in source tenant
                policies_to_delete.append(cln_policy)
        tenants_to_delete_from.append(policies_to_delete)
    
    return tenants_to_delete_from



