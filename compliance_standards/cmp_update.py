from sdk.color_print import c_print

def update_compliance_standard(session: object, cmp_id: str, standard: dict, logger):
    logger.debug('API - Updating compliance standard')
    session.request('PUT', f'/compliance/{cmp_id}', json=standard)

def update_compliance_requirement(session: object, req_id: str, requirement: dict, logger):
    logger.debug('API - Updating compliance requirement')
    session.request('PUT', f'/compliance/requirement/{req_id}', json=requirement)

def update_compliance_section(session: object, sec_id: str, section: dict, logger):
    logger.debug('API - Updating compliance requirement')
    session.request('PUT', f'/compliance/requirement/section/{sec_id}', json=section)