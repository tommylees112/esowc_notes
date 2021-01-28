from src.preprocess import ESACCIPreprocessor
import xarray as xr
from src.utils import get_modal_value_across_time


e = ESACCIPreprocessor()
ds = xr.open_mfdataset(e.get_filepaths("interim"))
ds = get_modal_value_across_time(ds.lc_class).to_dataset()
ds = e._one_hot_encode(ds, group=group)
