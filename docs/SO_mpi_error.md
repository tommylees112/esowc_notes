# MPI Errors 

The following just makes the example data to be used by the regridder

```python
import pandas as pd
import numpy as np
import xarray as xr

def make_dataset():
    time = pd.date_range('2010-01-01','2018-12-31',freq='M')
    lat = np.linspace(-5.175003, -4.7250023, 10)
    lon = np.linspace(33.524994, 33.97499, 10)
    precip = np.random.normal(0, 1, size=(len(time), len(lat), len(lon)))

    ds = xr.Dataset(
        {'precip': (['time', 'lat', 'lon'], precip)},
        coords={
            'lon': lon,
            'lat': lat,
            'time': time,
        }
    )
    return ds


def make_fcast_dataset(date_str):
    initialisation_date = pd.date_range(start=date_str, periods=1, freq='M')
    number = [i for i in range(0, 10)]
    lat = np.linspace(-5.175003, -5.202, 5)
    lon = np.linspace(33.5, 42.25, 5)
    forecast_horizon = np.array(
        [ 2419200000000000,  2592000000000000,  2678400000000000,
          5097600000000000,  5270400000000000,  5356800000000000,
          7689600000000000,  7776000000000000,  7862400000000000,
          7948800000000000, 10368000000000000, 10454400000000000,
          10540800000000000, 10627200000000000, 12960000000000000,
          13046400000000000, 13219200000000000, 15638400000000000,
          15724800000000000, 15811200000000000, 15897600000000000,
          18316800000000000, 18489600000000000, 18576000000000000 ],
          dtype='timedelta64[ns]'
    )
    valid_time = initialisation_date[:, np.newaxis] + forecast_horizon
    precip = np.random.normal(
        0, 1, size=(len(number), len(initialisation_date), len(forecast_horizon), len(lat), len(lon))
    )

    ds = xr.Dataset(
        {'precip': (['number', 'initialisation_date', 'forecast_horizon', 'lat', 'lon'], precip)},
        coords={
            'lon': lon,
            'lat': lat,
            'initialisation_date': initialisation_date,
            'number': number,
            'forecast_horizon': forecast_horizon,
            'valid_time': (['initialisation_date', 'step'], valid_time)
        }
    )
    return ds

# make the example datasets
regrid = make_dataset()
ds = make_fcast_dataset(date_str='2000-01-01')
```

When using the regridder I get the following error.
```python
import xesmf as xe

xe.Regridder(d_, regrid, 'nearest_s2d')

ipdb> xe.Regridder(d_, regrid.precip, 'nearest_s2d')
[mpiexec@linux1.ouce.ox.ac.uk] match_arg (utils/args/args.c:159): unrecognized argument pmi_args
[mpiexec@linux1.ouce.ox.ac.uk] HYDU_parse_array (utils/args/args.c:174): argument matching returned error
[mpiexec@linux1.ouce.ox.ac.uk] parse_args (ui/mpich/utils.c:1596): error parsing input array
[mpiexec@linux1.ouce.ox.ac.uk] HYD_uii_mpx_get_parameters (ui/mpich/utils.c:1648): unable to parse user arguments
[mpiexec@linux1.ouce.ox.ac.uk] main (ui/mpich/mpiexec.c:149): error parsing parameters
```

I am very inexperienced with MPI and so would really appreciate any pointers you might have!

Thanks very much
