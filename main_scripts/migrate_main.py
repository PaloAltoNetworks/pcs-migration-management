from tqdm import tqdm

from sdk.load_config import load_config_create_sessions
from sdk.color_print import c_print

from cloud_accounts import cld_migrate, cld_migrate_thread
from account_groups import acc_migrate
from resource_lists import rsc_migrate
from user_roles import role_migrate
from user_profiles import usr_migrate
from ip_allow_lists import ip_migrate
from compliance_standards import cmp_migrate, cmp_migrate_thread
from saved_searches import search_sync
from policies import plc_migrate_custom
from policies import plc_migrate_default
from alert_rules import alr_migrate
from enterprise_settings import set_sync
from anomaly_settings import ano_sync

#PROPER ORDER
#Cloud accounts
#Account Groups
#Resource Lists
#User Roles
#Users
#Trusted IPs
#Compliance Standards
#Saved Searches - done by policy
#Policy
#Alert Rules

def migrate(tenant_sessions: list, modes: dict, use_threading: bool, logger: object):
    '''
    Accepts a dictionary of the migrate modes that are enabled and list of tenant session objects.

    Depending on what modes are enabled, call those sync functions.
    '''

    #Checks if element is in the dictionary instead of for a value to keep the data structure
    # similar to the sync modes dictionary.

    mode_list = []
    for mode in modes.items():
        mode_list.append(mode[0])

    run_summary = {}

    for mode in tqdm(mode_list, desc='MIGRATION STATUS'):
        #CLOUD ACCOUNT MIGRATE-------------------------------------------------
        try:
            if 'cloud' == mode:
                added = 0
                if use_threading:
                    added = cld_migrate_thread.migrate(tenant_sessions, logger)
                else:
                    added = cld_migrate.migrate(tenant_sessions, logger)
                run_summary.update(added_cloud_accounts=added)
        except Exception as error:
            logger.exception(error)


        #ACCOUNT GROUPS MIGRATE------------------------------------------------
        try:
            if 'account' == mode:
                added = acc_migrate.migrate(tenant_sessions, logger)
                run_summary.update(added_account_groups=added)
        except Exception as error:
            logger.exception(error)

        #RESOURCE LIST MIGRATE-------------------------------------------------
        try:
            if 'resource' == mode:
                added = rsc_migrate.migrate(tenant_sessions, logger)
                run_summary.update(added_resource_lists=added)
        except Exception as error:
            logger.exception(error)

        #USER ROLES MIGRATE----------------------------------------------------
        try:
            if 'role' == mode:
                added = role_migrate.migrate(tenant_sessions, logger)
                run_summary.update(added_user_roles=added)
        except Exception as error:
            logger.exception(error)

        #USERS MIGRATE---------------------------------------------------------
        try:
            if 'user' == mode:
                added = usr_migrate.migrate(tenant_sessions, logger)
                run_summary.update(added_user_profiles=added)
        except Exception as error:
            logger.exception(error)
        
        #TRUSTED IP MIGRATE----------------------------------------------------
        try:
            if 'ip' == mode:
                tenant_networks_added, tenant_cidrs_added, tenant_login_ips_added = ip_migrate.migrate(tenant_sessions, logger)
                run_summary.update(added_networks=tenant_networks_added)
                run_summary.update(added_cidrs=tenant_cidrs_added)
                run_summary.update(added_login_ips=tenant_login_ips_added)
        except Exception as error:
            logger.exception(error) 

        #COMPLIANCE MIGRATE----------------------------------------------------
        try:
            if 'compliance' == mode:
                standards_added, requirements_added, sections_added = (0,0,0)
                if use_threading:
                    standards_added, requirements_added, sections_added = cmp_migrate_thread.migrate(tenant_sessions, logger)
                else:
                    standards_added, requirements_added, sections_added = cmp_migrate.migrate(tenant_sessions, logger)
                
                run_summary.update(added_compliance_standards=standards_added)
                run_summary.update(added_compliance_requirements=requirements_added)
                run_summary.update(added_compliance_sections=sections_added)
        except Exception as error:
            logger.exception(error)

        #SAVED SEARCH MIGRATE--------------------------------------------------
        try:
            if 'search' == mode:
                added_searches, deleted_searches, search_sync_data = search_sync.sync(tenant_sessions, modes['search'].get('add', True), False, logger)
                run_summary.update(added_searches=added_searches)
                run_summary.update(deleted_searches=deleted_searches)
        except Exception as error:
            logger.exception(error)
        
        #POLICY MIGRATE--------------------------------------------------------
        try:
            if 'c_policy' == mode:
                added = plc_migrate_custom.migrate_custom_policies(tenant_sessions, logger)
                run_summary.update(added_custom_policies=added)
        except Exception as error:
            logger.exception(error)

        #POLICY MIGRATE--------------------------------------------------------
        try:
            if 'd_policy' == mode:
                added = plc_migrate_default.migrate_builtin_policies(tenant_sessions, logger)
                run_summary.update(updated_default_policies=added)
        except Exception as error:
            logger.exception(error)
        
        #ALERT RULES MIGRATE---------------------------------------------------
        try:
            if 'alert' == mode:
                added = alr_migrate.migrate(tenant_sessions, logger)
                run_summary.update(added_alert_rules=added)
        except Exception as error:
            logger.exception(error)
            
        #ANOMALY SETTINGS MIGRATE----------------------------------------------
        try:
            if 'anomaly' == mode:
                added, updated, deleted, updated_network_settings, updated_ueba_settings, ano_sync_data = ano_sync.sync(tenant_sessions, modes['anomaly'].get('add', True), modes['anomaly'].get('update', True), False, logger)
                run_summary.update(added_anomaly=added)
                run_summary.update(updated_anomaly=updated)
                run_summary.update(updated_ueba_settings=updated_ueba_settings)
                run_summary.update(updated_network_settings=updated_network_settings)
        except Exception as error:
            logger.exception(error)

        #Enterprise settings---------------------------------------------------
        try:
            if 'settings' == mode:
                updated = set_sync.sync(tenant_sessions, logger)
                run_summary.update(updated_enterprise_settings=updated)
        except Exception as error:
            logger.exception(error)

    c_print('**************************', color='green')
    c_print('Finished migrating tenants', color='green')
    c_print('**************************', color='green')
    print()

    clone_tenant_sessions = tenant_sessions[1:]
    for index in range(len(clone_tenant_sessions)):
        tenant = clone_tenant_sessions[index]

        added_cloud_accounts = run_summary.get('added_cloud_accounts')

        added_account_groups = run_summary.get('added_account_groups')

        added_resource_lists = run_summary.get('added_resource_lists')

        added_user_roles = run_summary.get('added_user_roles')

        added_user_profiles = run_summary.get('added_user_profiles')

        added_networks = run_summary.get('added_networks')
        added_cidrs = run_summary.get('added_cidrs')
        added_login_ips = run_summary.get('added_login_ips')

        added_compliance_standards = run_summary.get('added_compliance_standards')
        added_compliance_requirements = run_summary.get('added_compliance_requirements')
        added_compliance_sections = run_summary.get('added_compliance_sections')

        added_searches = run_summary.get('added_searches')

        added_custom_policies = run_summary.get('added_custom_policies')

        updated_default_policies = run_summary.get('updated_default_policies')

        added_alert_rules = run_summary.get('added_alert_rules')

        added_anomaly = run_summary.get('added_anomaly')
        updated_anomaly = run_summary.get('updated_anomaly')
        updated_network_settings = run_summary.get('updated_network_settings')
        updated_ueba_settings = run_summary.get('updated_ueba_settings')

        updated_enterprise_settings = run_summary.get('updated_enterprise_settings')

        #Run Summary Output. Outputs to logger and to standard out
        logger.info(f'RUN SUMMARY FOR TENANT {tenant.tenant}')

        logger.info(f'Added {count(added_cloud_accounts, index)} Cloud Accounts')
        logger.info(f'Added {count(added_account_groups, index)} Cloud Account Groups')
        logger.info(f'Added {count(added_resource_lists, index)} Resource Lists')
        logger.info(f'Added {count(added_user_roles, index)} User Roles')
        logger.info(f'Added {count(added_user_profiles, index)} User Profiles')
        logger.info(f'Added {count(added_networks, index)} Trusted Networks')
        logger.info(f'Added {count(added_cidrs, index)} Trusted Network CIDRs')
        logger.info(f'Added {count(added_login_ips, index)} Trusted Login IPs')
        logger.info(f'Added {count(added_compliance_standards, index)} Compliance Standards')
        logger.info(f'Added {count(added_compliance_requirements, index)} Compliance Requirements')
        logger.info(f'Added {count(added_compliance_sections, index)} Compliance Sections')
        logger.info(f'Added {count(added_searches, index)} Saved Searches')
        logger.info(f'Added {count(added_custom_policies, index)} Custom Policies')
        logger.info(f'Updated {count(updated_default_policies, index)} Default Policies')
        logger.info(f'Added {count(added_alert_rules, index)} Alert Rules')

        logger.info(f'Updated {count(updated_network_settings, index)} Anomaly Network Settings')
        logger.info(f'Updated {count(updated_ueba_settings, index)} Anomaly UEBA Settings')
        logger.info(f'Added {count(added_anomaly, index)} Anomaly Lists')
        logger.info(f'Updated {count(updated_anomaly, index)} Anomaly Lists')

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
    migrate()

