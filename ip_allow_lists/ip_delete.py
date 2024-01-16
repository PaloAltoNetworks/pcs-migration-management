from sdk.color_print import c_print
from tqdm import tqdm

def delete_login_ips(session, ips, dst_ips, logger):
    deleted = 0
    if ips:
        logger.info(f'Deleting Trusted Login IPs from tenant: \'{session.tenant}\'')

        for ip in tqdm(ips, desc='Deleteing Login IPs', leave=False):
            name = ip.get('name')
            #Translate ID
            l_id = ''
            if name in [i.get('name') for i in dst_ips]:
                l_id = [i.get('id') for i in dst_ips if i.get('name') == name]
                if l_id:
                    l_id = l_id[0]
            logger.debug('API - Update login allow IP')
            session.request('DELETE', f'/ip_allow_list_login/{l_id}')
            deleted += 1
    else:
        logger.info(f'No Trusted Login IPs to delete for tenant: \'{session.tenant}\'')

    return deleted
