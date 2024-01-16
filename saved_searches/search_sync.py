from sdk.color_print import c_print
from sdk import load_config
import hashlib
from tqdm import tqdm

def sync(tenant_sessions: list, addMode: bool, delMode: bool, logger):
    #Get list of saved search from original tenant
    tenant_saved_searches = []
    for session in tenant_sessions:
        logger.debug('API - Getting saved searches for each tenant')
        querystring = {"filter":"saved"}
        res = session.request('GET', '/search/history', params=querystring)
        data = res.json()
        tenant_saved_searches.append(data)

    o_tenant = tenant_saved_searches[0]
    clone_tenants = tenant_saved_searches[1:]

    added_searches = []
    deleted_searches = []

    if addMode:
        
        #Compare saved searches across tenants and add missing ones
        #Loop over the saved searches of each tenant
        for index, d_tenant in enumerate(clone_tenants):
            added = 0
            saved_search_to_add = []
            for o_saved_search in o_tenant:
                if o_saved_search.get('searchName') not in [d_ss.get('searchName') for d_ss in d_tenant]:
                    saved_search_to_add.append(o_saved_search)
            for search in tqdm(saved_search_to_add, desc='Adding Saved Searches', leave=False):
                res = run_and_save_search(tenant_sessions[index + 1], search, logger)
                if res != 'BAD':
                    added += 1
            added_searches.append(added)

    #Saved searches don't seem to be able to updated so no reason to look for changes among searches

    if delMode:
        #Delete saved searches
        for index, d_tenant in enumerate(clone_tenants):
            deleted = 0
            saved_search_to_delete = []
            for d_saved_search in d_tenant:
                if d_saved_search.get('searchName') not in [o_ss.get('searchName') for o_ss in o_tenant]:
                    saved_search_to_delete.append(d_saved_search)
            for search in tqdm(saved_search_to_delete, desc='Deleting Saved Searches', leave=False):
                logger.debug('API - Deleteing saved search')
                s_id = search.get('id')
                tenant_sessions[index + 1].request('DELETE', f'/search/history/{s_id}', status_ignore=[204])
                deleted += 1
            deleted_searches.append(deleted)
    else:
        for index in clone_tenants:
            deleted_searches.append(0)

    return added_searches, deleted_searches, {}

#==============================================================================

def run_and_save_search(session, old_search, logger):
    #This functions calles the appropriate run RQL API
    #depending on the type of search
    if 'config from' in old_search.get('query'):
        return perfrom_config(session, old_search, logger)
    elif 'event from' in old_search.get('query'):
        return perform_event(session, old_search, logger)
    else: #Network
        return perform_network(session, old_search, logger)

#==============================================================================

def perfrom_config(session, search, logger):
    payload = {
        "query": search.get('query'),
        "timeRange": search.get('searchModel',{}).get('timeRange')
    }

    if 'from iam' in search.get('query'):
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
        payload.update(filters=search.get('filters'))

    if 'groupBy' in search:
        payload.update(groupBy=search.get('groupBy'))

    # if 'id' in search:
    #     payload.update(id=search['id'])

    if 'limit' in search:
        payload.update(limit=search.get('limit'))

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

    payload.update(query=search.get('query'))
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
    payload = {
        "id": new_search['id'],
        "name": old_search['searchName'],
        "searchType": new_search['searchType'],
        "saved": 'false',
        "timeRange": old_search['searchModel']['timeRange'],
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
        logger.debug('FAILED')
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
        return data.get('id')
    else:
        logger.debug(old_search)
        return 'BAD'

#==============================================================================

def get_saved_search_id_by_name(session, name, logger):

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


if __name__ == '__main__':
    tenant_sessions = load_config.load_config_create_sessions()
    sync(tenant_sessions, True, True)
