from cloud_accounts import cld_single_migrate
from account_groups import acc_single_migrate
from resource_lists import rsc_single_migrate
from user_roles import role_single_migrate
from user_profiles import usr_single_migrate
from ip_allow_lists import ip_single_migrate
from compliance_standards import cmp_single_migrate
from saved_searches import search_single_migrate
from policies import plc_single_migrate
from alert_rules import alr_single_migrate
from anomaly_settings import ano_single_migrate

#Used to migrate a single resource based on its ID/UUID
def single_migrate(tenant_sessions, entity_type, uuid, cmp_type, logger):
    try:
        if 'cloud' == entity_type:
            cld_single_migrate.single_migrate(tenant_sessions, uuid, logger)
    except Exception as error:
        logger.exception(error)

    try:        
        if 'account' == entity_type:
            acc_single_migrate.single_migrate(tenant_sessions, uuid, logger)
    except Exception as error:
        logger.exception(error)

    try:        
        if 'resource' == entity_type:
            rsc_single_migrate.single_migrate(tenant_sessions, uuid, logger)
    except Exception as error:
        logger.exception(error)

    try:    
        if 'role' == entity_type:
            role_single_migrate.single_migrate(tenant_sessions, uuid, logger)
    except Exception as error:
        logger.exception(error)

    try:    
        if 'user' == entity_type:
            usr_single_migrate.single_migrate(tenant_sessions, uuid, logger)
    except Exception as error:
        logger.exception(error)
    
    try:
        if 'ip' == entity_type:
            ip_single_migrate.single_migrate(tenant_sessions,uuid, logger)
    except Exception as error:
        logger.exception(error)
    
    try:
        if 'compliance' == entity_type:
            cmp_single_migrate.single_migrate(tenant_sessions, uuid, cmp_type, logger)
    except Exception as error:
        logger.exception(error)
    
    try:
        if 'search' == entity_type:
            search_single_migrate.single_migrate(tenant_sessions, uuid, logger)
    except Exception as error:
        logger.exception(error)

    try:
        if 'policy' == entity_type:
            plc_single_migrate.single_migrate(tenant_sessions, uuid, logger)
    except Exception as error:
        logger.exception(error)

    try:   
        if 'alert' == entity_type:
            alr_single_migrate.single_migrate(tenant_sessions, uuid, logger)
    except Exception as error:
        logger.exception(error)

    try:    
        if 'anomaly' == entity_type:
            ano_single_migrate.single_migrate(tenant_sessions, uuid, logger)
    except Exception as error:
        logger.exception(error)
