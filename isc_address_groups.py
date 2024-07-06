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
    cloudkey = UniFiController(config['controller']['address'],
                               config['controller']['port'],
                               config['controller']['site'])
    
    cloudkey.login(config['controller']['username'],
                   config['controller']['password'])

    current_ip_groups = cloudkey.get_address_groups()
    logging.debug(f'found the existing groups {current_ip_groups}')

    group_name = 'Dynamic - ISC Research Endpoints'
    if group_name not in current_ip_groups:
        research_ips = isc_feeds.get_threat_category('research')
        cloudkey.create_new_address_group(group_name, research_ips)
    else:
        pass # TODO: Update Existing Group

    group_name = 'Dynamic - ISC TOR Exit Nodes'
    if group_name not in current_ip_groups:
        tor_exit_nodes = isc_feeds.get_threat_list('torexit')
        cloudkey.create_new_address_group(group_name, tor_exit_nodes)
    else:
        pass # TODO: Update Existing Group


if __name__ == '__main__':
   main()
