"""
ftp://ftp.chg.ucsb.edu

ftp://ftp.chg.ucsb.edu/pub/org/chg/products/CHIRPS-2.0/global_pentad/netcdf/
"""

from typing import List, Optional
from bs4 import BeautifulSoup
import urllib.request
import os

data_dir = Path('data/')

def get_chirps_filenames() -> List:
    """
    ftp://ftp.chg.ucsb.edu/pub/org/chg/products/
        CHIRPS-2.0/global_pentad/netcdf/
    """
    base_url = 'ftp://ftp.chg.ucsb.edu'
    url = base_url + '/pub/org/chg/products/CHIRPS-2.0/global_pentad/netcdf/'

    # use urllib.request to read the page source
    req = urllib.request.Request(url)
    response = urllib.request.urlopen(req)
    the_page = response.read()

    # use BeautifulSoup to parse the html source
    page = str(BeautifulSoup(the_page))

    # split the page to get the filenames as a list
    firstsplit=page.split('\r\n')  # split the newlines
    secondsplit = [x.split(' ') for x in firstsplit]  # split the spaces
    flatlist = [item for sublist in secondsplit for item in sublist]  # flatten
    chirpsfiles = [x for x in flatlist if 'chirps' in x]

    return chirpsfiles


def wget_file(filepath: str, data_dir: Path):
    os.system(f"wget -np -nH --cut-dirs 7 {filepath} -P {data_dir.as_posix()}")


def download_chirps_files(chirps_files, data_dir: Path):
    """ download the chirps files using wget """
    # build the base url
    base_url = 'ftp://ftp.chg.ucsb.edu/pub/org/chg'
    base_url += '/products/CHIRPS-2.0/global_pentad/netcdf/'
    if base_url[-1] != '/':
        base_url += '/'

    filepaths = [base_url + f for f in chirps_files]

    pool = multiprocessing.pool(processes=100)
    pool.map(wget_file, filepaths, data_dir)




chirps_out_dir = data_dir / "raw" / "chirps"
if not chirps_out_dir.exists():
    chirps_out_dir.mkdir()

chirps_files = get_chirps_filenames()
download_chirps_files(chirps_files, chirps_out_dir)
