from client import FTP

if __name__ == "__main__":

    print("Console App Started\n")

    username = input("username: ")
    password = input("password: ")
    host = input("host: ")
    port = input("port: ")

    username = username if username != "" else "anonymous"
    password = password if password != "" else "anonymous@"
    host = host if host != "" else "localhost"
    port = port if port != "" else "21"

    debug_mode = input("Would you like to enter debug mode Y/N \n")
    debug = True if debug_mode in ["Y", "y", "S", "s", "Yes", "yes"] else False

    ftp = FTP(host, int(port), username, password, debug=debug)

    while True:

        command = input(">> ").split()

        match command[0].upper():
            case "SHOW":
                print(
                    """
        ALLO <size> : Reserva size bytes de espacio en el servidor para un archivo
        SITE <cmd>  : Enviar un comando al servidor distintos de los del protocolo. Se usa help primero
        SYST        : Solicitar información sobre el sistema operativo del servidor
        STAT        : Solicitar el estado del servidor
        ABOR        : Abortar una transferencia
        ACCT        : Enviar un nuevo nombre de cuenta
        LIST <path> : Mostrar los archivos y directorios en el directorio actual o en el directorio especificado
        MKD  <name> : Crear un directorio en el servidor
        NLST <path> : Devolver una lista de nombres de archivos en el directorio actual (por defecto) o en el directorio especificado 
        CWD  <dir>  : Cambiar el directorio de trabajo actual, en caso de recibir .. se mueve al anterior
        SIZE <name> : Obtener el tamaño de un archivo en el servidor
        SMNT <dir>  : Cambiar el sistema de archivos del servidor
        STRU <opt>  : Seleccionar la estructura de transferencia de archivos F : flujo, R : registro, P : paginas
        MODE <opt>  : Seleccionar el modo de transferencia de archivos S : stream, B : block, C : comprimido
        REIN        : Reiniciar la conexión de control
        RENM <previous> <new>       : Renombra un archivo en el servidor
        DELE <name> : Eliminar un archivo en el servidor
        MKD  <dir>  : Crear un directorio en el servidor
        RMD  <dir>  : Eliminar un directorio en el servidor
        PWD         : Obtener el directorio de trabajo actual
        QUIT        : Cerrar la conexión con el servidor
        CLOSE       : Cerrar la el archivo actual y el socket con el servidor
        MLSD <path> <facts>         : Listar un directorio en formato de lista de nombres de archivos
        STOR <name> <path> <type>   : Almacenar un archivo en el servidor
        STOU <path> <type>          : Almacenar un archivo en el servidor con un nombre único
        APPE <name> <path> <type>   : Agregar datos a un archivo en el servidor
        RETR <name> <path> <type>   : Recuperar un archivo del servidor
        HELP <cmd>  : Solicitar ayuda sobre los comandos del servidor
        NOOP        : Envia una instrucción al servidor para mantener la conexión abierta
                    """
                )
            case "ALLO":
                if len(command) == 2:
                    ftp.allo(command[1])
            case "SITE":
                if len(command) == 2:
                    ftp.site(command[1])
            case "SYST":
                if len(command) == 1:
                    ftp.syst()
            case "STAT":
                if len(command) == 1:
                    ftp.stat()
            case "ABOR":
                if len(command) == 1:
                    ftp.abort()
            case "ACCT":
                if len(command) == 1:
                    ftp.account(password)
            case "LIST":
                ftp.dir("" if len(command) <= 1 else command[1], None)
            case "MKD":
                if len(command) == 2:
                    ftp.mkd(command[1])
            case "NLST":
                ftp.nlst("" if len(command) <= 1 else command[1], None)
            case "CWD":
                if len(command) == 2:
                    ftp.cwd(command[1])
                else:
                    ftp.cwd()
            case "SIZE":
                if len(command) == 2:
                    ftp.site(command[1])
            case "SMNT":
                if len(command) == 2:
                    ftp.smnt(command[1])
            case "STRU":
                if len(command) == 2:
                    ftp.stru(command[1])
                if len(command) == 1:
                    ftp.stru()
            case "MODE":
                if len(command) == 2:
                    ftp.mode(command[1])
                if len(command) == 1:
                    ftp.mode()
            case "REIN":
                if len(command) == 1:
                    ftp.rein()
            case "RENM":
                if len(command) == 3:
                    ftp.rename(command[1], command[2])
            case "DELE":
                if len(command) == 2:
                    ftp.delete(command[1])
            case "MKD":
                if len(command) == 2:
                    ftp.mkd(command[1])
            case "RMD":
                if len(command) == 2:
                    ftp.rmd(command[1])
            case "PWD":
                if len(command) == 1:
                    ftp.pwd()
            case "QUIT":
                if len(command) == 1:
                    ftp.quit_and_close_connection()
                    break
            case "CLOSE":
                if len(command) == 1:
                    ftp.close_connection()
            case "MLSD":
                iterator = ftp.mlsd(
                    "./" if len(command) <= 1 else command[1],
                    "" if len(command) <= 2 else command[2],
                )
                for i in iterator:
                    print(i)
            case "STOR":
                if len(command) == 4:
                    ftp.stor(command[1], command[2], type=command[3])
                if len(command) == 3:
                    ftp.stor(command[1], command[2])
            case "STOU":
                if len(command) == 3:
                    ftp.stou(command[1], type=command[2])
                if len(command) == 2:
                    ftp.stou(command[1])
            case "APPE":
                if len(command) == 4:
                    ftp.appe(command[1], command[2], type=command[3])
                if len(command) == 3:
                    ftp.appe(command[1], command[2])
            case "RETR":
                ftp.retr(
                    command[1],
                    f"./{command[1]}" if len(command) <= 2 else command[2],
                    type="A" if len(command) <= 3 else command[3],
                )
            case "HELP":
                if len(command) == 2:
                    ftp.help(command[1])
                if len(command) <= 1:
                    ftp.help()
            case "NOOP":
                if len(command) == 1:
                    ftp.noop()
            case __:
                print("Invalid command")
                continue
