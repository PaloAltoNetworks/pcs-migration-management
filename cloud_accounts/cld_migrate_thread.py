import threading

from cloud_accounts import cld_get, cld_add, cld_keys, cld_compare

def migrate(tenant_sessions: list, logger: object):
    '''
    Accepts a list of tenant session objects.

    Migrates all cloud accounts from the first tenant, (source tenant)
    to all other tenants (clone tenants).
    '''

    #Get all cloud accounts names from both tenants
    tenant_cloud_account_names = []
    for i in range(len(tenant_sessions)):
        accounts = cld_get.get_names(tenant_sessions[i], logger)
        tenant_cloud_account_names.append(accounts)

    #Get private cloud keys from user
    gcp_account_keys = cld_keys.get_gcp_credentials(tenant_cloud_account_names[0], logger)
    azure_account_keys = cld_keys.get_azure_credentials(tenant_cloud_account_names[0], logger)

    #Compare cloud accounts to determine which accounts to add to new tenant
    tenant_cloud_accounts_to_add = cld_compare.get_accounts_to_add(tenant_sessions, tenant_cloud_account_names, logger)
    
    clone_tenants_cloud_accounts_to_upload = []
    for tenant in tenant_cloud_accounts_to_add:
        #BREAK TENANT_CLOUD_ACCOUNTS_TO_ADD INTO THREAD SECTIONS
        thread_tenant_cloud_accounts_to_add = break_into_threads(tenant)

        #Get additional info about the cloud accounts missing from the clones from the original tenant.
        pool = []

        cloud_accounts_to_upload = []
        for accounts_to_add in thread_tenant_cloud_accounts_to_add:
            #start threads
            x = threading.Thread(target=get_cloud_info_thread, args=(cloud_accounts_to_upload, accounts_to_add, tenant_sessions, logger))
            pool.append(x)
            x.start()

        for index, thread in enumerate(pool):
            thread.join()
            logger.info(f'Thread: \'{index}\' done')
        
        
        clone_tenants_cloud_accounts_to_upload.append(cloud_accounts_to_upload)

    #BREAK clone_tenants_cloud_accounts_to_upload INTO THREAD CHUNKS


    #Upload cloud accounts missing from each tenant
    tenant_accounts_added = []
    for i in range(len(clone_tenants_cloud_accounts_to_upload)):
        thread_accounts_to_add = break_into_threads(clone_tenants_cloud_accounts_to_upload[i])
        
        pool = []
        accounts_added = 0
        for accounts_to_add in thread_accounts_to_add:
            x = threading.Thread(target=add_accounts_thread, args=(accounts_added, tenant_sessions[i+1], accounts_to_add, azure_account_keys, gcp_account_keys, logger))
            pool.append(x)
            x.start()

        for index, thread in enumerate(pool):
            thread.join()
            logger.info(f'Thread \'{index}\' done')

        tenant_accounts_added.append(accounts_added)


    logger.info('Finished migrating Cloud Accounts')

    return tenant_accounts_added

def add_accounts_thread(accounts_added, session, accounts_to_add, azure_account_keys, gcp_account_keys, logger):
    accounts_added += cld_add.add_accounts(session, accounts_to_add, azure_account_keys, gcp_account_keys, logger)



def get_cloud_info_thread(accounts_to_upload, tenant_cloud_accounts_to_add,tenant_sessions, logger):
    for i in range(len(tenant_cloud_accounts_to_add)):
        account = tenant_cloud_accounts_to_add[i]
        ret = cld_get.get_info(tenant_sessions[0], account, logger)#get cloud account info from original tenant
        if ret != '':
            accounts_to_upload.append(ret)

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
    
    migrate(tenant_sessions)