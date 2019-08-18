from pathlib import Path
import xarray as xr
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

if 'tommylees' in Path('.').absolute().parts:
    data_dir = Path('/Volumes/Lees_Extend/data/ecmwf_sowc/data')
out_dir = data_dir / 'analysis' / 'region_analysis'

chirps = xr.open_dataset(
    data_dir / 'interim' /
    'chirps_preprocessed' / 'data_kenya.nc'
)


from src.analysis.exploration import (
    calculate_seasonal_anomalies, create_anomaly_df,
    plot_bar_anomalies
)


precip_anom = calculate_seasonal_anomalies(chirps, variable='precip')
# mam_anom = precip_anom.sel(time=precip_anom.season == 'MAM')
df = create_anomaly_df(precip_anom, mintime='1995', maxtime='2017-06')

fig, ax = plot_bar_anomalies(df)
ax.set_xlabel('Time')
ax.set_ylabel('Precipitation Anomaly [mm / season]')
ax.set_title('CHIRPS Precipitation Anomalies for Kenya')
fig.savefig('/Users/tommylees/Downloads/chirps_precip_seasonal_anomaly.png')
