import salem
import xarray as xr
import numpy as np
from pathlib import Path
from salem import get_demo_file, DataLevels, GoogleVisibleMap, Map
import matplotlib.pyplot as plt

data_dir = Path("/Volumes/Lees_Extend/data/ecmwf_sowc/")
path = data_dir / "chirps_kenya.nc"

ds = xr.open_dataset(path, decode_times=False)
times = pd.date_range("1900-01-01", "2019-12-31", freq="M")
ds["time"] = times
da = ds.precip
# sds = salem.open_xr_dataset(path, **dict(decode_times=False))

fig, ax = plt.subplots()
map_ = da.mean(dim="time").salem.quick_map(ax=ax)
map_

# conda install -c motionless
# prepare the figure
f, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

# read the shapefile and use its extent to define a ideally sized map
shp = salem.read_shapefile(get_demo_file("rgi_kesselwand.shp"))

g = GoogleVisibleMap(
    x=[shp.min_x, shp.max_x],
    y=[shp.min_y, shp.max_y],
    scale=2,  # scale is for more details
    maptype="satellite",
)  # try out also: 'terrain'
