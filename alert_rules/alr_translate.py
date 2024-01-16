def translate_dependencies(alr_rls, src_acc_grps, cln_acc_grps, src_rsc_lists, cln_rsc_lists, src_plcs, cln_plcs):
    for ar in alr_rls:
        #Account Groups
        acc_grp_ids = ar.get('target', {}).get('accountGroups', [])
        translated_acc_grp_ids = translate_acc_groups(acc_grp_ids, src_acc_grps, cln_acc_grps)
        ar['target']['accountGroups'] = translated_acc_grp_ids

        #Target Resource List
        if 'targetResourceList' in ar['target']:
            rsc_list_ids = ar.get('target', {}).get('targetResourceList', {}).get('ids', [])
            translated_rsc_list_ids = translate_rsc_lists(rsc_list_ids, src_rsc_lists, cln_rsc_lists)
            ar['target']['targetResourceList']['ids'] = translated_rsc_list_ids

        if 'policies' in ar:
            plc_ids = ar.get('policies', [])
            translated_plc_ids = translate_plcs(plc_ids, src_plcs, cln_plcs)
            ar['policies'] = translated_plc_ids

    return alr_rls


def translate_acc_groups(acc_grp_ids, src_acc_grps, cln_acc_grps):
    translated_ids = []
    for acc_id in acc_grp_ids:
        src_acc_name = [acc['name'] for acc in src_acc_grps if acc['id'] == acc_id]
        if src_acc_name:
            name = src_acc_name[0]
            cln_acc_id = [acc['id'] for acc in cln_acc_grps if acc['name'] == name]
            if cln_acc_id:
                #only append the transalted ID if it is found
                translated_ids.append(cln_acc_id[0])
            else:
                translated_ids.append(acc_id)
        else:
            translated_ids.append(acc_id)

    return translated_ids


def translate_rsc_lists(rsc_list_ids, src_rsc_lists, cln_rsc_lists):
    translated_ids = []
    for rsc_id in rsc_list_ids:
        src_rsc_name = [rsc['name'] for rsc in src_rsc_lists if rsc['id'] == rsc_id]
        if src_rsc_name:
            name = src_rsc_name[0]
            cln_rsc_id = [rsc['id'] for rsc in cln_rsc_lists if rsc['name'] == name]
            if cln_rsc_id:
                translated_ids.append(cln_rsc_id[0])
            else:
                translated_ids.append(rsc_id)
        else:
            translated_ids.append(rsc_id)

    return translated_ids

def translate_plcs(plc_ids, src_plcs, cln_plcs):
    translated_ids = []
    for plc_id in plc_ids:
        src_plc_name = [plc['name'] for plc in src_plcs if plc['policyId'] == plc_id]
        if src_plc_name:
            name = src_plc_name[0]
            cln_plc_id = [plc['policyId'] for plc in cln_plcs if plc['name'] == name]
            if cln_plc_id:
                translated_ids.append(cln_plc_id[0])
            else:
                translated_ids.append(plc_id)
        else:
            translated_ids.append(plc_id)

    return translated_ids