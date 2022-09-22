from ftplib import FTP


def ftp_download(ftp_url, ftp_dir, ftp_files):
    ftp = FTP(ftp_url)
    ftp.login()
    ftp.cwd(ftp_dir)  # change working directory
    print("ftp connected to " + ftp_url)

    for file in ftp_files:
        print("ftp retrieving " + file)
        with open(file, "wb") as fp:
            ftp.retrbinary("RETR " + file, fp.write)
        fp.close()

    ftp.quit()
    print("ftp closed")


def ftp_listdates(ftp_url, ftp_dir, ftp_files):
    ftp = FTP(ftp_url)
    ftp.login()
    ftp.cwd(ftp_dir)  # change working directory
    print("ftp connected to " + ftp_url)

    for file in ftp_files:
        print("ftp command MDTM " + file)
        time = ftp.sendcmd("MDTM " + file)
        print(file + " " + time)

    ftp.quit()
    print("ftp closed")
