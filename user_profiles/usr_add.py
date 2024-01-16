from sdk.color_print import c_print
from tqdm import tqdm

def add_users(session: object, users_to_add: list, logger):
    '''
    Accepts a tenant session object and a list of users to add.

    Adds each user in the list to the tenant of the provided tenant session.
    The User Profiles in the users_to_add list have to have already had their Role IDs
    translated before running this function.
    '''

    added = 0

    tenant_name = session.tenant
    # checks whether the list is empty
    if users_to_add:
        logger.info(f'Adding User Profiles to tenant: \'{tenant_name}\'')
        
        user_to_add = []
        #iterates through user_to_add and store the data by dictionaries individually
        for user in tqdm(users_to_add, desc='Adding User Profiles', leave=False):
            #The role IDs of each user were translated in the compare potion of the code
            logger.debug('API - Adding User Profile')
            res = session.request("POST", "/v2/user", json=user)
            if res.status_code == 200 or res.status_code == 201:
                added += 1


    #prints the following string if the list is empty
    else:
        logger.info(f'No User Profiles to add for tenant: \'{tenant_name}\'')

    return added
