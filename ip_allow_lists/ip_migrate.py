from ip_allow_lists import ip_add, ip_compare, ip_get
from sdk.color_print import c_print

def migrate(tenant_sessions, logger):
    '''
    Accepts a list of tenant session object.

    Migrates Trusted Alert IPs and Trusted Login IPs from source tenants to clone tenants.
    '''

    tenant_networks_added = []
    tenant_cidrs_added = []
    tenant_login_ips_added = []

    #Migrate Trusted Alert IP Networks first

    #Get trusted network ips from all tenants
    tenant_trusted_alert_networks = []
    for session in tenant_sessions:
        networks = ip_get.get_trusted_networks(session, logger)
        tenant_trusted_alert_networks.append(networks)

    #Get trusted network IPs that need to be added
    trusted_alert_networks_to_add = []
    src_networks = tenant_trusted_alert_networks[0]
    tenant_cln_networks = tenant_trusted_alert_networks[1:]
    for cln_networks in tenant_cln_networks:
        delta = ip_compare.compare_trusted_networks(src_networks, cln_networks)
        trusted_alert_networks_to_add.append(delta)

    #Upload the trusted alert IP networks to clone tenants
    for index, networks in enumerate(trusted_alert_networks_to_add):
        session = tenant_sessions[index + 1]
        added = ip_add.add_networks(session, networks, logger)
        tenant_networks_added.append(added)

    #Updated the lists of networks after one or more has been added.
    #Get trusted network ips from all tenants
    tenant_trusted_alert_networks = []
    for session in tenant_sessions:
        networks = ip_get.get_trusted_networks(session, logger)
        tenant_trusted_alert_networks.append(networks)

    #Update the cidr blocks of all networks in each tenant
    #Define lists
    source_tenant = tenant_trusted_alert_networks[0]
    clone_tenants = tenant_trusted_alert_networks[1:]
    for index, tenant in enumerate(clone_tenants):
        added = 0
        for src_network in source_tenant:
            #Check if all cidr blocks are present
            new_network = [network for network in tenant if network.get('name') == src_network.get('name')][0]
            if not new_network:
                #network would have just been added, can't update it here
                break
            cidr_to_add = []
            for cidr in src_network.get('cidrs'):
                if cidr.get('cidr') not in [n_cidr.get('cidr') for n_cidr in new_network.get('cidrs')]:
                    cidr_to_add.append(cidr)
            net_name = src_network.get('name')
            added += ip_add.add_network_allow_list_cidrs(tenant_sessions[index + 1], new_network.get('uuid'), cidr_to_add, logger)
        tenant_cidrs_added.append(added)


    #Next, migrate Trusted Login IPs

    #Get login ips
    tenant_login_ips_list = []
    for session in tenant_sessions:
        ips = ip_get.get_login_ips(session, logger)
        tenant_login_ips_list.append(ips)

    #Get the login ips that need to be added
    tenant_login_ips_to_add = []
    src_login_ips = tenant_login_ips_list[0]
    tenant_cln_login_ips = tenant_login_ips_list[1:]
    for cln_login_ips in tenant_cln_login_ips:
        delta = ip_compare.compare_login_ips(src_login_ips, cln_login_ips)
        tenant_login_ips_to_add.append(delta)

    #Upload login IPs to clone tenants
    for index, cln_ips in enumerate(tenant_login_ips_to_add):
        tenant_session = tenant_sessions[index + 1]
        added = ip_add.add_login_ips(tenant_session, cln_ips, logger)
        tenant_login_ips_added.append(added)

    logger.info('Finished Migrating Trusted IPs')

    return tenant_networks_added, tenant_cidrs_added, tenant_login_ips_added

if __name__ == '__main__':
    from sdk.load_config import load_config_create_sessions
    tenant_sessions = load_config_create_sessions()
    migrate(tenant_sessions)
    