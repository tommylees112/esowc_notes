from bs4 import BeautifulSoup
from ftplib import FTP
import urllib.request

ftp_path = 'ftp://ftp.ecmwf.int/pub/esowc'
with FTP(ftp_path) as ftp:
    ftp.login()
    ftp.dir()



req = urllib.request.Request(ftp_path)
response = urllib.request.urlopen(req)
the_page = response.read()

# use BeautifulSoup to parse the html source
page = str(BeautifulSoup(the_page))
