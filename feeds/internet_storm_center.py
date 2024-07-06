import logging
import requests

from ipaddress import IPv4Address
from ipaddress import collapse_addresses

class InternetStormCenter:

    def __init__(self,):
        pass

    def get_threat_category(self, category):
        response = requests.get(f'https://isc.sans.edu/api/threatcategory/{category}?json')
        return self.process_response(response)
    
    def get_threat_list(self, list):
        response = requests.get(f'https://isc.sans.edu/api/threatlist/{list}?json')
        return self.process_response(response)

    def process_response(self, response):
        """Connect to an Internet Storm Center REST API, obtain IPv4 addresses of interest,
        condense and convert them in CIDR block, and return addresses as either plain IPs (for /32)
        or network block with CIDR prefixes"""

        logging.debug(f'ICS API HTTP Response: {response.status_code}')

        if response.status_code == requests.codes.ok:
            response_content = response.json()

            # convert addresses into IPv4 objects
            network_addresses = [IPv4Address(x['ipv4']) for x in response_content]

            # condense addresses into CIDR blocks
            condensed_addresses = collapse_addresses(network_addresses)

            # remove /32 prefixes as the controller doesn't like it
            return [x.with_prefixlen.replace('/32', '') for x in  condensed_addresses]