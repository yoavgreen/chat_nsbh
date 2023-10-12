import json
import sys
from socket import error as socket_error
from Socket.custom_socket import CustomSocket, Thread
from Utils.utils import Utils
from Utils.config_parser import ConfigConstants as Config
from Utils.logger import Logger
from Server.server_logic import ServerConstants


class Client(CustomSocket):

    def __init__(self, server_ip: str, server_port: int, connection_protocol: str,
                 debug_mode: bool, chat_history: bool) -> None:
        super().__init__(connection_protocol)
        self.server_ip = server_ip
        self.server_port = server_port
        self.nickname = None
        self.receive_buffer = 1024
        self.chat_history = chat_history
        self.client_socket = super().create_socket()
        self.utils = Utils()
        # Set class logger
        self.logger = Logger(logger_name=self.__class__.__name__, debug_mode=debug_mode)

    def setup(self) -> None:
        try:
            self.client_socket.connect((str(self.server_ip), self.server_port))
            self.logger.logger.info(f"Connected to {self.server_ip}:{self.server_port}")

        except socket_error as err:
            raise ClientError(f"Unable to setup client, Error: {err}.")

    def receive_all(self):
        while True:
            try:

                msg = self.client_socket.recv(self.receive_buffer).decode(Config.UTF_8)
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

    def handle_registration(self):
        try:

            register_request = self.custom_send_recv(sck=self.client_socket, request=ServerConstants.REQ_REGISTER, response=True)
            print(register_request)
            username = input("Username: ")
            register_response = self.custom_send_recv(sck=self.client_socket, request=username, response=True)

            # Success
            if register_response == ServerConstants.REGISTER_SUCCESS:

                self.nickname = username
                print(ServerConstants.RES_WELCOME)

                # Get chat history
                if self.chat_history:
                    history_request = self.custom_send_recv(sck=self.client_socket, request=ServerConstants.MSG_HISTORY, response=True)
                    print(history_request)

                return True

            # Failed username not available
            if register_response == ServerConstants.REGISTER_FAILED_USERNAME:
                # TODO - implement max number of tries logix
                print(register_response)
                return False

            #  Failed group is full
            if register_response == ServerConstants.REGISTER_FAILED_GRP_FULL:
                print(register_response)
                self.client_socket.close()
                return False

        except Exception as err:
            raise ClientError(f"Unable to handle registration, Error: {err}")

    def start_chat(self):
        try:

            recv_thread = Thread(target=self.receive_all)
            recv_thread.start()
            send_thread = Thread(target=self.send_all)
            send_thread.start()

        except Exception as err:
            raise ClientError(f"Unable to start chat, Error: {err}")

    def run(self):
        try:
            self.setup()

            # Register
            if not self.handle_registration():
                return

            # Enter chat mode and start chat
            self.start_chat()

        except Exception as err:
            self.client_socket.close()
            raise ClientError(f"Unable to run client, Error: {err}.")


class ClientError(Exception):
    pass
