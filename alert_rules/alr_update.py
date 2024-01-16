from sdk.color_print import c_print

def update_alert_rules(session, alert_rules, logger):
    updated = 0
    if alert_rules:
        logger.info(f'Updating Alert Rules for tenant: \'{session.tenant}\'')

        for alert_rule in tqdm(alert_rules, desc='Updating Alert Rules', leave=False):
            alr_id = alert_rule['policyScanConfigId']

            logger.debug('API - Updating Alert Rule')
            session.request('PUT', f'/alert/rule/{alr_id}', json=alert_rule)
            updated += 1
    else:
        logger.info(f'No Alert Rule to update for tenant: \'{session.tenant}\'')

    return updated