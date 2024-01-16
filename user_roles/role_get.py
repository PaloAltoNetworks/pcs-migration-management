from sdk.color_print import c_print

def get_roles(session: object, logger):
    logger.debug('API - Getting roles')
    res = session.request('GET', '/user/role')

    return res.json() 