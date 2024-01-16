from sdk.color_print import c_print

def sync(tenant_sessions, logger):
    logger.debug('API - Getting enterprise settings')
    res = tenant_sessions[0].request('GET', '/settings/enterprise')
    
    settings = res.json()

    tenant_updated = []

    if 'userAttributionInNotification' not in settings:
        settings.update(userAttributionInNotification=False)

    clone_tenant_sessions = tenant_sessions[1:]
    for session in clone_tenant_sessions:
        logger.debug('API - Updating enterprise settings')
        session.request('POST', '/settings/enterprise', json=settings)
        tenant_updated.append(True)

    logger.info('Finished syncing Enterprise Settings')

    return tenant_updated

if __name__ == '__main__':
    from sdk.load_config import load_config_create_sessions

    tenant_sessions = load_config_create_sessions()

    sync(tenant_sessions)