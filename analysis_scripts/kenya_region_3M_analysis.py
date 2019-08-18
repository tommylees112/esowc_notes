from pathlib import Path
import xarray as xr
import pandas as pd
import numpy as np

from typing import Dict

# import sys
# sys.path.append('..')
# sys.path.append('../..')

# waiting for merge
from src.analysis import (
    VegetationDeficitIndex, SPI, MovingAverage
)
from src.utils import drop_nans_and_flatten

# ------------------------------------------------------
# setup the Paths
# ------------------------------------------------------

# load the data_dir
if 'tommylees' in Path('.').absolute().parts:
    data_dir = Path('/Volumes/Lees_Extend/data/ecmwf_sowc/data')
elif Path('.').absolute().parents[0] == 'ml_drought':
    data_dir = Path('data').absolute()
elif Path('.').absolute().parents[1] == 'ml_drought':
    data_dir = Path('../data').absolute()

out_dir = data_dir / 'analysis' / 'region_analysis'


# ------------------------------------------------------
# load the data
# ------------------------------------------------------

# fit VegetationDeficitIndex to TRUE data
vdi = VegetationDeficitIndex(data_dir / 'interim' / 'VCI_preprocessed' / 'data_kenya.nc')
vdi.fit('VCI')
da = vdi.index.VCI3_moving_average

# extract the data
vdi_ds = vdi.index

# ------------------------------------------------------
# groupby districts (l2 regions) -> pd.DataFrame
# ------------------------------------------------------
from src.analysis.region_analysis.groupby_region import KenyaGroupbyRegion

grouper =  KenyaGroupbyRegion(data_dir)
grouper.analyze(
    da=da, selection='level_2', mean=True,
    save_data_fname='vci3m_district_l2.csv'
)
l2_gdf = grouper.gdf

# Mean over time
mean_vci3m = l2_gdf.groupby(['region_name']).mean().reset_index()

mean_gdf = grouper.join_dataframe_geodataframe(
    df=mean_vci3m, gdf=l2_gdf,
    gdf_colname='DISTNAME', df_colname='region_name'
)


# ------------------------------------------------------
# plot each region VHI3M
# ------------------------------------------------------

# regions from the paper
regions = ['TURKANA', 'MARSABIT', 'MANDERA', 'WAJIR']
assert np.isin(regions, l2_gdf.region_name.unique()).all()

rois = l2_gdf.loc[l2_gdf.region_name.isin(regions)]

# import seaborn as sns
import matplotlib.pyplot as plt

fig, ax =  plt.subplots()
for roi in rois.region_name.unique():
    subset = rois.loc[rois.region_name == roi]
    ax.plot(subset['datetime'], subset['mean_value'], label=roi)
plt.legend()

# ------------------------------------------------------
# plot each region VDI
# ------------------------------------------------------


def VDI(df: pd.DataFrame,
        values_column: str,
        new_column: str = 'VDI') -> pd.DataFrame:
    """ pandas implementation of the VDI """
    bins = [0.0, 10., 20., 35., 50.]
    df[new_column] = np.digitize(df[values_column], bins)
    return df


# FIT the VegetationDeficitIndex
vdi_df = VDI(rois, 'mean_value')

fig, ax =  plt.subplots()
for roi in rois.region_name.unique():
    subset = rois.loc[rois.region_name == roi]
    ax.plot(subset['datetime'], subset['VDI'], label=roi)
plt.legend(loc='upper left')

# summary table p.11
(rois
 .groupby(['region_name', 'VDI'])
 .VDI.count()
 .unstack('VDI')
 .rename(columns={1: 'Extreme', 2: 'Severe', 3: 'Moderate'})
 .drop(columns=[4, 5])
)
