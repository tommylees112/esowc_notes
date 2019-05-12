"""
Workflow:
--------
assign time stamp
assign lat lon
create new dataset with these dimensions
Save the output file to new folder

# From the base of the download to the root
ftp.star.nesdis.noaa.gov/pub/corp/scsb/wguo/data/Blended_VH_4km/VH/
cd '../'*8
"""

import time
import xarray as xr
import pandas as pd
import numpy as np
from pathlib import Path
from pprint import pprint
import os

if os.getcwd().split('/')[-2] == "eswoc_notes":
    sys.path.append('..')
# TODO: need to use the already specified functions in src.
# assert False, f"Need to add `eswoc_notes` to current path - current path: {os.getcwd()}"
# TODO: current hack hardcoding the path to get it to work
sys.path.append('/soge-home/projects/crop_yield/esowc_notes')

# for subsetting kenya
from src.eng_utils import select_bounding_box_xarray
from src.api_helpers import Region
# ------------------------------------------------------------------------------
# 1. assign time stamp
# ------------------------------------------------------------------------------
def extract_timestamp(ds, netcdf_filepath, use_filepath=True, time_begin=True):
    """from the `attrs` create a datetime object for acquisition time.

    NOTE: the acquisition date is SOMEWHERE in this time range (satuday-friday)

    USE THE FILENAME
    """
    year = ds.attrs['YEAR']

    if use_filepath: # use the weeknumber in filename
        # https://stackoverflow.com/a/22789330/9940782
        YYYYWWW = netcdf_filepath.split('P')[-1].split('.')[0]
        year = YYYYWWW[:4]
        week = YYYYWWW[5:7]
        atime = time.asctime(
            time.strptime('{} {} 1'.format(year, week), '%Y %W %w')
        )

    else:
        if time_begin:
            day_num = ds.attrs['DATE_BEGIN']
        else: # time_end
            day_num = ds.attrs['DATE_END']

        atime = time.asctime(
            time.strptime('{} {}'.format(year, day_num), '%Y %j')
        )

    date = pd.to_datetime(atime)
    return date


# ------------------------------------------------------------------------------
# 1. assign lat lon
# ------------------------------------------------------------------------------
def create_lat_lon_vectors(ds):
    """ read the `ds.attrs` and create new latitude, longitude vectors """
    assert ds.WIDTH.size == 10000, f"We are hardcoding the lat/lon values so we need to ensure that all dims are the same. WIDTH != 10000, == {ds.WIDTH.size}"
    assert ds.HEIGHT.size == 3616, f"We are hardcoding the lat/lon values so we need to ensure that all dims are the same. HEIGHT != 3616, == {ds.HEIGHT.size}"

    # lonmax = ds.attrs['END_LONGITUDE_RANGE']
    # lonmin = ds.attrs['START_LONGITUDE_RANGE']
    # latmin = ds.attrs['END_LATITUDE_RANGE']
    # latmax = ds.attrs['START_LATITUDE_RANGE']
    lonmax = 180
    lonmin = -180.0
    latmin = -55.152
    latmax = 75.024
    # print(f"lonmax:{lonmax} lonmin:{lonmin} latmin:{latmin} latmax:{latmax}")

    # extract the size of the lat/lon coords
    lat_len = ds.HEIGHT.shape[0]
    lon_len = ds.WIDTH.shape[0]

    # create the vector
    longitudes = np.linspace(lonmin,lonmax,lon_len)
    latitudes = np.linspace(latmin,latmax,lat_len)

    return longitudes, latitudes

# ------------------------------------------------------------------------------
# 1. create new dataset with these dimensions
# ------------------------------------------------------------------------------

def create_new_dataarray(ds, variable, longitudes, latitudes, timestamp):
    """ Create a new dataarray for the `variable` from `ds` with geocoding and timestamp """
    # Assert statements - to a test function?
    assert variable in [v for v in ds.variables.keys()], f"variable: {variable} need to be a variable in the ds! Currently {[v for v in ds.variables.keys()]}"
    dims = [dim for dim in ds.dims]
    assert (ds[dims[0]].size == longitudes.size) or (ds[dims[1]].size == longitudes.size), f"Size of dimensions {dims} should be equal either to the size of longitudes. \n Currently longitude: {longitudes.size}. {ds[dims[0]]}: {ds[dims[0]].size} / {ds[dims[1]]}: {ds[dims[1]].size}"
    assert (ds[dims[0]].size == latitudes.size) or (ds[dims[1]].size == latitudes.size), f"Size of dimensions {dims} should be equal either to the size of latitudes. \n Currently latitude: {latitudes.size}. {ds[dims[0]]}: {ds[dims[0]].size} / {ds[dims[1]]}: {ds[dims[1]].size}"
    assert np.array(timestamp).size == 1, f"The function only currently works with SINGLE TIMESTEPS."

    da = xr.DataArray(
        [ds[variable].values],
        dims=['time','latitude','longitude'],
        coords={'longitude':longitudes,
                'latitude': latitudes,
                'time': [timestamp]
        }
    )
    da.name = variable
    return da


