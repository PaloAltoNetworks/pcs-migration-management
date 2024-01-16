from policies import plc_cmp_translate
from saved_searches import search_migrate_plc
from sdk.color_print import c_print
from tqdm import tqdm

def update_custom_policies(tenant_session: object, source_tenant_session: object, policies: dict, logger):
    updated = 0
    if policies:
        logger.info(f'Updateing Custom Policies for tenant: \'{tenant_session.tenant}\'')

        translate = plc_cmp_translate.Translate(tenant_session, logger)
        for policy in tqdm(policies, desc='Updating Custom Policies', leave=False):
            p_type = policy['policyType']
            plc_id = policy['policyId']
            name = policy['name']
            desc = name
            if 'description' in policy:
                desc = policy['description']

            #the saved search needs to be migrated if there is one
            if 'savedSearch' in policy['rule']['parameters']:
                savedSearch = policy['rule']['parameters']['savedSearch']
                if savedSearch == 'true' or savedSearch == True or savedSearch =='True' or savedSearch:
                    criteria = search_migrate_plc.migrate_search(tenant_session, source_tenant_session, policy['rule'], policy['name'], desc, logger)
                    policy['rule'].update(criteria=criteria)

            #The ID of the compliance standards needs to be updated if there is compliance data
            if 'complianceMetadata' in policy:
                complianceMetadata = build_compliance_metadata(policy['complianceMetadata'], translate)
                if complianceMetadata == "BAD":
                    logger.warning(f'Compliance Data not migrated for policy \'{name}\'. Unable to update')
                    #Skip updating this policy
                    continue
                policy.update(complianceMetadata=complianceMetadata)

            logger.debug(f'API - Updating policy: {name}')
            tenant_session.request('PUT', f'/policy/{plc_id}', policy)
            updated += 1
            
        return updated
    else:
        logger.info(f'No Custom Policies to update for tenant: \'{tenant_session.tenant}\'')


def build_compliance_metadata(compliance_metadata, translate):
    modified_compliance_metadata = []
    for el in compliance_metadata:
        if 'complianceId' in el:
            cmp_id = translate.translate_compliance_id(el['standardName'], el['requirementId'], el['sectionId'])
            if cmp_id == 'BAD':
                return 'BAD'
            el.update(complianceId = cmp_id)

            modified_compliance_metadata.append(el)

    return compliance_metadata
