from client import FTP

if __name__ == 'main':

    while True:
        
        command = input('>> ').split()

        match command[0]:

            case __:
                print('Invalid command')
                continue