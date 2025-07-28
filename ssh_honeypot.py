# Libraries
import logging
from logging.handlers import RotatingFileHandler
import socket
import paramiko

# Constants
logging_format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

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
                channel.close()
            elif command.strip() == b'pwd':
                response = b"\n" + b"\\usr\\local\\" + b"\r\n"
            elif command.strip() == b'whoami':
                response = b"\n" + b"corpuser1" + b"\r\n"
            elif command.strip() == b'ls':
                response = b"\n" + b"jumpbox1.conf" + b"\r\n"
            elif command.strip() == b'cat jumpbox1.conf':
                response = b"\n" + b"Go to deeboodah.com." + b"\r\n"
            else:
                response = b'\n' + b'Command not found' + b'\r\n'

        channel.send(response)
        channel.send(b'corporate-shell$ ')
        command = b""


# SSH Server + Sockets

class Server(paramiko.ServerInterface):

    def __init__(self, client_ip, input_username=None, input_password=None):
        self.client_ip = client_ip
        self.input_username = input_username
        self.input_password = input_password

    def check_channel_request(self, kind:str, chanid: int) -> int:
        # Check if the requested channel type is a 'session', which allows for shell or command execution
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
    
    def get_allowed_auths(self):
        # Specify that only 'password' authentication is allowed
        return "password"
    
    def check_auth_password(self, username: str, password: str) -> int:
        # Validate the provided username and password against expected values
        if self.input_username is not None and self.input_password is not None:
            if username == 'username' and password == 'password':
                return paramiko.AUTH_SUCCESSFUL
            else:
                return paramiko.AUTH_FAILED
    
    def check_channel_shell_request(self, channel) -> int:  # Check if the client is requesting a shell
        self.event.set()
        return True
   
    def check_channel_pty_request(self, channel, term, width, height, pixel_width, pixel_height) -> int:    # Approve the pseudo-terminal (PTY) request
        return True
    
    def check_channel_exec_request(self, channel, command) -> int:  # Check if the command is a valid shell command
        command = str(command)
        return True

# Provision SSH-based Honeypot