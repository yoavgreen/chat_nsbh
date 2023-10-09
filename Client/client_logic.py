import json
from socket import error as socket_error
from Socket.custom_socket import CustomSocket, Thread
from Utils.utils import Utils
from Utils.config_parser import ConfigConstants as Config
from logging import getLogger, basicConfig
from Server.server_logic import ServerConstants


class Client(CustomSocket):

    def __init__(self, server_ip: str, server_port: int, connection_protocol: str) -> None:
        super().__init__(connection_protocol)
        self.server_ip = server_ip
        self.server_port = server_port
        self.nickname = None
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

    def receive_all(self):
        while True:

            try:
                msg = self.client_socket.recv(1024).decode(Config.UTF_8)
                print(msg)

            except Exception as err:
                raise ClientError(f"Unable to receive message, Error: {err}")

    def send_all(self):
        while True:
            try:

                msg = input("")
                self.client_socket.send(f"{self.nickname}: {msg}".encode(Config.UTF_8))

            except Exception as err:
                raise ClientError(f"Unable to send message, Error: {err}")

    def unpack(self, decoded_packet: str):
        try:
            for key, value in json.loads(decoded_packet).items():
                return key, value

        except Exception as err:
            raise ClientError(f"Unable to unpack packet from server, Error: {err}")

    def register(self) -> bool:
        try:
            # Register
            enter_server = self.client_socket.recv(1024).decode(Config.UTF_8)
            key, value = self.unpack(enter_server)

            if key == ServerConstants.REGISTER:
                print(value)
                username = input("")
                self.nickname = username
                self.client_socket.send(username.encode(Config.UTF_8))
                result = self.client_socket.recv(1024).decode(Config.UTF_8)
                if result == ServerConstants.REGISTER_SUCCESS:
                    return True

            return False

        except Exception as err:
            raise ClientError(f"Unable to register, Error: {err}")

    def run(self):
        try:
            self.setup()

            if self.register():

                recv_thread = Thread(target=self.receive_all)
                recv_thread.start()
                send_thread = Thread(target=self.send_all)
                send_thread.start()

            else:
                print("Registration Failed.")

        except Exception as err:
            self.client_socket.close()
            raise ClientError(f"Unable to run client, Error: {err}.")


class ClientError(Exception):
    pass
