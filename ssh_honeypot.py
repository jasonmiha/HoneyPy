# Libraries
import logging
from logging.handlers import RotatingFileHandler
import socket
import paramiko
import threading

# Constants
logging_format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
SSH_BANNER = "SSH-2.0-OpenSSH_7.9p1 Debian-10+deb10u2"

host_key = paramiko.RSAKey(filename='server.key')

# Loggers & Logging Files

funnel_logger = logging.getLogger("FunnelLogger")       # Name the logger
funnel_logger.setLevel(logging.INFO)                    # Set the logging level
funnel_handler = RotatingFileHandler("audits.log", maxBytes=2000, backupCount=5)        # Create a file handler
funnel_handler.setFormatter(logging_format)  # Set the formatter
funnel_logger.addHandler(funnel_handler)    # Add the handler to the logger

creds_logger = logging.getLogger("CredsLogger")     
creds_logger.setLevel(logging.INFO)              
creds_handler = RotatingFileHandler("commands.log", maxBytes=2000, backupCount=5)        
creds_handler.setFormatter(logging_format)  
creds_logger.addHandler(creds_handler)  

# Emulated Shell
def emulated_shell(channel, client_ip):     # Define the emulated shell function
    channel.send(b'corporate-shell$ ')      # Send a message to the client
    command = b""
    while True:
        char = channel.recv(1)      # Receive a character from the client
        channel.send(char)
        if not char:
            channel.close()
        
        command += char     # Add the character to the command

        if char == b'\r':   # If the character is a carriage return, we've received a full command - we can now process it
            if command.strip() == b'exit':
                response = b'\n Exiting...\n'
                channel.send(response)
                return  # Exit the function instead of closing the channel
            elif command.strip() == b'pwd':
                response = b"\n" + b"\\usr\\local\\" + b"\r\n"
                creds_logger.info(f'Command {command.strip()}' + 'executed by ' + f'{client_ip}')
            elif command.strip() == b'whoami':
                response = b"\n" + b"corpuser1" + b"\r\n"
                creds_logger.info(f'Command {command.strip()}' + 'executed by ' + f'{client_ip}')
            elif command.strip() == b'ls':
                response = b"\n" + b"jumpbox1.conf" + b"\r\n"
                creds_logger.info(f'Command {command.strip()}' + 'executed by ' + f'{client_ip}')
            elif command.strip() == b'cat jumpbox1.conf':
                response = b"\n" + b"Go to deeboodah.com." + b"\r\n"
                creds_logger.info(f'Command {command.strip()}' + 'executed by ' + f'{client_ip}')
            else:
                response = b'\n' + b'Command not found' + b'\r\n'
                creds_logger.info(f'Command {command.strip()}' + 'executed by ' + f'{client_ip}')
            channel.send(response)
            channel.send(b'corporate-shell$ ')
            command = b""


# SSH Server + Sockets

class Server(paramiko.ServerInterface):

    def __init__(self, client_ip, input_username=None, input_password=None):
        self.event = threading.Event()
        self.client_ip = client_ip
        self.input_username = input_username
        self.input_password = input_password

    def check_channel_request(self, kind:str, chanid: int) -> int:
        # Check if the requested channel type is a 'session', which allows for shell or command execution
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
    
    def get_allowed_auths(self, username):
        # Specify that only 'password' authentication is allowed
        return "password"
    
    def check_auth_password(self, username: str, password: str) -> int:
        funnel_logger.info(f'Client {self.client_ip} attempted connection with ' + f'username: {username}, ' + f'password: {password}')
        creds_logger.info(f'{self.client_ip}, {username}, {password}')

        # Authenticate user by comparing provided credentials with expected honeypot credentials
        # If no expected credentials are set, accept any login attempt
        if self.input_username is not None and self.input_password is not None:
            if username == self.input_username and password == self.input_password:
                return paramiko.AUTH_SUCCESSFUL
            else:
                return paramiko.AUTH_FAILED
        else:
            return paramiko.AUTH_SUCCESSFUL
    
    def check_channel_shell_request(self, channel) -> int:  # Check if the client is requesting a shell
        self.event.set()
        return True
   
    def check_channel_pty_request(self, channel, term, width, height, pixel_width, pixel_height, modes) -> int:    # Approve the pseudo-terminal (PTY) request
        return True
    
    def check_channel_exec_request(self, channel, command) -> int:  # Check if the command is a valid shell command
        command = str(command)
        return True
    
def client_handle(client, addr, username, password):

    client_ip = addr[0]         # Extract the client's IP address from the connection tuple
    print(f"{client_ip} has connected to the server.")

    try:
        # Initialize a Paramiko SSH transport over the incoming client socket
        transport = paramiko.Transport(client)

        # Set the SSH version banner shown to the client
        transport.local_version = SSH_BANNER

        # Instantiate the server interface with provided credentials
        server = Server(client_ip=client_ip, input_username=username, input_password=password)

        # Add the server's private host key to the SSH transport (must be a paramiko.RSAKey object)
        transport.add_server_key(host_key)

        # Start the SSH server with our custom Server interface
        transport.start_server(server=server)

        # Wait for the client to open a channel (max wait: 100s)
        channel = transport.accept(100)
        if channel is None:
            print("No channel was opened.")     # Exit early if no channel is established

        # Send a short banner message after successful login
        standard_banner = b"** Authorized access only. Activity may be monitored. **\r\n\r\n"
        channel.send(standard_banner)

        # Launch the emulated shell to interact with the attacker
        emulated_shell(channel, client_ip=client_ip)

    except Exception as error:
        # Print the error if anything fails during the SSH session setup or interaction
        print(error)
        print("!!! Error !!!")

    finally:        # Always attempt to clean up the transport and client socket
        try:
            transport.close()
        except Exception as error:
            print(error)
            print("!!! Error !!!")

        client.close()      # Close the client socket no matter what

# Provision SSH-based Honeypot

def honeypot(address, port, username, password):

    socks = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socks.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    socks.bind((address, port))

    socks.listen(100)
    print(f"SSH server is listening port {port}.")

    while True:
        try:
            client, addr = socks.accept()
            ssh_honeypot_thread = threading.Thread(target=client_handle, args=(client, addr, username, password))
            ssh_honeypot_thread.start()
        except Exception as error:
            print(error)

honeypot('127.0.0.1', 2223, username=None, password=None)