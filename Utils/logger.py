from logging import getLogger, basicConfig, INFO, DEBUG, Filter
from Utils.config_parser import ConfigConstants as Config
from Utils.utils import Utils


class Logger:
    def __init__(self, logger_name: str, debug_mode: bool) -> None:
        # Create logger
        self.logger = getLogger(logger_name)
        self.utils = Utils()
        self.log_file = LoggerConstants.LOG_FILE_NAME
        self.log_file_mode = 'w'
        # self.log_file_mode = self.utils.set_file_mode(self.log_file)
        # Set level and format
        self.log_level = self.set_log_level(debug_mode)
        self.log_format = LoggerConstants.LOG_FORMAT
        self.date_format = Config.DATE_TIME_FORMAT
        basicConfig(filename=self.log_file, filemode=self.log_file_mode, level=self.log_level,
                    format=self.log_format, datefmt=self.date_format)


    @staticmethod
    def set_log_level(debug_mode: bool) -> int:

        try:
            if debug_mode:
                return DEBUG

            return INFO

        except Exception as err:
            raise LoggerError(err)


class LoggerConstants:

    # Logger Constants
    LOG_FILE_NAME = "chatify.log"
    LOG_FORMAT = "[%(asctime)s] - [%(name)s] - [%(levelname)s] --- %(message)s"


class LoggerError(Exception):
    pass