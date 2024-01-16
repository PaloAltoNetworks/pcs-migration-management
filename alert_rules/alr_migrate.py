from alert_rules import alr_get, alr_compare, alr_add, alr_translate
from account_groups import acc_get
from resource_lists import rsc_get
from policies import plc_get
from sdk.color_print import c_print

def migrate(tenant_sessions, logger):
    '''
    Accepts a list of tenant session.

    For each tenant_session, migrates all alert rules
    '''

    tenant_added_alert_rules = []

    #Get all alert rules
    tenant_alert_rules = []
    tenant_account_groups = []
    tenant_resource_lists = []
    tenant_policies_list = []
    for session in tenant_sessions:
        alerts = alr_get.get_alert_rules(session, logger)
        tenant_alert_rules.append(alerts)
        #Get account groups and resource list for Alert Rule Dependency translation.
        groups = acc_get.get_account_groups(session, logger)
        tenant_account_groups.append(groups)
        resources = rsc_get.get_resource_lists(session, logger)
        tenant_resource_lists.append(resources)

        policies = plc_get.api_get_custom(session, logger)
        dft_policies = plc_get.api_get_default(session, logger)
        all_policies = []
        all_policies.extend(policies)
        all_policies.extend(dft_policies)
        tenant_policies_list.append(all_policies)

    #Get alert rules to add
    tenant_alr_rls_to_add = []
    src_alr_rls = tenant_alert_rules[0]
    tenant_cln_alr_rls = tenant_alert_rules[1:]
    for cln_alr_rls in tenant_cln_alr_rls:
        alerts = alr_compare.compare_alert_rules(src_alr_rls, cln_alr_rls)
        tenant_alr_rls_to_add.append(alerts)

    #Translte IDs in alert rules
    translated_alr_rls_to_add = []
    tenant_cln_acc_grps =  tenant_account_groups[1:]
    tenant_cln_rsc_lists = tenant_resource_lists[1:]
    tenant_cln_policies_lists = tenant_policies_list[1:]
    for i, alr_rls in enumerate(tenant_alr_rls_to_add):
        translated = alr_translate.translate_dependencies(alr_rls, tenant_account_groups[0], tenant_cln_acc_grps[i], tenant_resource_lists[0], tenant_cln_rsc_lists[i], tenant_policies_list[0], tenant_cln_policies_lists[i])
        translated_alr_rls_to_add.append(translated)

    #Add alert rules
    for index, alr_rls in enumerate(translated_alr_rls_to_add):
        session = tenant_sessions[index + 1]
        added = alr_add.add_alert_rules(session, alr_rls, logger)
        tenant_added_alert_rules.append(added)

    logger.info('Finished migrating Alert Rules')

    return tenant_added_alert_rules


if __name__ == '__main__':
    from sdk import load_config
    tenant_sessions = load_config.load_config_create_sessions()
    migrate(tenant_sessions)

    