from client import FTP

if __name__ == 'main':

    print("Console App Started\N")
    username = input("username: ") 
    password = input("password: ")
    host = input("host: ")
    port = input("port: ")

    username = username if username != "" else "anonymous"
    password = password if password != "" else "anonymous@"
    host = host if host != "" else "localhost"
    port = port if port != "" else "port"

    debug_mode = input("Would you like to enter debug mode Y/N")
    debug = True if debug_mode in ["Y", "y", "S", "s", "Yes", "yes"] else False

    ftp = FTP(host, int(port), username, password, debug)

    while True:
        
        command = input('>> ').split()

        if command[0] == "SHOW":
            print(
                """
                
                """
            )
            continue

        match command[0]:
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
                if len(command) >= 3:
                    ftp.dir(command[1], None) # Sustituir command[2:] por un llamado al diccionario de los callbacks
            case "MKD":
                if len(command) == 2:
                    ftp.mkd(command[1])
            case "NLST":
                if len(command) >= 3:
                    ftp.nlst(command[1], None) # Sustituir command[2:] por un llamado al diccionario de los callbacks
            case "CWD":
                if len(command) == 2:
                    ftp.cwd(command[1])
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
            case "CLOSE":
                if len(command) == 1:
                    ftp.close_connection()
            case "MLSD":
                if len(command) >= 3:
                    ftp.mlsd(command[1], command[2:])
                if len(command) == 2:
                    ftp.mlsd(command[1], [])
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
                if len(command) == 4:
                    ftp.retr(command[1], command[2], type=command[3])
                if len(command) == 3:
                    ftp.retr(command[1], command[2])
            case "HELP":
                if len(command) == 2:
                    ftp.help(command[1])
                if len(command) == 1:
                    ftp.help()
            case "NOOP":
                if len(command) == 1:
                    ftp.noop()
            case __:
                print('Invalid command')
                continue