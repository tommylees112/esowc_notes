# ssh vertigo
# tmux attach -t 0
# source ~/.bashrc_; conda activate crp
# ipython
# !cd /soge-home/projects/crop_yield/ml_drought/
from src.models import EARecurrentNetwork
%load_ext autoreload
%autoreload 2
from pathlib import Path
import xarray as xr
import numpy as np
from collections import defaultdict
import pickle
import pandas as pd
from pandas.tseries.offsets import Day
import json
from typing import DefaultDict, Dict, Tuple, Optional, Union, List, Any
from src.utils import minus_timesteps


from pathlib import Path
from src.engineer.dynamic_engineer import DynamicEngineer

print("** Loaded in all Libraries! **")

# variables to ignore
static_ignore_vars = [
    # hydrometry_attributes
    "station_type",
    "flow_period_start",
    "flow_period_end",
    "flow_perc_complete",
    "bankfull_flow",
    "structurefull_flow",
    "q5_uncert_upper",
    "q5_uncert_lower",
    "q25_uncert_upper",
    "q25_uncert_lower",
    "q50_uncert_upper",
    "q50_uncert_lower",
    "q75_uncert_upper",
    "q75_uncert_lower",
    "q95_uncert_upper",
    "q95_uncert_lower",
    "q99_uncert_upper",
    "q99_uncert_lower",
    "quncert_meta",
    # soil_attributes
    "sand_perc",
    "sand_perc_missing",
    "silt_perc",
    "silt_perc_missing",
    "clay_perc",
    "clay_perc_missing",
    "organic_perc",
    "organic_perc_missing",
    "bulkdens",
    "bulkdens_missing",
    "bulkdens_5",
    "bulkdens_50",
    "bulkdens_95",
    "tawc",
    "tawc_missing",
    "tawc_5",
    "tawc_50",
    "tawc_95",
    "porosity_cosby",
    "porosity_cosby_missing",
    "porosity_cosby_5",
    "porosity_cosby_50",
    "porosity_cosby_95",
    "porosity_hypres_missing",
    "porosity_hypres_5",
    "porosity_hypres_50",
    "porosity_hypres_95",
    "conductivity_cosby",
    "conductivity_cosby_missing",
    "conductivity_cosby_5",
    "conductivity_cosby_50",
    "conductivity_cosby_95",
    "conductivity_hypres_missing",
    "conductivity_hypres_5",
    "conductivity_hypres_50",
    "conductivity_hypres_95",
    "root_depth",
    "root_depth_missing",
    "root_depth_5",
    "root_depth_50",
    "root_depth_95",
    "soil_depth_pelletier",
    "soil_depth_pelletier_missing",
    "soil_depth_pelletier_5",
    "soil_depth_pelletier_50",
    "soil_depth_pelletier_95",
    # landcover_attributes
    "grass_perc",
    "shrub_perc",
    "inwater_perc",
    "bares_perc",
    "dom_land_cover",
    # topographic_attributes
    "gauge_name",
    "gauge_lat",
    "gauge_lon",
    "gauge_easting",
    "gauge_northing",
    "gauge_elev",
    "area",
    "elev_mean",
    "elev_min",
    "elev_10",
    "elev_50",
    "elev_90",
    "elev_max",
    # hydrologic_attributes (?? I like these ??)
    "q_mean",
    "runoff_ratio",
    "stream_elas",
    "slope_fdc",
    "baseflow_index",
    "baseflow_index_ceh",
    "hfd_mean",
    "Q5",
    "Q95",
    "high_q_freq",
    "high_q_dur",
    "low_q_freq",
    "low_q_dur",
    "zero_q_freq",
    # hydrogeology_attributes
    "inter_high_perc",
    "inter_mod_perc",
    "inter_low_perc",
    "frac_high_perc",
    "frac_mod_perc",
    "frac_low_perc",
    "no_gw_perc",
    "low_nsig_perc",
    "nsig_low_perc",
    # humaninfluence_attributes
    "benchmark_catch",
    "discharges",
    "abs_agriculture_perc",
    "abs_amenities_perc",
    "abs_energy_perc",
    "abs_environmental_perc",
    "abs_industry_perc",
    "abs_watersupply_perc",
    "num_reservoir",
    "reservoir_he",
    "reservoir_nav",
    "reservoir_drain",
    "reservoir_wr",
    "reservoir_fs",
    "reservoir_env",
    "reservoir_nousedata",
    "reservoir_year_first",
    "reservoir_year_last",
    # climatic_attributes
    "p_mean",
    "pet_mean",
    "p_seasonality",
    "high_prec_freq",
    "high_prec_dur",
    "high_prec_timing",
    "low_prec_freq",
    "low_prec_dur",
    "low_prec_timing",
]

