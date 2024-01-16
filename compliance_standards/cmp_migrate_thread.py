from compliance_standards import cmp_compare, cmp_get, cmp_add
from sdk.color_print import c_print
from tqdm import tqdm
import threading

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
    for tenant in tqdm(clone_compliance_standards_to_migrate, desc='Getting Compliance Data', leave=False):
        tenant_compliance = []
        
        pool = []

        tenant_threads = break_into_threads(tenant)

        for tenant_thread in tenant_threads:
            x = threading.Thread(target=get_cmp_info, args=(tenant_compliance, tenant_thread, tenant_sessions[0], logger))
            pool.append(x)
            x.start()

        for index, thread in enumerate(pool):
            thread.join()
            logger.info(f'Thread: \'{index}\' done')

        clone_compliance_standards_data.append(tenant_compliance)

    #Migrate compliance standards. First migrate over the standards and translate the UUIDs.
    #Then migrate over the requirements and translate the UUIDS. Finnally migrate the sections.
    for index, tenant_standards in enumerate(clone_compliance_standards_data):
        #Migrate compliance standards
        added = 0
        for standard in tenant_standards:
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

        #Break tenant_standards into thread
        tenant_standards_treads = break_into_threads(tenant_standards)

        pool = []
        for thread in tenant_standards_treads:
            x = threading.Thread(target=add_cmp_thread, args=(thread, added_reqs, added_secs, tenant_sessions, index, logger))
            pool.append(x)
            x.start()

        for index, thread in enumerate(pool):
            thread.join()
            logger.info(f'Thread: \'{index}\' done')

        sections_added.append(added_secs)
        requirements_added.append(added_reqs)
    
    logger.info('Finished migrating Compliance Standards')
    print()


    return standards_added, requirements_added, sections_added


#==============================================================================
def add_cmp_thread(tenant_standards, added_reqs, added_secs, tenant_sessions, index, logger):
    for index2, standard in enumerate(tenant_standards):
        requirements = standard['requirements']
        std_id = standard['standard']['id']
        
        for requirement in requirements:
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
        
        for requirement in requirements:
            req_id = requirement['requirement']['id']
            sections = requirement['sections']
            
            for section in sections:
                cmp_add.add_section_to_requirement(tenant_sessions[index+1], req_id, section, logger)
                added_secs += 1

#==============================================================================
def get_cmp_info(tenant_compliance, tenant, session, logger):
    for standard in tenant:
        standard_dict = {}

        requirements = []
        requirements_data = cmp_get.get_compliance_requirement_list(session, standard, logger)

        for requirement in requirements_data:
            requirement_dict = {}
            
            sections = cmp_get.get_compliance_sections_list(session, requirement, logger)

            requirement_dict.update(requirement=requirement)
            requirement_dict.update(sections=sections)
            
            requirements.append(requirement_dict)

        standard_dict.update(standard=standard)
        standard_dict.update(requirements=requirements)

        tenant_compliance.append(standard_dict)


#==============================================================================
#Break list into equal sized chunks for threading        
def break_into_threads(list_to_break):
    max_threads = 10
    thread_size = len(list_to_break) // max_threads
    if thread_size < 1:
        thread_size = 1
    if max_threads > len(list_to_break):
        max_threads = len(list_to_break)


    thread_list = []
    for i in range(max_threads):
        start = i * thread_size
        end = start + thread_size
        if i + 1 == max_threads:
            items_for_thread = list_to_break[start:]
        else:
            items_for_thread = list_to_break[start:end]
        thread_list.append(items_for_thread)

    return thread_list

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