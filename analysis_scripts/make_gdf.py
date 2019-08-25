# make_gdf.py
from pathlib import Path
import xarray as xr
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import calendar
import geopandas as gpd
from mpl_toolkits.axes_grid1 import make_axes_locatable


if 'tommylees' in Path('.').absolute().parts:
    data_dir = Path('/Volumes/Lees_Extend/data/ecmwf_sowc/data')
out_dir = data_dir / 'analysis' / 'region_analysis'

from src.analysis.exploration import (
    calculate_seasonal_anomalies, create_anomaly_df,
    plot_bar_anomalies
)

%load_ext autoreload
%autoreload 2

# ------------------------------
# read the data
# ------------------------------
chirps = xr.open_dataset(
    data_dir / 'interim' /
    'chirps_preprocessed' / 'data_kenya.nc'
)
vci = xr.open_dataset(
    data_dir / 'interim' /
    'VCI_preprocessed' / 'data_kenya.nc'
)
srtm = xr.open_dataset(
    data_dir / 'interim' / 'static' /
    'srtm_preprocessed' / 'kenya.nc'
)



# ------------------------------
# group into geodataframes
# ------------------------------
from src.analysis.region_analysis.groupby_region import KenyaGroupbyRegion

# VCI
grouper = KenyaGroupbyRegion(data_dir)
grouper.analyze(
    da=vci.VCI, selection='level_2', mean=True,
    save_data_fname=None
)
vci_gdf = grouper.gdf.rename(columns={'mean_value': 'mean_vci'})

# precipitation
grouper.analyze(
    da=chirps.precip, selection='level_2', mean=True,
    save_data_fname=None
)
precip_gdf = grouper.gdf.rename(columns={'mean_value': 'mean_precip'})


era5 = xr.open_dataset(
    data_dir / 'interim' /
    'reanalysis-era5-single-levels-monthly-means_preprocessed' / 'data_kenya.nc'
)

# temperature
grouper = KenyaGroupbyRegion(data_dir)
grouper.analyze(
    da=era5.t2m, selection='level_2', mean=True,
    save_data_fname=None
)
temp_gdf = grouper.gdf.rename(columns={'mean_value': 'mean_temp'})
temp_gdf = temp_gdf.rename(columns={'mean_precip': 'mean_temp'})
pickle.dump(temp_gdf, open(out_dir / 'temp_gdf.pkl', 'wb'))

# potential evaporation
grouper.analyze(
    da=era5.pev, selection='level_2', mean=True,
    save_data_fname=None
)
pev_gdf = grouper.gdf.rename(columns={'mean_value': 'mean_pev'})
pickle.dump(pev_gdf, open(out_dir / 'pev_gdf.pkl', 'wb'))

# topography

assert False, 'IS NOT WORKING'
srtm = srtm.assign_coords(**{'time': pd.to_datetime('2000-01-01')})
srtm = srtm.expand_dims('time')
grouper.analyze(
    da=srtm.topography, selection='level_2', mean=True,
    save_data_fname=None
)
topo_gdf = grouper.gdf.rename(columns={'mean_value': 'mean_topography'})



# ------------------------------
# join the gdfs
# ------------------------------
# temp / pev
gdf_1 = pd.merge(
    temp_gdf, pev_gdf,
    how='inner', left_on=['datetime', 'region_name'],
    right_on=['datetime', 'region_name']
)
gdf_1 = gdf_1.drop(columns=[c for c in gdf_1.columns if c[-2:] == '_y'] + ['DISTNAME_x'])
gdf_1 = gdf_1.rename(columns={'geometry_x': 'geometry'})
pickle.dump(gdf_1, open(out_dir / 'temp_pev_gdf.pkl', 'wb'))

# precip / vci
gdf = pd.merge(
    precip_gdf, vci_gdf,
    how='inner', left_on=['datetime', 'region_name'],
    right_on=['datetime', 'region_name']
)
# drop duplicate columns
gdf = gdf.drop(columns=[c for c in gdf.columns if c[-2:] == '_y'] + ['DISTNAME_x'])
gdf = gdf.rename(columns={'geometry_x': 'geometry'})

# all
gdf_all = pd.merge(
    gdf_1, gdf,
    how='inner', left_on=['datetime', 'region_name'],
    right_on=['datetime', 'region_name']
)
# drop duplicate columns
gdf_all = gdf_all.drop(columns=[c for c in gdf_all.columns if c[-2:] == '_y'])
gdf_all = gdf_all.rename(columns={'geometry_x': 'geometry'})

# ------------------------------
# cleaning the data
# ------------------------------

# factorize the region / timestamp
dt_labels, datetime_levels = pd.factorize(gdf.datetime)
region_labels, region_levels = pd.factorize(gdf.region_name)

gdf_all['region_id'] = region_labels
gdf_all['datetime_id'] = dt_labels
gdf_all['month'] = [pd.to_datetime(dt).month for dt in gdf_all['datetime']]

# drop nans
gdf_all = gdf_all.dropna(
    subset=[
        'mean_vci', 'mean_precip', 'mean_precip',
        'mean_temp', 'mean_pev'
    ]
)

pickle.dump(gdf_all, open(out_dir / 'gdf_all.pkl', 'wb'))


# ------------------------------
# plots of the input data
# ------------------------------

def join_df_to_geometry(df: pd.DataFrame,
                        gdf: gpd.GeoDataFrame,
                        right_on: str,
                        left_on: str) -> gpd.GeoDataFrame:
    gdf = pd.merge(df, gdf, left_on=right_on, right_on=left_on)
    gdf = gpd.GeoDataFrame(gdf)
    return gdf
    #

def hist_plot_column(df, column: str):
    fig, ax = plt.subplots()
    sns.distplot(df[column], ax=ax, label=f'{column}_global')
    plt.legend()
    fig.savefig(f'/Users/tommylees/Downloads/{column}_global_hist.png')


value_columns = [
    'mean_vci', 'mean_precip', 'mean_precip',
    'mean_temp', 'mean_pev'
]


for col in value_columns:
    hist_plot_column(gdf_all, col)


for column in value_columns:
    fig, axs = plt.subplots(3, 4, figsize=(12, 8), sharex=True, sharey=True)
    for month in range(1, 12):
        ax = axs[np.unravel_index(month - 1, (3, 4))]

        sns.distplot(gdf_all.loc[gdf_all.month == month, column], ax=ax)
        # ax.set_xticklabels([''])
        ax.set_yticklabels([''])
        ax.set_xlabel('')
        ax.set_ylabel('')
        ax.set_title(calendar.month_name[month])
    fig.suptitle(column)
    fig.savefig(f'/Users/tommylees/Downloads/{column}_monthly_hist.png')


spatial_means = gpd.GeoDataFrame(
    gdf_all
    .groupby('region_name')
    .mean()
    .reset_index()
    .merge(gdf_all[['region_name', 'geometry']], right_on='region_name', left_on='region_name')
)

for column in value_columns:
    fig, ax = plt.subplots(figsize=(12, 8))
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.1)
    spatial_means.plot(column, ax=ax, legend=True, cax=cax)
    ax.set_title(column)
    ax.set_xticklabels([''])
    ax.set_yticklabels([''])
    ax.set_xlabel('')
    ax.set_ylabel('')
    fig.savefig(f'/Users/tommylees/Downloads/{column}_spatial_plot.png')




# -------------------------
# adjacency matrix
# -------------------------
# https://gis.stackexchange.com/a/244845/123489
