from Socket.custom_socket import socket, socket_error, CustomSocket, Thread
from socket import SOL_SOCKET, SO_REUSEADDR
from Utils.utils import Utils
from Utils.config_parser import create_config_file, load_config_file_to_memory, ConfigConstants as Config
from Utils.logger import Logger
from typing import Optional, Any
from os import path


# TODO - keepalive, if connection has been reset by peer, log and keep running
# TODO - Config package to hold all config files

class Server(CustomSocket):
    def __init__(self, server_ip: str, server_port: int, connection_protocol: str,
                 debug_mode: bool, save_chat_history: bool, log_all_messages: bool) -> None:
        super().__init__(connection_protocol)
        self.server_ip = server_ip
        self.server_port = server_port
        self.save_msg_history = save_chat_history
        self.log_all_messages = log_all_messages
        self.connected_sockets = []  # For the connected sockets only
        self.registered_clients = []  # For the entire connected clients
        self.active_connections = 0  # For the current active connections
        self.receive_buffer = 1024
        self.chat_history = []
        # Create server socket in the constructor
        self.server_socket = super().create_socket()
        self.utils = Utils()
        # Set class logger
        self.logger = Logger(logger_name=self.__class__.__name__, debug_mode=debug_mode)

    def setup(self) -> None:
        try:
            # Get server configs
            if not path.exists(ServerConstants.SERVER_CONFIG_FILE):
                create_config_file(file_path=ServerConstants.SERVER_CONFIG_FILE, data=ServerConstants.server_configs_template)

            # Insert to server RAM DB
            root_ram_template = ServerConstants.ram_clients_template.copy()
            server_configs = load_config_file_to_memory(ServerConstants.SERVER_CONFIG_FILE)
            root_ram_template[ServerConstants.CLIENT_NAME] = server_configs[ServerConstants.ROOT_USER]
            root_ram_template[ServerConstants.CLIENT_PASSWORD] = server_configs[ServerConstants.ROOT_PASSWORD]
            self.registered_clients.append(root_ram_template)

            # Reuse the socket port number
            self.server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

            # Bind server socket
            self.server_socket.bind((str(self.server_ip), self.server_port))

            # Start listen to incoming connections
            self.server_socket.listen()

        except socket_error as err:
            raise ServerError(f"Unable to setup server, Error: '{err}'.")

    def add_new_client(self, client: socket, clients_ram_template: dict) -> None:
        try:
            self.connected_sockets.append(client)
            self.registered_clients.append(clients_ram_template)
            self.active_connections += 1
            self.logger.logger.info(f"Added new client '{clients_ram_template[ServerConstants.CLIENT_NAME]}' successfully.")
            print(f"{clients_ram_template[ServerConstants.CLIENT_NAME]} has registered successfully.")

        except Exception as err:
            raise ServerError(f"Unable to add new client, Error: {err}")

    def handle_registration(self, client: socket, clients_ram_template: dict):
        try:

            # Get client username
            username = self.custom_send_recv(sck=client, request=ServerConstants.RES_REGISTER, response=True)

            # Root user
            if username == ServerConstants.server_configs_template[ServerConstants.ROOT_USER]:
                password = self.custom_send_recv(sck=client, request=ServerConstants.REGISTER_ROOT, response=True)
                if not self.fetch_data(ServerConstants.CLIENT_PASSWORD, value=password):
                    # TODO - implement max number of tries logic
                    self.custom_send_recv(sck=client, request=ServerConstants.REGISTER_FAILED_PASSWORD, response=False)

            # Banned user
            if self.fetch_data(column=ServerConstants.CLIENT_IS_BANNED, value=username):
                pass

            # Invalid username
            if self.fetch_data(column=ServerConstants.CLIENT_NAME, value=username):
                self.custom_send_recv(sck=client, request=ServerConstants.REGISTER_FAILED_USERNAME)

            # Max connections
            elif self.active_connections > 16:
                self.custom_send_recv(sck=client, request=ServerConstants.REGISTER_FAILED_GRP_FULL)

            # Register client
            else:
                clients_ram_template[ServerConstants.CLIENT_SOCKET] = client
                clients_ram_template[ServerConstants.CLIENT_NAME] = username
                clients_ram_template[ServerConstants.CLIENT_ID] = self.utils.generate_client_uuid()
                self.add_new_client(client, clients_ram_template)
                self.custom_send_recv(sck=client, request=ServerConstants.REGISTER_SUCCESS)

                # Broadcast to all chat members without the new registered client
                self.broadcast(msg=f"{username} has entered the chat.", connection_to_ignore=client)

        except Exception as err:
            raise ServerError(f"Unable to register client, Error: {err}")

    def handle_client(self, client: socket) -> None:
        try:
            # Create A RAM data copy
            clients_ram_template = ServerConstants.ram_clients_template.copy()
            clients_ram_template[ServerConstants.CLIENT_LAST_SEEN] = self.utils.last_seen()

            request = client.recv(self.receive_buffer).decode(Config.UTF_8)
            print(request)
            # Register
            if request == ServerConstants.REQ_REGISTER:
                self.handle_registration(client, clients_ram_template)

            # Get chat history
            if request == ServerConstants.MSG_HISTORY:
                self.custom_send_recv(sck=client, request="\n".join(self.chat_history), response=False)

            # Chat mode
            while True:
                msg = client.recv(self.receive_buffer).decode(Config.UTF_8)

                # Save all chat history
                if self.save_msg_history:
                    self.chat_history.append(msg)

                # Log all messages
                if self.log_all_messages:
                    self.logger.logger.info(f"Received: {msg} from {str(client.getpeername())}")

                self.broadcast(msg, connection_to_ignore=client)

        except Exception as err:
            raise ServerError(f"Unable to handle new client, Error: {err}")

    def broadcast(self, msg: str, connection_to_ignore: Optional[socket] = None) -> None:
        try:

            # Validate that connected list is not empty
            if self.registered_clients:
                for client in self.connected_sockets:
                    if client == connection_to_ignore:
                        continue

                    client.send(msg.encode(Config.UTF_8))

        except Exception as err:
            raise ServerError(f"Unable to broadcast message '{msg}', Error: {err}")

    def fetch_data(self, column: str, value: str) -> bool:
        """Fetches data from clients database."""
        if self.registered_clients:
            for name in self.registered_clients:

                if name.get(value) == column:
                    return True

            return False

    def shut_down(self):
        # TODO - for admin user
        for client in self.connected_sockets:
            client.client_socket.close()

        self.server_socket.close()

    def run(self) -> None:
        """Server main method to run all server logic."""
        try:
            self.setup()
            print(f"Server is now listening on {self.server_ip}:{self.server_port}...")

            while True:
                connection, address = self.server_socket.accept()
                self.logger.logger.info(f"Server connected to {str(connection.getpeername())}")

                # Create new thread for each connected client
                try:
                    client_thread = Thread(target=self.handle_client, args=(connection,))
                    client_thread.start()

                except Exception as err:
                    self.logger.logger.error(err)
                    connection.close()

                    # TODO - add join support for all clients threads

        except Exception as err:
            raise ServerError(f"Unable to setup server, Error: {err}.")


