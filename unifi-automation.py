import logging
import tomllib

from feeds.internet_storm_center import InternetStormCenter
from controller.controller import Controller as UniFiController

def main():
    # read configuration settings
    with open('config.toml', 'rb') as f:
        config = tomllib.load(f)

    # setup logging
    log_level = config['logging']['level'].upper()
    log_level_str = getattr(logging, log_level, logging.INFO)
    logging.basicConfig(format='%(asctime)s | %(levelname)s:%(name)s | %(message)s', level=log_level_str)

    try:
        # create a controller object
        controller = UniFiController(config['controller']['address'],
                                     config['controller']['port'],
                                     config['controller']['site'])
        
        # authenticate to the controller
        controller.login(config['controller']['username'],
                         config['controller']['password'])
        
        # create / update dynamic acls from the internet storm center
        if config['isc-acls']['enabled']:
            isc_feeds = InternetStormCenter()

            address_groups = controller.get_address_groups()
            logging.debug(f'found the existing groups {address_groups}')

            for allowed_feed in config['isc-acls']['allowed']:
                logging.info(f'processing "{allowed_feed}"')
                
                # get feed specific settings
                group_name = config['isc-acls'][allowed_feed]['name']
                api_endpoint = config['isc-acls'][allowed_feed]['endpoint']

                # get addresses from the internet storm center
                isc_ips = isc_feeds.get_api_endpoint(api_endpoint)
            
                # create a new address group, or update the existing one
                if group_name not in address_groups.keys():
                    controller.create_address_group(group_name, isc_ips)
                else:
                    group_id = address_groups[group_name]
                    controller.update_address_group(group_id, group_name, isc_ips)
    finally:
        # logout of the controller
        controller.logout()


if __name__ == '__main__':
   main()
