from ftplib import FTP_TLS

username = '***'
password = '***'


def connect():
    ftp = FTP_TLS()
    ftp.debugging = 2
    ftp.connect('hydras.ugent.be', 2225)
    ftp.login(username, password)
    return ftp


from ftplib import FTP_TLS
import ssl

def connect():
    ftp = FTP_TLS()
    ftp.ssl_version = ssl.PROTOCOL_SSLv23
    ftp.debugging = 2
    ftp.connect('hydras.ugent.be', 2225)
    ftp.login(username, password)
    return ftp


ftp = connect()

import pysftp
# cnopts = pysftp.CnOpts()
# cnopts.hostkeys = None

srv = pysftp.Connection(host="hydras.ugent.be", username=username, password=password,)  # cnopts=cnopts)
