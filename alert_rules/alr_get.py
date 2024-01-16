def get_alert_rules(session: object, logger):
    '''
    Accepts a tenant session object.

    Gets all alert rules from a tenant
    '''
    logger.debug('API - Getting Alert Rules')
    res = session.request("GET", "/v2/alert/rule")
    data = res.json()

    return data