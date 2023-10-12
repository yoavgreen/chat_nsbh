from json import dump, load


def create_config_file(file_path: str, data: dict) -> None:
    try:
        with open(file_path, 'w') as cf:
            dump(data, cf, indent=2)

    except Exception as err:
        raise ConfigParserError(f"Unable to create config file '{file_path}', Error: {err}")


def load_config_file_to_memory(config_file: str) -> dict:
    try:
        with open(config_file, 'r') as cf:
            return load(cf)

    except Exception as err:
        raise ConfigParserError(f"Unable to load config file '{config_file}' into memory, Error: {err}")


def get_configuration(data: dict, value: str) -> str:
    try:
        return data[value]

    except Exception as err:
        raise ConfigParserError("Unable to get configuration for value '{value}', Error: {err}.")


# Config Constants
class ConfigConstants:

    # Config constants
    CONFIG_FILE_NAME = "server_config.json"
    TRUE = "true"
    FALSE = "false"
    UTF_8 = 'utf-8'
    GENERIC_LOG = "Generic Log"
    DATE_TIME_FORMAT = "%D/%M/%Y %H:%M:%S"

    SERVER_IP_ADDRESS = "server_ip_address"
    SERVER_PORT = "server_port"
    SERVER_PROTOCOL = "server_protocol"
    DEBUG_MODE = "debug_mode"
    SAVE_CHAT_HISTORY = "save_chat_history"
    LOG_ALL_MESSAGES = "log_all_messages"

    config_file_template = {
        SERVER_IP_ADDRESS: "127.0.0.1",
        SERVER_PORT: 8888,
        SERVER_PROTOCOL: "tcp",
        DEBUG_MODE: "false",
        SAVE_CHAT_HISTORY: "true",
        LOG_ALL_MESSAGES: "false"
    }


class ConfigParserError(Exception):
    pass
