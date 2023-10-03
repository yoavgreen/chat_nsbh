from socket import socket, AF_INET, SOCK_STREAM, SOCK_DGRAM, error as socket_error
from threading import Thread


class CustomSocket(Thread):

    def __init__(self, connection_protocol: str) -> None:
        super().__init__()
        self.connection_protocol = connection_protocol

    def set_socket_protocol(self, connection_protocol: str):
        if connection_protocol == "tcp":
            return SOCK_STREAM
        elif connection_protocol == "udp":
            return SOCK_DGRAM
        else:
            raise ValueError(f"Unsupported connection protocol '{connection_protocol}'.")

    def create_socket(self) -> socket:
        try:
            protocol = self.set_socket_protocol(self.connection_protocol)
            custom_socket = socket(AF_INET, protocol)

            return custom_socket

        except socket_error as err:
            raise CustomSocketError(f"Unable to create socket, Error: {err}.")

    def setup(self) -> None:
        """Override method to setup server/client"""
        pass


class CustomSocketError(Exception):
    pass
