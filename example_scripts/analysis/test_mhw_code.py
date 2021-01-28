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
import xclim
import matplotlib.pyplot as plt

from src.exporters.base import get_kenya
from scripts.eng_utils import select_bounding_box_xarray

data_dir = Path("data")
interim_dir = data_dir / "interim"
p_dir = interim_dir / "chirps_preprocessed" / "chirps_19812019_kenya.nc"
v_dir = interim_dir / "vhi_preprocessed" / "vhi_preprocess_kenya.nc"

p = xr.open_dataset(p_dir)
p = p.sortby("time")
v = xr.open_dataset(v_dir)
v = v.sortby("time")

chirps_daily_dir = Path("/soge-home/data_not_backed_up/satellite/chirps_v20/")
daily_dirs = [
    chirps_daily_dir / file
    for file in ["chirps-v2.0.2010.days_p05.nc", "chirps-v2.0.2011.days_p05.nc"]
]

mf_ds = xr.open_mfdataset(daily_dirs)
ds = xr.open_dataset(daily_dirs[0])

kenya_region = get_kenya()
ds = select_bounding_box_xarray(ds, kenya_region)
mf_ds = select_bounding_box_xarray(mf_ds, kenya_region)

# test for part of a year
ds_ = mf_ds.isel(time=slice(0, -30))
ds_ = ds_.load()


# ------------------------------------------------------------------------------
# Calculate threshold and climatology
# ------------------------------------------------------------------------------
## test threshold comparison
variable = "precip"
time_period = "dayofyear"

# get seasonality for doy
clim = ds_.groupby(f"time.{time_period}").mean(dim="time")
# https://stackoverflow.com/a/47103407/9940782
# thresh = ds.groupby('time.dayofyear').reduce(np.nanpercentile, dim='time', q=0.9)
thresh = clim - ds_.groupby(f"time.{time_period}").std(dim="time")


def calculate_threshold(ds, clim, method, time_period, hilo=None):
    """
    method: str
        ["q90","q10","std","abs",]
    """
    if method == "q90":
        warnings.warn("this method is currently super slow")
        thresh = ds.groupby(f"time.{time_period}").reduce(
            np.nanpercentile, dim="time", q=0.9
        )

    elif method == "q10":
        warnings.warn("this method is currently super slow")
        thresh = ds.groupby(f"time.{time_period}").reduce(
            np.nanpercentile, dim="time", q=0.1
        )

    elif method == "std":
        assert (
            hilo is not None
        ), f"If you want to calculate the threshold as std \
            from mean, then have to specify `hilo` = ['low','high']"
        std = ds.groupby(f"time.{time_period}").std(dim="time")
        thresh = clim - std if hilo == "low" else clim + std

    elif method == "abs":
        assert False, "Not yet implemented the absolute value threshold"
        values = np.ones(ds[variable].shape) * value
        thresh = xr.Dataset(
            {variable: (["time", "latitude", "longitude"], values)},
            coords={
                "latitude": ds.latitude,
                "longitude": ds.longitude,
                "time": ds.time,
            },
        )

    else:
        assert (
            False
        ), 'Only implemented threshold calculations for \
            ["q90","q10","std","abs",]'

    return thresh


def get_thresh_clim_dataarrays(ds, time_period, hilo=None, method="std"):
    """Get the climatology and threshold xarray objects """
    clim = ds.groupby(f"time.{time_period}").mean(dim="time")
    thresh = calculate_threshold(
        ds, clim, method=method, time_period=time_period, hilo=hilo
    )
    return clim, thresh


time_period = "dayofyear"
clim = p.groupby(f"time.{time_period}").mean(dim="time")
calculate_threshold(p, clim, method="std", time_period="dayofyear", hilo="low")
# ------------------------------------------------------------------------------
# Compare values to climatology / threshold
# ------------------------------------------------------------------------------


