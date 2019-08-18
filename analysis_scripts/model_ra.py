from pathlib import Path
from mpl_toolkits.axes_grid1 import make_axes_locatable
from collections import namedtuple

from src.analysis import (
    AdministrativeRegionAnalysis
)
from src.analysis.region_analysis import GroupbyRegion, KenyaGroupbyRegion

if 'tommylees' in Path('.').absolute().parts:
    data_dir = Path('/Volumes/Lees_Extend/data/ecmwf_sowc/data')
out_dir = data_dir / 'analysis' / 'region_analysis'

admin_analyzer = AdministrativeRegionAnalysis(data_dir)
admin_analyzer.analyze()

# ------------------------
# extract the data
# ------------------------
if not (
    out_dir / 'regional_error_metrics_one_month_forecast_admin.csv'
).exists:
    model_perf_df = admin_analyzer.regional_mean_metrics
else:
    model_perf_df = pd.read_csv(
        out_dir / 'regional_error_metrics_one_month_forecast_admin.csv'
    )

l2_perf = model_perf_df.loc[model_perf_df['admin_level_name'] == 'district_l2_kenya']
l2_perf = l2_perf.dropna(subset=['rmse', 'mae', 'r2'])

# ------------------------
# join geopandas shapes
# ------------------------
da = xr.open_dataset(data_dir / 'interim/chirps_preprocessed/chirps_kenya.nc')['precip']

if not (out_dir / 'reference_l2_admin_gdf.csv').exists():
    d = KenyaGroupbyRegion(data_dir)
    d.analyze(
        da=da, selection='level_2', mean=True, save_data_fname=None
    )
    l2_gdf = d.gdf
    l2_gdf = l2_gdf[
        l2_gdf.datetime == l2_gdf.datetime.unique()[0]
    ].drop(columns=['datetime', 'mean_value'])
    l2_gdf.to_csv(out_dir / 'reference_l2_admin_gdf.csv')
else:
    l2_gdf = gpd.read_file(out_dir / 'reference_l2_admin_gdf.csv')
    # pd.read_csv(out_dir / 'vci3m_district_l2.csv')

d = KenyaGroupbyRegion(data_dir)

l2_perf_gdf = d.join_dataframe_geodataframe(
    df=l2_perf, gdf=l2_gdf,
    gdf_colname='DISTNAME', df_colname='region_name'
).drop(columns='Unnamed: 0')

# ------------------------
# plot maps
# ------------------------

PlotMetric = namedtuple('PlotMetric', ['metric', 'cmap', 'vmin', 'vmax'])
rmse = PlotMetric(
    metric='rmse',
    cmap='viridis',
    vmin=None,
    vmax=10,
)
mae = PlotMetric(
    metric='mae',
    cmap='plasma',
    vmin=None,
    vmax=10,
)
r2 = PlotMetric(
    metric='r2',
    cmap='inferno_r',
    vmin=0,
    vmax=1.0,
)

# plot all one plot
fig, axs = plt.subplots(1, 3, figsize=(24, 6))
for i, metric in enumerate([rmse, mae, r2]):
    ax = axs[i]
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.1)
    l2_perf_gdf.plot(
        metric.metric, ax=ax, legend=True,
        cmap=metric.cmap, vmin=metric.vmin,
        vmax=metric.vmax, cax=cax
    )
    ax.set_title(f'{metric.metric.upper()}')

# plot individually
metric = r2

fig, ax = plt.subplots()
divider = make_axes_locatable(ax)
cax = divider.append_axes("right", size="5%", pad=0.1)
l2_perf_gdf.plot(
    metric.metric, ax=ax, legend=True,
    cmap=metric.cmap, cax=cax,
    **dict(vmin=metric.vmin, vmax=metric.vmax)
)
ax.set_title(f'{metric.metric.upper()}')

print(f'* Plotted {metric.metric} *')


# TEST
from src.analysis.region_analysis import RegionGeoPlotter

plotter = RegionGeoPlotter(data_dir)
plotter.plot_regional_error_metric(l2_perf_gdf, 'rmse')
