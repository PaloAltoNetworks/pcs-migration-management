from sdk.color_print import c_print
from tqdm import tqdm

def delete_alert_rules(session, alert_rules, logger):
    deleted = 0
    if alert_rules:
        logger.info(f'Deleteing Alert Rules from tenant: \'{session.tenant}\'')

        for alert in tqdm(alert_rules, desc='Deleting Alert Rules', leave=False):
            alr_id = alert['policyScanConfigId']
            status_ignore = [201, 204]
            logger.debug('Deleteing Alert Rule')
            session.request("DELETE", f"/alert/rule/{alr_id}", status_ignore=status_ignore)
            deleted += 1

    else:
        logger.info(f'No Alert Rules to delete from tenant: \'{session.tenant}\'')

    return deleted