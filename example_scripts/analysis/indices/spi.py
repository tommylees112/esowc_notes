from pathlib import Path
import xarray as xr
import pandas as pd

# data_dir = Path('data')
# p_dir = data_dir / 'interim' / 'chirps_preprocessed' / 'chirps_19812019_kenya.nc'
# v_dir = data_dir / 'interim' / 'vhi_preprocessed' / 'vhi_preprocess_kenya.nc'
# p = xr.open_dataset(p_dir)
# v = xr.open_dataset(v_dir)

# ------------------------------------------------------------------------------
# LOAD DATA
# ------------------------------------------------------------------------------
data_dir = Path('/Volumes/Lees_Extend/data/ecmwf_sowc/data')

era5_dir = data_dir / "interim" / "era5POS_preprocessed" / "era5POS_kenya.nc"
chirps_dir = data_dir / "interim" / "chirps_preprocessed" / "chirps_kenya.nc"

## load xarray datasets
c = xr.open_dataset(chirps_dir)
e = xr.open_dataset(era5_dir)

times = pd.date_range('1900-01-01', freq='M', periods=1440)  # '2019-03-31',
c_lt = xr.open_dataset(
        '/Volumes/Lees_Extend/data/ecmwf_sowc/chirps_kenya.nc',
        decode_times=False
)
c_lt['time'] = times

# fix the datasets
# convert c to mm/day
c['precip'] = c.precip / 5
c.attrs['units'] = 'mm/day'

e['precip'] = e['precipitation_amount_1hour_Accumulation'] * 24
e.precip.attrs['units'] = 'mm/day'

# convert to monthly
c = c.sortby('time')
c = c.resample(time='M').mean()

c_ = c.sel(time=slice('2010', '2015'))
ts = c_.isel(lat=0, lon=100)

da_precip = c_.precip

# ------------------------------------------------------------------------------
## TEST SPI
# ------------------------------------------------------------------------------
from climate_indices import indices
from climate_indices.__main__ import _spi

# indices.spi

# https://stackoverflow.com/questions/53108606/xarray-apply-ufunc-with-groupby-unexpected-number-of-dimensions
da_precip_groupby = da_precip.stack(point=('lat', 'lon')).groupby('point')

# apply the SPI function to the data array
scale = 3
distribution = climate_indices.indices.Distribution.gamma
data_start_year = 2010
calibration_year_initial = 2010
calibration_year_final = 2015
periodicity = climate_indices.compute.Periodicity.monthly

da_spi = xr.apply_ufunc(indices.spi,
                        da_precip_groupby,
                        scale,
                        distribution,
                        data_start_year,
                        calibration_year_initial,
                        calibration_year_final,
                        periodicity)


# unstack the array back into original dimensions
da_spi = da_spi.unstack('point')
