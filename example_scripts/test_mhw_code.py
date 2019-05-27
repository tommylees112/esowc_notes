"""
Ufuncs are faster to operate on xarray objects
https://docs.scipy.org/doc/numpy/reference/ufuncs.html

Can run
http://xarray.pydata.org/en/stable/computation.html
"""

from pathlib import Path
import xarray as xr
import numpy as np
import pandas as pd
# import xclim

from src.exporters.base import get_kenya
from scripts.eng_utils import select_bounding_box_xarray

data_dir = Path('data')
p_dir = data_dir / 'interim' / 'chirps_preprocessed' / 'chirps_19812019_kenya.nc'
v_dir = data_dir / 'interim' / 'vhi_preprocessed' / 'vhi_preprocess_kenya.nc'

p = xr.open_dataset(p_dir)
v = xr.open_dataset(v_dir)

chirps_daily_dir = Path('/soge-home/data_not_backed_up/satellite/chirps_v20/')
daily_dirs = [chirps_daily_dir / file for file in ['chirps-v2.0.2010.days_p05.nc', 'chirps-v2.0.2011.days_p05.nc']]

mf_ds = xr.open_mfdataset(daily_dirs)
ds = xr.open_dataset(daily_dirs[0])

kenya_region = get_kenya()
ds = select_bounding_box_xarray(ds, kenya_region)
mf_ds = select_bounding_box_xarray(mf_ds, kenya_region)

# test for part of a year
ds_ = mf_ds.isel(time=slice(0,-30))
ds_ = ds_.load()


# ------------------------------------------------------------------------------
# Calculate threshold and climatology
# ------------------------------------------------------------------------------
## test threshold comparison
variable = 'precip'
time_period = 'dayofyear'

# get seasonality for doy
clim = ds_.groupby(f'time.{time_period}').mean(dim='time')
# https://stackoverflow.com/a/47103407/9940782
# thresh = ds.groupby('time.dayofyear').reduce(np.nanpercentile, dim='time', q=0.9)
thresh = clim - ds_.groupby(f'time.{time_period}').std(dim='time')


def recreate_ds(ds):
    """recreate the ds (sometimes helps?)

    Note:
        1. Assumes that only 3 coords (e.g. lat lon time)
        2. Assumes that only 1 variable (`variables[0]`)
    """
    coords = [c for c in ds.coords.keys()]
    variables = [v for v  in ds.variables.keys() if v not in coords]

    # TODO: flexible for loop for each variable (work to `xr.DataArray` first)
    # TODO: need to sort by the size of the coord array
    # coords.sort(key=lambda x,y: cmp(ds[x].shape[0], ds[y].shape[0]))
    # ds[variables[0]].shape  # ORDER BY the shape of the variable

    out = xr.Dataset(
        {variables[0]: (['time','latitude','longitude'], ds[variables[0]])},
        coords = {
            coords[0]: ds[coords[0]],
            coords[1]: ds[coords[1]],
            coords[2]: ds[coords[2]],
        }
    )

    return out

# ------------------------------------------------------------------------------
# Compare values to climatology / threshold
# ------------------------------------------------------------------------------

def create_shape_aligned_climatology(ds, clim, variable, time_period):
    """
    Arguments:
    ---------
    ds : xr.Dataset
        the dataset with the raw values that you are comparing to climatology

    clim: xr.Dataset
        the climatology values for a given `time_period`

    variable: str
        name of the variable that you are comparing to the climatology

    time_period: str
        the period string used to calculate the climatology
         time_period = {'dayofyear', 'season', 'month'}

    Notes:
        1. assumes that `latitude` and `longitude` are the
        coord names in ds
    """
    # create a doy variable
    ds[time_period] = ds[f'time.{time_period}']

    t = clim[variable].values  # (365, lats, lons)
    doy = clim[time_period].values  # (365,)
    d_doy = ds[time_period].values  # (`doys`,)

    time_period_lookup = {'dayofyear':365, 'month':12, 'season':4}
    modulo = time_period_lookup[time_period]

    new_t_vals = t[d_doy%modulo, :, :]  # (`doys`, lats, lons)

    # create new_clim object with the new_t_vals
    #  (climatology values for all `time_periods`)
    new_clim = xr.Dataset(
        {variable: (['time','latitude','longitude'], new_t_vals)},
        coords={
            'time': ds.time,
            'latitude': clim.latitude,
            'longitude': clim.longitude,
        }
    )

    return new_clim


new_thresh = create_shape_aligned_threshold(ds_, thresh, variable, time_period)
new_clim = create_shape_aligned_threshold(ds_, clim, variable, time_period)

hilo = 'low'
# if hilo == 'low':
    # diff = new_thresh - ds
# elif hilo == 'high':
diff = ds_ - new_thresh

# ------------------------------------------------------------------------------
#
# ------------------------------------------------------------------------------
from scripts.eng_utils import get_ds_mask

# mask out the true null values (e.g. Sea values)
mask = get_ds_mask(ds)

# non_exceedences = (diff[variable] <= 0).where(~mask)
# exceedences = (diff[variable] > 0).where(~mask)
non_exceedences = diff[variable] <= 0
exceedences = diff[variable] > 0



# ------------------------------------------------------------------------------
# XClim test
# ------------------------------------------------------------------------------

## daily intensity each month
daily_int = xclim.indices._threshold.daily_pr_intensity(ds.precip, freq="QS-DEC")

cdd = xclim.icclim.CDD(ds.precip,freq='QS-DEC')
cdd['season'] = cdd['time.season']
cdd


#
