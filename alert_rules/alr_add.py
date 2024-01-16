from sdk.color_print import c_print
from tqdm import tqdm

def add_alert_rules(session, alert_rules, logger):
    added = 0
    if alert_rules:
        logger.info(f'Adding Alert Rules for tenant: \'{session.tenant}\'')

        for alr in tqdm(alert_rules, desc='Adding Alert Rules', leave=False):
            logger.debug('API - Adding Alert Rule')
            res = session.request("POST", "/alert/rule", json=alr)
            if res.status_code == 201 or res.status_code == 200:
                added += 1

    else:
        logger.info(f'No Alert Rules to add for tenant: \'{session.tenant}\'')

    return added