# data_dir = Path('/Volumes/Lees_Extend/data/ecmwf_sowc/data')
data_dir = Path('/lustre/soge1/projects/crop_yield/ml_drought/data')


dynamic_ignore_vars = ['temperature', 'discharge_vol', 'discharge_spec',
                       'pet', 'humidity', 'shortwave_rad', 'longwave_rad', 'windspeed']
target_var = "discharge_spec"
test_years = [2011, 2012, 2013, 2014, 2015]
seq_length = 365


# ENGINEERS
# de = DynamicEngineer(data_dir, process_static=True)
# print("** Initialised Engineer! **")

# de.engineer(
#     augment_static=False,
#     static_ignore_vars=static_ignore_vars,
#     dynamic_ignore_vars=dynamic_ignore_vars,
#     logy=True,
#     test_years=test_years,
#     target_variable=target_var,
# )
# print("** Run the Engineer! **")

# MODELS
from src.models import EARecurrentNetwork

ealstm = EARecurrentNetwork(
    data_folder=data_dir,
    batch_size=1000,
    hidden_size=128,
    experiment='one_timestep_forecast',
    dynamic=True,
    seq_length=365,
    dynamic_ignore_vars=dynamic_ignore_vars,
    static_ignore_vars=static_ignore_vars,
    target_var='discharge_spec',
    test_years=np.arange(2011, 2017),
)
print("** Initialised Models! **")

# test the training functionality
ealstm.train(
    num_epochs=1,  # 100
    # early_stopping=10
)

# test the prediction functionality
# test_arrays_dict, preds_dict = ealstm.predict()
ealstm.evaluate(
    spatial_unit_name='station_id',
    save_preds=True
)
results_dict = json.load(open('data/models/one_timestep_forecast/ealstm/results.json', 'rb'))
print("Overall RMSE: ", results_dict['total'])

# 1 epoch = 1.04 / 2.81
# 100 epochs = 0.72 / 2.04

# save the model
ealstm.save_model()

# load the model
from src.models import load_model
ealstm2 = load_model(Path('data/models/one_timestep_forecast/ealstm/model.pt'))

# ------------------------------------------------------------------------
## ANALYSIS
# ------------------------------------------------------------------------
import matplotlib.pyplot as plt

# checking the performance of the models
EXPERIMENT = 'one_timestep_forecast'
from src.analysis import read_pred_data
from src.analysis.evaluation import join_true_pred_da

# making predictions
ealstm_pred = read_pred_data('ealstm', data_dir, experiment=EXPERIMENT)
ealstm_pred['station_id'] = ealstm_pred['station_id'].astype(int)

## NOTE: un-log transform (np.exp) the data
# ealstm_pred['preds'] = (np.exp(ealstm_pred['preds'])) - 0.001
# ealstm_pred['preds'] = np.exp(ealstm_pred['preds'] - 0.001)
## NOTE: un-normalize the data
# norm_dict = pickle.load(open(Path('data/features/one_timestep_forecast/normalizing_dict.pkl'), 'rb'))
# p = ((ealstm_pred['preds'] * norm_dict['discharge_spec']['std']) + norm_dict['discharge_spec']['mean'])

# read in the true data
ds = xr.open_dataset(Path(f'data/features/{EXPERIMENT}/data.nc'))
ds['station_id'] = ds['station_id'].astype(int)

# get the observed y_test
times = ealstm_pred.time.values
station_ids = ealstm_pred.station_id.values

# 'target_var_original'
y_test = ds['discharge_spec'].sel(station_id=station_ids).sel(time=times)
y_test = ds['target_var_original'].sel(station_id=station_ids).sel(time=times)

