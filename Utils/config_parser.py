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

    LOG_FILE_NAME = "chatify.log"
    LOG_FORMAT = "[%(asctime)s] - [%(name)s] - [%(levelname)s] --- %(message)s"
    DATE_TIME_FORMAT = "%D/%M/%Y %H:%M:%S"
    UTF_8 = 'utf-8'




class ConfigParserError(Exception):
	pass
