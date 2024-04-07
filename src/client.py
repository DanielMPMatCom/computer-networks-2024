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

    def send_command(self, command: str, response_type: str = "get"):
        """
        Send command to server and recieve response
        response_type = "get" or "void" or "multiline"
        """

        self.sock.sendall(command.encode(self.encoding) + B_CRLF)
        if self.debug:
            print(f"Sent: {command}")
        return self.get_response(response_type)

    def get_response(self, response_type: str = "get"):
        """
        Recieve response from server
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

    def set_passive_server(self, val):
        self.passive_server = val

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

    def sendport(self, host, port):  # 318 sendport and sendeprt
        if self.af == socket.AF_INET:
            host = host.replace(".", ",")
            port = f"{port >> 8},{port & 0xff}"
            response = self.send_command(f"PORT {host},{port}")
        else:
            fields = ["", repr(2), host, repr(port), ""]
            response = self.send_command("EPRT " + "|".join(fields))

    def makeport(self):
        # https://es.wikipedia.org/wiki/Protocolo_de_transferencia_de_archivos
        """Create a new socket and send a PORT command for the data channel."""
        sock = socket.create_server(("", 0), family=self.af, backlog=1)
        port = sock.getsockname()[1]
        host = self.sock.getsockname()[0]
        self.sendport(host, port)
        return sock

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

    def active_connection(self, command, rest=None):
        with self.makeport() as sock:
            if rest is not None:
                self.send_command(f"REST {rest}")
            response = self.send_command(command)
            if response[0] == 2:
                response = self.get_response()
            if response[0] != "1":
                raise error_reply(response)
            connection, _ = sock.accept()
            connection.timeout(self.timeout)
        return connection

    def create_subprocess(self, command, rest=None):
        """
        Create New Connection for the transfer data
        """

        if self.passive_server:
            return self.passive_connection(command, rest)
        else:
            with self.makeport() as sock:
                if rest is not None:
                    self.send_command(f"REST {rest}")
                response = self.send_command(command)
                if response[0] == "2":
                    response = self.get_response()
                if response[0] != "1":
                    raise error_reply(response)
                connection, _ = sock.accept()
                connection.timeout(self.timeout)
        if response[:3] == "150":
            size = self.validate_150(response)
        return connection, size

    def retrieve_file(self, command, callback=None):

        if callback is None:
            callback = print

        response = self.send_command("TYPE A", "void")

        with self.create_subprocess(command)[0] as conn, conn.makefile(
            "r", encoding=self.encoding
        ) as fp:
            
            while True:
                line = fp.readline(self.maxline + 1)
                if len(line) > self.maxline:
                    raise Error(f"Got more than {self.maxline} bytes")
                if not line:
                    break
                if line[-2:] == CRLF:
                    line = line[:-2]
                elif line[-1:] == "\n":
                    line = line[:-1]
                callback(line)

        return self.get_response(response_type="void")
    
    def retrieve_binary(self, command, callback, blocksize=8192, rest=None):

        self.send_command("TYPE I", response_type="void")

        with self.create_subprocess(command, rest)[0] as conn:
            while data := conn.recv(blocksize):
                callback(data)

        return self.get_response(response_type="void")

    def send_file(self, command, file_object, callback=None):
        """command: Stor or Stou and file object with realines method"""
        self.send_command("TYPE A", "void")
        with self.create_subprocess(command)[0] as conn:
            while True:
                buffer = file_object.readlines(self.maxline + 1)
                if not buffer:
                    break
                if buffer[-2:] != B_CRLF:
                    if buffer[-1] in B_CRLF:
                        buffer = buffer[:-1]
                    conn.sendall(b"".join(buffer))
                    if callback:
                        callback(b"".join(buffer))
        return self.get_response("void")

    def send_binary(
        self, command, file_object, blocksize=8192, callback=None, rest=None
    ):
        """command: Stor or Stou and file object with realines method"""
        self.send_command("TYPE I", "void")
        with self.create_subprocess(command, rest)[0] as conn:
            while True:
                buf = file_object.read(blocksize)
                if not buf:
                    break
                conn.sendall(buf)
                if callback:
                    callback(buf)
        return self.get_response("void")

    def read_multilines(self, first_line=""):
        """use in case to read a multiline response and return it as a string"""
        lines = first_line if first_line != "" else self.file.readline()
        if lines[3] == "-":
            code = lines[:3]
            while True:
                next_line = self.file.readline()
                lines += "\n" + next_line
                if next_line[:3] == code and next_line[3:4] != "-":
                    break
        return lines

    def allo(self, size):
        """
        Allocate given size in server to store files
        """

        response = self.send_command("ALLO " + str(size))

        if self.debug:
            print(f"Allocated {size} bytes in server")

        return response

    def site(self, command):
        """Enviar un comando al servidor distintos de los del protocolo. Se usa help primero"""
        resp = self.send_command(
            "SITE " + command,
        )
        return resp

    def syst(self):
        """Solicitar información sobre el sistema operativo del servidor."""
        resp = self.send_command("SYST")
        return resp

    def stat(self):
        """
        Request server status
        """

        response = self.send_command("STAT")

        if self.debug:
            print(f"Server status requested with response: {response}")

        return response

    def abort(self):
        """Abort transfer, out of band
        Responses:
        225: La solicitud de aborto fue exitosa, y la conexión de datos se ha cerrado.
        226: La solicitud de aborto fue exitosa, y la transferencia de archivos se ha completado.
        426: La conexión se cerró; la transferencia de archivos no se completó.
        500: El comando ABOR no fue reconocido o no se pudo ejecutar.
        """
        command = b"ABOR" + B_CRLF
        response = self.sock.sendall(command, MSG_OOB)
        response = self.read_multilines()
        if response[:3] not in ["225", "226", "426", "500"]:
            raise error_not_expected(response)
        return response

    def account(self, password):
        """Send new account name."""
        cmd = "ACCT " + password
        return self.send_command(cmd, "void")

    def dir(self, pathname="", callback=None):  # list is a language word
        command = "LIST " + pathname
        return self.retrieve_file(command, callback)

    # NLST - Machado

    def cwd(self, directory_name):
        """
        Change working directory to given directory
        """

        if directory_name == "..":
            try:
                return self.send_command("CDUP", response_type="void")
            except error_perm as msg:
                raise

        elif directory_name == "":
            directory_name = "."

        cmd = "CWD " + directory_name
        return self.send_command(cmd, response_type="void")

    def size(self, filename):
        """
        Get file size in server
        """

        response = self.send_command("SIZE " + filename)

        if response[:3] == "213":
            return int(response[3:].strip())

    def smnt(self, directory_system):
        """change filesystem
        - `202`: El comando `SMNT` fue aceptado, pero la acción solicitada no se tomó porque el servidor no necesita cambiar el sistema de archivos.
        - `250`: El comando `SMNT` fue aceptado y la acción solicitada se completó. El servidor ha cambiado al sistema de archivos especificado.
        - `421`: El servicio no está disponible y la conexión se cerrará.
        - `500`: El comando `SMNT` no fue reconocido o no se pudo ejecutar.
        - `501`: Los parámetros del comando `SMNT` no eran correctos.
        - `502`: El comando `SMNT` no ha sido implementado en el servidor.
        - `530`: No estás autenticado, necesitas iniciar sesión.
        - `550`: El sistema de archivos especificado no existe o no está disponible.
        """
        response = self.send_command("SMNT " + directory_system, "void")
        return response

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
