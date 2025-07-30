# Libraries
import argparse
from ssh_honeypot import *

# Main entry point for the HoneyPy honeypot framework
if __name__ == "__main__":
    # Set up command line argument parser
    parser = argparse.ArgumentParser(description="HoneyPy - SSH and HTTP Honeypot Framework")

    # Network configuration arguments
    parser.add_argument('-a', '--address', type=str, required=True, help="IP address to bind the honeypot to")
    parser.add_argument('-p', '--port', type=int, required=True, help="Port number to listen on")
    
    # Authentication arguments (optional for SSH honeypot)
    parser.add_argument('-u', '--username', type=str, help="Expected username for SSH authentication")
    parser.add_argument('-pw', '--password', type=str, help="Expected password for SSH authentication")

    # Honeypot type selection (mutually exclusive)
    parser.add_argument('-s', '--ssh', action="store_true", help="Start SSH honeypot")
    parser.add_argument('-w', '--http', action="store_true", help="Start HTTP WordPress honeypot")

    args = parser.parse_args()

    try:
        # Start the appropriate honeypot based on user selection
        if args.ssh:
            print("[-] Running SSH Honeypot...")
            honeypot(args.address, args.port, args.username, args.password)

            if not args.username:
                username = None
            if not args.password:
                password = None
        elif args.http:
            print("[-] Running HTTP WordPress Honeypot...")
            # TODO: Implement HTTP honeypot functionality
            pass
        else:
            print("[!] Choose a honeypot type (SSH --ssh) or (HTTP --http).")

    except KeyboardInterrupt:
        # Handle graceful shutdown on Ctrl+C
        print("\n Exiting HONEYPY...\n")
    except Exception as e:
        # Handle any other unexpected errors
        print(f"[!] Error: {e}")
        print("\n Exiting HONEYPY...\n")