class ServerConstants:

    SERVER_CONFIG_FILE = "server_config.json"

    # TODO - data class
    # RAM DB constants
    CLIENT_ID = "client_id"
    CLIENT_NAME = "client_name"
    CLIENT_PASSWORD = "client_password"
    CLIENT_LAST_SEEN = "client_last_seen"
    CLIENT_IS_BANNED = "is_banned"
    CLIENT_SOCKET = "client_socket"

    # Dictionary format for saving clients data in RAM memory
    ram_clients_template = {
        CLIENT_ID: '{}',
        CLIENT_NAME: '{}',
        CLIENT_PASSWORD: '{}',
        CLIENT_LAST_SEEN: '{}',
        CLIENT_IS_BANNED: '{}',
        CLIENT_SOCKET: ""
    }

    ROOT_USER = "root_user"
    ROOT_PASSWORD = "root_password"

    server_configs_template = {
        ROOT_USER: "root",
        ROOT_PASSWORD: "qwer1234"
    }

    SERVER_ART_LOGO = """
    
       ____ _           _   _  __       
      / ___| |__   __ _| |_(_)/ _|_   _ 
     | |   | '_ \ / _` | __| | |_| | | |
     | |___| | | | (_| | |_| |  _| |_| |
      \____|_| |_|\__,_|\__|_|_|  \__, |
                                  |___/ 
    
        """

    # For message protocol
    REGISTER = "register"
    REGISTER_RESULT = "register_result"
    REGISTER_ROOT = "Please enter root password: "
    REGISTER_SUCCESS = "register_success"
    REGISTER_FAILED_USERNAME = "Username is not available, please choose another: "
    REGISTER_FAILED_PASSWORD = "Password is incorrect, please try again: "
    REGISTER_FAILED_GRP_FULL = "Group is full."
    MSG_HISTORY = "msg_history"
    REQ_REGISTER = "REQ_REGISTER"
    RES_REGISTER = "Please Enter Your username: "
    RES_WELCOME = (f"{SERVER_ART_LOGO}"
                   f"\n{'#'*40}"
                   f"\n# Welcome to Chatify chat group"
                   f"\n{'#'*40}\n")
    INPUT_PREFIX = "$: "
    CHAT_MODE = "CHAT_MODE"
    ACK = "ACK"


class ServerError(Exception):
    pass
