import hashlib
def migrate_search(tenant_session: object, original_session: object, rule: str, policy_name: str, policy_description: str, logger):
    '''
    Main function that will get info about the search to be migrated, like the RQL and time range, then dispatches
    the proper functions to perform and then save the search resulting in the saved search UUID being returned
    '''
    if 'criteria' not in rule:
        return None
    search_id = rule['criteria']

    #detect rql vs ID
    if 'config' in search_id or 'network' in search_id or 'event' in search_id:
        #search id is an rql statement, skip getting info and build a search object
        search = build_search_payload(rule=rule, search_id=search_id)

        #call the run and save function for the search
        return run_and_save_search(tenant_session, search, logger)
        

    params = {"filter":"saved"}
    logger.debug(f'API - getting old saved search with ID: {search_id}')
    response = original_session.request("GET", f'/search/history/{search_id}', params=params)

    data = response.json()

    if data['name'] == '':
        hash_object = hashlib.sha1(bytes(policy_description, 'utf-8'))
        plc_hash = hash_object.hexdigest()
        data['name'] = policy_name +  " - " + str(plc_hash)
    
    if response.status_code == 200:
        return run_and_save_search(tenant_session, data, logger)
    else:
        return None

#==============================================================================

def run_and_save_search(session, old_search, logger):
    #This functions calles the appropriate run RQL API
    #depending on the type of search
    if 'config from' in old_search['query']:
        return perfrom_config(session, old_search, logger)
    elif 'event from' in old_search['query']:
        return perform_event(session, old_search, logger)
    else: #Network
        return perform_network(session, old_search, logger)

#==============================================================================

def perfrom_config(session, search, logger):
    timeRange = search.get('timeRange')
    payload = {
        "query": search['query'],
        "timeRange": search.get('searchModel',{}).get('timeRange', timeRange)
    }

    if 'from iam' in search['query']:
        logger.debug('API - Performing config IAM search')
        response = session.request("POST", "/api/v1/permission", json=payload)
    else:
        logger.debug('API - Performing config search')
        response = session.request("POST", "/search/config", json=payload)

    if response.status_code == 200:
        return save_search(session, response.json(), search, logger)
    else:
        return 'BAD'

#==============================================================================

def perform_event(session, search, logger):
    '''
    Performs an event search
    '''
    payload = {
        "filters": [],
        "limit": 100,
        "sort": [
            {
                "direction": "desc",
                "field": "time"
            }
        ]
    }
    
    if 'filters' in search:
        payload.update(filters=search['filters'])

    if 'groupBy' in search:
        payload.update(groupBy=search['groupBy'])

    # if 'id' in search:
    #     payload.update(id=search['id'])

    if 'limit' in search:
        payload.update(limit=search['limit'])

    if 'query' in search:
        payload.update(query=search['query'])

    if 'sort' in search:
        payload.update(sort=search['sort'])

    timeRange = search.get('timeRange', {})
    payload.update(timeRange=search.get('searchModel', {}).get('timeRange', timeRange))

    logger.debug('API - Performing event search')
    response = session.request("POST", "/search/event", json=payload)
    
    if response.status_code == 200:
        return save_search(session, response.json(), search, logger)
    else:
        return 'BAD'

#==============================================================================

def perform_network(session, search, logger):
    '''
    Performs a networks search
    '''
    
    #Build payload object with values that are given
    payload =  {}

    payload.update(query=search['query'])
    timeRange = search.get('timeRange', {})
    payload.update(timeRange=search.get('searchModel', {}).get('timeRange', timeRange))
    
    if 'default' in search:
        payload.update(default=search['default'])

    if 'description' in search:
        payload.update(description=search['description'])

    # if 'id' in search:
    #     payload.update(id=search['id'])

    if 'name' in search:
        payload.update(name=search['name'])

    if 'cloudType' in search:
        payload.update(name=search['cloudType'])

    query = payload.get('query')
    response = None
    if 'from iam' in query:
        logger.debug('API - Performing config IAM search')
        response = session.request("POST", "/api/v1/permission", json=payload)
    else:
        logger.debug('API - Performing network search')
        response = session.request("POST", "/search", json=payload)
    
    if response.status_code == 200:
        return save_search(session, response.json(), search, logger)
    else:
        return 'BAD'

