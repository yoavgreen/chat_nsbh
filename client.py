#!/usr/bin/python3
from os import path
from sys import exit
from Client.client_logic import Client
from Utils.config_parser import (create_config_file, load_config_file_to_memory, get_configuration,
                                 ConfigParserError, ConfigConstants as Config)
from Utils.utils import Utils


def main():
    # Validate config file
    if not path.exists(path.abspath(Config.CONFIG_FILE_NAME)):
        try:
            create_config_file(Config.CONFIG_FILE_NAME, Config.config_file_template)
        except ConfigParserError as err:
            print(err)
            exit()

    try:

        utils = Utils()

        # Get server configs
        server_configs = load_config_file_to_memory(Config.CONFIG_FILE_NAME)
        server_ip_address = str(get_configuration(server_configs, Config.SERVER_IP_ADDRESS))
        server_port = int(get_configuration(server_configs, Config.SERVER_PORT))
        server_protocol = str(get_configuration(server_configs, Config.SERVER_PROTOCOL))
        debug_mode = utils.set_config_mode(str(get_configuration(server_configs, Config.DEBUG_MODE)))
        chat_history = utils.set_config_mode(str(get_configuration(server_configs, Config.SAVE_CHAT_HISTORY)))

        # Setup and run server
        client = Client(server_ip=server_ip_address, server_port=server_port,
                        connection_protocol=server_protocol, debug_mode=debug_mode,
                        chat_history=chat_history)
        client.run()

    except Exception as err:
        print(err)
        exit()


if __name__ == "__main__":
    main()
