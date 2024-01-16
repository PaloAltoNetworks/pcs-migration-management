

def api_get_custom(tenant: object, logger):
    '''
    Accepts a tenant session object and a logging flag.

    Gets custom policies from the tenant.
    '''
    endpoint_url = '/v2/policy'
    params = {"policy.policyMode":"custom"}

    res = tenant.request('GET', endpoint_url, params=params)

    logger.info(f'Got {len(res.json())} custom policies.', color='green')

    policies = res.json()
    
    return policies

#==============================================================================

def api_get_default(tenant: object, logger):
    endpoint_url = '/v2/policy'
    params = {"policy.policyMode":"redlock_default"}

    res = tenant.request('GET', endpoint_url, params=params)

    logger.info(f'Got {len(res.json())} default policies', color='green')

    policies = res.json()
    
    return policies

#==============================================================================

if __name__ == '__main__':
    from sdk import load_config

    tenant_sessions = load_config.load_config_create_sessions()

    api_get_custom(tenant_sessions[0], True)
    # api_get_default(tenant_sessions[0])