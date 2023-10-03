#!/usr/bin/python3
from os import path
from sys import exit
from Server.server_logic import ServerConstants
from Client.client_logic import Client
from Utils.config_parser import create_config_file, load_config_file_to_memory, get_configuration, ConfigParserError


def main():
    # Validate config file
    if not path.exists(path.abspath(ServerConstants.CONFIG_FILE_NAME)):
        try:
            create_config_file(ServerConstants.CONFIG_FILE_NAME, ServerConstants.config_file_template)
        except ConfigParserError as err:
            print(err)
            exit()

    try:
        # Get server configs
        server_configs = load_config_file_to_memory(ServerConstants.CONFIG_FILE_NAME)
        server_ip_address = str(get_configuration(server_configs, ServerConstants.SERVER_IP_ADDRESS))
        server_port = int(get_configuration(server_configs, ServerConstants.SERVER_PORT))
        server_protocol = str(get_configuration(server_configs, ServerConstants.SERVER_PROTOCOL))

        # Setup and run server
        client = Client(server_ip=server_ip_address, server_port=server_port, connection_protocol=server_protocol)
        client.run()

    except Exception as err:
        print(err)
        exit()


if __name__ == "__main__":
    main()