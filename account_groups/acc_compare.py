def compare_account_groups(src_acc_grps, cln_acc_grps):
    '''
    Compares account groups between the source tenant and a clone tenant.
    Returns the list of account groups missing from the clone tenant
    '''
    acc_grps_to_add = []
    for src_ag in src_acc_grps:
        #Ignore Auto Created
        if src_ag['autoCreated']:
            continue
        if src_ag['name'] not in [cln_ag['name'] for cln_ag in cln_acc_grps]:
            acc_grps_to_add.append(src_ag)

    return acc_grps_to_add


def get_account_groups_to_update(src_acc_grps, cln_acc_grps):
    '''
    Compares attributes of the cloud accounts from both tenants to find differences that need
    to be updated.
    '''
    acc_grps_to_update = []
    for src_ag in src_acc_grps:
        #Ignore Auto Created
        if src_ag['autoCreated']:
            continue
        for cln_ag in cln_acc_grps:
            if src_ag['name'] == cln_ag['name']:
                src_acc_ids = src_ag.get('accountIds')
                src_acc_ids.sort()
                src_data = [
                    {
                    'description': src_ag.get('description'),
                    'nonOnboardedCloudAccountIds': src_ag.get('nonOnboardedCloudAccountIds'),
                    'accountIds': src_acc_ids
                    }
                ]
                cln_acc_ids = cln_ag.get('accountIds')
                cln_acc_ids.sort()
                cln_data = [
                    {
                    'description': cln_ag.get('description'),
                    'nonOnboardedCloudAccountIds': cln_ag.get('nonOnboardedCloudAccountIds'),
                    'accountIds': cln_acc_ids
                    }
                ]

                if src_data != cln_data:
                    src_ag.update(id=cln_ag.get('id'))
                    acc_grps_to_update.append(src_ag)

    return acc_grps_to_update

def get_account_groups_to_delete(src_acc_grps, cln_acc_grps):
    '''
    Compares account groups in the clone tenant to the source tenant. Account groups
    not found in the source tenant that are in the clone tenant will be added to the
    list of accounts to remove.
    '''
    acc_grps_to_delete = []
    for cln_ag in cln_acc_grps:
        #Ignore Auto Created
        if cln_ag['autoCreated']:
            continue
        if cln_ag['name'] not in [src_ag['name'] for src_ag in src_acc_grps]:
            acc_grps_to_delete.append(cln_ag)

    return acc_grps_to_delete
