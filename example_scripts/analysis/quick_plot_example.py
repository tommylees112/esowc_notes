"""
probability distribution of precipitation intensity and how it varies with latitude and time

https://github.com/pangeo-data/pangeo_cmip6_examples

TODO:
* make this example work (currently taken straight from the notebook)
"""

# import intake
import xarray as xr
from matplotlib import pyplot as plt
import numpy as np

plt.rcParams['figure.figsize'] = 12, 6

import holoviews as hv
import geoviews as gv
import geoviews.feature as gf
import cartopy.crs as crs
from holoviews.operation.datashader import regrid
hv.extension('bokeh', 'matplotlib')

# ------------------------------------------------------------------------------
# PLOTTING FUNCTIONS
# ------------------------------------------------------------------------------
def quick_plot(da, dims, redim_range=None, **user_options):
    options = dict(cmap='viridis', colorbar=True,
                   width=700, height=450)
    options.update(user_options)
    name = da.name
    dataset = hv.Dataset(da)
    image = (dataset.to(hv.QuadMesh, dims, dynamic=True)
                       .options(**options))
    if redim_range is not None:
        image = image.redim.range(**{name: redim_range})

    return hv.output(image, backend='bokeh')

def quick_map(da, dims=['lon', 'lat'], redim_range=None, **user_options):
    options = dict(cmap='viridis', colorbar=True,
                   fig_size=300,
                   projection=crs.Robinson(central_longitude=180))
    options.update(user_options)
    name = da.name
    dataset = gv.Dataset(da)
    image = (dataset.to(gv.Image, dims, dynamic=True)
                       .options(**options))
    if redim_range is not None:
        image = image.redim.range(**{name: redim_range})

    return gv.output(image * gf.coastline(), backend='matplotlib')


# ------------------------------------------------------------------------------
# Example Use Case - Precipitation Intensity Histogram
# ------------------------------------------------------------------------------

def xr_histogram(data, bins, dims, **kwargs):

    bins_c = 0.5 * (bins[1:] + bins[:-1])
    func = lambda x: np.histogram(x, bins=bins, **kwargs)[0] / x.size

    output_dim_name = data.name + '_bin'
    res = xr.apply_ufunc(func, data,
                         input_core_dims=[dims],
                         output_core_dims=[[output_dim_name]],
                         output_dtypes=['f8'],
                         output_sizes={output_dim_name: len(bins_c)},
                         vectorize=True, dask='parallelized')
    res[output_dim_name] = output_dim_name, bins_c
    res[output_dim_name].attrs.update(data.attrs)
    return res

bins = np.logspace(-8, -3, 100)
def func(da):
    da = da.chunk({'lat': 1, 'lon': None, 'time': None})
    return xr_histogram(da, bins, ['lon', 'time'], density=False)
pr_3hr_hist = ds.pr.groupby('time.year').apply(func)
pr_3hr_hist


quick_plot(pr_3hr_hist, ['pr_bin', 'lat'], cmap='OrRd',
           logx=True, redim_range=(0, 0.04), tools=['hover'])


# x = precip_bins, y = latitude, color = probability
pr_daily = ds.pr.resample(time='1D').mean(dim='time')
pr_daily_hist = pr_daily.groupby('time.year').apply(func)

quick_plot(pr_daily_hist, ['pr_bin', 'lat'], cmap='OrRd',
           logx=True, redim_range=(0, 0.04), tools=['hover'])
