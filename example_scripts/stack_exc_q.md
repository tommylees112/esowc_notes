#### Code Sample, a copy-pastable example if possible

A "Minimal, Complete and Verifiable Example" will make it much easier for maintainers to help you:
http://matthewrocklin.com/blog/work/2018/02/28/minimal-bug-reports

Code is all from this [Stack Exchange post here](https://stackoverflow.com/questions/55995471/python-get-month-of-maximum-value-xarray)

I have used a similar approach to dealing with nan values as @jhamman [here](https://stackoverflow.com/a/50499427/9940782)

**NOTE**: this dataset is >2GB
```python
# Your code here
import os
if not os.path.exists('grun.nc'):
  process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
  output, error = process.communicate()

# read the data
import xarray as xr
ds = xr.open_dataset('grun.nc')

# select a subset so we can work with it more quickly
ds = ds.isel(time=slice(-100,-1))

#
def my_func(ds, dim=None):
    return ds.isel(**{dim: ds['Runoff'].argmax(dim)})

mask = ds['Runoff'].isel(time=0).notnull()  # determine where you have valid data
ds2 = ds.fillna(-9999)  # fill nans with a missing flag of some kind
new = ds2.reset_coords(drop=True).groupby('time.month').apply(my_func, dim='time').where(mask)  # do the groupby operation/reduction and reapply the mask

```
#### Problem description

[this should explain **why** the current behavior is a problem and why the expected output is a better solution.]

#### Expected Output

#### Output of ``xr.show_versions()``

<details>
# Paste the output here xr.show_versions() here

</details>