# join the true and the pred data into one pd.DataFrame
true_da = y_test
# pred_da = ealstm_pred['preds']
pred_da = np.exp(ealstm_pred['preds']) - 0.001

df = (
    join_true_pred_da(
        true_da, pred_da
    ).to_dataframe()
    .reset_index()
    .set_index('time')
)

# run performance metrics
from src.analysis.evaluation import (r2_score, rmse, spatial_rmse, spatial_r2, spatial_nse)
from src.analysis.evaluation import temporal_rmse, temporal_r2, temporal_nse

# calculate performance for each station (collapse time)
rmse_da = spatial_rmse(y_test, ealstm_pred.preds)
r2_da = spatial_r2(y_test, ealstm_pred.preds)
nse_da = spatial_nse(y_test, ealstm_pred.preds)

# calculate performance for each station (collapse space)
rmse_time = temporal_rmse(y_test, ealstm_pred.preds)
r2_time = temporal_r2(y_test, ealstm_pred.preds)
nse_time = temporal_nse(y_test, ealstm_pred.preds)

print(f"Mean Station RMSE: {rmse_da.mean().values:.2f}")
print(f"Mean Station NSE: {nse_da.mean().values:.2f}")
print(f"Mean Station R2: {r2_da.mean().values:.2f}")

print(f"\n\nMean Time RMSE: {rmse_time.mean().values:.2f}")
print(f"Mean Time NSE: {nse_time.mean().values:.2f}")
print(f"Mean Time R2: {r2_time.mean().values:.2f}")

# crooks and martinez stations
catchment_ids = ["12002", "15006", "27009", "27034", "27041", "39001",
                 "39081", "43021", "47001", "54001", "54057", "71001", "84013", ]
catchment_ids = [int(c_id) for c_id in catchment_ids]
catchment_names = ["Dee@Park", "Tay@Ballathie", "Ouse@Skelton", "Ure@Kilgram", "Derwent@Buttercrambe", "Thames@Kingston",
                   "Ock@Abingdon", "Avon@Knapp", "Tamar@Gunnislake", "Severn@Bewdley", "Severn@Haw", "Ribble@Samlesbury", "Clyde@Daldowie"]
station_map = dict(zip(catchment_ids, catchment_names))

valid_catchment_ids = [c for (ix, c) in enumerate(catchment_ids) if c in ealstm_pred.station_id.values]
valid_station_name = np.array(catchment_names)[[ix for (ix, c) in enumerate(catchment_ids) if c in ealstm_pred.station_id.values]]
for ix, (station_id, station_name) in enumerate(zip(valid_catchment_ids, valid_station_name)):
    print(f"{station_name} ID: {station_id}")
    print(f"\tRMSE: {rmse_da.sel(station_id=station_id).values:.2f}")
    print(f"\tNSE: {nse_da.sel(station_id=station_id).values:.2f}")
    print(f"\tR2: {r2_da.sel(station_id=station_id).values:.2f}")
    print("\n")

#
# rmse and r2 df
metrics_df = rmse_da.to_dataframe().drop(columns='time').rename(columns={"preds": "rmse"}).join(
    r2_da.to_dataframe().drop(columns='time').rename(columns={"preds": "r2"})
)
metrics_df = metrics_df.join(
    nse_da.to_dataframe().rename(columns={"preds": "nse"})
)

metrics_df = metrics_df.reset_index()

# TEMPORAL rmse and r2 df
metrics_time = rmse_time.to_dataframe().rename(columns={"discharge_vol": "rmse"}).join(
    r2_time.to_dataframe().rename(columns={"discharge_vol": "r2"})
)
metrics_time = metrics_time.join(
    nse_time.to_dataframe().rename(columns={"discharge_vol": "nse"})
)

metrics_time = metrics_time.reset_index()
metrics_time['time'] = [pd.to_datetime(t) for t in metrics_time.time]
metrics_time.head()

# iterate over crooks and martinez stations
for ix, (station_id, station_name) in enumerate(zip(catchment_ids, catchment_names)):
    d = df.query(f"station_id == '{station_id}'").drop(columns='station_id')
    if len(d) > 0:
        break

