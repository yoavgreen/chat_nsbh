from Socket.custom_socket import socket, socket_error, CustomSocket, Thread
from socket import SOL_SOCKET, SO_REUSEADDR
from Utils.utils import Utils
from Utils.config_parser import ConfigConstants as Config
from logging import getLogger, basicConfig


class Server(CustomSocket):
    def __init__(self, server_ip: str, server_port: int, connection_protocol: str) -> None:
        super().__init__(connection_protocol)
        self.server_ip = server_ip
        self.server_port = server_port
        self.connected_sockets = [] # For the connected sockets only
        self.registered_clients = [] # For the entire connected clients
        self.active_connections = 0 # For the current active connections
        # Create server socket in the constructor
        self.server_socket = super().create_socket()
        self.utils = Utils()
        # Set class logger
        self.logger = getLogger(self.__class__.__name__)
        basicConfig(filename=Config.LOG_FILE_NAME, filemode=self.utils.set_file_mode(Config.LOG_FILE_NAME),
                    format=Config.LOG_FORMAT, datefmt=Config.DATE_TIME_FORMAT)

    def setup(self) -> None:
        try:
            # Reuse the socket port number
            self.server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

            # Bind server socket
            self.server_socket.bind((str(self.server_ip), self.server_port))

            # Start listen to incoming connections
            self.server_socket.listen()
            self.logger.info(f"Setup server successfully.")

        except socket_error as err:
            raise ServerError(f"Unable to setup server, Error: '{err}'.")

    def add_new_client(self,client: socket, clients_ram_template: dict) -> None:
        try:
            self.connected_sockets.append(client)
            self.registered_clients.append(clients_ram_template)
            self.active_connections += 1
            self.logger.info(f"Added new client '{clients_ram_template[ServerConstants.CLIENT_NAME]}' successfully.")

        except Exception as err:
            raise ServerError(f"Unable to add new client, Error: {err}")

    def handle_new_client(self, client: socket):
        try:
            # TODO - if active_connection > 16 send error to client

            # Create A RAM data copy
            clients_ram_template = ServerConstants.ram_clients_template.copy()
            clients_ram_template[ServerConstants.CLIENT_LAST_SEEN] = self.utils.last_seen()

            # TODO - forward messages between clients
            # New client first message
            client.send("Please enter your nickname: ".encode(Config.UTF_8))
            msg = client.recv(1024).decode(Config.UTF_8)

            # TODO - refactor into a different method
            # Handle registration
            if not self.is_registered(msg):

                clients_ram_template[ServerConstants.CLIENT_SOCKET] = client
                clients_ram_template[ServerConstants.CLIENT_NAME] = msg
                clients_ram_template[ServerConstants.CLIENT_ID] = self.utils.generate_client_uuid()
                self.add_new_client(client, clients_ram_template)
                self.broadcast(f"{msg} has entered the chat.")
            else:
                self.broadcast(msg)

        except Exception as err:
            raise ServerError(f"Unable to handle new client, Error: {err}")

    def broadcast(self, msg: str) -> None:
        try:
            # Validate that connected list is not empty
            if self.registered_clients:
                for client in self.connected_sockets:
                    client.send(msg.encode(Config.UTF_8))

        except Exception as err:
            raise ServerError(f"Unable to broadcast message '{msg}'.") 
    
    def is_connected(self, client: socket) -> bool:
        if client in self.connected_sockets:
            return True
        return False

    def is_registered(self, username: str) -> bool:
        if self.registered_clients:
            if username in list(self.registered_clients[0][ServerConstants.CLIENT_NAME]):
                return True
            return False

    def run(self):
        try:
            self.setup()

            self.logger.info(f"Server is now listening on {self.server_ip}:{self.server_port}.")
            print(ServerConstants.SERVER_ART_LOGO, end="\n\n")
            print(f"{'#'*40}\n# Welcome to chatify message server\n{'#'*40}\n")

            while True:
                connection, address = self.server_socket.accept()
                self.logger.info(f"Server connected to {str(address)}")

                # Create new thread for each connected client
                try:
                    client_thread = Thread(target=self.handle_new_client, args=(connection, ))
                    client_thread.start()

                except Exception as err:
                    self.server_socket.close()

                    # TODO - add join support for all clients threads

        except Exception as err:
            raise ServerError(f"Unable to setup server, Error: {err}.")


class ServerConstants:

    # RAM DB constants
    CLIENT_ID = "client_id"
    CLIENT_NAME = "client_name"
    CLIENT_LAST_SEEN = "client_last_seen"
    CLIENT_IS_BANNED = "is_banned"
    CLIENT_SOCKET = "client_socket"

    # Config constants
    CONFIG_FILE_NAME = "server_config.json"

    SERVER_IP_ADDRESS = "server_ip_address"
    SERVER_PORT = "server_port"
    SERVER_PROTOCOL = "server_protocol"

    config_file_template = {
        SERVER_IP_ADDRESS: "127.0.0.1",
        SERVER_PORT: 8888,
        SERVER_PROTOCOL: "tcp"
    }

    SERVER_ART_LOGO = """
    
       ____ _           _   _  __       
      / ___| |__   __ _| |_(_)/ _|_   _ 
     | |   | '_ \ / _` | __| | |_| | | |
     | |___| | | | (_| | |_| |  _| |_| |
      \____|_| |_|\__,_|\__|_|_|  \__, |
                                  |___/ 
    
        """

    # Dictionary format for saving clients data in RAM memory
    ram_clients_template = {
        CLIENT_ID: '{}',
        CLIENT_NAME: '{}',
        CLIENT_LAST_SEEN: '{}',
        CLIENT_IS_BANNED: '{}',
        CLIENT_SOCKET: "" 
    }


class ServerError(Exception):
    pass
