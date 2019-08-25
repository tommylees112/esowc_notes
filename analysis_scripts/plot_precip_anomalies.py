from pathlib import Path
import xarray as xr
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

if 'tommylees' in Path('.').absolute().parts:
    data_dir = Path('/Volumes/Lees_Extend/data/ecmwf_sowc/data')
out_dir = data_dir / 'analysis' / 'region_analysis'

from src.analysis.exploration import (
    calculate_seasonal_anomalies, create_anomaly_df,
    plot_bar_anomalies
)

%load_ext autoreload
%autoreload 2

# -----------------------
# overall function
# -----------------------


def create_anomaly_plot(ds: xr.Dataset,
                        variable: str,
                        title: str = 'Anomaly Plot 1995-2017',
                        positive_color: str = 'b',
                        negative_color: str = 'r'):
    anom_da = calculate_seasonal_anomalies(ds, variable=variable)
    df = create_anomaly_df(anom_da, mintime='1995', maxtime='2017-06')

    fig, ax = plot_bar_anomalies(
        df, positive_color=positive_color, negative_color=negative_color
    )
    ax.set_xlabel('Time')
    ax.set_ylabel(f'{variable} Anomaly')
    ax.set_title(title)
    fig.savefig(f'/Users/tommylees/Downloads/{variable}_seasonal_anomaly.png')



# -----------------------
# CHIRPS Precipitation
# -----------------------

chirps = xr.open_dataset(
    data_dir / 'interim' /
    'chirps_preprocessed' / 'data_kenya.nc'
)


precip_anom = calculate_seasonal_anomalies(chirps, variable='precip')
# mam_anom = precip_anom.sel(time=precip_anom.season == 'MAM')
df = create_anomaly_df(precip_anom, mintime='1995', maxtime='2017-06')

fig, ax = plot_bar_anomalies(df)
ax.set_xlabel('Time')
ax.set_ylabel('Precipitation Anomaly [mm / season]')
ax.set_title('CHIRPS Precipitation Anomalies for Kenya')
fig.savefig('/Users/tommylees/Downloads/chirps_precip_seasonal_anomaly.png')


# -----------------------
# GLEAM Evaporation
# -----------------------

gleam = xr.open_dataset(
    data_dir / 'interim' /
    'gleam_preprocessed' / 'data_kenya.nc'
)

# e = gleam.E
# root = gleam.SMroot
# surf = gleam.SMsurf


create_anomaly_plot(gleam, variable='E', title='GLEAM Evaporation Anomaly')
create_anomaly_plot(gleam, variable='SMroot', title='GLEAM Rootzone Soil Moisture Anomaly (mm/day)')
create_anomaly_plot(gleam, variable='SMsurf', title='GLEAM Surface Soil Moisture Anomaly (mm/day)')


# -----------------------
# ERA5 Temperature
# -----------------------

era5 = xr.open_dataset(
    data_dir / 'interim_chirps_grid' /
    'reanalysis-era5-single-levels-monthly-means_preprocessed' /
    'reanalysis-era5-single-levels-monthly-means_kenya.nc'
)

era5.t2m

create_anomaly_plot(
    era5, variable='t2m', title='ERA5 Temperature Anomaly',
    positive_color='r', negative_color='b'
)


#
