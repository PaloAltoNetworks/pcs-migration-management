import requests
from sdk.color_print import c_print
from tqdm import tqdm

def update_user_profiles(session, users, logger):
    updated = 0
    if users:
        logger.info(f'Updating User Profiles on tenant: \'{session.tenant}\'')

        for user in tqdm(users, desc='Updating User Profiles', leave=False):
            #The email address that is used as the ID in the URL must be encoded. 
            encoded_id = requests.utils.quote(user['email'])
            
            logger.debug('API - Updating User Profile')
            session.request('PUT', f'/v2/user/{encoded_id}', user)
            updated += 1

    else:
        logger.info(f'No User Profiles to update for tenant: \'{session.tenant}\'')

    return updated