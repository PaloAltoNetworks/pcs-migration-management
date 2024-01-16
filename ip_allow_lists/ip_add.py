from sdk.color_print import c_print
from tqdm import tqdm

def add_networks(session, networks, logger):
    '''
    Accepts a tenant session object and a list of networks.

    Adds each network and then dispatches function to add the network cidrs
    '''

    added = 0

    if networks:
        logger.info(f'Adding Trusted Alert IP Networks to tenant: \'{session.tenant}\'')

        for network in tqdm(networks, desc='Adding Networks', leave=False):
            logger.debug('API - Adding Trusted Alert IP Network')
            res = session.request('POST', '/allow_list/network', json=network)
            added += 1
            if res.status_code == 200 or res.status_code == 201:
                data = res.json()
                add_network_cidrs(session, data, network.get('cidrs'), logger)
    else:
        logger.info(f'No Trusted Alert IP Networks to add for tenant: \'{session.tenant}\'')

    return added

#==============================================================================

def add_network_cidrs(session, network, cidrs, logger):
    '''
    Accepts a tenant session, network and a cidr lists.

    Adds network ciders to each given network.
    '''
    if cidrs:
        logger.info(f'Adding Network CIDRs to tenant: \'{session.tenant}\'')

        networkUuid = network.get('uuid')
        name = network['name']
        for cidr in tqdm(cidrs, desc='Adding Network CIDRs', leave=False):
            #upload each cider in a network
            logger.debug(f'API - Adding cidr blocks to network{name}')
            session.request('POST', f'allow_list/network/{networkUuid}/cidr', json=cidr, redlock_ignore=['duplicate_public_network'])
            # session.request('POST', f'network/{networkUuid}/cidr', json=cidr, redlock_ignore=['duplicate_public_network'])
    else:
        logger.info(f'No Network Cidrs to add for tenant: \'{session.tenant}\'')


#==============================================================================

def add_network_allow_list_cidrs(session, net_uuid, cidrs, logger):
    '''
    Accepts a tenant session, the network uuid, and a list of cidrs.

    Adds all cidr blocks to the network with the provided UUID.
    '''

    added = 0

    if cidrs:
        for cidr in tqdm(cidrs, desc='Adding CIDRs to network', leave=False):
            logger.debug('API - Adding CIDRs to network')
            res = session.request('POST', f'/allow_list/network/{net_uuid}/cidr', json=cidr)
            if res.status_code == 200 or res.status_code == 201:
                added += 1

    return added



def add_login_ips(session, ips, logger):
    '''
    Accepts a tenant session and a list of Login Allow IPs.

    Adds the Login Allow IPs.
    '''
    added = 0
    if ips:
        logger.info(f'Adding Login IPs to tenant: \'{session.tenant}\'')

        for ip in ips:
            logger.debug('API - Adding login allow IP')
            session.request('POST', '/ip_allow_list_login', json=ip)
            added += 1
    else:
        logger.info(f'No Login IPs to add for tenant: \'{session.tenant}\'')

    return added