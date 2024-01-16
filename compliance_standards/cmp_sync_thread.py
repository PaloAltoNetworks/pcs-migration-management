from compliance_standards import cmp_compare, cmp_get
from compliance_standards.cmp_migrate_thread import break_into_threads
from sdk.color_print import c_print
from tqdm import tqdm
import threading

def sync(tenant_sessions: list, addMode: bool, upMode: bool, delMode: bool, logger, tenant_compliance_standards_data=[]):
    '''
    Normalizes custom compliance standards accross all tenants using the first tenant as the template
    for the others. Does a deep search accross all tenants to collect all compliance standards, requirements
    and sections so that they can be compared. Compliance data will be added, updated or delted from the clone
    tenants until each clone tenant matches the one source tenant.
    '''

    added_standards_list = []
    added_requirements_list = []
    added_sections_list = []
    
    updated_standards_list = []
    updated_requirements_list = []
    updated_sections_list = []
    
    deleted_standards_list = []
    deleted_requirements_list = []
    deleted_sections_list = []

    
    if not tenant_compliance_standards_data:#Sometimes the compliance data is passed in. Mainly used by the delete function
        #Get complance standards from all tenants
        tenant_compliance_standards_lists = []
        for session in tenant_sessions:
            tenant_compliance_standards_lists.append(cmp_get.get_compliance_standard_list(session, logger))

        #Get all requirements and sections for each standard. This is a deep nested search and takes some time
        for index in range(len(tenant_compliance_standards_lists)):
            tenant = tenant_compliance_standards_lists[index]
            tenant_compliance = []


            #Break 'tenant' into sections for threads
            tenant_threads = break_into_threads(tenant)
            pool = []
            for thread in tenant_threads:
                x = threading.Thread(target=get_cmp_info_thread, args=(thread, tenant_compliance, tenant_sessions, index, logger))
                pool.append(x)
                x.start()

            for index, thread in enumerate(pool):
                thread.join()
                logger.info(f'Thread: \'{index}\' done')
            
            tenant_compliance_standards_data.append(tenant_compliance)

    #Once the compliance standards have been gathered, get compliance data that needs to be added, updated, and deleted

    source_compliance_standards = tenant_compliance_standards_data[0]
    clone_compliance_standards = tenant_compliance_standards_data[1:]

    #Sync compliance data
    for index, clone in enumerate(clone_compliance_standards):
        session = tenant_sessions[index + 1]
        res = cmp_compare.update_add_delete_compliance_data(source_compliance_standards, clone, session, addMode, upMode, delMode, logger)

        added_standards, added_requirements, added_sections, updated_standards, updated_requirements, updated_sections, deleted_standards, deleted_requirements, deleted_sections = res
        
        added_standards_list.append(added_standards)
        added_requirements_list.append(added_requirements)
        added_sections_list.append(added_sections)
        updated_standards_list.append(updated_standards)
        updated_requirements_list.append(updated_requirements)
        updated_sections_list.append(updated_sections)
        deleted_standards_list.append(deleted_standards)
        deleted_requirements_list.append(deleted_requirements)
        deleted_sections_list.append(deleted_sections)

    logger.info('Finished syncing Compliance Data')
    print()

    return added_standards_list, added_requirements_list, added_sections_list, updated_standards_list, updated_requirements_list, updated_sections_list, deleted_standards_list, deleted_requirements_list, deleted_sections_list, tenant_compliance_standards_data

#==============================================================================
def get_cmp_info_thread(tenant, tenant_compliance, tenant_sessions, index, logger):
    for standard in tqdm(tenant, desc=f'Getting Compliance Data from Tenant {tenant_sessions[index].tenant}', leave=False):
        standard_dict = {}

        requirements = []
        requirements_data = cmp_get.get_compliance_requirement_list(tenant_sessions[index], standard, logger)

        for requirement in requirements_data:
            requirement_dict = {}
            
            sections = cmp_get.get_compliance_sections_list(tenant_sessions[index], requirement, logger)

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

    sync(tenant_sessions, True, True, True)

        


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