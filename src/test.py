from client import *


def debugger(*args):
    hr = "= = = = " * 10
    print(hr + "\n" + str(args) + "\n" + hr)
    return args


def Test1():  # send file
    debugger("Test 1")
    ftp = FTP("localhost", username="osvaldo", password="123456", debug=True)
    ftp.stor("test.txt", "./src/test/test.txt")
    # Filezilla no me deja hacer STOU\
    ftp.quit_and_close_connection()


def Test2():  # send binary
    debugger("Test 2")
    ftp = FTP("localhost", username="osvaldo", password="123456", debug=True)
    ftp.stor("test.txt", "./src/test/test.txt", type="I")
    ftp.appe("test.txt", "./src/test/new_file_for_test_restriveLines.txt", type="I")
    ftp.quit_and_close_connection()


def Test3():  # retrive lines
    debugger("Test 3")
    ftp = FTP("localhost", username="osvaldo", password="123456", debug=True)

    ftp.retr(
        "test.txt",
        "./src/test/test12.txt",
    )

    ftp.quit_and_close_connection()


def Test4():  # retrive binaries
    debugger("Test 4")
    ftp = FTP("localhost", username="osvaldo", password="123456", debug=True)

    new_file_retive_binaries = open(
        "./src/test/new_file_for_test_restriveBinaries.txt", "w"
    )
    ftp.retrieve_binary(
        "RETR test.txt",
        callback=lambda data: new_file_retive_binaries.write(data.decode()),
    )
    ftp.quit_and_close_connection()


def Test5():  # basic commands
    debugger("Test 5")
    ftp = FTP("localhost", username="osvaldo", password="123456", debug=True)
    print(ftp.dir())
    print(ftp.mkd("test"))
    print(ftp.dir())
    print(ftp.rename("test", "test2"))
    debugger(ftp.nlst("Osvaldo/Redes"))
    print(ftp.rmd("test2"))
    print(ftp.nlst(callback=print))
    print(ftp.pwd())
    print(ftp.quit_and_close_connection())


def Test6():  # create a new user for an ftp
    debugger("TEST 6")
    ftp = FTP("ftp1.at.proftpd.org", username="", password="", debug=True)
    try:
        print(ftp.account("123456"))
    except:
        pass
    print(ftp.quit_and_close_connection())


def Test7():
    debugger("TEST 7")
    ftp = FTP("localhost", username="osvaldo", password="123456", debug=True)
    print(ftp.nlst(callback=print))
    ftp.cwd("Osvaldo")
    print(ftp.nlst(callback=print))
    ftp.cwd("Redes")
    print(ftp.nlst(callback=print))
    ftp.cwd("../")
    print(ftp.nlst(callback=print))
    ftp.quit_and_close_connection()


def Test8():
    debugger("TEST 8")
    ftp = FTP("localhost", username="osvaldo", password="123456", debug=True)
    iterator = ftp.mlsd()
    for i in iterator:
        print(i)
    ftp.quit_and_close_connection()


def Test9():
    debugger("Test 9")
    ftp = FTP("localhost", username="osvaldo", password="123456", debug=True)
    # ftp.rein()
    # ftp.abort()
    ftp.syst()
    ftp.help()
    ftp.stru("F")
    # ftp.mode("B")
    ftp.quit_and_close_connection()


def Test10():
    debugger("TEST 10 OUR SERVER")
    ftp = FTP("127.0.0.1", debug=True)
    ftp.cwd("../")
    ftp.dir()
    ftp.pwd()
    ftp.help()
    ftp.mkd("newDirectoryFromClient")
    ftp.dir()
    ftp.rmd("newDirectoryFromClient")
    ftp.dir()
    ftp.syst()
    ftp.stor("test.txt", "./src/test/test.txt")
    ftp.rename("test.txt", "renombrado.txt")
    ftp.stou("./src/test/test.txt")
    ftp.retr("renombrado.txt", "./src/test/recibido.txt")
    ftp.size("renombrado.txt")
    ftp.account("123456")
    ftp.appe("renombrado.txt", "./src/test/recibido.txt")
    ftp.nlst()
    ftp.mlsd()
    ftp.allo(334)
    ftp.site("LFS")
    ftp.stat()
    ftp.smnt("mainStorage")
    ftp.quit_and_close_connection()


if __name__ == "__main__":
    print("Start Program ...")
    # Test1()
    # Test2()
    # Test3()
    # Test4()
    # Test5()
    # Test6()
    # Test7()
    # Test8()
    # Test9()
    Test10()
