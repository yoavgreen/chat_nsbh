from socket import socket, AF_INET, SOCK_STREAM, SOCK_DGRAM, error as socket_error
from threading import Thread


class CustomSocket(Thread):

    def __init__(self, socket_ip: str, socket_port: int, connection_protocol: str) -> None:
        

    def create_server_socket(self, connection_protocol: str) -> socket:
        try:
            protocol = self.set_socket_protocol(connection_protocol)
            # TODO - validate socket creation
            server_socket = socket(AF_INET, protocol)

            return socket

        except socket_error as err:
            raise CustomSocketError(f"Unable to create socket, Error: {err}.")


class CustomSocketError(Exception):
    pass
