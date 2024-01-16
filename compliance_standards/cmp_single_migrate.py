from compliance_standards import cmp_add, cmp_get, cmp_add
from tqdm import tqdm

#Used to migrate a single compliance standard, section or requirement based on its ID
def single_migrate(tenant_sessions, uuid, cmp_type, logger):
    source_session = tenant_sessions[0]


    if cmp_type == 'std':
        std_to_add = {}
        res = source_session.request('GET', f'/compliance/{uuid}')
        std_to_add = res.json()

        if std_to_add:
            #Add standard
            for session in tenant_sessions[1:]:
                cmp_add.add_compliance_standard(session, std_to_add, logger)
    else:
        tenant_compliance_standards_lists = []
        for session in tenant_sessions:
            tenant_compliance_standards_lists.append(cmp_get.get_compliance_standard_list(session, logger))

        tenant_compliance_standards_data = []
        #Get all requirements and sections for each standard. This is a deep nested search and takes some time
        for index in range(len(tenant_compliance_standards_lists)):
            tenant = tenant_compliance_standards_lists[index]
            tenant_compliance = []
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
            
            tenant_compliance_standards_data.append(tenant_compliance)
        
        source_compliance_standards = tenant_compliance_standards_data[0]
        
        clone_compliance_standards = tenant_compliance_standards_data[1:]


        if cmp_type == 'req':
            std_to_add_name = ''
            std_to_add_id = {}
            req_to_add = {}

            for std in source_compliance_standards:
                if std['standard'].get('id') == uuid:
                    logger.error('Standard found instead of section')
                else:
                    for req in std['requirements']:
                        if req['requirement'].get('id') == uuid:
                            std_to_add_name = std['standard'].get('name')
                            req_to_add = req['requirement']

            if req_to_add:
                #Add requirement
                for index, session in enumerate(tenant_sessions[1:]):
                    #translate ID using name
                    for std in clone_compliance_standards[index]:
                        if std['standard'].get('name') == std_to_add_name:
                            std_to_add_id = std['standard'].get('id')
                    cmp_add.add_requirement_to_standard(session, std_to_add_id, req_to_add, logger)
            else:
                logger.info(f'Could not find Compliance Requirement with UUID of \'{uuid}\'')

        else:
            std_to_add_name = ''
            req_to_add_name = ''
            req_to_add_id = {}
            sec_to_add = {}


            for std in source_compliance_standards:
                if std['standard'].get('id') == uuid:
                    logger.error('Standard found instead of section')
                else:
                    for req in std['requirements']:
                        if req['requirement'].get('id') == uuid:
                            logger.error('Requirement found instead of section')
                        else:
                            for sec in req['sections']:
                                if sec.get('id') == uuid:
                                    std_to_add_name = std['standard'].get('name')
                                    req_to_add_name = req['requirement'].get('name')
                                    sec_to_add = sec
            if sec_to_add:
                #Add section
                for index, session in enumerate(tenant_sessions[1:]):
                    for std in clone_compliance_standards[index]:
                        if std['standard'].get('name') == std_to_add_name:
                            for req in std['requirements']:
                                if req['requirement'].get('name') == req_to_add_name:
                                    req_to_add_id = req['requirement'].get('id')
                    
                    cmp_add.add_section_to_requirement(session, req_to_add_id, sec_to_add, logger)
            else:
                logger.info(f'Could not find Compliance Section with UUID of \'{uuid}\'')