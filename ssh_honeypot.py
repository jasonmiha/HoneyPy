# Libraries
import logging
from logging.handlers import RotatingFileHandler
import socket

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

# Provision SSH-based Honeypot