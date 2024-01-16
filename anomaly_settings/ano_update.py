from sdk.color_print import c_print
from tqdm import tqdm

def update_settings(session: list, settings: list, logger):
    if settings:
        logger.info('Updating Anomaly Settings')

        items = settings.items()
        for item in items:
            update_setting(session, item[1], item[0], logger)
    else:
        logger.info('No Anomaly Settings to update')

def update_setting(session: object, plc_id: str, setting: dict, logger):
    logger.debug(f'API - Updating policy anomaly setting')
    session.request('POST', f'/anomalies/settings/{plc_id}', json=setting)

def add_trusted_list(session: object, trusted_list: dict, logger):
    logger.debug('API - Adding anomaly trusted list')
    session.request('POST', '/anomalies/trusted_list', json=trusted_list)

def update_trusted_list(session: object, trusted_list: dict, logger):
    ano_id = trusted_list['id']
    logger.debug('API - Updating trusted anomaly list')
    session.request('PUT', f'/anomalies/trusted_list/{ano_id}', json=trusted_list)

def delete_trusted_list(session: object, trusted_list: dict, logger):
    ano_id = trusted_list['id']
    logger.debug('API - Deleting trusted anomaly list')
    session.request('DELETE', f'/anomalies/trusted_list/{ano_id}')
    