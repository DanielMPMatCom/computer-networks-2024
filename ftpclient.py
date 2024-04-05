import socket
import sys
import re


class FTPClient:
    def __init__(self, server_address, server_port):
        self.server_address = server_address
        self.server_port = server_port
        self.control_socket = None
        self.data_socket = None

    def connect(self):
        try:
            # Conexión al servidor FTP
            self.control_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.control_socket.connect((self.server_address, self.server_port))

            # Leer mensaje de bienvenida
            response = self.control_socket.recv(4096)
            print(response.decode().strip())

            return True
        except Exception as e:
            print("Error al conectar al servidor FTP:", e)
            return False

    def login(self, username, password):
        try:
            # Enviar credenciales
            self.send_command("USER " + username)
            response_code = self.get_response_code()
            if response_code == "331":
                print("Usuario OK.")
                self.send_command("PASS " + password)
                print("Contraseña OK.")
                response_code = self.get_response_code()
                print(response_code)
                if response_code == "230":
                    print("Inicio de sesión exitoso.")
                    return True
                else:
                    print("Error al iniciar sesión:", self.get_response())
                    return False
            else:
                print("Usuario incorrecto:", self.get_response())
                return False

        except Exception as e:
            print("Error al iniciar sesión:", e)
            return False

    def send_command(self, command):
        self.control_socket.send((command + "\r\n").encode())

    def get_response(self):
        return self.control_socket.recv(4096).decode().strip()

    def get_response_code(self):
        response = self.get_response()
        return response[:3]

    def open_data_connection(self):
        try:
            # Pedir al servidor que abra una conexión de datos
            self.send_command("PASV")
            response = self.get_response()
            # Extraer dirección y puerto del mensaje PASV
            match = re.search(r"(\d+),(\d+),(\d+),(\d+),(\d+),(\d+)", response)
            if match:
                data_host = ".".join(match.group(i) for i in range(1, 5))
                data_port = int(match.group(5)) * 256 + int(match.group(6))
                self.data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.data_socket.connect((data_host, data_port))
                return True
            else:
                print("Error al abrir conexión de datos:", response)
                return False
        except Exception as e:
            print("Error al abrir conexión de datos:", e)
            return False

    def download_file(self, remote_file, local_file):
        try:
            # Abrir conexión de datos
            if not self.open_data_connection():
                print("Error al establecer conexión de datos.")
                return

            # Pedir al servidor que envíe el archivo
            self.send_command("RETR " + remote_file)
            response_code = self.get_response_code()

            if response_code == "150":
                # Recibir datos y escribir al archivo local
                with open(local_file, "wb") as f:
                    while True:
                        data = self.data_socket.recv(4096)
                        if not data:
                            break
                        f.write(data)
                print("Archivo descargado con éxito:", local_file)
            else:
                print("Error al descargar archivo:", self.get_response())
        except Exception as e:
            print("Error al descargar archivo:", e)
        finally:
            # Cerrar conexión de datos
            if self.data_socket:
                self.data_socket.close()

    def upload_file(self, local_file, remote_file):
        try:
            # Abrir conexión de datos
            if not self.open_data_connection():
                print("Error al establecer conexión de datos.")
                return

            # Pedir al servidor que acepte el archivo
            self.send_command("STOR " + remote_file)
            response_code = self.get_response_code()

            if response_code == "150":
                # Leer datos del archivo local y enviar al servidor
                with open(local_file, "rb") as f:
                    for data in f:
                        self.data_socket.sendall(data)
                print("Archivo subido con éxito:", remote_file)
            else:
                print("Error al subir archivo:", self.get_response())
        except Exception as e:
            print("Error al subir archivo:", e)
        finally:
            # Cerrar conexión de datos
            if self.data_socket:
                self.data_socket.close()

    def list_files(self):
        try:
            # Abrir conexión de datos
            if not self.open_data_connection():
                print("Error al establecer conexión de datos.")
                return
            # Pedir al servidor que liste los archivos
            self.send_command("LIST")
            response_code = self.get_response_code()
            if response_code == "150":
                # Recibir y mostrar la lista de archivos
                data = self.data_socket.recv(4096).decode()
                print("Lista de archivos:")
                print(data.strip())
            else:
                print("Error al listar archivos:", self.get_response())
        except Exception as e:
            print("Error al listar archivos:", e)
        finally:
            # Cerrar conexión de datos
            if self.data_socket:
                self.data_socket.close()

    def rename_file(self, old_name, new_name):
        try:
            # Enviar comando para renombrar archivo remoto
            self.send_command("RNFR " + old_name)
            response_code = self.get_response_code()

            if response_code == "350":
                self.send_command("RNTO " + new_name)
                response_code = self.get_response_code()
                if response_code == "250":
                    print("Archivo renombrado con éxito:", old_name, "->", new_name)
                else:
                    print("Error al renombrar archivo:", self.get_response())
            else:
                print("Error al renombrar archivo:", self.get_response())
        except Exception as e:
            print("Error al renombrar archivo:", e)

    def get_file_info(self, remote_file):
        try:
            # Enviar comando para obtener información del archivo remoto
            self.send_command("SIZE " + remote_file)
            response_code = self.get_response_code()

            if response_code == "213":
                print("Tamaño del archivo", remote_file, ":", self.get_response())
            else:
                print("Error al obtener información del archivo:", self.get_response())
        except Exception as e:
            print("Error al obtener información del archivo:", e)

    def delete_file(self, remote_file):
        try:
            # Pedir al servidor que elimine el archivo
            self.send_command("DELE " + remote_file)
            response_code = self.get_response_code()

            if response_code == "250":
                print("Archivo eliminado con éxito:", remote_file)
            else:
                print("Error al eliminar archivo:", self.get_response())
        except Exception as e:
            print("Error al eliminar archivo:", e)

    def make_directory(self, directory):
        try:
            # Pedir al servidor que cree un directorio
            self.send_command("MKD " + directory)
            response_code = self.get_response_code()

            if response_code == "257":
                print("Directorio creado con éxito:", directory)
            else:
                print("Error al crear directorio:", self.get_response())
        except Exception as e:
            print("Error al crear directorio:", e)

    def change_directory(self, directory):
        try:
            # Pedir al servidor que cambie el directorio de trabajo
            self.send_command("CWD " + directory)
            response_code = self.get_response_code()

            if response_code == "250":
                print("Directorio cambiado con éxito:", directory)
            else:
                print("Error al cambiar directorio:", self.get_response())
        except Exception as e:
            print("Error al cambiar directorio:", e)

    def print_working_directory(self):
        try:
            # Enviar comando para obtener el directorio actual
            self.send_command("PWD")
            response_code = self.get_response_code()

            if response_code == "257":
                print(
                    "Directorio actual:", self.get_response()[4:-1]
                )  # El formato del mensaje es "257 "PATH"\r\n"
            else:
                print("Error al obtener directorio actual:", self.get_response())
        except Exception as e:
            print("Error al obtener directorio actual:", e)

    def remove_directory(self, directory):
        try:
            # Enviar comando para eliminar directorio remoto
            self.send_command("RMD " + directory)
            response_code = self.get_response_code()

            if response_code == "250":
                print("Directorio eliminado con éxito:", directory)
            else:
                print("Error al eliminar directorio:", self.get_response())
        except Exception as e:
            print("Error al eliminar directorio:", e)

    def quit(self):
        try:
            # Enviar comando QUIT al servidor
            self.send_command("QUIT")
            response_code = self.get_response_code()
            if response_code == "221":
                print("Desconexión del servidor FTP.")
            else:
                print("Error al cerrar sesión:", self.get_response())
        except Exception as e:
            print("Error al cerrar sesión:", e)
        finally:
            # Cerrar socket de control
            if self.control_socket:
                self.control_socket.close()


