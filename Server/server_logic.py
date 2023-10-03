from socket import socket, AF_INET, SOCK_STREAM, SOCK_DGRAM, error as socket_error
from Socket.custom_socket import CustomSocket
import threading


class Server(CustomSocket):
    def __init__(self, server_ip: str, server_port: int, connection_protocol: str) -> None:
        super().__init__(connection_protocol)
        self.server_ip = server_ip
        self.server_port = server_port

        # Create server socket in the constructor
        self.connected_clients = []
        self.active_connections = 0
        self.server_socket = super().create_socket()

    def setup_server(self) -> None:
        try:
            self.server_socket.bind((str(self.server_ip), self.server_port))
            self.server_socket.listen()

        except socket_error as err:
            raise ServerError(f"Unable to setup server, Error: '{err}'.")

    def run(self):
        try:
            self.setup_server()
            print(ServerConstants.SERVER_ART_LOGO, end="\n\n")
            print(f"Server is now listening on {self.server_ip}:{self.server_port}...")

            while True:
                connection, address = self.server_socket.accept()
                print(f"Server connected to {str(address)}")

        except Exception as err:
            raise ServerError(f"Unable to setup server, Error: {err}.")


class ServerConstants:
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


class ServerError(Exception):
    pass
