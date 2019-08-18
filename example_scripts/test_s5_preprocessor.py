%load_ext autoreload
%autoreload 2

from src.preprocess import S5Preprocessor
from pathlib import Path

data_path = Path('data')
p = S5Preprocessor(data_path)

# p.get_filepaths(p.raw_folder, variable='total_precipitation')

regrid_ds = data_path / "interim" / "chirps_preprocessed" / "chirps_kenya.nc"
p.preprocess(variable='total_precipitation', regrid=regrid_ds)
# p.merge_and_resample(
#    variable='tp'
# )
