from saved_searches.search_sync import run_and_save_search

def single_migrate(tenant_sessions, uuid, logger): 
    tenant_saved_searches = [] 
    for session in tenant_sessions:
        logger.debug('API - Getting saved searches for each tenant')
        querystring = {"filter":"saved"}
        res = session.request('GET', '/search/history', params=querystring)
        data = res.json()
        tenant_saved_searches.append(data)

    source_tenant = tenant_saved_searches[0]
    clone_tenants = tenant_saved_searches[1:]
    
    search_to_add = {}
    for src_search in source_tenant:
        print(src_search.get('id'))
        if src_search.get('id') == uuid:
            search_to_add = src_search
            break
    
    if search_to_add:
        for session in tenant_sessions[1:]:
            run_and_save_search(session, search_to_add, logger)
    else:
        logger.info(f'Seaved Search with UUID \'{uuid}\' not found')


