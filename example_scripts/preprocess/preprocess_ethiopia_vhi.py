from pathlib import Path

# from src.preprocess.vhi import VHIPreprocesser
from src.preprocess import VHIPreprocessor

data_dir = Path('/scratch/chri4118/data/')

v = VHIPreprocessor(data_folder=data_dir)
v.preprocess(
    subset_str='ethiopia',
    regrid=None,
    parallel=True,
    resample_time = None
)

# wait
import salem
%matplotlib
ds = xr.open_dataset(data_dir)
ds.VHI.salem.quick_map()
