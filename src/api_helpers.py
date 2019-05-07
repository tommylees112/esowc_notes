from collections import namedtuple
from pathlib import Path
import xarray as xr
import numpy as np


import cdsapi


Region = namedtuple('Region', ['name',"lonmin","lonmax","latmin","latmax",])

def create_subset(Region):
    """create a subset string for the CDS API from a Region object"""
    x = [Region.latmax, Region.lonmin, Region.latmin, Region.lonmax]
    return "/".join(["{:.3f}".format(x) for x in x])





def download_data(cdsapi_client, cdstype, save_data_path, api_args):
    """ General function for sending API requests """
    datapath = Path(save_data_path)
    if not datapath.exists():
        cdsapi_client.retrieve(cdstype, api_args, save_data_path)
    else:
        print('Dataset already downloaded!')

    return datapath

def create_api_args(param, the_subset, years, months=np.arange(1,13), days=np.arange(1,32), times=np.arange(0,24)):
    """ API arguments dict
    Default behaviour: ALL TIMES; ALL DAYS; ALL MONTHS
    '"""
    args = {"product_type" : "reanalysis",
           "format"       : "netcdf",
           "area"         : the_subset,
           "variable"     : param,
           "year"         : ["{:04d}".format(year) for year in years],
           "month"        : ["{:02d}".format(x) for x in months],
           "day"          : ["{:02d}".format(x) for x in days],
           "time"         : ["{:02d}:00".format(x) for x in times]}

    return args


# CDS Type seems like a strange argument - make into partial functions
# pressure_levels = partial(download_data, client=c, cdstype='reanalysis-era5-pressure-levels')
# surface_levels = partial(download_data, client=c, cdstype='reanalysis-era5-single-levels')
# monthly_levels = partial(download_data, client=c, cdstype='reanalysis-era5-single-levels-monthly-means')
