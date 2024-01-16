def compare_alert_rules(src_ar: list, dst_ar: list):
    print('++++', len(src_ar), len(dst_ar))
    ar_to_add = []
    # loops through src_ar (source tenant) to find the missing alert rules
    for item in src_ar:
        # skips alert rule named 'Default Alert Rule'
        if item['name'] == 'Default Alert Rule' in [key['name'] for key in dst_ar]:
            continue
        #check if the key 'name' is in both tenants. If not, appends the missing alert rule to a new list
        if item['name'] not in [key['name'] for key in dst_ar]:
            # prints the value of key 'policyScanConfigId' and 'name' of the missing value
            # appends the missing values from src_ar
            ar_to_add.append(item)
    return ar_to_add

def get_alert_rules_to_update(src_alr_rls, src_rsc_lists, src_acc_grps, src_plcs, cln_alr_rls, cln_rsc_lists, cln_acc_grps, cln_plcs):
    alert_rules_to_update = []
    for src_alr in src_alr_rls:
        for cln_alr in cln_alr_rls:
            if src_alr.get('name') == cln_alr.get('name'):
                #Compare RUN types
                if src_alr.get('scanConfigType') == 'STANDARD' and src_alr.get('name') != 'Default Alert Rule':
                    #Get policy names for comparision
                    src_alr_policies = []
                    for src_alr_plc_id in src_alr.get('policies'):
                        for src_plc in src_plcs:
                            if src_plc.get('policyId') == src_alr_plc_id:
                                src_alr_policies.append(src_plc.get('name'))
                    src_alr_policies.sort()
                    
                    #Get account group names for comparison
                    src_alr_grps = []
                    for src_alr_grp_id in src_alr.get('target').get('accountGroups'):
                        for src_acc_grp in src_acc_grps:
                            if src_acc_grp.get('id') == src_alr_grp_id:
                                src_alr_grps.append(src_acc_grp.get('name'))
                    src_alr_grps.sort()

                    src_data = {
                            'description': src_alr.get('description'),
                            'policies': src_alr_policies,
                            'enabled': src_alr.get('enabled'),
                            'accountGroups': src_alr_grps,
                        }

                    #Get 
                    cln_alr_policies = []
                    for cln_alr_plc_id in cln_alr.get('policies'):
                        for cln_plc in cln_plcs:
                            if cln_plc.get('policyId') == cln_alr_plc_id:
                                cln_alr_policies.append(cln_plc.get('name'))
                    cln_alr_policies.sort()
                    
                    #Get account group names for comparison
                    cln_alr_grps = []
                    for cln_alr_grp_id in cln_alr.get('target').get('accountGroups'):
                        for cln_acc_grp in cln_acc_grps:
                            if cln_acc_grp.get('id') == cln_alr_grp_id:
                                cln_alr_grps.append(cln_acc_grp.get('name'))
                    cln_alr_grps.sort()

                    cln_data = {
                            'description': cln_alr.get('description'),
                            'policies': cln_alr_policies,
                            'enabled': cln_alr.get('enabled'),
                            'accountGroups': cln_alr_grps,
                        }

                    if src_data != cln_data:
                        #Update policyScanConfigId
                        src_alr.update(policyScanConfigId=cln_alr.get('policyScanConfigId'))

                        #Update account group IDs
                        acc_ids = []
                        for acc_name in src_data['accountGroups']:
                            for acc in cln_acc_grps:
                                if acc_name == acc.get('name'):
                                    acc_ids.append(acc.get('id'))
                        src_alr['target'].update(accountGroups=acc_ids)

                        #Update policy IDs
                        plc_ids = []
                        for plc_name in cln_data['policies']:
                            for plc in cln_plcs:
                                if plc_name == plc.get('name'):
                                    plc_ids.append(plc.get('policyId'))
                        src_alr.update(policies=plc_ids)

                        alert_rules_to_update.append(src_alr)
                #Compare BUILD type
                #=======================================================================================================
                if src_alr.get('scanConfigType') == 'SHIFTLEFT' and src_alr.get('name') != 'Default Alert Rule':
                    #Get policy names for comparision
                    src_alr_policies = []
                    for src_alr_plc_id in src_alr.get('policies'):
                        for src_plc in src_plcs:
                            if src_plc.get('policyId') == src_alr_plc_id:
                                src_alr_policies.append(src_plc.get('name'))
                    src_alr_policies.sort()
                    
                    #Get resource list names for comparison
                    src_alr_rsc = []
                    for src_rsc_id in src_alr.get('target').get('targetResourceList').get('ids'):
                        for src_rsc in src_rsc_lists:
                            if src_rsc.get('id') == src_rsc_id:
                                src_alr_rsc.append(src_rsc.get('name'))
                    src_alr_rsc.sort()

                    #Create data structure for comparison
                    src_data = {
                            'description': src_alr.get('description'),
                            'policies': src_alr_policies,
                            'enabled': src_alr.get('enabled'),
                            'resourceLists': src_alr_rsc,
                        }

                    #Get policy names for comparision
                    cln_alr_policies = []
                    for cln_alr_plc_id in cln_alr.get('policies'):
                        for cln_plc in cln_plcs:
                            if cln_plc.get('policyId') == cln_alr_plc_id:
                                cln_alr_policies.append(cln_plc.get('name'))
                    cln_alr_policies.sort()
                    
                    #Get resource lists names for comparison
                    cln_alr_rsc = []
                    for cln_rsc_id in cln_alr.get('target').get('targetResourceList').get('ids'):
                        for cln_rsc in cln_rsc_lists:
                            if cln_rsc.get('id') == cln_rsc_id:
                                cln_alr_rsc.append(cln_rsc.get('name'))
                    cln_alr_rsc.sort()

                    #Create data structure for comparision
                    cln_data = {
                            'description': cln_alr.get('description'),
                            'policies': cln_alr_policies,
                            'enabled': cln_alr.get('enabled'),
                            'resourceLists': cln_alr_rsc,
                        }

                    if src_data != cln_data:
                        #Update policyScanConfigId
                        src_alr.update(policyScanConfigId=cln_alr.get('policyScanConfigId'))

                        #Update resource list IDs
                        rsc_ids = []
                        for rsc_name in src_data['resourceLists']:
                            for rsc in cln_rsc_lists:
                                if rsc_name == rsc.get('name'):
                                    rsc_ids.append(rsc.get('id'))
                        src_alr['target']['targetResourceList'].update(ids=rsc_ids)

                        #Update policy IDs
                        plc_ids = []
                        for plc_name in cln_data['policies']:
                            for plc in cln_plcs:
                                if plc_name == plc.get('name'):
                                    plc_ids.append(plc.get('policyId'))
                        src_alr.update(policies=plc_ids)

                        alert_rules_to_update.append(src_alr)

    return alert_rules_to_update


def get_alert_rules_to_delete(src_alerts: list, cln_alerts: list):
    ar_to_del = []
    # loops through src_ar (source tenant) to find the missing alert rules
    for cln_alr in cln_alerts:
        # skips alert rule named 'Default Alert Rule'
        if cln_alr['name'] == 'Default Alert Rule':
            continue
        #check if the key 'name' is in both tenants. If not, appends the missing alert rule to a new list
        if cln_alr['name'] not in [alr['name'] for alr in src_alerts]:
            # prints the value of key 'policyScanConfigId' and 'name' of the missing value
            # appends the missing values from src_ar
            ar_to_del.append(cln_alr)
    return ar_to_del