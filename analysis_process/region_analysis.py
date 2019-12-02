from typing import List
from src.analysis.region_analysis import RegionGeoPlotter, AdministrativeRegionAnalysis
warnings.filterwarnings('ignore')

# ---------------------------
# -------- FUNCTIONS --------
# ---------------------------
def create_dataframe_of_regional_values(da: xr.DataArray, region_path: Path) -> pd.DataFrame:
    # extract region information
    admin_level_name = region_path.name.replace('.nc', '')
    region_da, region_lookup, region_group_name = analyzer.load_region_data(
        region_path
    )
    valid_region_ids = [k for k in region_lookup.keys()]

    # create a dictionary of the mean values in each region
    region_names = []
    true_mean_value = []
    datetimes = [pd.to_datetime(t) for t in da.time.values]

    region_data_dict = {}
    region_data_dict['datetime'] = datetimes

    for valid_region_id in valid_region_ids:
        region_vals = da.where(region_da == valid_region_id).mean(
            dim=['lat', 'lon']).values
        region_data_dict[region_lookup[valid_region_id]] = region_vals

    # convert to DataFrame
    return pd.DataFrame(region_data_dict)




def plot_region_time_series(
    region: str,
    all_gdf: gpd.GeoDataFrame,
    ax=None,
    model: List[str] = ['ealstm']
):
    times = all_gdf.loc[(all_gdf.region_name == region) &
                        (all_gdf.model == 'rnn')].datetime
    obs_ts = all_gdf.loc[(all_gdf.region_name == region) & (
        all_gdf.model == 'rnn')].true_mean_value
    rnn_ts = all_gdf.loc[(all_gdf.region_name == region) & (
        all_gdf.model == 'rnn')].predicted_mean_value
    ealstm_ts = all_gdf.loc[(all_gdf.region_name == region) & (
        all_gdf.model == 'ealstm')].predicted_mean_value
    lr_ts = all_gdf.loc[(all_gdf.region_name == region) & (
        all_gdf.model == 'linear_regression')].predicted_mean_value
    ln_ts = all_gdf.loc[(all_gdf.region_name == region) & (
        all_gdf.model == 'linear_network')].predicted_mean_value
    bline_ts = all_gdf.loc[(all_gdf.region_name == region) & (
        all_gdf.model == 'previous_month')].predicted_mean_value

    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = plt.gcf()
    df_dict = {'obs': obs_ts.values}

    if 'lstm' in model:
        df_dict['lstm'] = rnn_ts.values
    if 'ealstm' in model:
        df_dict['ealstm'] = ealstm_ts.values
    if 'lr' in model:
        df_dict['lr'] = lr_ts.values
    if 'ln' in model:
        df_dict['ln'] = ln_ts.values
    if 'baseline' in model:
        df_dict['baseline'] = bline_ts.values

    pd.DataFrame(df_dict, index=times).iloc[1:].plot(ax=ax)

    ax.set_ylim(0, 100)
    ax.set_title(f'{region} Predicted vs. Modelled')

    return fig, ax


def plot_region_seasonality(region, ax=None):
    ts = (
        all_df
        .loc[:, ['datetime', region]
             ].set_index('datetime')
    )

    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = plt.gcf()
    ts.groupby(ts.index.month).mean().plot(ax=ax)
    ax.set_title(f'Seasonal Cycle')
    ax.set_xlabel('Month')
    ax.set_ylabel('Mean NDVI')

    return fig, ax


def plot_region_vs_observed_seasonality(region, model, ax=None):
    ts = (
        all_gdf.loc[
            (all_gdf.model == model) & (all_gdf.region_name == region),
            ['datetime', 'true_mean_value', 'predicted_mean_value']
        ].set_index('datetime')
    ).rename(
        columns={'true_mean_value': 'Observed',
                 'predicted_mean_value': f'Predicted ({model.upper()})'}
    )
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = plt.gcf()

    ts.groupby(ts.index.month).mean().plot(ax=ax)
    ax.set_title(f'Seasonal Cycle for {region} District')
    ax.set_xlabel('Month')
    ax.set_ylabel('Mean VCI')

    return fig, ax


# ---------------------------
# --------- SCRIPTS ---------
# ---------------------------
# initialise the objects
analyzer = AdministrativeRegionAnalysis(data_dir=data_dir)
r = RegionGeoPlotter(data_dir)

# ** create a TRUE dataframe per region **
# region_path = analyzer.region_data_paths[0]
# da = ds.VCI
# all_df = create_dataframe_of_regional_values(da, region_path)
# all_df.head()


# ** create a PREDS/TRUE dataframe per region **
# Calculate the model performances per region
analyzer.analyze()

# calculate GeoDataFrame for spatial plots (chloropleths)
region_plotter = analyzer.create_model_performance_by_region_geodataframe()
region_df = analyzer.df
gdf = region_plotter.gdf

# join into one dataframe with true/predicted values for different models
all_gdf = region_plotter.merge_all_model_performances_gdfs(analyzer.df)


# ** plot time series in particular regions **

# ASAL regions
regions = ['TURKANA', 'MANDERA', 'SAMBURU', 'GARISSA', 'MARSABIT',
           'WAJIR', 'TANA RIVER', 'WEST POKOT', 'ISIOLO', 'KITUI', 'MOYALE']

for region in regions:
    fig, ax = plt.subplots(figsize=(12, 8))
    plot_region_time_series(region=region, ax=ax, model=['ealstm'])
    fig.savefig('')

# Lake Victoria Regions
plot_region_time_series(region='BUSIA')
plot_region_time_series(region='HOMA BAY')
plot_region_time_series(region='SIAYA')
plot_region_time_series(region='MIGORI')

# Rift Valley
plot_region_time_series(region='BARINGO')
plot_region_time_series(region='NAKURU')
plot_region_time_series(region='NAROK')
plot_region_time_series(region='KAJIADO')

# Central Highlands
plot_region_time_series(region='KIRINYAGA')
plot_region_time_series(region='NYERI')
plot_region_time_series(region='MURANGA')
plot_region_time_series(region='KIAMBU')
plot_region_time_series(region='NYANDARUA')
