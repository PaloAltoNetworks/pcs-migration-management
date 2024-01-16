from compliance_standards import cmp_compare, cmp_get, cmp_add
from sdk.color_print import c_print
from tqdm import tqdm

def migrate(tenant_sessions: list, logger):
    '''
    Accepts a list of tenant session objects.
    Gets a list of the top level compliance standards that are missing and migrates
    the missing compliance standard and all its requirements and sections. Does not
    search for and add missing requirements or sections. That is handled in the 
    sync module which does a much more time intensive nested search of all the 
    compliance data accross all tenants
    '''

    standards_added = []
    requirements_added = []
    sections_added = []

    #Get complance standards from all tenants
    tenant_compliance_standards_lists = []
    for session in tenant_sessions:
        tenant_compliance_standards_lists.append(cmp_get.get_compliance_standard_list(session, logger))

    #Compare compliance standards
    clone_compliance_standards_to_migrate = cmp_compare.get_compliance_stanadards_to_add(tenant_sessions, tenant_compliance_standards_lists, logger)

    #Get all requirements and sections for each standard. This is a deep nested search and takes some time
    clone_compliance_standards_data = []
    for tenant in tqdm(clone_compliance_standards_to_migrate, desc='Getting Compliance Data from each Tenant', leave=False):
        tenant_compliance = []
        for standard in tqdm(tenant, desc='Getting Compliance Standards', leave=False):
            standard_dict = {}

            requirements = []
            requirements_data = cmp_get.get_compliance_requirement_list(tenant_sessions[0], standard, logger)

            for requirement in requirements_data:
                requirement_dict = {}
                
                sections = cmp_get.get_compliance_sections_list(tenant_sessions[0], requirement, logger)

                requirement_dict.update(requirement=requirement)
                requirement_dict.update(sections=sections)
                
                requirements.append(requirement_dict)

            standard_dict.update(standard=standard)
            standard_dict.update(requirements=requirements)

            tenant_compliance.append(standard_dict)
        
        clone_compliance_standards_data.append(tenant_compliance)

    #Migrate compliance standards. First migrate over the standards and translate the UUIDs.
    #Then migrate over the requirements and translate the UUIDS. Finnally migrate the sections.
    for index, tenant_standards in tqdm(enumerate(clone_compliance_standards_data), desc='Adding Compliance Data for each Tenant', leave=False):
        #Migrate compliance standards
        added = 0
        for standard in tqdm(tenant_standards, desc='Adding Compliance Standards', leave=False):
            cmp_add.add_compliance_standard(tenant_sessions[index + 1], standard['standard'], logger)
            added += 1
        standards_added.append(added)

        #Translate compliance IDs
        clone_standards = cmp_get.get_compliance_standard_list(tenant_sessions[index + 1], logger)
        for i in range(len(tenant_standards)):
            name = tenant_standards[i]['standard']['name']  
            for j in range(len(clone_standards)):
                if clone_standards[j]['name'] == name:
                    new_id = clone_standards[j]['id']
                    tenant_standards[i]['standard'].update(id=new_id)
                    break
        
        #Migrate compliance requirements
        added_reqs = 0
        added_secs = 0
        for index2, standard in tqdm(enumerate(tenant_standards), desc='Processing Compliance Standards', leave=False):
            requirements = standard['requirements']
            std_id = standard['standard']['id']
            
            for requirement in tqdm(requirements, desc='Adding Compliance Requirements', leave=False):
                cmp_add.add_requirement_to_standard(tenant_sessions[index + 1], std_id, requirement['requirement'], logger)
                added_reqs += 1

            #Translate compliance IDs
            clone_requirements = cmp_get.get_compliance_requirement_list(tenant_sessions[index+1], standard['standard'], logger)
            for i in range(len(requirements)):
                name = requirements[i]['requirement']['name']
                for j in range(len(clone_requirements)):
                    if clone_requirements[j]['name'] == name:
                        new_id = clone_requirements[j]['id']
                        requirements[i]['requirement'].update(id=new_id)
                        break

            #Update requirements list with the list that has the new ids - maybe not needed but easy to do
            tenant_standards[index2].update(requirements=requirements)

            #Migrate sections now that the requirement UUIDs have been updated
            
            for requirement in tqdm(requirements, desc='Processing Compliance Requirements', leave=False):
                req_id = requirement['requirement']['id']
                sections = requirement['sections']
                
                for section in tqdm(sections, desc='Adding Compliance Sections', leave=False):
                    cmp_add.add_section_to_requirement(tenant_sessions[index+1], req_id, section, logger)
                    added_secs += 1
        sections_added.append(added_secs)
        
        requirements_added.append(added_reqs)
    
    logger.info('Finished migrating Compliance Standards')
    print()


    return standards_added, requirements_added, sections_added

#==============================================================================
#Test code
if __name__ == '__main__':
    from sdk import load_config
    tenant_sessions = load_config.load_config_create_sessions()

    migrate(tenant_sessions)

        


    





# tenant_compliance = [ 
#     {
#         'standard': standard_dict,
#         'requirements': [
#             {
#                 'requirement': requirement_dict,
#                 'sections': [
#                     section_dict
#                 ]
#             }
#             ]
#     }
# ]