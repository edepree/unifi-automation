import json
import logging
import requests

class Controller:
    def __init__(self, address, port, site):
        # base url
        self.controller_url = f'https://{address}:{port}'

        self.session = requests.Session()

        self.headers = {'Content-Type': 'application/json'}
        
        # allow self signed certificates
        self.session.verify = False
        requests.packages.urllib3.disable_warnings()

        # reused api endpoint
        self.firewall_groups_url = f'{self.controller_url}/proxy/network/api/s/{site}/rest/firewallgroup'

    def __del__(self):
        logging.debug('logging out')
        self.logout()
        logging.debug('closing session')
        self.session.close()

    def process_response(self, response):
        """A simple helper function for processing requests from the UniFi controller."""
        logging.debug(f'UniFi Controller API HTTP Response: {response.status_code}')

        if response.status_code == requests.codes.ok:
            if response.headers.get('X-CSRF-Token'):
                self.headers.update({'X-CSRF-Token': response.headers['X-CSRF-Token']})
        else:
            raise
    
    def login(self, username, password):
        logging.debug(f'authenticating to "{self.controller_url}" as "{username}"')

        login_url = f'{self.controller_url}/api/auth/login'

        response = self.session.post(login_url,
                                     headers=self.headers,
                                     data=json.dumps({'username': username,
                                                      'password': password}))

        self.process_response(response)

    def logout(self):
        logout_url = f'{self.controller_url}/api/auth/logout'

        response = self.session.post(logout_url, headers=self.headers)

        self.process_response(response)

    def get_address_groups(self):
        response = self.session.get(self.firewall_groups_url, headers=self.headers)

        self.process_response(response)

        return [x['name'] for x in response.json()['data'] if x['group_type'] == 'address-group']
    
    def create_new_address_group(self, name, members):
        logging.debug(f'adding the group {name}')

        data = {'name': name,
                'group_type': 'address-group',
                'group_members': members}

        response = self.session.post(self.firewall_groups_url,
                                     headers=self.headers,
                                     data=json.dumps(data))
        
        self.process_response(response)