# get_chirps_parallel.py

import multiprocessing
import os
import glob


def process_url(url):
    os.system(f"wget -r -nH --cut-dirs=8 -nc {url}")

    return


all_files = glob.glob("*")
all_years = [str(yr) for yr in range(1981, 2019)]
missing_years = [year for year in all_years if year not in all_files]
all_urls = [
    f"ftp://ftp.chg.ucsb.edu/pub/org/chg/products/CHIRPS-2.0/africa_daily/tifs/p05/{year}/"
    for year in missing_years
]

pool = multiprocessing.Pool(processes=20)
pool.map(process_url, all_urls)
