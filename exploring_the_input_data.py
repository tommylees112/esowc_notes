import xarray as xr
import pandas as pd
from geopandas import GeoDataFrame
import pickle
from pathlib import Path
data_dir = Path('/Volumes/Lees_Extend/data/ecmwf_sowc/data')

from src.analysis.region_analysis.groupby_region import KenyaGroupbyRegion
from src.analysis.region_analysis.groupby_region import GroupbyRegion
from src.analysis import read_train_data

# ------------------------
# Read the training data
# ------------------------
X, y = read_train_data(data_dir)

# extract mean values for each region for each variable
region_grouper = KenyaGroupbyRegion(data_dir=data_dir)
region_precip_df = region_grouper.analyze(X.precip, selection='level_2')
region_precip_gdf = region_grouper.gdf.rename(columns={'mean_value': 'precip'})

region_grouper = KenyaGroupbyRegion(data_dir=data_dir)
region_E_df = region_grouper.analyze(X.E, selection='level_2')
region_E_gdf = region_grouper.gdf.rename(columns={'mean_value': 'E'})

region_grouper = KenyaGroupbyRegion(data_dir=data_dir)
region_SMsurf_df = region_grouper.analyze(X.SMsurf, selection='level_2')
region_SMsurf_gdf = region_grouper.gdf.rename(columns={'mean_value': 'SMsurf'})

region_grouper = KenyaGroupbyRegion(data_dir=data_dir)
region_VCI_df = region_grouper.analyze(y.VCI, selection='level_2')
region_VCI_gdf = region_grouper.gdf.rename(columns={'mean_value': 'VCI'})


# region_precip_gdf = region_precip_gdf.rename(columns={'mean_value': 'precip'})
# region_E_gdf = region_E_gdf.rename(columns={'mean_value': 'E'})
# region_SMsurf_gdf = region_SMsurf_gdf.rename(columns={'mean_value': 'SMsurf'})
# region_VCI_gdf = region_VCI_gdf.rename(columns={'mean_value': 'VCI'})



def engineer_region_dataframe(da: xr.DataArray,
                              region_grouper: GroupbyRegion,
                              selection: str) -> GeoDataFrame:
    """From a DataArray create a GeoDataFrame for the mean spatial
    values stored in a tabular format.

    Arguments:
    ---------
    da: xr.DataArray
        DataArray you want to group into regions
    region_grouper: GroupbyRegion
        the GroupbyRegion object (e.g. KenyaGroupbyRegion()).
        NOTE: must be initialised when handed to method
    selection: str
        the region selection (e.g. 'level_2' in Kenya) to
        group by.
    """
    variable = da.name
    region_grouper.analyze(da, selection=selection)
    return region_grouper.gdf.rename(columns={'mean_value': variable})



def merge_to_one_gdf(region_gdfs: List):
    """ """
    gdf = region_gdfs[0]

    for region_gdf in region_gdfs[1:]:
        gdf = pd.merge(gdf, region_gdf, how='inner', left_on=['datetime', 'region_name'], right_on=['datetime', 'region_name'])

    cols = [c for c in gdf.columns if '_y' in c]
    cols += [c for c in gdf.columns if 'E_x' in c]
    gdf = gdf.drop(columns=cols)

    return gdf


# RUN the functions
X, y = read_train_data(data_dir)

region_grouper = KenyaGroupbyRegion(data_dir=data_dir)
region_precip_gdf = engineer_region_dataframe(
    da=X.precip, region_grouper=region_grouper, selection='level_2'
)
region_E_gdf = engineer_region_dataframe(
    da=X.E, region_grouper=region_grouper, selection='level_2'
)
region_SMsurf_gdf = engineer_region_dataframe(
    da=X.SMsurf, region_grouper=region_grouper, selection='level_2'
)
region_VCI_gdf = engineer_region_dataframe(
    da=X.VCI, region_grouper=region_grouper, selection='level_2'
)

region_gdfs = [
    region_precip_gdf,
    region_E_gdf,
    region_SMsurf_gdf,
    region_VCI_gdf,
]

gdf = merge_to_one_gdf(region_gdfs)
with open(data_dir / 'analysis' / 'all_gdf.pkl', 'wb') as f:
    pickle.dump(gdf, f)

gdf = pickle.load(open(data_dir / 'analysis' / 'all_gdf.pkl', 'rb'))


# ------------------------
# pickle objects
# ------------------------

import pickle

with open(data_dir / 'analysis' / 'region_precip_gdf.pkl', 'wb') as f:
    pickle.dump(region_precip_gdf, f)

with open(data_dir / 'analysis' / 'region_E_gdf.pkl', 'wb') as f:
    pickle.dump(region_E_gdf, f)

with open(data_dir / 'analysis' / 'region_SMsurf_gdf.pkl', 'wb') as f:
    pickle.dump(region_SMsurf_gdf, f)


d    pickle.dump(region_VCI_gdf, f)

with open(data_dir / 'analysis' / 'all_gdf.pkl', 'wb') as f:
    pickle.dump(gdf, f)

# load the files
region_precip_gdf = pickle.load(open(data_dir / 'analysis' / 'region_precip_gdf.pkl', 'rb'))
region_E_gdf = pickle.load(open(data_dir / 'analysis' / 'region_E_gdf.pkl', 'rb'))
region_SMsurf_gdf = pickle.load(open(data_dir / 'analysis' / 'region_SMsurf_gdf.pkl', 'rb'))
region_VCI_gdf = pickle.load(open(data_dir / 'analysis' / 'region_VCI_gdf.pkl', 'rb'))
gdf = pickle.load(open(data_dir / 'analysis' / 'all_gdf.pkl', 'rb'))


# ------------------------
# plot functions
# ------------------------

def plot_spatial_timestep(gdf: gpd.GeoDataFrame,
                          datetime: str,
                          variable: str = 'mean_value') -> None:
    """ """
    gdf.loc[gdf.datetime==datetime].plot(variable)


def plot_region_timeseries(gdf: Union[gpd.GeoDataFrame, pd.DataFrame],
                           region_name: str,
                           ax: plt.Axes) -> None:
    """ """
    assert np.isin(['datetime', 'mean_value'], gdf.columns).all()
    (gdf
     .loc[gdf.region_name == region_name]
     .set_index('datetime')
     .mean_value.plot(ax=ax, label=region_name)
    )


fig, ax = plt.subplots()
plot_region_timeseries(region_precip_gdf, 'TURKANA', ax=ax)
plot_region_timeseries(region_precip_gdf, 'MARSABIT', ax=ax)
plt.legend()

fig, ax = plt.subplots()
plot_region_timeseries(region_VCI_gdf, 'TURKANA', ax=ax)
plot_region_timeseries(region_VCI_gdf, 'KITUI', ax=ax)
plt.legend()
