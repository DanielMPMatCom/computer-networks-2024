import socket
import os
import threading
import socket
import os
import threading
import socket
import os
import threading


class FTPServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        self.server_socket.bind((self.host, self.port))
        self.data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.data_port = None

    def start(self):
        self.server_socket.listen(5)
        print("Servidor FTP iniciado. Escuchando en {}:{}".format(self.host, self.port))
        while True:
            client_socket, client_address = self.server_socket.accept()
            print("Conexión aceptada desde:", client_address)
            client_handler = threading.Thread(
                target=self.handle_client, args=(client_socket,)
            )
            client_handler.start()

    def handle_client(self, client_socket):
        client_socket.send("220 Servidor FTP listo.\r\n".encode())
        while True:
            request = client_socket.recv(4096).decode().strip()
            if not request:
                break
            print("Comando recibido:", request)
            command = request.split()[0].upper()

            if command == "USER":
                client_socket.send("331 Usuario OK, ingrese contraseña.\r\n".encode())
            elif command == "PASS":
                client_socket.send("230 Inicio de sesión exitoso.\r\n".encode())
            elif command == "PASV":
                self.data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.data_socket.bind((self.host, 0))
                self.data_socket.listen(1)
                self.data_port = self.data_socket.getsockname()[1]
                pasv_response = (
                    "227 Entering Passive Mode ({},{},{},{},{},{})\r\n".format(
                        *self.host.split("."),
                        self.data_port // 256,
                        self.data_port % 256,
                    )
                )
                client_socket.send(pasv_response.encode())
            elif command == "PWD":
                current_dir = os.getcwd()
                client_socket.send(
                    ('257 "%s" es el directorio actual.\r\n' % current_dir).encode()
                )
            elif command == "LIST":
                file_list = "\n".join(os.listdir())
                client_socket.send(
                    (
                        "150 Aquí está la lista de archivos:\r\n%s\r\n" % file_list
                    ).encode()
                )
            elif command == "RETR":
                file_name = request.split()[1]
                if os.path.exists(file_name):
                    client_socket.send(
                        "150 Iniciando transferencia de archivo.\r\n".encode()
                    )
                    with open(file_name, "rb") as file:
                        data = file.read(4096)
                        while data:
                            client_socket.send(data)
                            data = file.read(4096)
                    client_socket.send("226 Transferencia completa.\r\n".encode())
                else:
                    client_socket.send("550 El archivo no existe.\r\n".encode())
            elif command == "STOR":
                file_name = request.split()[1]
                client_socket.send("150 Listo para recibir archivo.\r\n".encode())
                with open(file_name, "wb") as file:
                    data = client_socket.recv(4096)
                    while data:
                        file.write(data)
                        data = client_socket.recv(4096)
                client_socket.send("226 Archivo recibido con éxito.\r\n".encode())
            elif command == "DELE":
                file_name = request.split()[1]
                if os.path.exists(file_name):
                    os.remove(file_name)
                    client_socket.send(
                        "250 Archivo eliminado correctamente.\r\n".encode()
                    )
                else:
                    client_socket.send("550 El archivo no existe.\r\n".encode())
            elif command == "MKD":
                dir_name = request.split()[1]
                os.mkdir(dir_name)
                client_socket.send("257 Directorio creado correctamente.\r\n".encode())
            elif command == "CWD":
                dir_name = request.split()[1]
                try:
                    os.chdir(dir_name)
                    client_socket.send(
                        ("250 Directorio cambiado a %s.\r\n" % dir_name).encode()
                    )
                except FileNotFoundError:
                    client_socket.send("550 El directorio no existe.\r\n".encode())
            elif command == "SIZE":
                file_name = request.split()[1]
                if os.path.exists(file_name):
                    file_size = os.path.getsize(file_name)
                    client_socket.send(("213 %d\r\n" % file_size).encode())
                else:
                    client_socket.send("550 El archivo no existe.\r\n".encode())
            elif command == "RMD":
                dir_name = request.split()[1]
                if os.path.exists(dir_name):
                    os.rmdir(dir_name)
                    client_socket.send(
                        "250 Directorio eliminado correctamente.\r\n".encode()
                    )
                else:
                    client_socket.send("550 El directorio no existe.\r\n".encode())
            elif command == "RNFR":
                old_name = request.split()[1]
                if os.path.exists(old_name):
                    client_socket.send(
                        "350 Listo para recibir el nombre de archivo nuevo.\r\n".encode()
                    )
                    new_name_request = client_socket.recv(4096).decode().strip()
                    new_name = new_name_request.split()[1]
                    os.rename(old_name, new_name)
                    client_socket.send("250 Renombrado exitoso.\r\n".encode())
                else:
                    client_socket.send("550 El archivo no existe.\r\n".encode())
            elif command == "QUIT":
                client_socket.send("221 Adiós.\r\n".encode())
                client_socket.close()
                break
            else:
                client_socket.send("500 Comando no reconocido.\r\n".encode())


if __name__ == "__main__":
    host = "127.0.0.1"  # Update the host to the loopback address
    port = 21

    ftp_server = FTPServer(host, port)
    ftp_server.start()
