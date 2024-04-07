from socket import _GLOBAL_DEFAULT_TIMEOUT
from message import *
import socket
import re
import os

MAXLINE = 8192  # Defalult max line length
MSG_OOB = 0x1   # Data out of band
CRLF = "\r\n"
B_CRLF = b"\r\n"
TRUST_IN_PASS_IPV4 = False

class FTP:

    def __init__ (
            self,
            host="",
            port=21,
            username="anonymous",
            password="anonymous",
            acct="",
            timeout=_GLOBAL_DEFAULT_TIMEOUT,
            source_address=None,
            encoding="utf-8",
            debug=False,
            passive_server=True
    ):
        self.debug = debug
        self.encoding = encoding
        self.source_address = source_address
        self.file = None
        self.welcome = None

        # self.sock = socket.socket(socket.AF_INET, socket.SOCKSTREAM)
        self.sock = None

        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.timeout = timeout
        self.acct = acct

        self.passive_server = passive_server
        self.maxline = MAXLINE

        # Connect to host and authenticate
        if host:
            pass


    def connect(self):
        self.sock = socket.create_connection(
            (self.host, self.port), self.timeout, self.source_address
        )
        self.af = self.sock.family
        # self.sock.connect((self.host, self.port))
        return self.get_response()

    # Authenticate - Osvaldo
    def authenticate(self):
        pass

    # Send command - Toledo
    def send_command(self, command: str, response_type: str = "get"):
        """
        response_type = "get" or "void" or "multiline"
        """

        self.sock.sendall(command.encode(self.encoding) + B_CRLF)
        if self.debug:
            print(f"Sent: {command}")
        return self.get_response(response_type)
    
    # Get response - Toledo
    def get_response(self, response_type: str = "get"):
        """
        response_type = "get" or "void" or "multiline"
        """

        self.file = self.sock.makefile("r", encoding="utf-8")
        response = self.file.readline(MAXLINE)

        if self.debug:
            print(f"Recieved: {response}")

        if response_type == "void":
            if response[0] != "2":
                raise error_reply(response)
        
        if response_type == "get":
            if response[0] in ["4", "5", "6"]:
                raise error_mapper(response[0])(response)
            
        return response

    # Set passive server - Machado

    # Make passive server - Machado

    # Validations 150, 227, 229, 257 - Osvaldo

    # Sendport - Machado

    # Makeport - Machado

    # Passive connection - Osvaldo

    # Active connection - Machado

    # Create subprocess - Toledo

    # Retrieve file - Toledo

    # Retrieve binary - Toledo

    # Send file - Osvaldo

    # Send binary - Osvaldo

    # Read multiple lines - Osvaldo

    # ALLO - Toledo

    # SITE - Osvaldo

    # SYST - Machado

    # STAT - Toledo

    # ABOR - Osvaldo
    
    # ACCT - Machado

    # LIST - Osvaldo

    # NLST - Machado

    # CWD / CDUP - Toledo

    # SIZE - Toledo

    # SMNT - Osvaldo

    # STRU - Machado

    # MODE - Osvaldo

    # REIN - Toledo

    # RNFR / RNTO - Machado

    # DELE - Toledo

    # MKD - Osvaldo

    # RMD - Machado

    # PWD - Osvaldo

    # QUIT - Toledo
 
    # CLOSE - Machado

    # MLSD - Osvaldo

    # STOR - Toledo

    # STOU - Machado

    # APPE - Osvaldo

    # HELP - Toledo

    # NOOP - Machado