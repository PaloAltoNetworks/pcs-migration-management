from anomaly_settings import ano_get, ano_update, ano_compare
from sdk.color_print import c_print
from tqdm import tqdm

def sync(tenant_sessions: list, addMode: bool, upMode: bool, delMode: bool, logger):
    tenant_added_trusted_lists = []
    updated_network_settings = []
    updated_ueba_settings = []
    updated_lists = []
    deleted_lists = []

    #Get network settings----
    network_settings_list = []
    for session in tenant_sessions:
        data = ano_get.get_all_network_settings(session, logger)
        network_settings_list.append(data)

    if upMode:
        #Get settings to update
        settings_to_update = ano_compare.compare_settings(network_settings_list)

        #Update settings
        updated_network = 0
        for index, tenant in enumerate(settings_to_update):
            for n_setting in tqdm(tenant, desc='Updating Anomaly Network Settings', leave=False):
                ano_update.update_setting(tenant_sessions[index + 1], n_setting[0], n_setting[1], logger)
                updated_network += 1
        updated_network_settings.append(updated_network)

    #Get UEBA settings----
    ueba_settings_list = []
    for session in tenant_sessions:
        data = ano_get.get_all_ueba_settings(session, logger)
        ueba_settings_list.append(data)
    
    if upMode:
        #Get settings to update
        settings_to_update = ano_compare.compare_settings(ueba_settings_list)

        #Update settings
        updated_ueba= 0
        for index, tenant in enumerate(settings_to_update):
            for n_setting in tqdm(tenant, desc='Updating Anomaly UEBA Settings', leave=False):
                ano_update.update_setting(tenant_sessions[index + 1], n_setting[0], n_setting[1], logger)
                updated_ueba += 1
                
        updated_ueba_settings.append(updated_ueba)

    #Update settings

    #Get anomaly trusted lists----
    trusted_lists_list = []
    for session in tenant_sessions:
        data = ano_get.get_trusted_lists(session, logger)
        trusted_lists_list.append(data)

    if addMode:
        #Getting anomaly lists to add
        trusted_lists_to_add = ano_compare.get_lists_to_add(trusted_lists_list)
        added = 0
        for index, tenant in enumerate(trusted_lists_to_add):
            for t_list in tqdm(tenant, desc='Adding Trusted IP Lists', leave=False):
                ano_update.add_trusted_list(tenant_sessions[index + 1], t_list, logger)
                added +=1
        tenant_added_trusted_lists.append(added)
    if upMode:
        updated = 0
        #Get anomaly lists to update
        trusted_lists_to_update = ano_compare.get_lists_to_update(trusted_lists_list)
        for index, tenant in enumerate(trusted_lists_to_update):
            for t_list in tqdm(tenant, desc='Updating Trusted IP Lists', leave=False):
                ano_update.update_trusted_list(tenant_sessions[index + 1], t_list, logger)
                updated += 1
        updated_lists.append(updated)

    if delMode:
        deleted = 0
        #Get anomaly lists to delete
        trusted_lists_to_delete = ano_compare.get_lists_to_delete(trusted_lists_list)
        for index, tenant in enumerate(trusted_lists_to_delete):
            for t_list in tqdm(tenant, desc='Deleteing Trusted IP Lists', leave=False):
                ano_update.delete_trusted_list(tenant_sessions[index + 1], t_list, logger)
                deleted += 1
        deleted_lists.append(deleted)
    else:
        for index in trusted_lists_list[1:]:
            deleted_lists.append(0)

    logger.info('Finished syncing Anomaly Settings')

    return tenant_added_trusted_lists, updated_lists, deleted_lists, updated_network_settings, updated_ueba_settings, {}


if __name__ == '__main__':
    from sdk.load_config import load_config_create_sessions

    tenant_sessions = load_config_create_sessions()

    sync(tenant_sessions, True, True, True)