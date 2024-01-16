from sdk.color_print import c_print
from sdk.load_config import load_config_create_sessions

class Translate:
    def __init__(self, session, logger):
        logger.debug('API - Getting Policy Compliance data')
        self.new_plc_cmp_standards = session.request('GET', '/policy/compliance').json()
        self.logger = logger

#==============================================================================

    def translate_compliance_id(self, standardName, requirementId, sectionId):
        #translates the compliance ID for the policies.
        #This is in an object so the API getting thelist of old and new
        #compliance standards does not have to be called over and over makeing
        #this process much faster.

        complianceData = ''
        try:
            complianceData = self.new_plc_cmp_standards[standardName]
        except:
            self.logger.error(f'ERROR. Compliance Standard {standardName} not yet migrated')

            return "BAD"

        for el in complianceData:
            if el['requirementId'] == requirementId and el['sectionId'] == sectionId:
                return el['complianceId']
        
        self.logger.error('ERROR. Did not get new ID', color='red')

if __name__ == '__main__':
    tenant_sessions = load_config_create_sessions()
    translate = Translate(tenant_sessions[1], tenant_sessions[0], logger)

    c_print('OLD COMPLIANCE:', color='green')
    print(translate.old_plc_cmp_standards)
    # for el in translate.old_plc_cmp_standards:
    #     print(el)
    #     print()

    print()

    c_print('NEW COMPLIANCE:', color='green')
    print(translate.new_plc_cmp_standards)
    # for el in translate.new_plc_cmp_standards:
    #     print(el)
    #     print()
