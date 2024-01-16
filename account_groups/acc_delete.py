from sdk.color_print import c_print

def delete_account_groups(session, account_groups, logger):
    deleted = 0
    if account_groups:
        logger.info(f'Deleting Account Groups from tenant: \'{session.tenant}\'')

        for acc in tqdm(account_groups, desc='Deleteing Account Groups', leave=False):
            grp_id = acc.get('id')
            logger.debug('API - Deleteing Account Group')
            session.request('DELETE', f"/cloud/group/{grp_id}")
            deleted += 1

    else:
        logger.info(f'No Account Groups to delete for tenant: \'{session.tenant}\'')

    return deleted