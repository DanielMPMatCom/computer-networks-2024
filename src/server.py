import sys
import socket
from socket import _GLOBAL_DEFAULT_TIMEOUT
import datetime
import os
import threading
import uuid
import time

MAXLINE = 8192  # Default maximum line length
MSG_OOB = 0x1  # Data out of band
CRLF = "\r\n"
B_CRLF = b"\r\n"
TRUST_IN_PASS_IPV4 = False


class FTPServer:
    users = {"admin": "admin"}

    def __init__(
        self,
        host="localhost",
        port=21,
        file_system=["./src/server/mainStorage/"],
        current_file_system_index=1,
        max_connections=5,
        timeout=_GLOBAL_DEFAULT_TIMEOUT,
        encoding="utf-8",
        debug=False,
        passive_server=True,
        welcome_message="Welcome. FTP Server 2024 v1.2",
    ):
        self.host = host
        self.port = port
        self.file_system = file_system
        self.current_file_system_index = current_file_system_index
        self.data_port = 0
        self.cwd = ""
        self.change_file_system(0)
        self.max_connections = max_connections
        self.timeout = timeout
        self.encoding = encoding
        self.debug = debug
        self.passive_server = passive_server
        self.authenticate = False
        self.welcome_message = welcome_message
        self.control_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.transfer_type = "I"
        self.restart_point = 0

    def reset_server(self):
        self.current_file_system_index = 1
        self.transfer_type = "I"
        self.passive_server = True
        self.authenticate = False
        self.welcome_message = "Welcome, FTP Server 2024 v1.4. Made with ❤️ in Python"
        self.restart_point = 0
        self.timeout = _GLOBAL_DEFAULT_TIMEOUT
        self.debug = False
        self.encoding = "utf-8"
        self.authenticate = False
        self.max_connections = 5
        self.port = 21
        self.host = "127.0.0.1"
        self.data_port = 0
        self.cwd = ""
        self.change_file_system(0)

        pass

    def change_file_system(self, index):
        self.cwd = os.path.join(os.getcwd(), self.file_system[index])
        if not os.path.exists(self.cwd):
            os.mkdir(self.cwd)
        return

    def handle_client(self, connection, address):
        self.welcome(connection)
        while True:
            try:
                data = connection.recv(1024).decode()

                if data == "":
                    self.send_response(
                        connection, "500 Syntax error, command unrecognized"
                    )
                    return

                command = data.split()[0].upper()
                print(command)
                if command == "USER":
                    current_username = data.split()[1]
                    self.user(connection, username=current_username)
                elif command == "PASS":
                    self.password(
                        connection, current_username, password=data.split()[1]
                    )
                elif command == "ACCT":
                    self.account(connection, password=data.split()[1])
                elif command == "PASV":
                    print("Hello world")
                    self.passive_mode(connection)
                elif command == "LIST":
                    self.list_files(connection, data)
                elif command == "NLST":
                    self.list_files(connection, data)
                elif command == "RETR":
                    self.retrieve_file(connection, data)
                elif command == "STOR":
                    self.store_file(connection, data.split()[1])
                elif command == "APPE":
                    self.append_file(connection, data.split()[1])
                elif command == "QUIT":
                    self.quit(connection)
                    break
                elif command == "SYST":
                    self.system_type(connection)
                elif command == "PWD":
                    self.print_working_directory(connection)
                elif command == "CWD" or command == "CDUP":
                    self.change_working_directory(connection, data)
                elif command == "MKD":
                    self.make_directory(connection, data)
                elif command == "RMD":
                    self.remove_directory(connection, data)
                elif command == "DELE":
                    self.delete_file(connection, data)
                elif command == "RNFR":
                    filename = data.split()[1]
                    self.rename_from(connection, fileName=filename)
                elif command == "RNTO":
                    self.rename_to(
                        connection, oldName=filename, newName=data.split()[1]
                    )
                elif command == "TYPE":
                    self.set_transfer_type(connection, data)
                elif command == "PORT":
                    self.port(connection, data.split()[1])
                elif command == "NOOP":
                    self.no_operation(connection)
                elif command == "HELP":
                    self.help(connection)
                elif command == "REST":
                    self.restart(connection, data)
                elif command == "SIZE":
                    self.size(connection, filename=data.split()[1])
                elif command == "MDTM":
                    self.modification_time(connection, data)
                elif command == "STOU":
                    self.store_unique(connection)
                elif command == "REIN":
                    self.restart_server()
                elif command == "MODE":
                    self.send_response(connection, "200 MODE is always S")
                elif command == "STRU":
                    self.send_response(connection, "200 STRU is always F")
                elif command == "ALLO":
                    self.send_response(
                        connection, "200 ALLO is always Maximum buffer size"
                    )
                elif command == "SITE":
                    self.site(connection, data)
                elif command == "SMNT":
                    self.smnt(connection, data)
                # elif command == "AUTH":
                #     self.auth(connection, addresss, command)
                # elif command == "PBSZ":
                #     self.pbsz(connection, addresss, command)
                # elif command == "PROT":
                #     self.prot(connection, addresss, command)
                # elif command == "FEAT":
                #     self.features(connection, addresss, command)
                elif command == "MlSD":
                    self.mlsd(connection, data)
                elif command == "EPSV":
                    self.extended_passive_mode(connection)
                elif command == "EPRT":
                    self.extended_active_mode(connection)
                elif command == "OPTS":
                    self.opts(connection, data)
                elif command == "ABOR":
                    self.send_response(connection, "226 ABOR command successful")
                elif command == "STAT":
                    self.stat(connection)
                else:
                    self.send_response(connection, "502 Command not implemented")
                    return

            except Exception as e:
                if e is BrokenPipeError:
                    print("Error Client side close connection")
                else:
                    print("500 Fail to process command" + str(e))
                break

    def authenticate_require_manager(self, connecion, addresss, command):
        if not self.authenticate:
            self.send_response("530	Not logged in")
        return

    def send_response(self, connection, response):
        if self.debug:
            print("Response " + response)
        connection.sendall(response.encode(self.encoding) + B_CRLF)

    def welcome(self, connection):
        self.send_response(connection, self.welcome_message)

    def user(self, connection, username):
        if username in self.users or username == "anonymous":
            self.send_response(connection, "331 User name okay, need password")
        else:
            self.send_response(connection, "530 Not logged in")

    def password(self, connection, username, password: str):
        if self.users.get(username) == password:
            self.authenticate = True
            self.send_response(connection, "230 User logged in, proceed")
        if username == "anonymous" and password.startswith("anonymous"):
            self.authenticate = True
            self.send_response(
                connection, "230 Anonymous access granted, restrictions apply"
            )
        else:
            self.send_response(connection, "430	Invalid username or password")

    def account(self, connection, password):
        unique_user_name = "user" + str(len(self.users))
        self.users[unique_user_name] = password
        self.authenticate = True
        self.send_response(connection, "230 User logged in, proceed")

    def passive_mode(self, connection):
        self.data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.data_socket.bind((self.host, 0))
        self.data_port = self.data_socket.getsockname()[1]
        self.data_socket.listen(1)
        host_bytes = self.host.split(".")
        port_bytes = [self.data_port // 256, self.data_port % 256]
        print("host:" + str(self.host) + "port:" + str(self.data_port))
        self.send_response(
            connection,
            f"227 Entering Passive Mode ({host_bytes[0]},{host_bytes[1]},{host_bytes[2]},{host_bytes[3]},{port_bytes[0]},{port_bytes[1]})",
        )

    def mlsd(self, connection, command):
        path = self.cwd if len(command.split()) < 2 else command.split()[1]
        dir_list = "\n".join(os.listdir(os.path.join(self.cwd, path))) + "\r\n"
        self.send_response(connection, "150 Here comes the directory listing.")
        data_conn, _ = self.data_socket.accept()
        for name in os.listdir(dir_list):
            full_path = os.path.join(path, name)
            stats = os.stat(full_path)
            facts = {
                "type": "dir" if os.path.isdir(full_path) else "file",
                "size": stats.st_size,
                "modify": time.strftime("%Y%m%d%H%M%S", time.gmtime(stats.st_mtime)),
            }
            facts_line = ";".join(f"{fact}={value}" for fact, value in facts.items())
            data_conn.sendall(f"{facts_line} {name}\r\n".encode("utf-8"))
        data_conn.close()
        self.send_response(connection, "226 Directory send OK.")

    def list_files(self, connection, command):
        try:
            extra_dir = extra_dir = (
                self.cwd if len(command.split()) < 2 else command.split()[1]
            )
            self.send_response(connection, "150 Here comes the directory listing")
            data_conn, _ = self.data_socket.accept()
            dir_list = "\n".join(os.listdir(os.path.join(self.cwd, extra_dir))) + "\r\n"
            data_conn.sendall(dir_list.encode())
            data_conn.close()
            self.send_response(connection, "226 Directory send OK")
        except Exception as e:
            self.send_response(connection, f"550 Failed to list directory: {e}")
            print(f"Error listing directory: {e}")
            if data_conn:
                data_conn.close()

    def quit(self, connection):
        self.authenticate = False
        self.send_response(connection, "221 Goodbye")

    def system_type(self, connection):
        self.send_response(connection, "215 FTP Simulation usign Python in " + os.name)

    def help(self, connection):
        self.send_response(connection, "214-The following commands are recognized")
        self.send_response(
            connection,
            "214 USER PASS PASV LIST RETR STOR QUIT SYST PWD CWD MKD RMD DELE RNFR RNTO \
            TYPE PORT NOOP HELP REST SIZE MDTM AUTH PBSZ PROT FEAT EPSV EPRT OPTS",
        )

    def print_working_directory(self, connection):
        self.send_response(connection, f"257 {self.cwd} is the current directory")

    def change_working_directory(self, connection, command):
        new_path = os.path.realpath(os.path.join(self.cwd, command.split()[1]))

        exist = os.path.isdir(new_path)

        if exist:
            self.cwd = new_path
            self.send_response(connection, f"250 Directory changed to {self.cwd}")
        else:
            self.send_response(
                connection, f"550 Failed to change directory to {new_path}"
            )

    def make_directory(self, connection, command):
        try:
            os.mkdir(os.path.join(self.cwd, command.split()[1]))
            self.send_response(
                connection, f"257 Directory {command.split()[1]} created"
            )
        except Exception as e:
            self.send_response(connection, f"550 Failed to create directory: {e}")

    def remove_directory(self, connection, command):
        try:
            os.rmdir(os.path.join(self.cwd, command.split()[1]))
            self.send_response(
                connection, f"250 Directory {command.split()[1]} removed"
            )
        except Exception as e:
            self.send_response(connection, f"550 Failed to remove directory: {e}")

    def delete_file(self, connection, command):
        try:
            os.remove(os.path.join(self.cwd, command.split()[1]))
            self.send_response(connection, f"250 File {command.split()[1]} removed")
        except Exception as e:
            self.send_response(connection, f"550 Failed to remove file: {e}")

    def rename_from(self, connection, fileName):
        try:
            filename_cwd = os.path.join(self.cwd, fileName)
            if os.path.exists(filename_cwd) or os.path.isfile(filename_cwd):
                self.send_response(
                    connection,
                    f"350 File {self.rename_from} exists, ready for destination name",
                )
            else:
                raise FileNotFoundError(f"File {self.rename_from} does not exist")
        except Exception as e:
            self.send_response(connection, f"550 Failed to rename file: {e}")

    def rename_to(self, connection, oldName, newName):
        try:
            oldName_cwd = os.path.join(self.cwd, oldName)
            newName_cwd = os.path.join(self.cwd, newName)
            os.rename(oldName_cwd, newName_cwd)
            self.send_response(connection, f"250 File {oldName} renamed to {newName}")
        except Exception as e:
            self.send_response(connection, f"550 Failed to rename file: {e}")

    def size(self, connection, filename):
        try:
            size = os.path.getsize(os.path.join(self.cwd, filename))
            self.send_response(connection, f"213 {size} bytes")
        except Exception as e:
            self.send_response(connection, f"550 Failed to get file size: {e}")

    def modification_time(self, connection, command):
        filename = os.path.join(self.cwd, command.split()[1])

        if os.path.exists(filename):
            timestamp = os.path.getmtime(filename)
            mod_time = datetime.datetime.fromtimestamp(timestamp).strftime(
                "%Y%m%d%H%M%S"
            )
            self.send_response(connection, f"213 {mod_time}")
        else:
            self.send_response(connection, "550 File not found")

    def set_transfer_type(self, connection, command):
        try:
            transfer_type = command.split()[1]
            if transfer_type not in ["A", "I"]:
                raise ValueError("550 Invalid transfer type")
            self.transfer_type = transfer_type
            self.send_response(connection, "200 Type set to " + transfer_type)
        except Exception as e:
            self.send_response(connection, str(e))

    def no_operation(self, connection):
        return self.send_response(connection, "250 Noop")

    def store_unique(self, connection):
        unique_name = os.path.join(self.cwd, str(uuid.uuid4()))
        self.store_file(connection, unique_name)

    def append_file(self, connection, filename):
        path = os.path.join(self.cwd, filename)
        exist = os.path.exists(path)
        if exist and os.path.isfile(path):
            current_content = open(path, "r").read()
            self.store_file(connection, filename)
            new_content = open(path, "r").read()
            open(path, "w").write(current_content + new_content)
        else:
            self.store_file(connection, filename)

    def store_file(self, connection, filename):
        try:
            self.send_response(connection, "150 Opening data connection")
            data_conn, _ = self.data_socket.accept()
            new_file = os.path.join(self.cwd, filename)
            if self.transfer_type == "A":
                self.STOR_like_A(data_conn, new_file)
            elif self.transfer_type == "I":
                self.STOR_like_I(data_conn, new_file)
            self.send_response(connection, f"226 File {filename} uploaded successfully")

        except Exception as e:
            self.send_response("550 Failed to upload file: {e}")

    def STOR_like_A(self, data_conn, filename):
        with open(filename, "w+") as file:
            file.seek(self.restart_point)
            while True:
                data = data_conn.recv(8192)
                if not data:
                    break
                file.write(data.decode("ascii"))
            self.restart_point = 0
            data_conn.close()

    def STOR_like_I(self, data_conn, filename):

        with open(filename, "a+b") as file:
            file.seek(self.restart_point)
            while True:
                data = data_conn.recv(8192)
                if not data:
                    break
                file.write(data)
            self.restart_point = 0
            data_conn.close()

    def stat(self, connection):
        return self.send_response(connection, "211 Server status is OK")

    def port(self, connection, parameters):
        data = parameters.split(",")
        self.data_address = ".".join(data[:4])
        self.data_port = int(data[4]) * 256 + int(data[5])
        self.data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.data_socket.connect((self.data_address, self.data_port))
        except Exception as e:
            self.send_response(connection, "425 Can't open data connection")
            print(f"Error opening data connection: {e}")
            return

        self.send_response(connection, "200 PORT command successful")

    def extended_active_mode(self, connection):
        self.send_response(connection, "502 Command not implemented")

    def restart_server(self, connection):
        self.reset_server()
        self.send_response(connection, "220 Service ready for new user.")

    def retrieve_file(self, connection, command):
        try:
            self.send_response(connection, "150 Opening data connection")
            data_conn, _ = self.data_socket.accept()
            filename = command.split()[1]
            file_path = os.path.join(self.cwd, filename)
            if self.transfer_type == "A":
                self.RETR_like_A(data_conn, file_path)
            elif self.transfer_type == "I":
                self.RETR_like_I(data_conn, file_path)
            self.send_response(
                connection, f"226 File {filename} downloaded successfully"
            )
        except Exception as e:
            self.send_response(connection, f"550 Failed to download file: {e}")

    def RETR_like_A(self, data_conn, filename):
        with open(filename, "r") as file:
            file.seek(self.restart_point)
            for line in file:
                data_conn.sendall(line.encode("ascii"))
            data_conn.close()
        self.restart_point = 0

    def RETR_like_I(self, data_conn, filename):
        with open(filename, "rb") as file:
            file.seek(self.restart_point)
            for line in file:
                data_conn.sendall(line)
            data_conn.close()
        self.restart_point = 0

    def extended_passive_mode(self, connection):
        self.data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.data_socket.bind((self.host, 0))
        self.data_port = self.data_socket.getsockname()[1]
        self.data_socket.listen(1)
        self.send_response(
            connection,
            f"229 Entering Extended Passive Mode (|||{self.data_port}|)",
        )

    def restart(self, connection, command):
        self.restart_point = int(command[5:])
        self.send_response(
            connection,
            f"350 Restarting at {self.restart_point}. Send STORE or RETRIEVE to initiate transfer.",
        )

    def opts(self, connection, command):
        options = command[5:].split()
        if options[0] == "UTF8" and options[1] == "ON":
            self.utf8 = True
            self.send_response(connection, "200 UTF8 mode enabled")
        else:
            self.send_response(
                connection, "501 Syntax error in parameters or arguments"
            )

    def site(self, connection, command):
        if command[4:].strip() == "LFS":
            self.LFS(connection)
        else:
            self.send_response(
                connection,
                "500 Syntax error, command unrecognized, only LFS is supported as SITE.",
            )

    def LFS(self, connection):
        self.send_response(
            connection,
            "200 The current file system is "
            + self.cwd
            + "Other file systems are: "
            + str(self.file_system),
        )

    def smnt(self, connection, data):
        fileSystemName = data.split()[1]
        if fileSystemName in self.file_system:
            self.change_file_system(self.file_system.index(fileSystemName))
            self.send_response(
                connection, "202 File system changed to " + fileSystemName
            )
        else:
            self.send_response(connection, "202 Superfluous command")


if __name__ == "__main__":
    ftp_server = FTPServer(host="127.0.0.1")
    ftp_server.control_sock.bind((ftp_server.host, ftp_server.port))
    ftp_server.control_sock.listen(ftp_server.max_connections)
    print(f"Server listening on {ftp_server.host}:{ftp_server.port}")

    while True:
        conn, addr = ftp_server.control_sock.accept()
        threading.Thread(target=ftp_server.handle_client, args=(conn, addr)).start()
