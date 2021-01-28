"""
Download Clement Atzberger NDVI Time Series from:

1km
ftp://141.244.38.19/EA/

250m
ftp://141.244.38.19/EA/Bw/

Preprocessing steps applied can be found here:

"""
import urllib.request
import os
from pathlib import Path
from bs4 import BeautifulSoup

from typing import List

# -----------------------


def get_filenames(url: str, identifying_string: str) -> List[str]:
    """ Get the filenames from the ftp url"""
    # use urllib.request to read the page source
    req = urllib.request.Request(url)
    response = urllib.request.urlopen(req)
    the_page = response.read()

    # use BeautifulSoup to parse the html source
    page = str(BeautifulSoup(the_page, features="lxml"))  # type: ignore

    # split the page to get the filenames as a list
    firstsplit = page.split("\r\n")  # split the newlines
    secondsplit = [x.split(" ") for x in firstsplit]  # split the spaces
    flatlist = [item for sublist in secondsplit for item in sublist]  # flatten

    # get the name of the files by the identifying_string
    files = [f for f in flatlist if identifying_string in f]
    return files


def wget_file(url_filepath: str, output_folder: Path) -> None:
    """
    https://explainshell.com/explain?cmd=wget+-np+-nH+--cut
    -dirs+7+www.google.come+-P+folder
    """
    os.system(
        f"wget -np -nH --cut-dirs 2 {url_filepath} \
        -P {output_folder.as_posix()}"
    )


# -------------------

base_url_250 = "ftp://141.244.38.19/EA/Bw/"
base_url_1000 = "ftp://141.244.38.19/EA/"
base_url = base_url_1000

identifying_string = ".tif"
# data_dir = Path('/Volumes/Lees_Extend/data/ecmwf_sowc/data')
data_dir = Path("/lustre/soge1/projects/crop_yield/ml_drought/data")
output_dir = data_dir / "raw/modis_ndvi_1000"

if not output_dir.exists():
    output_dir.mkdir(exist_ok=True, parents=True)

fnames = get_filenames(base_url, identifying_string)
urls = [base_url + f for f in fnames]

for url in urls:
    wget_file(url, output_dir)