#==============================================================================

def save_search(session, new_search, old_search, logger):
    '''
    After a search as been exected, it can then be saved. This function uses
    the details of a saved search from the source tenant to save an equivalent search
    on the clone tenant.
    '''
    payload = {
        "id": new_search['id'],
        "name": old_search['name'],
        "searchType": new_search['searchType'],
        "saved": 'false',
        "timeRange": old_search['timeRange'],
        "query": new_search['query'],
        }

    if 'cloudType' in old_search:
        payload.update(cloudType=old_search['cloudType'])

    if 'description' in old_search:
        payload.update(description=old_search['description'])

    if 'data' in old_search:
        payload.update(data=old_search['data'])
    
    if 'default' in old_search:
        payload.update(default=old_search['default'])
    
    

    search_id = new_search['id']
    logger.debug(f'API - Saving search with ID of: {search_id}')
    response = session.request("POST", f"/search/history/{search_id}", json=payload, redlock_ignore=['duplicate_search_name'])
    
    if response.status_code != 200 and 'duplicate_search_name' in response.headers['x-redlock-status']:
        logger.info('Search already saved. Getting ID')
        if 'searchName' in old_search:
            return get_saved_search_id_by_name(session, old_search.get('searchName'), logger)
        elif 'name' in old_search:
            return get_saved_search_id_by_name(session, old_search.get('name'), logger) 
        else:
            logger.debug(old_search)
            return 'BAD'

    if response.status_code == 200:
        data = response.json()
        return data['id']
    else:
        logger.debug(old_search)
        return 'BAD'

#==============================================================================

def get_saved_search_id_by_name(session, name, logger):
    '''
    If the search has already been saved to the clone tenant, then 
    just return its ID instead of re saving it.
    '''

    params = {"filter": "saved"}

    logger.debug('API - Getting saved searches')
    response = session.request('GET', '/search/history', params=params)

    data = response.json()

    for el in data:
        if el['searchName'] == name:
            logger.info('Found saved ID')
            return el['id']
    logger.info('ID not found')
    return 'BAD'

#==============================================================================

def build_search_payload(rule, search_id):
    '''
    Builds up a saved search payload used for migrating saved searches
    '''
    
    #Build a payload based off keys used in the rule from a policy
    search = {}
        
    #Build up a search object out of default values or values from the rule
    search.update(query = search_id) #required

    search.update(searchType=rule['type'])

    time_range = {
        "relativeTimeType": "BACKWARD",
        "type": "relative",
        "value": {
            "amount": 24,
            "unit": "hour"
            }
        }
    if 'timeRange' in rule:
        time_range = rule['timeRange']

    search.update(timeRange = time_range) #required

    if 'name' in rule:
        search.update(name = rule['name'])

    if 'id' in rule:
        search.update(id = rule['id'])

    if 'alertId' in rule:
        search.update(alertId = rule['alertId'])

    if 'limit' in rule:
        search.update(limit = rule['limit'])

    if 'sort' in rule:
        search.update(sort = rule['sort'])

    if 'filters' in rule:
        search.update(filters = rule['filters'])

    if 'cloudType' in rule:
        search.update(cloudType = rule['cloudType'])

    if 'default' in rule:
        search.update(default = rule['default'])

    if 'groupBy' in rule:
        search.update(groupBy=rule['groupBy'])        

    if 'description' in rule:
        search.update(description=rule['description'])

    if 'savedSearch' in rule['parameters']:
        search.update(saved=rule['parameters']['savedSearch'])

    return search
