import xarray as xr
import numpy as np
from pathlib import Path
from src.preprocess import CHIRPSPreprocesser
from src.preprocess.base import BasePreProcessor
from scripts.eng_utils import

data_dir = Path('data')
chirps_path = data_dir / 'interim' / 'chirps_preprocessed' / 'chirps_kenya.nc'
vhi_path = data_dir / 'interim' / 'vhi_preprocessed' / 'vhi_kenya.nc'

c_ds = xr.open_dataset(chirps_path)
v_ds = xr.open_dataset(vhi_path)

pp = BasePreProcessor(data_dir)
c_ds = pp.regrid(c_ds, v_ds)
c_ds = pp.resample_time(c_ds)

v_ds = pp.resample_time(v_ds)

v_ds.to_netcdf(vhi_path.home() / vhi_path.parent / 'vhi_kenya_regrid.nc')
v_ds.to_netcdf(chirps_path.home() / chirps_path.parent / 'chirps_kenya_regrid.nc')



#
def overwrite_save(ds, filepath):
    """ """
    import shutil

    rand_number = abs(np.random.normal(0,1))
    new_fp = filepath.home() / filepath.parent / f"{filepath.stem}_OLD_{rand_number:.1f}.nc"
    temp_fp = filepath.home() / filepath.parent / "temp.nc"
    ds.to_netcdf(temp_fp)
    ds.close()

    shutil.move(filepath, new_fp)
    ds = xr.open_dataset(temp_fp)
    ds.to_netcdf(filepath)

    return filepath

overwrite_save(c_ds, chirps_path)
