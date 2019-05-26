from ftplib import FTP
from pathlib import Path

OUTPUT_DIR = Path(f'/Users/tommylees/Downloads')

with FTP('ftp.star.nesdis.noaa.gov') as ftp:
    ftp.login()
    ftp.cwd('/pub/corp/scsb/wguo/data/Blended_VH_4km/VH/')

    # append the filenames to a list
    listing = []
    ftp.retrlines("LIST", listing.append)
    # extract the filename
    filepaths = [f.split(' ')[-1] for f in listing]
    # extract only the filenames of interest
    vhi_files = [f for f in filepaths if ".VH.nc" in f]

    # download file locally
    filename = vhi_files[0]
    local_filename = OUTPUT_DIR / filename
    with open(local_filename,'wb') as lf:
        ftp.retrbinary("RETR " + filename, lf.write)