def create_new_dataset(ds, longitudes, latitudes, timestamp, all_vars=False):
    """ Create a new dataset from ALL the variables in `ds` with the dims"""
    # initialise the list
    da_list = []

    # for each variable create a new data array and append to list
    if all_vars:
        for variable in [v for v in ds.variables.keys()]:
            da_list.append( create_new_dataarray(ds, variable, longitudes, latitudes, timestamp))
    else:
        # only export the VHI data
        da_list.append(create_new_dataarray(ds, "VHI", longitudes, latitudes, timestamp))

    # merge all of the variables into one dataset
    new_ds = xr.merge(da_list)
    new_ds.attrs = ds.attrs

    return new_ds

# ------------------------------------------------------------------------------
# 1. Save the output file to new folder
# ------------------------------------------------------------------------------

def create_filename(t, netcdf_filepath, subset=False, subset_name=None)):
    """ create a sensible output filename (HARDCODED for this problem)
    Arguments:
    ---------
    t : pandas._libs.tslibs.timestamps.Timestamp, datetime.datetime
        timestamp of this netcdf file

    Example Output:
    --------------
    STAR_VHP.G04.C07.NN.P_20110101_VH.nc
    VHP.G04.C07.NJ.P1996027.VH.nc
    """
    substr = netcdf_filepath.split('/')[-1].split('.P')[0]
    if subset:
        assert subset_name!=None, "If you have set subset=True then you need to assign a subset name"
        new_filename = f"STAR_{substr}_{t.year}_{t.month}_{t.day}_kenya_VH.nc"
    else:
        new_filename = f"STAR_{substr}_{t.year}_{t.month}_{t.day}_VH.nc"
    return new_filename


# ------------------------------------------------------------------------------
# 1. Chop out East Africa
# ------------------------------------------------------------------------------
# from src.api_helpers import Region
#
# # kenya_region = Region(
# #     name='kenya',
# #     lonmin=33.501,
# #     lonmax=42.283,
# #     latmin=-5.202,
# #     latmax=6.002,
# # )
# ea_region = Region(
#     name='ea_region',
#     lonmin=21,
#     lonmax=51.8,
#     latmin=-11,
#     latmax=23,
# )
#
# from src.eng_utils import select_bounding_box_xarray

def select_kenya_region(ds):
    """ simple helper function to return a subset xarray object for Kenya"""
    kenya_region = Region(
        name='kenya',
        lonmin=33.501,
        lonmax=42.283,
        latmin=-5.202,
        latmax=6.002,
    )
    return select_bounding_box_xarray(ds, kenya_region)


# ------------------------------------------------------------------------------
# 1. Wrap all into one function
# ------------------------------------------------------------------------------

def preprocess_VHI_data(netcdf_filepath, output_dir):
    """
    Process:
    -------
    * assign time stamp
    * assign lat lon
    * create new dataset with these dimensions
    * Save the output file to new folder
    """
    print(f"** Starting work on {netcdf_filepath.split('/')[-1]} **")
    # 1. read in the dataset
    ds = xr.open_dataset(netcdf_filepath)

    # 2. extract the timestamp for that file (from the filepath)
    timestamp = extract_timestamp(ds, netcdf_filepath, use_filepath=True)

    # 3. extract the lat/lon vectors
    longitudes, latitudes = create_lat_lon_vectors(ds)

    # 4. create new dataset with these dimensions
    new_ds = create_new_dataset(ds, longitudes, latitudes, timestamp)

    # 5. chop out EastAfrica
    kenya_ds = select_kenya_region(new_ds)

    # 5. create the filepath and save to that location
    filename = create_filename(timestamp, netcdf_filepath, subset=True, subset_name="kenya")
    print(f"Saving to {output_dir}/{filename}")
    # TODO: change to pathlib.Path objects
    new_ds.to_netcdf(f"{output_dir}/{filename}")

    print(f"** Done for VHI {netcdf_filepath.split('/')[-1]} **")
    return

# ------------------------------------------------------------------------------
# 1. reproject (Plate Caree to WGS84)
# ------------------------------------------------------------------------------
"""
No Need because WGS84 = Plate_Carree:

`ds.attrs['PROJECTION'] # Plate_Carree`

# https://epsg.io/4087
WGS 84 / World Equidistant Cylindrical
EPSG 4807

# https://proj4.org/operations/projections/eqc.html
Equidistant Cylindrical (Plate Carrée)
"standard for global raster datasets, such as Celestia and NASA World Wind"
proj4_str = `"+proj=eqc +lat_ts=0 +lat_0=0 +lon_0=0 +x_0=0 +y_0=0 +ellps=WGS84 +datum=WGS84 +units=m +no_defs"`
"""
