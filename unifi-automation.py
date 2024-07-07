import tomllib

import logging
import logging.handlers

from feeds.internet_storm_center import InternetStormCenter
from controller.controller import UniFiController

def setup_logging(config):
    # create the base logger
    global logger
    logger = logging.getLogger('unifi-automation')
    logger.setLevel(logging.DEBUG)

    # create the base logging format
    formatter = logging.Formatter('%(asctime)s | %(levelname)-7s | %(name)s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    # setup console logging
    if config['logging']['console']['enabled']:
        log_settings = config['logging']['console']

        log_level = getattr(logging,
                            log_settings['level'].upper(),
                            logging.INFO)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # setup file logging
    if config['logging']['file']['enabled']:
        log_settings = config['logging']['file']

        log_level = getattr(logging,
                            log_settings['level'].upper(),
                            logging.INFO)

        file_handler = logging.handlers.TimedRotatingFileHandler('unifi-automation.log',
                                                                 when='midnight',
                                                                 backupCount=30)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # setup email logging
    if config['logging']['email']['enabled']:
        log_settings = config['logging']['email']

        log_level = getattr(logging,
                            log_settings['level'].upper(),
                            logging.INFO)

        email_handler = logging.handlers.SMTPHandler(mailhost=(log_settings['smtp_server'], log_settings['smtp_port']),
                                                     fromaddr=log_settings['sender'],
                                                     toaddrs=log_settings['recipients'],
                                                     subject='UniFi Automation',
                                                     credentials=(log_settings['smtp_username'], log_settings['smtp_password']),
                                                     secure=())
        email_handler.setLevel(log_level)
        email_handler.setFormatter(formatter)
        logger.addHandler(email_handler)

def dynamic_isc_acls(controller, config):
    isc_feeds = InternetStormCenter()

    address_groups = controller.get_address_groups()
    logger.debug(f'found the existing groups {address_groups}')

    for allowed_feed in config['isc-acls']['allowed']:
        logger.info(f'processing "{allowed_feed}"')

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

def main():
    # read configuration settings
    with open('config.toml', 'rb') as f:
        config = tomllib.load(f)

    setup_logging(config)

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
            dynamic_isc_acls(controller, config)
    finally:
        # logout of the controller
        controller.logout()


if __name__ == '__main__':
   main()
