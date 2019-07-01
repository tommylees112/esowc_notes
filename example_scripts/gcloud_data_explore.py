from typing import Dict, List, Optional
from pathlib import Path

import xarray as xr
import salem

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd



data_dir = data_path = Path('data')
interim_dir = data_dir / 'interim'

plot_dir = Path('/home/gabrieltseng95/plots')
# plot_dir = Path('/soge-home/projects/crop_yield/plots')
if not plot_dir.exists():
    plot_dir.mkdir(exist_ok=True)

svg_dir = plot_dir / 'svg'
if not svg_dir.exists():
    svg_dir.mkdir(exist_ok=True)

png_dir = plot_dir / 'png'
if not png_dir.exists():
    png_dir.mkdir(exist_ok=True)


gleam_dir = interim_dir / 'gleam_preprocessed' / 'gleam_kenya.nc'
chirps_dir = interim_dir / 'chirps_preprocessed' / 'chirps_kenya.nc'
vhi_dir = interim_dir / 'vhi_preprocessed' / 'vhi_kenya.nc'
# era5_dir = interim_dir / 'era5POS_preprocessed' / 'era5POS_kenya.nc'
era5_dir = interim_dir / 'TEMP' / 'era5POS_kenya.nc'


v = xr.open_dataset(vhi_dir)  # 0-100
c = xr.open_dataset(chirps_dir)  # mm/month
g = xr.open_dataset(gleam_dir)  # mm.month-1; m3/m3; m3/m3
e = xr.open_dataset(era5_dir)  # mm.month-1; m3/m3; m3/m3
e = e.rename({'precipitation_amount_1hour_Accumulation': 'precip'})
e = e.rename({'air_temperature_at_2_metres': 'temp'})
e = e.rename({'air_temperature_at_2_metres_1hour_Maximum': 'tmax'})


e['precip'] = e['precip'] * 24 * 30
# ------------------------------------------------------------------------------
# Spatial Plots
# ------------------------------------------------------------------------------
def plot_spatial(da, title=None, product=None, savefig=True, **kwargs):
    dims = [dim for dim in da.dims]
    assert 'time' not in dims, f"data should be 2D for the plot_mean_time function"
    var = da.name

    fig, ax = plt.subplots()
    map = da.salem.quick_map(ax=ax, **kwargs)

    # set the title
    if title is None:
        title = f'{da.name}'

    ax.set_title(title)

    if savefig:
        fig.savefig(png_dir / f'{product + "_" if product is not None else ""}{var.lower()}_mean_spatial_plot.png', dpi=300)
        fig.savefig(svg_dir / f'{product + "_" if product is not None else ""}{var.lower()}_mean_spatial_plot.svg', dpi=300)

    return fig, ax, map


def save_spatial_mean_plots(ds, product=None, **kwargs):
    dims = [dim for dim in ds.dims]
    vars = [var for var in ds.variables if var not in dims]
    ds_mean = ds.mean(dim='time')

    min_time = pd.to_datetime(ds.time.min().values).strftime('%Y-%m-%d')
    max_time = pd.to_datetime(ds.time.max().values).strftime('%Y-%m-%d')

    figs = axs = []
    for var in vars:
        da = ds_mean[var]
        title = f'Mean {product}{var}\n{min_time} : {max_time}'
        fig, ax, _ = plot_spatial(da, title=title, product=product, **kwargs)
        figs.append(fig)
        axs.append(ax)

    plt.close('all')
    return figs, axs

plt.close('all')
# plot vhi
kwargs = {'cmap': 'viridis'}  # , 'vmin': 20, 'vmax': 80}
save_spatial_mean_plots(ds=v, **kwargs)

# plot precip
kwargs = {'cmap': 'cividis_r', 'vmin': 0, 'vmax': 150}
save_spatial_mean_plots(ds=c, product='CHIRPS', **kwargs)

