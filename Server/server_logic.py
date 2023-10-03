from socket import socket, AF_INET, SOCK_STREAM, SOCK_DGRAM, error as socket_error
import threading

class Server:
	def __init__(self, server_ip: str, server_port: int, connection_protocol: str) -> None:
		self.server_ip = server_ip
		self.server_port = server_port
		# Create server socket in the constructor
		self.connected_clients = []
		self.server_socket = self.create_server_socket(connection_protocol)

	def set_server_protocol(self, connection_protocol: str):
		if connection_protocol == "tcp":
			return SOCK_STREAM
		elif connection_protocol == "udp":
			return SOCK_DGRAM
		else:
			raise ValueError(f"Unsupported connection protocol '{connection_protocol}'.")

	def create_server_socket(self, connection_protocol) -> socket:
		try:
			protocol = self.set_server_protocol(connection_protocol)
			# TODO - validate socket creation
			server_socket = socket(AF_INET, protocol)
			
			return server_socket 	

		except socket_error as err:
			raise ServerError(f"Unable to create server socket, Error: {err}.")


	def setup_server(self) -> None:	
		try:
			self.server_socket.bind((str(self.server_ip), self.server_port))
			self.server_socket.listen()
			print(f"Server is now listening on {self.server_ip}:{self.server_port}...")	

		except socket_error as err:
			raise ServerError(f"Unable to setup server, Error: '{err}'.")


class ServerConstants:
	
	CONFIG_FILE_NAME = "Server/server_config.json"
	
	SERVER_IP_ADDRESS = "server_ip_address"
	SERVER_PORT = "server_port"
	SERVER_PROTOCOL = "server_protocol"

	config_file_template = {
		SERVER_IP_ADDRESS: "127.0.0.1",
		SERVER_PORT: 8888,
		SERVER_PROTOCOL: "tcp"
	}


class ServerError(Exception):
	pass
