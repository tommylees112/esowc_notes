# find . -name "*.py" -exec grep -H "napiri" {} \;

"""
https://github.com/napari/napari/pull/649/files
napari/_vispy/vispy_base_layer.py
L99: +mode='constant'
L114: +mode='constant'
"""
%load_ext autoreload
%autoreload 2
from pathlib import Path
import xarray as xr
import numpy as np
import napari
import pickle
import calendar
from src.preprocess.utils import select_bounding_box
from src.preprocess.utils import Region

data_path = Path('/Users/tommylees/Downloads/static_embeddings.nc')
ds = xr.open_dataset(data_path)
cluster_ds = ds
da = ds.cluster_5

array = da.values[:, ::-1, :]  # time, lat, lon

%gui qt
napari.gui_qt()
# viewer = napari.Viewer()

for i in range(array.shape[0]):
    viewer.add_image(
        array[i, :, :],
        contrast_limits=[0, 4],
        colormap='viridis',
        name=calendar.month_abbr[i+1]
    )


# viewer.layers
[l.name for l in viewer.layers]
kitui = [l.data for l in viewer.layers if l.name == 'kitui']
victoria = [l.data for l in viewer.layers if l.name == 'victoria']
turkana_edge = [l.data for l in viewer.layers if l.name == 'turkana_edge']
nw_pastoral = [l.data for l in viewer.layers if l.name == 'nw_pastoral']
coastal = [l.data for l in viewer.layers if l.name == 'coastal']

victoria = [l.data for l in viewer.layers if l.name == 'victoria']
turkana = [l.data for l in viewer.layers if l.name == 'lake_turkana']
southern_highlands = [l.data for l in viewer.layers if l.name == 'southern_highlands']
coastal = [l.data for l in viewer.layers if l.name == 'coastal']
# ------------------------------------------------------
# REGIONS 1
# ------------------------------------------------------
{
    'kitui': kitui[0][0],
    'victoria': victoria[0][0],
    'turkana_edge': turkana_edge[0][0],
    'nw_pastoral': nw_pastoral[0][0],
    'coastal': coastal[0][0],
}

kitui = Region(
    name='kitui',
    lonmin=cluster_ds.isel(lon=13).lon.values,
    lonmax=cluster_ds.isel(lon=19).lon.values,
    latmin=cluster_ds.isel(lat=-34).lat.values,
    latmax=cluster_ds.isel(lat=-24).lat.values,
)
victoria = Region(
    name='victoria',
    lonmin=cluster_ds.isel(lon=0).lon.values,
    lonmax=cluster_ds.isel(lon=12).lon.values,
    latmin=cluster_ds.isel(lat=-31).lat.values,
    latmax=cluster_ds.isel(lat=-15).lat.values,
)
turkana_edge = Region(
    name='turkana_edge',
    lonmin=cluster_ds.isel(lon=14).lon.values,
    lonmax=cluster_ds.isel(lon=29).lon.values,
    latmin=cluster_ds.isel(lat=-9).lat.values,
    latmax=cluster_ds.isel(lat=-2).lat.values,
)
nw_pastoral = Region(
    name='nw_pastoral',
    lonmin=cluster_ds.isel(lon=0).lon.values,
    lonmax=cluster_ds.isel(lon=12).lon.values,
    latmin=cluster_ds.isel(lat=-6).lat.values,
    latmax=cluster_ds.isel(lat=-1).lat.values,
)
coastal = Region(
    name='coastal',
    lonmin=cluster_ds.isel(lon=21).lon.values,
    lonmax=cluster_ds.isel(lon=34).lon.values,
    latmin=cluster_ds.isel(lat=-25).lat.values,
    latmax=cluster_ds.isel(lat=-13).lat.values,
)



# ------------------------------------------------------
# REGIONS 2
# ------------------------------------------------------
{
    'victoria': victoria[0][0],
    'turkana': turkana[0][0],
    'southern_highlands': southern_highlands[0][0],
    'coastal': coastal[0][0],
}

victoria = Region(
    name='victoria',
    lonmin=cluster_ds.isel(lon=0).lon.values,
    lonmax=cluster_ds.isel(lon=7).lon.values,
    latmin=cluster_ds.isel(lat=-28).lat.values,
    latmax=cluster_ds.isel(lat=-18).lat.values,
)
turkana = Region(
    name='turkana',
    lonmin=cluster_ds.isel(lon=5).lon.values,
    lonmax=cluster_ds.isel(lon=16).lon.values,
    latmin=cluster_ds.isel(lat=-16).lat.values,
    latmax=cluster_ds.isel(lat=-6).lat.values,
)
southern_highlands = Region(
    name='southern_highlands',
    lonmin=cluster_ds.isel(lon=3).lon.values,
    lonmax=cluster_ds.isel(lon=13).lon.values,
    latmin=cluster_ds.isel(lat=-41).lat.values,
    latmax=cluster_ds.isel(lat=-31).lat.values,
)
coastal = Region(
    name='coastal',
    lonmin=cluster_ds.isel(lon=15).lon.values,
    lonmax=cluster_ds.isel(lon=20).lon.values,
    latmin=cluster_ds.isel(lat=-44).lat.values,
    latmax=cluster_ds.isel(lat=-34).lat.values,
)

fig, ax = plt.subplots()
select_bounding_box(cluster_ds, southern_highlands).cluster_5.isel(time=0).plot()