ds = e.drop(['temp', 'tmax'])
kwargs = {'cmap': 'cividis_r'}  #, 'vmin': 0, 'vmax': 150}
save_spatial_mean_plots(ds=ds, product='ERA5', **kwargs)

ds = e.drop('precip')
kwargs = {'cmap': 'plasma'}
save_spatial_mean_plots(ds=ds, product='ERA5', **kwargs)

# plot soil moisture params
kwargs = {'cmap': 'Blues', 'vmin': 0, 'vmax': 0.45}
save_spatial_mean_plots(ds=g.drop('E'), **kwargs)

# plot evaporation
kwargs = {'cmap': 'inferno', 'vmin': 0, 'vmax': 140}
save_spatial_mean_plots(ds=g.drop(['SMroot', 'SMsurf']), **kwargs)





plt.close('all')
# ------------------------------------------------------------------------------
# Time Series Plots
# ------------------------------------------------------------------------------
from scripts.eng_utils import select_pixel

def plot_pixel(da, loc, ax, marker=True, **kwargs):
    pixel_da = select_pixel(da, loc)

    if marker:
        pixel_da.plot.line(ax=ax, marker='o', **kwargs)
    else:
        pixel_da.plot.line(ax=ax, **kwargs)

    return ax


def plot_ds_pixel(ds, ipixel, time_slice=('2008-01-01', '2014-12-31'), product=None, **kwargs):
    plt.close('all')
    dims = [dim for dim in ds.dims]
    vars = [var for var in ds.variables if var not in dims]

    for var in vars:
        da = (
            ds[var]
            .sel(time=slice(time_slice[0], time_slice[1]))
        )
        loc = (da.isel(lat=ipixel).lat.values, da.isel(lon=ipixel).lon.values)

        fig, ax = plt.subplots()
        ax = plot_pixel(da, loc, ax, **kwargs)
        title = f'{product}{var} time series'.title()
        ax.set_title(title)

        fig = plt.gcf()
        fig.savefig(png_dir / f'{product}{var.lower()}_time_series_P{ipixel}_plot.png', dpi=300)
        fig.savefig(svg_dir / f'{product}{var.lower()}_time_series_P{ipixel}_plot.svg', dpi=300)

        plt.close('all')

# Plot individual pixels

ds = c
kwargs = {'color':'#2977b4'}
plot_ds_pixel(ds, ipixel=100, product='CHIRPS', **kwargs)

ds = g.drop(['SMroot', 'SMsurf'])
kwargs = {'color':'#ee7e33'}
plot_ds_pixel(ds, ipixel=100, product='GLEAM', **kwargs)

ds = g.drop(['E'])
kwargs = {'color':'#57bfd0'}
plot_ds_pixel(ds, ipixel=100, product='GLEAM', **kwargs)

ds = v
kwargs = {'color':'#52a02e'}
plot_ds_pixel(ds, ipixel=100, product='NOAA', **kwargs)


ds = e.drop(['temp', 'tmax'])
kwargs = {'color': '#d7392e'}  #, 'vmin': 0, 'vmax': 150}
plot_ds_pixel(ds, ipixel=100, product='ERA5', **kwargs)

ds = e.drop('precip')
kwargs = {'color': '#2977b4'}
plot_ds_pixel(ds, ipixel=100, product='ERA5', **kwargs)


# spatial mean
plt.close('all')
kwargs = {'color':'#2977b4'}
var = 'precip'
time_slice = ('2008-01-01', '2014-12-31')
da = c[var].mean(dim=['lat', 'lon']).sel(time=slice(time_slice[0], time_slice[1]))
fig, ax = plt.subplots()
da.plot(ax=ax, marker='o', **kwargs)
fig = plt.gcf()
fig.savefig(png_dir / f'{var.lower()}_time_series_spatial_mean_plot.png', dpi=300)
fig.savefig(svg_dir / f'{var.lower()}_time_series_spatial_mean_plot.svg', dpi=300)
