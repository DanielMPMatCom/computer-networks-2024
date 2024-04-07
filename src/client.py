from socket import _GLOBAL_DEFAULT_TIMEOUT
from message import *
import socket
import re
import os

MAXLINE = 8192  # Defalult max line length
MSG_OOB = 0x1  # Data out of band
CRLF = "\r\n"
B_CRLF = b"\r\n"
TRUST_IN_PASS_IPV4 = False


class FTP:

    def __init__(
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
        passive_server=True,
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

    def authenticate(self):
        """
        Command: USER {username}
        Response: Need password
        Command: PASS {password}
        if user is not register, we use ACCT {password}
        """
        response = self.send_command(f"USER {self.username}")
        if response[0] == "3":
            response = self.send_command(f"PASS {self.password}")
        if response[0] == "3":
            response = self.send_command(f"ACCT {self.acct}")
        if response[0] != "2":
            raise error_reply(response)
        return response

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
    def set_passive_server(self, val):
        self.passive_server = val

    # Make passive server - Machado
    def make_passive_server(self):
        if self.af == socket.AF_INET:
            parmas = self.send_command("PASV")
            host, port = self.validate_227(parmas)
            if not TRUST_IN_PASS_IPV4:
                host = self.sock.getpeername()[0]
        else:
            host, port = self.validate_229(
                self.send_command("EPSV"), self.sock.getpeername()
            )
        return host, port

    def validate_150(self, response):
        """150 Opening binary mode data connection for file transfer ({size} bytes)"""
        if response[:3] != "150":
            raise error_reply(response)
        regular_expression_150 = re.compile(
            r"150 .* \((\d+) bytes\)", re.IGNORECASE | re.ASCII
        )
        m = regular_expression_150.match(response)
        return int(m.group(1)) if m else None

    def validate_227(self, response):
        """227 Entering Passive Mode (192,168,1,2,197,143)"""
        if response[:3] != "227":
            raise error_reply(response)
        regular_expresion_227 = re.compile(
            r"(\d+),(\d+),(\d+),(\d+),(\d+),(\d+)", re.ASCII
        )
        m = regular_expresion_227.search(response)
        if not m:
            raise error_not_expected()
        n = m.groups()
        host = ".".join(n[:4])
        port = (int(n[4]) << 8) + int(n[5])
        return host, port

    def validate_229(self, response, peer):
        """229 Entering Extended Passive Mode (|||6446|)"""
        if response[:3] != "229":
            raise error_reply(response)
        host = peer[0]
        port = int(response.split("|")[-2])  # (|||port|).
        return host, port

    def validate_257(self, response):
        """257 "/home/usuario/directorio" is the current directory"""
        if response[:3] != "257":
            raise error_reply(response)
        if response[3:5] != ' "':
            return ""
        directory_name = ""
        i = 5
        n = len(response)
        while i < n:
            c = response[i]
            i += 1
            if c == '"':
                if i >= n or response[i] != '"':
                    break
                i += 1
                directory_name += c
        return directory_name

    # Sendport - Machado

    # Makeport - Machado

    def passive_connection(self, command, rest=None):
        host, port = self.make_passive_server()

        connection = socket.create_connection(
            (host, port), self.timeout, source_address=self.source_address
        )
        try:
            if rest is not None:
                self.send_command(f"REST {rest}")
            response = self.send_command(command)
            if response[0] == 2:
                response = self.get_response()
            if response[0] != "1":
                raise error_reply(response)
            return (connection, response)
        except:
            connection.close()
            raise

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
