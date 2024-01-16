def get_resource_lists(session: object, logger):
    '''
    Calls the API and gets the list of resource list.
    '''

    logger.debug('API - Getting Resource Lists')
    res = session.request('GET', '/v1/resource_list')
    rsc_lists = res.json()

    return rsc_lists