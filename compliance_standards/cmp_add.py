from sdk import load_config
from sdk.color_print import c_print
from tqdm import tqdm

def add_compliance_standard(session: object, standard: dict, logger):
    '''
    Accepts a tenant session object and a compliance standard.

    Adds the compliance standard to the supplied tenant.
    '''

    desc = ''
    if 'description' in standard:
        desc = standard['description']

    payload = {
        "description": desc,
        "name": standard['name']
    }

    logger.debug('API - Adding compliance standard: ', standard['name'])
    session.request('POST', '/compliance', json=payload)

#==============================================================================

def add_requirement_to_standard(session, standard_id, requirement, logger):
    '''
    Accepts a tenant session object, a compliance standard ID, and a requirement.

    Adds the compliance requirement to the supplied compliance standard.
    '''

    desc = ''
    if 'description' in requirement:
        desc = requirement['description']

    payload = {
        "description": desc,
        "name": requirement['name'],
        "requirementId": requirement['requirementId']
    }

    logger.debug('API - Adding compliance requirement: ',requirement['name'])
    session.request('POST', f'/compliance/{standard_id}/requirement', json=payload)

#==============================================================================

def add_section_to_requirement(session, req_id, section, logger):
    '''
    Accepts a tenant session object, a requirement id, and a section.

    Adds the compliance section to the supplied requirement.
    '''

    sec_id = section['sectionId']
    desc = ''
    if 'description' in section:
        desc = section['description']

    payload = {
        "description": desc,
        "sectionId": sec_id
    }

    logger.debug(f'API - Adding compliance section: {sec_id}')
    session.request('POST', f'/compliance/{req_id}/section', json=payload)

#==============================================================================

def add_compliance_standards(session: object, standards_data: list, logger):
    '''
    Accepts a tenant session object and a list of compliance standards.

    Adds all the compliance standards to the supplied tenant.
    '''

    for data in tqdm(standards_data, desc='Adding Compliance Standards', leave=False):
        standard = data[0]

        desc = ''
        if 'description' in standard:
            desc = standard['description']

        payload = {
            "description": desc,
            "name": standard['name']
        }

        logger.debug('API - Adding compliance standard: ', standard['name'])
        res = session.request('POST', '/compliance', json=payload)

#==============================================================================

def add_compliance_requirements(session: object, compliance_standard_id: str, requirements_data: list, logger):
    '''
    Accepts a tenant session object, a compliance standard id, and a list of requirements to add.

    Adds the compliance requirements to the supplied standard.
    '''

    cmp_id = compliance_standard_id

    for el in tqdm(requirements_data, desc='Adding Compliance Requirements', leave=False):
        requirement = el[0]
        sections = el[1]

        req_id = requirement['requirementId']


        desc = ''
        if 'description' in requirement:
            desc = requirement['description']

        payload = {
            "description": desc,
            "name": requirement['name'],
            "requirementId": req_id
        }

        logger.debug('API - Adding compliance requirement: ',requirement['name'])
        res = session.request('POST', f'/compliance/{cmp_id}/requirement', json=payload)
        if res.status_code != 200:
            pass

#==============================================================================

def add_compliance_sections(session: object, requirement_id: str, sections: list, logger):
    '''
    Accepts a tenant session object, a requirement id, and a list of sections to add.

    Adds the compliance sections to the supplied requirement.
    '''

    req_id = requirement_id
    for section in tqdm(sections, desc='Adding Compliance Sections', leave=False):
        sec_id = section['sectionId']

        desc = ''
        if 'description' in section:
            desc = section['description']

        payload = {
            "description": desc,
            "sectionId": sec_id
        }

        logger.debug(f'API - Adding compliance section: {sec_id}')
        res = session.request('POST', f'/compliance/{req_id}/section', json=payload)
        if res.status_code != 200:
            pass


    pass

#==============================================================================
#Test code
if __name__ == '__main__':
    tenant_sessions = load_config.load_config_create_sessions()
    req = {
        "description": 'I am the desc',
        "name": 'I am named Adam',
        "requirementId": 'This should be what ever I want'
    }
    req_data = [[req, []]]
    add_compliance_requirements(tenant_sessions[1], '98043f24-2975-4d70-b409-45fc09cb01b5', req_data)


# standards = [ 
#     [standard, [ 
#             [requirements, [
#                 sections
#                 ] 
#             ] 
#         ] 
#     ]
# ]
#
# standard =            standards[index][0]
# requirements_data =   standards[index][1]
# requirements =        standards[index][1][0]
# sections =            standards[index][1][1]