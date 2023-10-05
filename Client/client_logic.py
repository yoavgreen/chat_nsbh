from socket import error as socket_error
from Socket.custom_socket import CustomSocket, Thread
from Utils.utils import Utils
from Utils.config_parser import ConfigConstants as Config
from logging import getLogger, basicConfig


class Client(CustomSocket):

    def __init__(self, server_ip: str, server_port: int, connection_protocol: str) -> None:
        super().__init__(connection_protocol)
        self.server_ip = server_ip
        self.server_port = server_port
        self.client_socket = super().create_socket()
        self.utils = Utils()
        # Set class logger
        self.logger = getLogger(self.__class__.__name__)
        basicConfig(filename=Config.LOG_FILE_NAME, filemode=self.utils.set_file_mode(Config.LOG_FILE_NAME),
                    format=Config.LOG_FORMAT, datefmt=Config.DATE_TIME_FORMAT)

    def setup(self) -> None:
        try:
            self.client_socket.connect((str(self.server_ip), self.server_port))
            self.logger.info(f"Connected to {self.server_ip}:{self.server_port}")

        except socket_error as err:
            raise ClientError(f"Unable to setup client, Error: {err}.")

    def custom_receive(self):
        while True:

            try:

                msg = self.client_socket.recv(1024).decode(Config.UTF_8)
                print(msg)

            except Exception as err:
                raise ClientError(f"Unable to receive message, Error: {err}")

    def custom_send(self):
        while True:
            try:
                msg = input("")
                self.client_socket.send(msg.encode(Config.UTF_8))
                
            except Exception as err:
                raise ClientError(f"Unable to send message, Error: {err}")

    def run(self):
        try:
            self.setup()

            recv_thread = Thread(target=self.custom_receive)
            recv_thread.start()
            send_thread = Thread(target=self.custom_send)
            send_thread.start()

        except Exception as err:
            self.client_socket.close()
            raise ClientError(f"Unable to run client, Error: {err}.")


class ClientError(Exception):
    pass
