from sdk.color_print import c_print

def get_trusted_networks(session: object, logger:object):
    '''
    Accepts a tenant session object.

    Gets information about the trusted alert IP networks.
    '''

    logger.debug('API - Getting list of Trusted Alert IP networks')
    res = session.request('GET', '/allow_list/network')
    data = res.json()

    return data

def get_ip_ciders(session: object, network: object, logger:object):
    '''
    Accepts a tenant session object and a Trusted Alert Network.

    Gets CIDR list for the supplied network
    '''

    name = network.get('name')
    networkUuid = network.get('uuid')
    logger.debug(f'API - Getting CIDR lists for Network: \'{name}\'')
    res = session.request('GET', f'/network/{networkUuid}')
    data = res.json()

    return data

def get_login_ips(session: object, logger):
    '''
    Accepts a tenant session object.

    Gets the trusted login IPs for the suppled tenant session.
    '''

    logger.debug('API - Getting list of Trusted Login IPs')
    res = session.request('GET', '/ip_allow_list_login')
    data = res.json()

    return data

if __name__ == '__main__':
    from sdk.load_config import load_config_create_sessions
    tenant_sessions = load_config_create_sessions()
    data = get_trusted_networks(tenant_sessions[0])

    for el in data:
        print(el)