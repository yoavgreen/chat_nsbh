from logging import getLogger, basicConfig, INFO, DEBUG, Filter
from Utils.config_parser import ConfigConstants as Config
from os import path


class Logger:
    def __init__(self, logger_name: str, debug_mode: str) -> None:
        # Create logger
        self.logger = getLogger(logger_name)
        self.log_file = LoggerConstants.LOG_FILE_NAME
        self.log_file_mode = self.set_log_file_mode(self.log_file)
        # Set level and format
        self.log_level = self.set_log_level(debug_mode)
        self.log_format = LoggerConstants.LOG_FORMAT
        self.date_format = Config.DATE_TIME_FORMAT
        self.logger.addFilter(CustomFilter())
        basicConfig(filename=self.log_file, filemode=self.log_file_mode, level=self.log_level,
                    format=self.log_format, datefmt=self.date_format)

    @staticmethod
    def set_log_file_mode(log_file: str) -> str:

        if path.exists(log_file):
            return 'a'
        else:
            return 'w'

    @staticmethod
    def set_log_level(debug_mode: str) -> int:

        try:
            if debug_mode == Config.TRUE.lower():
                return DEBUG

            return INFO

        except Exception as err:
            raise LoggerError(err)


class CustomFilter(Filter):
    # Server will format this name according to the new connected client
    filter_name = None

    def filter(self, record) -> bool:
        record.custom_attribute = self.filter_name
        return True


class LoggerConstants:

    # Logger Constants
    LOG_FILE_NAME = "chatify.log"
    LOG_FORMAT = "[%(asctime)s] - [%(name)s] - [%(levelname)s] --- %(message)s"


class LoggerError(Exception):
    pass