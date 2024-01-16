from policies import plc_get, plc_add, plc_update
from sdk.color_print import c_print
from tqdm import tqdm

def migrate_builtin_policies(tenant_sessions: list, logger):
    '''
    Updates the default/built in policies of all clone tenants so they are the same as the
    source tenant. Default policies can not be added or deleted.
    '''

    tenant_updated_policies = []

    tenant_default_policies = []
    for tenant_session in tenant_sessions:
        tenant_default_policies.append(plc_get.api_get_default(tenant_session, logger))

    original_tenant = tenant_default_policies[0]
    clone_tenant_default_policies = tenant_default_policies[1:]
    for index, tenant in enumerate(clone_tenant_default_policies):
        added = 0
        for plc in tqdm(tenant, desc='Syncing Default Policies', leave=False):
            for old_plc in original_tenant:
                if plc['name'] == old_plc['name']:
                    #Compliance metadata is not apart of every policy so it has to be compared situationally
                    complianceMetadata = []
                    if 'complianceMetadata' in plc:
                        complianceMetadata = plc['complianceMetadata']
                    old_complianceMetadata = []
                    if 'complianceMetadata' in old_plc:
                        old_complianceMetadata = old_plc['complianceMetadata']
                    compFlag = False
                    for el in old_complianceMetadata:
                        name = el['standardName']
                        if name not in [cmp['standardName'] for cmp in complianceMetadata]:
                            compFlag = True
                            break
                        req_id = el['requirementId']
                        if req_id not in [cmp['requirementId'] for cmp in complianceMetadata]:
                            compFlag = True
                            break
                        sec_id = el['sectionId']
                        if sec_id not in [cmp['sectionId'] for cmp in complianceMetadata]:
                            compFlag = True
                            break
                    
                    #Sort Labels
                    labels = plc['labels']
                    o_labels = old_plc['labels']
                    labels.sort()
                    o_labels.sort()

                    #If there is a difference between the source tenant policy and the destination tenant policy, then update the policy
                    # if plc['severity'] != old_plc['severity'] or plc['labels'] != old_plc['labels'] or plc['rule'] != old_plc['rule'] or compFlag:
                    if plc['severity'] != old_plc['severity'] or labels != o_labels or plc['rule'] != old_plc['rule'] or compFlag:
                        res = plc_add.update_default_policy(tenant_sessions[index + 1], old_plc, logger)
                        if res != 'BAD':
                            added += 1
        tenant_updated_policies.append(added)

    logger.info('Finished migrating Default Policies')

    return tenant_updated_policies

if __name__ == '__main__':
    from sdk.load_config import load_config_create_sessions
    tenant_sessions = load_config_create_sessions()
    
    migrate_builtin_policies(tenant_sessions)


