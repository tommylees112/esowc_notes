import os
import sys
if os.getcwd().split('/')[-2] == "eswoc_notes":
    sys.path.append('..')


from src.api_helpers import Region
import src.clean_vhi_data
from pathlib import Path
import xarray as xr
import numpy as np

data_dir = Path("/soge-home/projects/crop_yield/ESoWC_dummy/data/vhi/ftp.star.nesdis.noaa.gov/pub/corp/scsb/wguo/data/Blended_VH_4km/VH")
netcdf_filepaths = [f for f in data_dir.glob('*')]

netcdf_filepath = netcdf_filepaths[0]
