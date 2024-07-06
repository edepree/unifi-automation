import logging
import configparser

from feeds.internet_storm_center import InternetStormCenter
from controller.controller import Controller as UniFiController

def main():
    # read configuration settings
    config = configparser.ConfigParser()
    config.read('config.ini')

    # setup logging
    log_level = config['logging']['level'].upper()
    log_level_str = getattr(logging, log_level, logging.INFO)

    logging.basicConfig(format='%(asctime)s | %(levelname)s:%(name)s | %(message)s', level=log_level_str)

    isc_feeds = InternetStormCenter()

    try:
        cloudkey = UniFiController(config['controller']['address'],
                                   config['controller']['port'],
                                   config['controller']['site'])
        
        cloudkey.login(config['controller']['username'],
                       config['controller']['password'])

        current_ip_groups = cloudkey.get_address_groups()
        logging.debug(f'found the existing groups {current_ip_groups}')

        group_name = 'Dynamic - ISC Research Endpoints'
        logging.info(f'processing "{group_name}"')
        research_ips = isc_feeds.get_threat_category('research')

        if group_name not in current_ip_groups.keys():
            cloudkey.create_address_group(group_name, research_ips)
        else:
            group_id = current_ip_groups[group_name]
            cloudkey.update_address_group(group_id, group_name, research_ips)

        group_name = 'Dynamic - ISC TOR Exit Nodes'
        logging.info(f'processing "{group_name}"')
        tor_exit_nodes = isc_feeds.get_threat_list('torexit')

        if group_name not in current_ip_groups:    
            cloudkey.create_address_group(group_name, tor_exit_nodes)
        else:
            group_id = current_ip_groups[group_name]
            cloudkey.update_address_group(group_id, group_name, tor_exit_nodes)
    finally:
        cloudkey.logout


if __name__ == '__main__':
   main()
