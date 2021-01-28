#  https://gist.github.com/Ryanb58/43e8bf5a8935405c455c5b41f8f8a0a3
# WOrks in python 2.7 not sure if it works in python 3.

# Just straight up connect by any means possible.
from ftplib import FTP_TLS


def connect():
    ftp = FTP_TLS()
    ftp.debugging = 2
    ftp.connect("localhost", 2121)
    ftp.login("developer", "password")
    return ftp


ftp = connect()
ftp.retrlines("LIST")


# Connect, but only using SSL version 2 aor 3
from ftplib import FTP_TLS
import ssl


def connect():
    ftp = FTP_TLS()
    ftp.ssl_version = ssl.PROTOCOL_SSLv23
    ftp.debugging = 2
    ftp.connect("localhost", 2121)
    ftp.login("developer", "password")
    return ftp


# Connect, but only using TLS version 1.2
from ftplib import FTP_TLS
import ssl


def connect():
    ftp = FTP_TLS()
    ftp.ssl_version = ssl.PROTOCOL_TLSv1_2
    ftp.debugging = 2
    ftp.connect("localhost", 2121)
    ftp.login("developer", "password")
    return ftp


ftp = connect()
ftp.retrlines("LIST")
