#Translate account group IDS
def translate_acc_grp_ids(grp_id, dest_acc_grps, src_acc_grps):
    if grp_id in [a_id['id'] for a_id in src_acc_grps]:
        src_group = [grp for grp in src_acc_grps if grp['id'] == grp_id][0]
        if src_group['name'] in [a_id['name'] for a_id in dest_acc_grps]:
            dst_group = [grp for grp in dest_acc_grps if grp['name'] == src_group['name']][0]
            return dst_group['id']

    return 'BAD'

def translate_rsc_list_ids(rsc_id, dest_rsc_lists, src_rsc_lists):
    if rsc_id in [r_id['id'] for r_id in src_rsc_lists]:
        src_resource = [rsc for rsc in src_rsc_lists if rsc['id'] == rsc_id][0]
        if src_resource['name'] in [a_id['name'] for a_id in dest_rsc_lists]:
            dst_resource = [rsc for rsc in dest_rsc_lists if rsc['name'] == src_resource['name']][0]
            return dst_resource['id']

    return 'BAD'