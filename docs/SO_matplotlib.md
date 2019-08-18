I need to create a 2D image of gridded data with unevenly spaced values. I am plotting a categorical dataset where the categories are encoded with numerical values corresponding to a specific label.

I need to be able to use the formatter to assign a different color to each category in the dataset. This should preferably be flexible because the true dataset has ~30 unique categories that I am plotting. Thus I should have a unique color for when the value is `10` and when it is `40`.

Making the example data to demonstrate
```python
import xarray as xr
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

time = pd.date_range('2010-01-31', '2015-12-31', freq='M')
lat = np.linspace(0, 1, 224)
lon = np.linspace(0, 1, 176)
valid_vals = [10., 40., 50., 60.]
labels = ['type_1', 'type_2', 'type_3', 'type_4']
lookup = dict(zip(valid_vals, labels))

values = np.random.choice(valid_vals, size=(len(time), len(lat), len(lon)))
rand_nans = np.random.random(size=(len(time), len(lat), len(lon))) < 0.3
values[rand_nans] = np.nan

coords = {'time': time, 'lat': lat, 'lon': lon}
dims = ['time', 'lat', 'lon']

ds = xr.Dataset({'lc_code': (dims, values)}, coords=coords)

# convert to numpy array (only the first timestep)
im = ds.isel(time=0).lc_code.values

ds
Out[]:
<xarray.Dataset>
Dimensions:  (lat: 224, lon: 176, time: 72)
Coordinates:
  * time     (time) datetime64[ns] 2010-01-31 2010-02-28 ... 2015-12-31
  * lat      (lat) float64 0.0 0.004484 0.008969 0.01345 ... 0.991 0.9955 1.0
  * lon      (lon) float64 0.0 0.005714 0.01143 0.01714 ... 0.9886 0.9943 1.0
Data variables:
    lc_code  (time, lat, lon) float64 50.0 nan 60.0 50.0 ... 40.0 10.0 40.0 10.0
```

Just plotting the image data alone has two problems:
1) The tick labels are not the strings defined in `labels`
2) The colorbar is evenly spaced but the values are not. Such that we have values at `10, 40, 50, 60`

```python
plt.imshow(im, cmap=plt.cm.get_cmap('tab10', len(valid_vals)))
plt.colorbar()
```

So I have tried with the `FuncFormatter`. However this image still has the problem that no values are mapped to the `type_2` color despite the tick label lining up in the centre of the colorbar.

```python
fig, ax = plt.subplots(figsize=(12, 8))

plt.imshow(im, cmap=plt.cm.get_cmap('tab10', len(valid_vals)))

# calculate the POSITION of the tick labels
min_ = min(valid_vals)
max_ = max(valid_vals)
positions = np.linspace(min_, max_, len(valid_vals))
val_lookup = dict(zip(positions, labels))

def formatter_func(x, pos):
    'The two args are the value and tick position'
    val = val_lookup[x]
    return val

formatter = plt.FuncFormatter(formatter_func)

# We must be sure to specify the ticks matching our target names
plt.colorbar(ticks=positions, format=formatter, spacing='proportional');

# set the colorbar limits so that the ticks are evenly spaced
plt.clim(0, 70)
```

But this code forces the second category (values of `40`, `type_2`) to not be shown with the color the `tick` lines up with. Therefore, the colorbar isn't effectively reflecting the data in the image.

```python
(im == 40).mean()

Out[]:
0.17347301136363635
```