if __name__ == "__main__":
    # Dirección y puerto del servidor FTP
    server_address = "ftp1.at.proftpd.org"
    server_port = 21

    # Nombre de usuario y contraseña
    username = "anonymous"
    password = "anonymous"

    # Archivo remoto y local
    remote_file = "archivo.txt"
    local_file = "archivo_descargado.txt"

    # Crear cliente FTP
    ftp_client = FTPClient(server_address, server_port)

    # Conectar al servidor FTP
    if not ftp_client.connect():
        sys.exit(1)

    # Iniciar sesión
    if not ftp_client.login(username, password):
        sys.exit(1)

    # Lista de archivos remotos
    ftp_client.list_files()

    # Descargar archivo
    ftp_client.download_file(remote_file, local_file)

    # Subir archivo
    ftp_client.upload_file(local_file, "archivo_subido.txt")

    # Eliminar archivo remoto
    ftp_client.delete_file("archivo_a_eliminar.txt")

    # Crear directorio remoto
    ftp_client.make_directory("nuevo_directorio")

    # Cambiar directorio remoto
    ftp_client.change_directory("nuevo_directorio")

    # Obtener información del archivo remoto
    ftp_client.get_file_info("archivo.txt")

    # Imprimir directorio actual
    ftp_client.print_working_directory()

    # Borrar un directorio remoto
    ftp_client.remove_directory("directorio_a_borrar")

    # Renombrar un archivo remoto
    ftp_client.rename_file("nombre_antiguo.txt", "nombre_nuevo.txt")

    # Cerrar sesión y conexión
    ftp_client.quit()
