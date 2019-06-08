import xarray as xr
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import mapclassify as mc
import os
from typing import List

%matplotlib

if os.getcwd().split('/')[2] == "tommylees":
    data_dir = Path('/Volumes/Lees_Extend/data/ecmwf_sowc/data')
else:
    data_dir = Path('data')

era5_dir = data_dir / "interim" / "era5POS_preprocessed" / "era5POS_kenya.nc"
chirps_dir = data_dir / "interim" / "chirps_preprocessed" / "chirps_kenya.nc"

c = xr.open_dataset(chirps_dir)
e = xr.open_dataset(era5_dir)

# convert c to mm/day
c['precip'] = c.precip / 5
c.attrs['units'] = 'mm/day'

e['precip'] = e['precipitation_amount_1hour_Accumulation'] * 24
e.precip.attrs['units'] = 'mm/day'

# convert to monthly
c = c.sortby('time')
c = c.resample(time='M').mean()

times = pd.date_range('1900-01-01', freq='M', periods=1440)  # '2019-03-31',
c_lt = xr.open_dataset(
        '/Volumes/Lees_Extend/data/ecmwf_sowc/chirps_kenya.nc',
        decode_times=False
)
c_lt['time'] = times

# -----------------------------------------------------------------------------
## calculate GEV xarray
# -----------------------------------------------------------------------------


# -----------------------------------------------------------------------------
## calculate GEV pandas
# -----------------------------------------------------------------------------
def get_test_df(ds: xr.Dataset,
                variable: str,
                min_yr: int = 2010,
                max_yr: int = 2015):
    df = (
        ds.sel(time=slice(str(min_yr), str(max_yr)))
        .isel(lat=0,lon=0)[variable]
        .to_dataframe(name=variable)
        .reset_index()
        .set_index('time')
    )

    return df


variable = 'precip'
df = get_test_df(c_lt, variable, min_yr=1900, max_yr=2018)
df = df.drop(['lat','lon'], axis=1)

# get annual_maxima
annual_maxima = df.resample('Y').max()

fig, ax = plt.subplots()
annual_maxima.plot(ax=ax)
ax.set_title('Annual Maxima')

# get 3month cumsum

## Fit a gev
# https://github.com/kikocorreoso/scikit-extremes/blob/master/skextremes/models/classic.py - been barking up the wrong tree here trying to get

import lmoments
%run /Users/tommylees/miniconda3/envs/crop/lib/python3.7/site-packages/lmoments/lmoments.py

series = annual_maxima[variable]

# sample lmoments = find the lmoments from the data
LMU = samlmu(series.values)

# parameter estimation
gevfit = pelgev(LMU)
expfit = pelexp(LMU)
gumfit = pelgum(LMU)
gpafit = pelgpa(LMU)
pe3fit = pelpe3(LMU)
gamfit = pelgam(LMU)
glofit = pelglo(LMU)
# weifit = pelwei(LMU)

# calculate return periods
rps  = [2, 5, 10, 20, 50, 100, 200, 500, 1000]  # (average return interval)
rps_qua = [1.0 - (1.0 / rp) for rp in rps]  # convert 1:YYYY -> 0:1
gevqua = quagev(rps_qua, gevfit)  # quantiles

# plot the log return interval
plt.plot(rps, gevqua)
plt.xscale('log')
plt.xlabel('Log (Average Return Interval in Year)')
plt.ylabel('Max Annual Precipitation')
plt.title("GEV Distribution")

# plot the raw return interval
plt.close('all')
plt.plot(rps, gevqua)
plt.xlabel('Average Return Interval in Year')
plt.ylabel('Max Annual Precipitation')
plt.title("GEV Distribution")




# get return years (1.1 to 1000)
T = np.arange(0.1, 999.1, 0.1) + 1

# generate from the fitted parameters (quantile functions)
gevST = quagev(1.0-1./T, gevfit)
expST = quaexp(1.0-1./T, expfit)

# compare to empirical distribution

from matplotlib.legend_handler import HandlerLine2D

plt.close('all')
plt.xscale('log')
plt.xlabel('Average Return Interval (Year)')
plt.ylabel('Precipitation (mm)')
line1, = plt.plot(T, gevST, 'g', label='GEV')
# line2, = plt.plot(T, expST, 'r', label='EXP')

# plot empirical distribution


N = np.array([val for val in range(series.size)])  # np.r_[1:len(series.index) + 1] * 1.0
Nmax = max(N)  # len(N)
plt.scatter(Nmax/N, sorted(series.values), color = 'orangered', facecolors='none', label='Empirical')
plt.scatter(N, sorted(series.values), label='Empirical')
plt.legend(handler_map={line1: HandlerLine2D(numpoints=4)})



def GEV(series):
    paras = distr.gev.lmom_fit(series.values)
    return paras

GEV(series)

##
"""
import scipy.misc as sm
import scipy.special as sp

REPLACE sm.comb => sp.comb
"""

import skextremes as ske
data_array = series.values
GEV_model = ske.models.classic.GEV(data_array, fit_method='mle', ci=0.05, ci_method='delta')
params = GEV_model.params
plt.close('all')
GEV_model.plot_summary()

# -----------------------------------------------------------------------------
## Marginalia
# -----------------------------------------------------------------------------
from scipy.stats import genextreme as gev

def GEV(series):
    scale, loc, shape = gev.fit(series)
    return shape, loc, scale

shape, loc, scale = GEV(annual_maxima[variable])
l = loc + scale / shape


def plot_GEV_fit(series, shape, loc, scale):
    """`scipy` order, e.g. scale, loc, shape"""
    xx = np.linspace(l+0.00001, l+0.00001+35, num=71)
    yy = gev.pdf(xx, scale, loc, shape)

    fig, ax = plt.subplots()
    # plot histogram of observed data
    series.plot.hist(ax=ax)

    ax.plot(xx, yy, 'ro')
    plt.show()

plot_GEV_fit(annual_maxima[variable], shape, loc, scale)
