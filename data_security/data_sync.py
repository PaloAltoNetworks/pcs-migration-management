def sync(tenant_sessions, logger):
    tenant_ds_enabled = []
    #Get DS enabled status for all tenants
    for session in tenant_sessions:
        logger.debug('API - Getting Data Security Enabled Status')
        res = session.request('GET', '/api/v1/provision/dlp/status')
        info = res.json().get('status')

        if info:
            if info == 'provisionNotStarted':
                tenant_ds_enabled.append(True)
            else:
                tenant_ds_enabled.append(False)

    #Enable DS on clone tenants if source tenant has it enabled
    source_tenant = tenant_ds_enabled[0]
    if source_tenant == True:
        clone_sessions = tenant_sessions[1:]
        for session in clone_sessions:
            logger.debug(f'API - Enabling Data Security for tenant: \'{session.tenant}\'')
            session.request('POST', 'api/v1/provision/dlp')
            



if __name__ == '__main__':
    from sdk.load_config import load_config_create_sessions
    from loguru import logger
    tenant_sessions = load_config_create_sessions(True, logger)


    # #Check if DS is enabled
    # res = tenant_sessions[0].request('GET', '/api/v1/provision/dlp/status')
    # print(res.json())

    # #Enabled DS
    # res = tenant_sessions[1].request('POST', 'api/v1/provision/dlp')
    # print(res.json())

    sync(tenant_sessions, logger)
    
    