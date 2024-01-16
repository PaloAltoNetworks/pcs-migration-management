from sdk.color_print import c_print
from cloud_accounts import cld_migrate, cld_get, cld_compare, cld_update, cld_delete, cld_migrate_thread
import threading

def sync(tenant_sessions: list, addMode: bool, upMode: bool, delMode: bool, logger:object):
    '''Update, add, or delete cloud accounts to normalize all tenants to be the same as the source tenant'''

    added_cloud = []
    updated_cloud = []
    deleted_cloud = []

    if addMode:
        #Migrate missing cloud accounts first using migrate module
        added_cloud = cld_migrate_thread.migrate(tenant_sessions, logger)

    if upMode or delMode:
        #Get all cloud accounts from both tenants
        tenant_accounts = []
        for i in range(len(tenant_sessions)):
            accounts = cld_get.get_names(tenant_sessions[i], logger)
            tenant_accounts.append(accounts)

        #Get the full information for each cloud account
        tenants_cloud_accounts = []
        for i in range(len(tenant_accounts)):

            pool = []
            cloud_accounts_to_upload = []
            cld_acc_threads = break_into_threads(tenant_accounts[i])

            for thread in cld_acc_threads:
                x = threading.Thread(target=cld_get_all_thread, args=(cloud_accounts_to_upload, thread, tenant_sessions, i, logger))
                pool.append(x)
                x.start()

            for index, thread in enumerate(pool):
                thread.join()
                logger.info(f'Thread: \'{index}\' done')


            tenants_cloud_accounts.append(cloud_accounts_to_upload)

        #Sync each tenants cloud accounts
        source_tenant_cloud_accounts = tenants_cloud_accounts[0]
        clone_tenants_cloud_accounts = tenants_cloud_accounts[1:]
        cln_tenant_sessions = tenant_sessions[1:]
        for index in range(len(clone_tenants_cloud_accounts)):
            if upMode:
                accounts_to_update = cld_compare.get_accounts_to_update(source_tenant_cloud_accounts, clone_tenants_cloud_accounts[index], tenant_sessions[0], cln_tenant_sessions[index], logger)
                updated = 0
                session = cln_tenant_sessions[index]
                
                acc_to_update_threads = break_into_threads(accounts_to_update)
                pool = []
                for thread in acc_to_update_threads:
                    x = threading.Thread(target=update_cld_thread, args=(session, thread, updated, logger))
                    pool.append(x)
                    x.start()

                for index, thread in enumerate(pool):
                    thread.join()
                    logger.info(f'Thread: \'{index}\' done')

                updated_cloud.append(updated)
            
            if delMode:
                accounts_to_delete = cld_compare.get_accounts_to_delete(source_tenant_cloud_accounts, clone_tenants_cloud_accounts[index])
                deleted = cld_delete.delete_accounts(cln_tenant_sessions[index], accounts_to_delete, logger)
                deleted_cloud.append(deleted)
            else:
                deleted_cloud.append(0)

    return added_cloud, updated_cloud, deleted_cloud, {}

#==============================================================================
def update_cld_thread(session, accounts_to_update, updated, logger):
    updated += cld_update.update_accounts(session, accounts_to_update, logger)

#==============================================================================
def cld_get_all_thread(cloud_accounts_to_upload, cld_accounts, tenant_sessions, i, logger):
    for j in range(len(cld_accounts)):
        account = cld_accounts[j]
        ret = cld_get.get_all_info(tenant_sessions[i], account, logger)#get info from original tenant
        if ret != '':
            cloud_accounts_to_upload.append(ret)

#==============================================================================
#Break list into equal sized chunks for threading        
def break_into_threads(list_to_break):
    max_threads = 10
    thread_size = len(list_to_break) // max_threads
    if thread_size < 1:
        thread_size = 1
    if max_threads > len(list_to_break):
        max_threads = len(list_to_break)


    thread_list = []
    for i in range(max_threads):
        start = i * thread_size
        end = start + thread_size
        if i + 1 == max_threads:
            items_for_thread = list_to_break[start:]
        else:
            items_for_thread = list_to_break[start:end]
        thread_list.append(items_for_thread)

    return thread_list

if __name__ == '__main__':
    from sdk import load_config
    
    #Generate a API session for each tenant
    tenant_sessions = load_config.load_config_create_sessions()
    
    sync(tenant_sessions, True, True, True)


