from datetime import datetime
from Utils.config_parser import ConfigConstants as Config
from uuid import uuid4
from os import path

class Utils:

    @staticmethod
    def last_seen() -> str:
        try:
            now = datetime.now()
            return now.strftime(Config.DATE_TIME_FORMAT)

        except Exception as err:
            raise UtilsError(f"Unable to get current date and time, Error: {err}")

    def generate_client_uuid(self) -> hex:
        """
        Generates a client bytes UUID in a specific size.
        :return: The newly generated client UUID.
        """
        try:
            client_uuid = uuid4().hex
            return client_uuid

        except Exception as err:
            raise UtilsError(f"Unable to generate client UUID, Error: {err}.")

    def set_file_mode(self, file_path: str) -> str:
        try:
            if path.exists(file_path):
                return 'a'
            else:
                return 'w'

        except Exception as err:
            raise UtilsError(f"Unable to set file mode for file '{file_path}', Error: {err}.")


class UtilsError(Exception):
    pass