def create_shape_aligned_climatology(ds, clim, variable, time_period):
    """match the time dimension of `clim` to the shape of `ds` so that can
    perform simple calculations / arithmetic on the values of clim

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
    ds[time_period] = ds[f"time.{time_period}"]

    values = clim[variable].values
    keys = clim[time_period].values
    # map the `time_period` to the `values` of the climatology (threshold or mean)
    lookup_dict = dict(zip(keys, values))

    # extract an array of the `time_period` values from the `ds`
    timevals = ds[time_period].values

    # use the lat lon arrays (climatology values) in `lookup_dict` corresponding
    #  to time_period values defined in `timevals` and stack into new array
    new_clim_vals = np.stack([lookup_dict[timevals[i]] for i in range(len(timevals))])

    assert (
        new_clim_vals.shape == ds[variable].shape
    ), f"Shapes for new_clim_vals and ds must match! new_clim_vals.shape: {new_clim_vals.shape} ds.shape: {ds[variable].shape}"

    # copy that forward in time
    new_clim = xr.Dataset(
        {variable: (["time", "latitude", "longitude"], new_clim_vals)},
        coords={
            "latitude": clim.latitude,
            "longitude": clim.longitude,
            "time": ds.time,
        },
    )

    return new_clim


# create_shape_aligned_climatology(ds, clim, variable, time_period)

new_thresh = create_shape_aligned_climatology(ds_, thresh, variable, time_period)
new_clim = create_shape_aligned_climatology(ds_, clim, variable, time_period)

hilo = "low"
# if hilo == 'low':
# diff = new_thresh - ds
# elif hilo == 'high':
diff = ds_ - new_thresh

# NOTE: all np.nan values are wiped out with these boolean operators
if hilo == "low":
    group = (ds_ < new_thresh)[variable]
elif hilo == "high":
    group = (ds_ > new_thresh)[variable]

from scripts.eng_utils import get_ds_mask

# mask out the true null values (e.g. Sea values)
mask = get_ds_mask(ds)

# converts from bool -> int ([0,1,np.nan])
group = group.where(~mask).astype(bool)

# ------------------------------------------------------------------------------
# calculate exceedences of threshold
# ------------------------------------------------------------------------------

# non_exceedences = (diff[variable] <= 0).where(~mask)
# exceedences = (diff[variable] > 0).where(~mask)
non_exceedences = diff[variable] <= 0
exceedences = diff[variable] > 0

# ------------------------------------------------------------------------------
# Calculate CONSECUTIVE EXCEEDENCES
# http://xarray.pydata.org/en/stable/indexing.html
# ------------------------------------------------------------------------------

events, n_events = ndimage.label(exceed_bool)  # mhw approach

# personal approach -> pandas dataframe
raw_df = ds.precip.to_dataframe(name="precip")
thresh_df = new_thresh.precip.to_dataframe(name="threshold")
exceed_df = group.to_dataframe(name="exceedence")

# xclim approach
# windowed_run_events : Return the number of runs of a minimum length.
# windowed_run_events : Return the number of consecutive true values in array for runs at least as long as given duration.
# longest_run : Return the length of the longest consecutive run of True values.
# .apply(rl.windowed_run_count_ufunc, window=4)
# .apply(rl.windowed_run_count, window=4, dim='time')

from xclim.run_length import rle, windowed_run_events, longest_run

runs = rle(group).load()
wind_events = windowed_run_events(group, window=3).load()
wind_events = wind_events.where(~mask)


fig, ax = plt.subplots()
wind_events.plot(ax=ax)
ax.set_title(
    f"Number of {variable} events per pixel \
    [{ds_.time.min().values} - {ds_.time.max().values}]\
    \nwindow=3; threshold=mean-1std; hilo={hilo}"
)

# ------------------------------------------------------------------------------
# Calculate event characteristics
# http://xarray.pydata.org/en/stable/indexing.html
# ------------------------------------------------------------------------------

# where is the max run?
# https://stackoverflow.com/a/40197248/9940782
# https://github.com/pydata/xarray/issues/60
runs.max(dim="time")
# max_runs = runs.where(runs == runs.max(), drop=True).squeeze()
# max_runs = [max_runs.isel(time=i) for i in range(len(max_runs.time.values))]

runs.isel_points(runs=runs.argmax(["latitude", "longitude"]))

r = runs.to_dataset(name="runs")

# ------------------------------------------------------------------------------
# XClim test
# ------------------------------------------------------------------------------

## daily intensity each month
daily_int = xclim.indices._threshold.daily_pr_intensity(ds.precip, freq="QS-DEC")

cdd = xclim.icclim.CDD(ds.precip, freq="QS-DEC")
cdd["season"] = cdd["time.season"]
cdd

# ------------------------------------------------------------------------------
# Run for chirps_precip (SUBSET)
# ------------------------------------------------------------------------------
from scripts.eng_utils import get_ds_mask
from xclim.run_length import rle, windowed_run_events

p_dir = data_dir / "interim" / "chirps_preprocessed" / "chirps_19812019_kenya.nc"
p = xr.open_dataset(p_dir)
p = p.sortby("time")

variable = "precip"
time_period = "dayofyear"
hilo = "low"

# work on subset
p = p.sel(time=slice("1980-01-01", "1985-01-01"))

# calculate thresholds

pclim, pthresh = get_thresh_clim_dataarrays(p, time_period, hilo=hilo, method="std")
pnew_thresh = create_shape_aligned_climatology(p, pthresh, variable, time_period)
pnew_clim = create_shape_aligned_climatology(p, pclim, variable, time_period)

# calculate exceedences
# NOTE: all np.nan values are wiped out with these boolean operators
if hilo == "low":
    group = (ds_ < new_thresh)[variable]
elif hilo == "high":
    group = (ds_ > new_thresh)[variable]

runs = rle(pgroup).load()
wind_events = windowed_run_events(pgroup, window=3).load()


pmask = get_ds_mask(p)
wind_events = wind_events.where(~pmask)


# ------------------------------------------------------------------------------
# Run for chirps_precip ALL DATA
# ------------------------------------------------------------------------------
from pathlib import Path
import xarray as xr
import numpy as np
import pandas as pd


from scripts.eng_utils import get_ds_mask
import xclim.run_length as rl
from xclim.run_length import rle, windowed_run_events, longest_run
from xclim.indices import maximum_consecutive_dry_days

data_dir = Path("data")
p_dir = data_dir / "interim" / "chirps_preprocessed" / "chirps_19812019_kenya.nc"
p = xr.open_dataset(p_dir)
p = p.sortby("time")

variable = "precip"
time_period = "dayofyear"
hilo = "low"

# calculate thresholds
pclim, pthresh = get_thresh_clim_dataarrays(p, time_period, hilo=hilo, method="std")

# create TIME ALIGNED matrices
pclim = create_shape_aligned_climatology(p, pclim, variable, time_period)
pthresh = create_shape_aligned_climatology(p, pthresh, variable, time_period)

# flag exceedences
if hilo == "low":
    pexceed = (p < pthresh)[variable]
elif hilo == "high":
    pexceed = (p > pthresh)[variable]


# save the outputs to netcdf
# pclim.to_netcdf(interim_dir / "chirps_preprocessed" / "chirps_19812019_kenya_mean_doy.nc")
# pthresh.to_netcdf(interim_dir / 'chirps_preprocessed' / 'chirps_19812019_kenya_1STD_thresh.nc')
# pthresh = xr.open_dataset('data/interim/chirps_preprocessed/chirps_19812019_kenya_1STD_thresh.nc')
# pclim = xr.open_dataset('data/interim/chirps_preprocessed/chirps_19812019_kenya_mean_doy.nc')
# pclim.to_netcdf(interim_dir / "chirps_preprocessed" / "chirps_19812019_kenya_mean_doy_FULL.nc")
# pthresh.to_netcdf(interim_dir / 'chirps_preprocessed' / 'chirps_19812019_kenya_1STD_thresh_FULL.nc')


def calculate_threshold_exceedences(ds, variable, time_period, hilo, method="std"):
    """ """
    ds = ds.sortby("time")

    # calculate climatology and threshold
    clim, thresh = get_thresh_clim_dataarrays(ds, time_period, hilo=hilo, method=method)

    # make them the same size as the ds variable
    clim = create_shape_aligned_climatology(ds, clim, variable, time_period)
    thresh = create_shape_aligned_climatology(ds, thresh, variable, time_period)

    # flag exceedences
    if hilo == "low":
        exceed = (ds < thresh)[variable]
    elif hilo == "high":
        exceed = (ds > thresh)[variable]

    return clim, thresh, exceed


pclim, pthresh, pexceed = calculate_threshold_exceedences(
    p, variable, time_period, hilo, method="std"
)


def caclulate_runs_of_exceedences(exceedences):
    """use xclim to calculate the number of consecutive exceedences"""
    assert exceedences.dtype == np.dtype(
        "bool"
    ), f"Expected exceedences to be\
        an array of boolean type. Got {exceedences.dtype}"

    runs = rle(exceedences).load()
    return runs


# mask out the true null values (e.g. Sea values)
pmask = get_ds_mask(p.precip)

# calculate the runs
runs = rle(pexceed).load()

# calculate the number of events that exceed the size of the window
window_size = 3
wind_events = windowed_run_events(pexceed, window=window_size).load()

# calculate the longest run
p_longest = longest_run(pexceed, dim="time").load()
fig, ax = plt.subplots()
p_longest.plot(ax=ax)


# mask out the ocean
wind_events = wind_events.where(~pmask)

# plot the windowed events
fig, ax = plt.subplots()
wind_events.plot(ax=ax)
min_time = pd.to_datetime(p.time.min().values.astype(datetime))
max_time = pd.to_datetime(p.time.max().values.astype(datetime))
date_range = f"{min_time.year}-{min_time.month} - \
    {max_time.year}-{max_time.month}"
ax.set_title(
    f"Number of {variable} events per pixel \
    [{date_range}]\
    \nwindow={window_size}; threshold=mean-1std; hilo={hilo}"
)


# recreate maximum_consecutive_dry_days(p) with variable threshold
# What is the MAXIMUM number of consecutive pentads below 1std
group = pexceed
max_seasonal_dry_periods = pexceed.resample(time="QS-NOV").apply(
    longest_run, dim="time"
)

# ------------------------------------------------------------------------------
# Random functions
# ------------------------------------------------------------------------------


def recreate_ds(ds):
    """recreate the ds (sometimes helps?)

    Note:
        1. Assumes that only 3 coords (e.g. lat lon time)
        2. Assumes that only 1 variable (`variables[0]`)
    """
    coords = [c for c in ds.coords.keys()]
    variables = [v for v in ds.variables.keys() if v not in coords]

    # TODO: flexible for loop for each variable (work to `xr.DataArray` first)
    # TODO: need to sort by the size of the coord array
    # coords.sort(key=lambda x,y: cmp(ds[x].shape[0], ds[y].shape[0]))
    # ds[variables[0]].shape  # ORDER BY the shape of the variable

    out = xr.Dataset(
        {variables[0]: (["time", "latitude", "longitude"], ds[variables[0]])},
        coords={
            coords[0]: ds[coords[0]],
            coords[1]: ds[coords[1]],
            coords[2]: ds[coords[2]],
        },
    )

    return out


def create_shape_aligned_climatology2(ds, clim, variable, time_period):
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
    assert (
        False
    ), "This function only works when the doy/months are STANDARD (e.g. pentads won't work)"
    # create a time_period variable
    ds[time_period] = ds[f"time.{time_period}"]

    t = clim[variable].values  # (365, lats, lons)
    doy = clim[time_period].values  # (365,)
    d_doy = ds[time_period].values  # (`time_periods`,)

    time_period_lookup = {"dayofyear": 365, "month": 12, "season": 4}
    tps = time_period_lookup[time_period]

    # NOTE: working with pentad data = len(time) == 72
    new_t_vals = t[d_doy % tps, :, :]  # (`time_periods`, lats, lons)

    # create new_clim object with the new_t_vals
    #  (climatology values for all `time_periods`)
    new_clim = xr.Dataset(
        {variable: (["time", "latitude", "longitude"], new_t_vals)},
        coords={
            "time": ds.time,
            "latitude": clim.latitude,
            "longitude": clim.longitude,
        },
    )

    return new_clim


#
def rle(da, dim="time", max_chunk=1000000):
    # number of timesteps
    n = len(da[dim])
    # time indexes
    i = xr.DataArray(np.arange(da[dim].size), dims=dim).chunk({"time": 1})
    ind = xr.broadcast(i, da)[0].chunk(da.chunks)
    # where is da false? = where the exceedence is NOT met
    b = ind.where(~da)


da = p.isel(time=slice(0, 100)) < 20


def characteristics():
    # strength = difference from seasonality, difference from threshold
    #  normalised difference from threshold (normalised by difference of threshold:climatology)
    #  absolute value
    mhw_relSeas = temp_mhw - seas_mhw
    mhw_relThresh = temp_mhw - thresh_mhw
    mhw_relThreshNorm = (temp_mhw - thresh_mhw) / (thresh_mhw - seas_mhw)
    mhw_abs = temp_mhw

    # peak intensity

    # Duration

    # MHW Intensity metrics
    mhw["intensity_max"].append(mhw_relSeas[tt_peak])
    mhw["intensity_mean"].append(mhw_relSeas.mean())
    mhw["intensity_var"].append(np.sqrt(mhw_relSeas.var()))
    mhw["intensity_cumulative"].append(mhw_relSeas.sum())
    mhw["intensity_max_relThresh"].append(mhw_relThresh[tt_peak])
    mhw["intensity_mean_relThresh"].append(mhw_relThresh.mean())
    mhw["intensity_var_relThresh"].append(np.sqrt(mhw_relThresh.var()))
    mhw["intensity_cumulative_relThresh"].append(mhw_relThresh.sum())
    mhw["intensity_max_abs"].append(mhw_abs[tt_peak])
    mhw["intensity_mean_abs"].append(mhw_abs.mean())
    mhw["intensity_var_abs"].append(np.sqrt(mhw_abs.var()))
    mhw["intensity_cumulative_abs"].append(mhw_abs.sum())

    return
