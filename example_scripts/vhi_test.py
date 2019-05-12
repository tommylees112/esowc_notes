import os
import sys
if os.getcwd().split('/')[-2] == "eswoc_notes":
    sys.path.append('..')

from src.api_helpers import Region
from src.clean_vhi_data import *
from src.eng_utils import select_bounding_box_xarray
from pathlib import Path
import xarray as xr
import numpy as np

data_dir = Path("/soge-home/projects/crop_yield/esowc_notes/data/vhi/ftp.star.nesdis.noaa.gov/pub/corp/scsb/wguo/data/Blended_VH_4km/VH")

netcdf_filepaths = [f for f in data_dir.glob('*.nc')]
netcdf_filepath = netcdf_filepaths[0]

ds = xr.open_dataset(netcdf_filepath)
timestamp = extract_timestamp(ds, netcdf_filepath.as_posix(), use_filepath=True)
new_ds = create_new_dataset(ds, longitudes, latitudes, timestamp)

kenya_region = Region(
    name='kenya',
    lonmin=33.501,
    lonmax=42.283,
    latmin=-5.202,
    latmax=6.002,
)
# TODO: why does this not work with lat/lon but not latitude/longitude
# new_ds_ = new_ds.copy().rename({'latitude':'lat','longitude':'lon'})
kenya_ds = select_bounding_box_xarray(new_ds, kenya_region)
