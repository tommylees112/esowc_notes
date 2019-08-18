from pathlib import Path
import xarray as xr
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from src.analysis.indices import (
    ZScoreIndex,
    PercentNormalIndex,
    DroughtSeverityIndex,
    ChinaZIndex,
    DecileIndex,
    AnomalyIndex,
    SPI
)

%load_ext autoreload
%autoreload 2

data_dir = Path('/Volumes/Lees_Extend/data/ecmwf_sowc/data')
out_dir = data_dir / 'analysis' / 'indices'
if not out_dir.exists():
    out_dir.mkdir(parents=True, exist_ok=True)
data_path = data_dir / "interim" / "chirps_preprocessed" / "chirps_kenya.nc"


# --------------------------------------------------------
# fit all indices
# --------------------------------------------------------
if (out_dir / 'all_indices.nc').exists():
    ds = xr.open_dataset(out_dir / 'all_indices.nc')

else:
    indices = (
        ZScoreIndex,
        PercentNormalIndex,
        DroughtSeverityIndex,
        ChinaZIndex,
        DecileIndex,
        AnomalyIndex,
        SPI
    )

    out = {}
    for index in indices:
        i = index(data_path)
        i.fit(variable='precip')
        out[index.name] = i

    print([k for k in out.keys()])

    # --------------------------------------------------------
    # join all indices -> 1 dataset
    # --------------------------------------------------------

    ds_objs = [index.index
        for index in out.values()
    ]
    ds = xr.merge(ds_objs)
    ds = ds.drop(['month', 'precip_cumsum']).isel(time=slice(2,-1))
    ds.to_netcdf(out_dir / 'all_indices.nc')

# --------------------------------------------------------
# View correlation between all indices
# --------------------------------------------------------
# 1. as time series
ts = ds.drop('quintile').mean(dim=['lat', 'lon'])
# drop inf
ts = ts.where(~(ts.RAI == np.inf)).dropna(dim='time')
norm_df = ((ts - ts.mean()) / ts.std()).to_dataframe()

fig, ax = plt.subplots()
norm_df.loc[np.isin(norm_df.index.year,np.arange(2008, 2015))].plot(ax=ax)
ax.set_title('Normalised Index Values 2008 - 2014')
ax.axhline(0, 0, 1, color='k', ls='--', alpha=0.4)
# 2. over the whole spatial domain



spi = SPI(data_path)
spi.fit(variable='precip')

# k_2010 = s.index.sel(time=np.isin(s.index['time.year'], [2008, 2009, 2010, 2011, 2012]))
k_2010 = spi.index.sel(time=slice('2008','2013'))

fig, ax = plt.subplots()
k_2010.mean(dim=['lat','lon']).SPI.plot(ax=ax)
ax.set_title('SPI3 over time')
ax.axhline(y=0, xmin=0, xmax=1, color='k', ls='--', alpha=0.5)
plt.show()
