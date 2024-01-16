def get_account_groups(session, logger):
    '''
    Calls the Prisma Cloud API for the given tenant session and returns
    the list of account groups from that tenant.
    '''

    logger.debug('API - Getting Account Groups')
    res = session.request('GET', '/cloud/group')
    acc_grps = res.json()
    return acc_grps

