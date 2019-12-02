import xarray as xr
import numpy as np
from osgeo import gdal
from pathlib import Path
import shutil


def tif_to_nc(tif_file: Path, nc_file: Path) -> None:
    ds = gdal.Open(tif_file.resolve().as_posix())  # type: ignore
    _ = gdal.Translate(format='NetCDF', srcDS=ds,  # type: ignore
                       destName=nc_file.resolve().as_posix())


# data_dir = Path('/Volumes/Lees_Extend/data/ecmwf_sowc/data')
data_dir = Path('/lustre/soge1/projects/crop_yield/ml_drought/data')
raw_dir = data_dir / 'raw/modis_ndvi_1000'
assert raw_dir.exists()

# create lists of files
tif_files = [f for f in raw_dir.glob('*.tif')]
TMP_nc_files = [f.parents[0] / (f.stem + '_TMP.nc') for f in tif_files]
nc_files = [f.parents[0] / (f.stem + '.nc') for f in tif_files]

tif_files.sort()
TMP_nc_files.sort()
nc_files.sort()

# -------------------------
# convert tif to netcdf
# -------------------------

# print('\n')
# for tif_file, nc_file in zip(tif_files, TMP_nc_files):
#     tif_to_nc(tif_file, nc_file)
#     print(f'-- Converted {tif_file.name} to netcdf --')

# -------------------------
# Move all files to .../tifs/
# -------------------------

# dst_dir = raw_dir / 'tifs'
# if not dst_dir.exists():
#     dst_dir.mkdir(exist_ok=True, parents=True)

# dst_tif_files = [dst_dir / f.name for f in tif_files]

# for src, dst in zip(tif_files, dst_tif_files):
#     shutil.move(src, dst)

# -------------------------
# rename BAND1 to rename_str
# -------------------------

rename_str = 'modis_ndvi']
tif_files = [f for f in raw_dir.glob('tifs/*.tif')]
TMP_nc_files = [f for f in raw_dir.glob('*TMP.nc')]
nc_files = [f.parents[1] / (f.stem + '.nc') for f in tif_files]

TMP_nc_files.sort()
nc_files.sort()

print('\n')
for tmp_file, nc_file in zip(TMP_nc_files, nc_files):
    ds = xr.open_dataset(tmp_file).rename(dict(Band1=rename_str))
    da = ds[rename_str]
    da.to_netcdf(nc_file)
    print(f'-- Renamed {nc_file.name} to {rename_str} --')

# -------------------------
# Remove the temporary files
# -------------------------

[f.unlink() for f in TMP_nc_files]
print('Removed *TMP.nc files')
