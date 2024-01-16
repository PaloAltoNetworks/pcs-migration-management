from sdk.color_print import c_print

def get_all_network_settings(session: object, logger):
    params = {'type':'Network'}
    logger.debug('API - Getting all anomaly settings')
    res = session.request('GET', '/anomalies/settings', params=params)
    data = {}
    try:
        data = res.json()
    except:
        data = {}

    return data

def get_all_ueba_settings(session: object, logger):
    params = {'type':'UEBA'}
    logger.debug('API - Getting all anomaly settings')
    res = session.request('GET', '/anomalies/settings', params=params)
    data = {}
    try:
        data = res.json()
    except:
        data = {}

    return data

def get_setting(session: object, plc_id: str, logger):
    logger.debug('API - Getting anomaly setting')
    res = session.request('GET', f'/anomalies/settings/{plc_id}')
    data = {}
    try:
        data = res.json()
    except:
        data = {}
    
    return data

def get_trusted_lists(session: object, logger):
    logger.debug('API - Getting anomaly trusted list')
    res = session.request('GET', '/anomalies/trusted_list')
    data = {}
    try:
        data = res.json()
    except:
        data = {}

    return data

if __name__ == '__main__':
    from sdk.load_config import load_config_create_sessions
    tenant_sessions = load_config_create_sessions()
    
    data = get_all_network_settings(tenant_sessions[0])

    print(data)
    print()
    for el in data:
        print(el)
        res = get_setting(tenant_sessions[0], el)
        print(res)