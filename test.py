import os
import zipfile  
import ftplib

def zipit(folders, zip_filename):
    zip_file = zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED)

    for folder in folders:
        for dirpath, dirnames, filenames in os.walk(folder):
            for filename in filenames:
                zip_file.write(
                    os.path.join(dirpath, filename),
                    os.path.relpath(os.path.join(dirpath, filename), os.path.join(folders[0], '../..')))

    zip_file.close()

def send_ftp(folders_path,zipname,FTP_HOST,FTP_USER,FTP_PASS):
    # //Nen folder folder_path
    zipit(folders_path, zipname)
    # //dang nhap tai khoan FTP
    ftp = ftplib.FTP(FTP_HOST, FTP_USER, FTP_PASS)
    # force UTF-8 encoding
    ftp.encoding = "utf-8"
    # //send file nen
    with open(zipname, "rb") as file:
        # use FTP's STOR command to upload the file
        ftp.storbinary(f"STOR {zipname}", file)
    # //return ketqua
    # os.remove(zipname)
print("sending")
send_ftp(folders_path=["model","logs"],zipname="result_model.zip",
                            FTP_HOST="hbqweblog.com",
                            FTP_USER="ftpuser",
                            FTP_PASS="Thehoang091184")
print("done")