# Libraries
import logging
from logging.handlers import RotatingFileHandler

# Constants
logging_format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# Loggers & Logging Files

funnel_logger = logging.getLogger("FunnelLogger")       # Name the logger
funnel_logger.setLevel(logging.INFO)                    # Set the logging level
funnel_handler = RotatingFileHandler("audits.log", maxBytes=2000, backupCount=5)        # Create a file handler
funnel_handler.setFormatter(logging_format)  # Set the formatter
funnel_logger.addHandler(funnel_handler)    # Add the handler to the logger

creds_logger = logging.getLogger("CredsLogger")       # Name the logger
creds_logger.setLevel(logging.INFO)                    # Set the logging level
creds_handler = RotatingFileHandler("commands.log", maxBytes=2000, backupCount=5)        # Create a file handler
creds_handler.setFormatter(logging_format)  # Set the formatter
creds_logger.addHandler(creds_handler)    # Add the handler to the logger

# Emulated Shell

# SSH Server + Sockets

# Provision SSH-based Honeypot