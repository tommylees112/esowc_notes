from pathlib import Path
import xarray as xr

data_dir = Path('data')
p_dir = data_dir / 'interim' / 'chirps_preprocessed' / 'chirps_19812019_kenya.nc'
v_dir = data_dir / 'interim' / 'vhi_preprocessed' / 'vhi_preprocess_kenya.nc'

p = xr.open_dataset(p_dir)
v = xr.open_dataset(v_dir)

## TEST SPI
from climate_indices import indices
