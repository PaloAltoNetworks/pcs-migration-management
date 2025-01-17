from tqdm import tqdm

from sdk.load_config import load_config_create_sessions
from sdk.color_print import c_print

from cloud_accounts import cld_sync, cld_sync_thread
from account_groups import acc_sync
from resource_lists import rsc_sync
from user_roles import role_sync
from user_profiles import usr_sync
from ip_allow_lists import ip_sync
from compliance_standards import cmp_sync, cmp_sync_thread
from saved_searches import search_sync
from policies import plc_sync, plc_sync_default
from alert_rules import alr_sync
from anomaly_settings import ano_sync
from enterprise_settings import set_sync

def sync(tenant_sessions: list, modes: dict, use_threading: bool, logger):
    '''
    Accepts the enabled sync modes dictionary and a list of tenant_session objects.
    
    Depending on what sync modes are enabled, calls the sync functions while 
    specifying the operations that are enabled.
    '''

    run_summary = {}

    mode_list = []
    for mode in modes.items():
        mode_list.append(mode[0])

    #ADDING AND UPDATING - Order based on dependencies.
    for mode in tqdm(mode_list, desc='SYNC ADD/UPDATE STATUS'):
        try:
            if 'cloud' == mode:
                added, updated, deleted = (0,0,0)
                if use_threading:
                    added, updated, deleted, cld_sync_data = cld_sync_thread.sync(tenant_sessions, modes['cloud'].get('add', True), modes['cloud'].get('update', True), False, logger)
                else:
                    added, updated, deleted, cld_sync_data = cld_sync.sync(tenant_sessions, modes['cloud'].get('add', True), modes['cloud'].get('update', True), False, logger)

                added, updated, deleted, cld_sync_data = cld_sync.sync(tenant_sessions, modes['cloud'].get('add', True), modes['cloud'].get('update', True), False, logger)
                run_summary.update(added_cloud_accounts=added)
                run_summary.update(updated_cloud_accounts=updated)
                run_summary.update(deleted_cloud_accounts=deleted)
        except Exception as error:
            logger.exception(error)

        try:        
            if 'account' == mode:
                added, updated, deleted, acc_sync_data = acc_sync.sync(tenant_sessions, modes['account'].get('add', True), modes['account'].get('update', True), False, logger)
                run_summary.update(added_account_groups=added)
                run_summary.update(updated_account_groups=updated)
                run_summary.update(deleted_account_groups=deleted)
        except Exception as error:
            logger.exception(error)

        try:        
            if 'resource' == mode:
                added, updated, deleted, rsc_sync_data = rsc_sync.sync(tenant_sessions, modes['resource'].get('add', True), modes['resource'].get('update', True), False, logger)
                run_summary.update(added_resource_lists=added)
                run_summary.update(updated_resource_lists=updated)
                run_summary.update(deleted_resource_lists=deleted)
        except Exception as error:
            logger.exception(error)

        try:    
            if 'role' == mode:
                added, updated, deleted, role_sync_data = role_sync.sync(tenant_sessions, modes['role'].get('add', True), modes['role'].get('update', True), False, logger)
                run_summary.update(added_roles=added)
                run_summary.update(updated_roles=updated)
                run_summary.update(deleted_roles=deleted)
        except Exception as error:
            logger.exception(error)

        try:    
            if 'user' == mode:
                added, updated, deleted, usr_sync_data = usr_sync.sync(tenant_sessions, modes['user'].get('add', True), modes['user'].get('update', True), False, logger)
                run_summary.update(added_profiles=added)
                run_summary.update(updated_profiles=updated)
                run_summary.update(deleted_profiles=deleted)
        except Exception as error:
            logger.exception(error)
        
        try:
            if 'ip' == mode:
                added_networks, added_network_cidrs, added_logins, updated_network_cidrs, updated_logins, deleted_network_cidrs, deleted_logins, ip_sync_data = ip_sync.sync(tenant_sessions, modes['ip'].get('add', True), modes['ip'].get('update', True), False, logger)
                run_summary.update(added_networks=added_networks)
                run_summary.update(added_networks_cidrs=added_network_cidrs)
                run_summary.update(added_login_ips=added_logins)
                run_summary.update(updated_network_cidrs=updated_network_cidrs)
                run_summary.update(updated_login_ips=updated_logins)
                run_summary.update(deleted_network_cidrs=deleted_network_cidrs)
                run_summary.update(deleted_logins=deleted_logins)
        except Exception as error:
            logger.exception(error)
        
        try:
            if 'compliance' == mode:
                added_standards, added_requirements, added_sections, updated_standards, updated_requirements, updated_sections, deleted_standards, deleted_requirements, deleted_sections, cmp_sync_data = (0,0,0,0,0,0,0,0,0,0)
                if use_threading:
                    added_standards, added_requirements, added_sections, updated_standards, updated_requirements, updated_sections, deleted_standards, deleted_requirements, deleted_sections, cmp_sync_data = cmp_sync_thread.sync(tenant_sessions, modes['compliance'].get('add', True), modes['compliance'].get('update', True), False, logger)
                else:
                    added_standards, added_requirements, added_sections, updated_standards, updated_requirements, updated_sections, deleted_standards, deleted_requirements, deleted_sections, cmp_sync_data = cmp_sync.sync(tenant_sessions, modes['compliance'].get('add', True), modes['compliance'].get('update', True), False, logger)
                run_summary.update(added_standards=added_standards)
                run_summary.update(added_requirements=added_requirements)
                run_summary.update(added_sections=added_sections)
                run_summary.update(updated_standards=updated_standards)
                run_summary.update(updated_requirements=updated_requirements)
                run_summary.update(updated_sections=updated_sections)
                run_summary.update(deleted_standards=deleted_standards)
                run_summary.update(deleted_requirements=deleted_requirements)
                run_summary.update(deleted_sections=deleted_sections)
        except Exception as error:
            logger.exception(error)
        
        try:
            if 'search' == mode:
                added_searches, deleted_searches, search_sync_data = search_sync.sync(tenant_sessions, modes['search'].get('add', True), False, logger)
                run_summary.update(added_searches=added_searches)
                run_summary.update(deleted_searches=deleted_searches)
        except Exception as error:
            logger.exception(error)

        try:
            if 'c_policy' == mode:
                added, updated, deleted, plc_sync_data = plc_sync.sync(tenant_sessions, modes['policy'].get('add', True), modes['policy'].get('update', True), False, logger)
                run_summary.update(added_policies=added)
                run_summary.update(updated_policies=updated)
                run_summary.update(deleted_policies=deleted)
        except Exception as error:
            logger.exception(error)

        #FIXME
        try:
            if 'd_policy' == mode:
                updated_default = plc_sync_default.sync_builtin_policies(tenant_sessions, logger)
                run_summary.update(updated_default_policies=updated_default)

        except Exception as error:
            logger.exception(error)

        try:   
            if 'alert' == mode:
                added, updated, deleted, alr_sync_data = alr_sync.sync(tenant_sessions, modes['alert'].get('add', True), modes['alert'].get('update', True), False, logger)
                run_summary.update(added_alerts=added)
                run_summary.update(updated_alerts=updated)
                run_summary.update(deleted_alerts=deleted)
        except Exception as error:
            logger.exception(error)

        try:    
            if 'anomaly' == mode:
                added, updated, deleted, updated_network_settings, updated_ueba_settings, ano_sync_data = ano_sync.sync(tenant_sessions, modes['anomaly'].get('add', True), modes['anomaly'].get('update', True), False, logger)
                run_summary.update(added_anomaly=added)
                run_summary.update(updated_anomaly=updated)
                run_summary.update(deleted_anomaly=deleted)
                run_summary.update(updated_ueba_settings=updated_ueba_settings)
                run_summary.update(updated_network_settings=updated_network_settings)
        except Exception as error:
            logger.exception(error)

        try:   
            if 'settings' == mode:
                updated = set_sync.sync(tenant_sessions, logger)
                run_summary.update(updated_enterprise_settings=updated)
        except Exception as error:
            logger.exception(error)

    #DELETEING - Order based on dependencies
    mode_list = mode_list[::-1]
    #Cloud accounts need to be deleted before account groups
    if 'cloud' in mode_list and 'account' in mode_list:
        mode_list[len(mode_list)-1], mode_list[len(mode_list)-2] = mode_list[len(mode_list)-2], mode_list[len(mode_list)-1]

    for mode in tqdm(mode_list, desc='SYNC DELETE STATUS'):
        try:
            if 'anomaly' == mode:
                if modes['anomaly'].get('delete', False):
                    added, updated, deleted, updated_network_settings, updated_ueba_settings, ano_sync_data = ano_sync.sync(tenant_sessions, False, False, True, logger)
                    run_summary.update(deleted_anomaly=deleted)
        except Exception as error:
            logger.exception(error)

        try:
            if 'alert' == mode:
                if modes['alert'].get('delete', False):
                    added, updated, deleted, alr_sync_data = alr_sync.sync(tenant_sessions, False, False, True, logger)
                    run_summary.update(deleted_alerts=deleted)
        except Exception as error:
            logger.exception(error)
        
        try:
            if 'policy' == mode:
                if modes['policy'].get('delete', False):
                    added, updated, deleted, updated_default, plc_sync_data = plc_sync.sync(tenant_sessions, False, False, True, logger)
                    run_summary.update(deleted_policies=deleted)
        except Exception as error:
            logger.exception(error)
        
        try:
            if 'search' == mode:
                if modes['search'].get('delete', False):
                    added_searches, deleted_searches, search_sync_data = search_sync.sync(tenant_sessions, False, True, logger)
                    run_summary.update(deleted_searches=deleted_searches)
        except Exception as error:
            logger.exception(error)
        
        try:
            if 'compliance' == mode:
                if modes['compliance'].get('delete', False):
                    added_standards, added_requirements, added_sections, updated_standards, updated_requirements, updated_sections, deleted_standards, deleted_requirements, deleted_sections, cmp_sync_data = cmp_sync.sync(tenant_sessions, False, False, True, logger, cmp_sync_data)
                    run_summary.update(deleted_standards=deleted_standards)
                    run_summary.update(deleted_requirements=deleted_requirements)
                    run_summary.update(deleted_sections=deleted_sections)
        except Exception as error:
            logger.exception(error)
        
        try:
            if 'ip' == mode:
                if modes['ip'].get('delete', False):
                    added_networks, added_network_cidrs, added_logins, updated_network_cidrs, updated_logins, deleted_network_cidrs, deleted_logins, ip_sync_data = ip_sync.sync(tenant_sessions, False, False, True, logger)
                    run_summary.update(deleted_network_cidrs=deleted_network_cidrs)
                    run_summary.update(deleted_logins=deleted_logins)
        except Exception as error:
            logger.exception(error)
        
        try:
            if 'user' == mode:
                if modes['user'].get('delete', False):
                    added, updated, deleted, usr_sync_data = usr_sync.sync(tenant_sessions, False, False, True, logger)
                    run_summary.update(deleted_profiles=deleted)
        except Exception as error:
            logger.exception(error)
        
        try:
            if 'role' == mode:
                if modes['role'].get('delete', False):
                    added, updated, deleted, role_sync_data = role_sync.sync(tenant_sessions, False, False, True, logger)
                    run_summary.update(deleted_roles=deleted)
        except Exception as error:
            logger.exception(error)
        
        try:
            if 'resource' == mode:
                if modes['resource'].get('delete', False):
                    added, updated, deleted, rsc_sync_data = rsc_sync.sync(tenant_sessions, False, False, True, logger)
                    run_summary.update(deleted_resource_lists=deleted)
        except Exception as error:
            logger.exception(error)
        
        try:
            if 'cloud' == mode:
                if modes['cloud'].get('delete', False):
                    added, updated, deleted, cld_sync_data = cld_sync.sync(tenant_sessions, False, False, True, logger)
                    run_summary.update(deleted_cloud_accounts=deleted)
        except Exception as error:
            logger.exception(error)

        try:
            if 'account' == mode:
                if modes['account'].get('delete', False):
                    added, updated, deleted, acc_sync_data = acc_sync.sync(tenant_sessions, False, False, True, logger)
                    run_summary.update(deleted_cloud_accounts=deleted)
        except Exception as error:
            logger.exception(error)

    
    c_print('************************', color='green')
    c_print('Finished syncing tenants', color='green')
    c_print('************************', color='green')
    print()

    clone_tenant_sessions = tenant_sessions[1:]
    for index in range(len(clone_tenant_sessions)):
        tenant = clone_tenant_sessions[index]

        added_cloud_accounts = run_summary.get('added_cloud_accounts')
        updated_cloud_accounts = run_summary.get('updated_cloud_accounts')
        deleted_cloud_accounts = run_summary.get('deleted_cloud_accounts')

        added_account_groups = run_summary.get('added_account_groups')
        updated_account_groups = run_summary.get('updated_account_groups')
        deleted_account_groups = run_summary.get('deleted_account_groups')

        added_resource_lists = run_summary.get('added_resource_lists')
        updated_resource_lists = run_summary.get('updated_resource_lists')
        deleted_resource_lists = run_summary.get('deleted_resource_lists')

        added_roles = run_summary.get('added_roles')
        updated_roles = run_summary.get('updated_roles')
        deleted_roles = run_summary.get('deleted_roles')

        added_profiles = run_summary.get('added_profiles')
        updated_profiles = run_summary.get('updated_profiles')
        deleted_profiles = run_summary.get('deleted_profiles')

        added_networks = run_summary.get('added_networks')
        added_networks_cidrs = run_summary.get('added_networks_cidrs')
        added_login_ips = run_summary.get('added_login_ips')
        updated_network_cidrs = run_summary.get('updated_network_cidrs')
        updated_login_ips = run_summary.get('updated_login_ips')
        deleted_network_cidrs = run_summary.get('deleted_network_cidrs')
        deleted_logins = run_summary.get('deleted_logins')

        added_standards = run_summary.get('added_standards')
        added_requirements = run_summary.get('added_requirements')
        added_sections = run_summary.get('added_sections')
        updated_standards = run_summary.get('updated_standards')
        updated_requirements = run_summary.get('updated_requirements')
        updated_sections = run_summary.get('updated_sections')
        deleted_standards = run_summary.get('deleted_standards')
        deleted_requirements = run_summary.get('deleted_requirements')
        deleted_sections = run_summary.get('deleted_sections')

        added_searches = run_summary.get('added_searches')
        deleted_searches = run_summary.get('deleted_searches')

        added_policies = run_summary.get('added_policies')
        updated_policies = run_summary.get('updated_policies')
        updated_default_policies = run_summary.get('updated_default_policies')
        deleted_policies = run_summary.get('deleted_policies')

        added_alerts = run_summary.get('added_alerts')
        updated_alerts = run_summary.get('updated_alerts')
        deleted_alerts = run_summary.get('deleted_alerts')

        added_anomaly = run_summary.get('added_anomaly')
        updated_anomaly = run_summary.get('updated_anomaly')
        deleted_anomaly = run_summary.get('deleted_anomaly')
        updated_network_settings = run_summary.get('updated_network_settings')
        updated_ueba_settings = run_summary.get('updated_ueba_settings')

        updated_enterprise_settings = run_summary.get('updated_enterprise_settings')

        logger.info(f'RUN SUMMARY FOR TENANT {tenant.tenant}')

        logger.info(f'Added {count(added_cloud_accounts, index)} Cloud Accounts')
        logger.info(f'Updated {count(updated_cloud_accounts, index)} Cloud Accounts')
        logger.info(f'Deleted {count(deleted_cloud_accounts, index)} Cloud Accounts')

        logger.info(f'Added {count(added_account_groups, index)} Cloud Account Groups')
        logger.info(f'Updated {count(updated_account_groups, index)} Cloud Acccount Groups')
        logger.info(f'Deleted {count(deleted_account_groups, index)} Cloud Account Groups')

        logger.info(f'Added {count(added_resource_lists, index)} Resource Lists')
        logger.info(f'Updated {count(updated_resource_lists, index)} Resource Lists')
        logger.info(f'Deleted {count(deleted_resource_lists, index)} Resource Lists')

        logger.info(f'Added {count(added_roles, index)} User Roles')
        logger.info(f'Updated {count(updated_roles, index)} User Roles')
        logger.info(f'Deleted {count(deleted_roles, index)} User Roles')

        logger.info(f'Added {count(added_profiles, index)} User Profiles')
        logger.info(f'Updated {count(updated_profiles, index)} User Profiles')
        logger.info(f'Deleted {count(deleted_profiles, index)} User Profiles')

        logger.info(f'Added {count(added_networks, index)} Networks')
        logger.info(f'Added {count(added_networks_cidrs, index)} Network CIDRs')
        logger.info(f'Added {count(added_login_ips, index)} Login IPs')
        logger.info(f'Updated {count(updated_network_cidrs, index)} Network CIDRs')
        logger.info(f'Updated {count(updated_login_ips, index)} Login IPs')
        logger.info(f'Deleted {count(deleted_network_cidrs, index)} Network CIDRs')
        logger.info(f'Deleted {count(deleted_logins, index)} Login IPs')

        logger.info(f'Added {count(added_standards, index)} Compliance Standards')
        logger.info(f'Added {count(added_requirements, index)} Compliance Requirements')
        logger.info(f'Added {count(added_sections, index)} Compliance Sections')
        logger.info(f'Updated {count(updated_standards, index)} Compliance Standards')
        logger.info(f'Updated {count(updated_requirements, index)} Compliance Requirements')
        logger.info(f'Updated {count(updated_sections, index)} Compliance Sections')
        logger.info(f'Deleted {count(deleted_standards, index)} Compliance Standards')
        logger.info(f'Deleted {count(deleted_requirements, index)} Compliance Requirements')
        logger.info(f'Deleted {count(deleted_sections, index)} Compliance Sections')

        logger.info(f'Added {count(added_searches, index)} Saved Searches')
        logger.info(f'Deleted {count(deleted_searches, index)} Saved Searches')

        logger.info(f'Added {count(added_policies, index)} Custom Policies')
        logger.info(f'Updated {count(updated_policies, index)} Custom Policies')
        logger.info(f'Updated {count(updated_default_policies, index)} Default Policies')
        logger.info(f'Deleted {count(deleted_policies, index)} Custom Policies')

        logger.info(f'Added {count(added_alerts, index)} Alert Rules')
        logger.info(f'Updated {count(updated_alerts, index)} Alert Rules')
        logger.info(f'Deleted {count(deleted_alerts, index)} Alert Rules')

        logger.info(f'Updated {count(updated_network_settings, index)} Anomaly Network Settings')
        logger.info(f'Updated {count(updated_ueba_settings, index)} Anomaly UEBA Settings')
        logger.info(f'Added {count(added_anomaly, index)} Anomaly Lists')
        logger.info(f'Updated {count(updated_anomaly, index)} Anomaly Lists')
        logger.info(f'Deleted {count(deleted_anomaly, index)} Anomaly Lists')

        updated_enter_set = count(updated_enterprise_settings, index)
        if updated_enter_set == 0:
            updated_enter_set = False
        logger.info(f'Updated enterprise settings T/F: {updated_enter_set}')

#Helper function for Run Summary
def count(count_list: list, index: int):
    try:
        val = count_list[index]
        return val
    except:
        return 0

if __name__ == '__main__':
    sync()


# DELETION ORDER
# Policies - Saved Search - Users - Roles - Resource Lists - Cloud Accounts - Account Groups
# Cant deleteete an account group that is still linked to a cloud account so cloud accounts must be synced/updated first.
