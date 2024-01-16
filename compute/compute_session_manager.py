import time
from sdk.load_config import load_config_create_sessions
import requests


class Compute_Session:
    def __init__(self, tenant_name: str, api_url: str, pc_token: str, logger: object):
        """
        Initializes a Prisma Cloud API session for a given tenant.

        Keyword Arguments:
        tenant_name -- Name of tenant associated with session
        a_key -- Tenant Access Key
        s_key -- Tenant Secret Key
        api_url -- API URL Tenant is hosted on
        """
        self.logger = logger
        self.tenant = tenant_name
        self.api_url = api_url
        self.pc_token = pc_token
        self.token = self.api_login()
        self.headers = {
            'content-type': 'application/json; charset=UTF-8',
            'Authorization': 'Bearer ' + self.token
            }
        self.retries = 6
        self.retry_statuses = [401, 429, 500, 502, 503, 504]
        if self.token != 'BAD':
            logger.info(f'Session created for tenant: {tenant_name}')
        else:
            logger.error(f'Session creation failed for tenant: {tenant_name}')
            logger.info('Exiting...')
            quit()

#==============================================================================

    def api_login(self) -> None:
        '''
        Calls the Prisma Cloud API to generate a x-redlock-auth JWT.

        Returns:
        x-redlock-auth JWT.
        '''

        #Build request
        url = f'{self.api_url}/api/v1/authenticate'
        
        headers = {
            'content-type': 'application/json; charset=UTF-8'
            }

        payload = {
            "username":None,
            "password":None,
            "token":self.pc_token
        }

        self.logger.debug('API - Generating compute session token.')
        response = object()
        try:
            response = requests.request("POST", url, headers=headers, json=payload)
        except:
            self.logger.error('Failed to connect to API.')
            self.logger.warning('Make sure any offending VPNs are disabled.')
            self.logger.info('Exiting...')
            quit()


        #Results
        if response.status_code == 200:
            self.logger.success('SUCCESS')
            data = response.json()

            token = data.get('token')
            self.token = token
            self.headers = {
            'content-type': 'application/json; charset=UTF-8',
            'x-redlock-auth': token
            }
            
            return token
        elif response.status_code == 401:
            self.logger.error('FAILED')
            self.logger.warning('Invalid Login Credentials. Compute JWT not generated.')
            self.token = 'BAD'
            return 'BAD'
        else:
            self.logger.error('FAILED')
            self.logger.error('ERROR Logging In. Compute JWT not generated.')
            self.token = 'BAD'

            self.logger.warning('RESPONSE:')
            self.logger.info(response)
            self.logger.warning('RESPONSE URL:')
            self.logger.info(response.url)
            self.logger.warning('RESPONSE TEXT:')
            self.logger.info(response.text)
            
            return 'BAD'

#==============================================================================

    def api_call_wrapper(self, method: str, url: str, json: dict=None, data: dict=None, params: dict=None, redlock_ignore: list=None, status_ignore: list=[]):
        """
        A wrapper around all API calls that handles token generation, retrying
        requests and API error console output logging.

        Keyword Arguments:
        method -- Request method/type. Ex: POST or GET
        url -- Full API request URL
        data -- Body of the request in a json compatible format
        params -- Queries for the API request

        Returns:
        Respose from API call.

        """
        self.logger.debug(f'{url}')
        res = self.request_wrapper(method, url, headers=self.headers, json=json, data=data, params=params)
        
        if res.status_code == 200 or res.status_code in status_ignore:
            self.logger.success('SUCCESS')
            return res
        
        # if res.status_code == 401:
        #     self.logger.warning('Token expired. Generating new Token and retrying.')
        #     self.api_login()
        #     self.logger.debug(f'{url}')
        #     res = requests.request(method, url, headers=self.headers, json=json, data=data, params=params)

        retries = 0
        while res.status_code in self.retry_statuses and retries < self.retries:
            if res.status_code == 401:
                self.logger.warning('Token expired. Generating new Token and retrying.')
                self.api_login()
            self.logger.warning(f'Retrying request. Code {res.status_code}.')
            self.logger.debug(f'{url}')
            res = self.request_wrapper(method, url, headers=self.headers, json=json, data=data, params=params)
            retries += 1
        
        if res.status_code == 200 or res.status_code in status_ignore:
            self.logger.success('SUCCESS')
            return res

        #Some redlock errors need to be handled elsewhere and don't require this debugging output
        if 'x-redlock-status' in res.headers and redlock_ignore:
            for el in redlock_ignore:
                if el in res.headers['x-redlock-status']:
                    return res

        self.logger.error('FAILED')
        self.logger.error('REQUEST DUMP:')
        self.logger.warning('REQUEST HEADERS:')
        self.logger.info(self.headers)
        self.logger.warning('REQUEST JSON:')
        self.logger.info(json)
        if data:
            self.logger.warning('REQUEST DATA:')
            self.logger.info(data)
        self.logger.warning('REQUEST PARAMS:')
        self.logger.info(params)
        self.logger.warning('RESPONSE:')
        self.logger.info(res)
        self.logger.warning('RESPONSE URL:')
        self.logger.info(res.url)
        self.logger.warning('RESPONSE HEADERS:')
        self.logger.info(res.headers)
        self.logger.warning('RESPONSE REQUEST BODY:')
        self.logger.info(res.request.body)
        self.logger.warning('RESPONSE STATUS:')
        if 'x-redlock-status' in res.headers:
            self.logger.info(res.headers['x-redlock-status'])
        self.logger.warning('RESPONSE TEXT:')
        self.logger.info(res.text)
        self.logger.warning('RESPONSE JSON:')
        if res.text != "":
            for json_data in res.json():
                self.logger.info(json_data)

        return res

#==============================================================================

    def request(self, method: str, endpoint_url: str, json: dict=None, data: dict=None, params: dict=None, redlock_ignore: list=None, status_ignore: list=[]):
        '''
        Function for calling the PC API using this session manager. Accepts the
        same arguments as 'requests.request' minus the headers argument as 
        headers are supplied by the session manager.
        '''
        #Validate method
        method = method.upper()
        if method not in ['POST', 'PUT', 'GET', 'OPTIONS', 'DELETE', 'PATCH']:
            self.logger.warning('Invalid method.')
        
        #Build url
        if endpoint_url[0] != '/':
            endpoint_url = '/' + endpoint_url

        url = f'{self.api_url}{endpoint_url}'

        #Call wrapper
        return self.api_call_wrapper(method, url, json=json, data=data, params=params, redlock_ignore=redlock_ignore, status_ignore=status_ignore)


    def request_wrapper(self, method, url, headers, json, data, params):
        counter = 1
        r = ''
        while r == '' and counter < self.retries:
            counter += 1
            try:
                r = requests.request(method, url, headers=headers, json=json, data=data, params=params)
                return r
            except:
                self.logger.error('Request failed, retrying...')
                time.sleep(3)
                continue
            

        return requests.request(method, url, headers=headers, json=json, data=data, params=params)

def create_sessions(tenant_sessions):
    compute_sessions = []
    for session in tenant_sessions:
        res = session.request('GET', 'meta_info')
        compute_url = res.json()['twistlockUrl']
        
        compute_session = Compute_Session(session.tenant, compute_url, session.token, session.logger)
        compute_sessions.append(compute_session)

    return compute_sessions