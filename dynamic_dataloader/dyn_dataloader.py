%load_ext autoreload
%autoreload 2
from pathlib import Path
import xarray as xr
import numpy as np
from collections import defaultdict
import pickle
import pandas as pd
from pandas.tseries.offsets import Day

from typing import DefaultDict, Dict, Tuple, Optional, Union, List, Any
from src.utils import minus_timesteps

# -----------------
# ASSUME INTERIM CREATED
# -----------------
# -----------------
# Process:
# 0. engineer = load data from interim/<DATA>_preprocessed
# 1. engineer the static features -> one hot encoded etc.
# 1. engineer = calculate normalisation dict from training data
# 1. engineer = ignore vars
# -----------------

# ---------------------------------------------------------------------------
# Dynamic Engineer
# ---------------------------------------------------------------------------
# DONE

# ---------------------------------------------------------------------------
# Dynamic Dataloading
# ---------------------------------------------------------------------------

# -----------------
# Process:
# 1. Iterator = iterate loading of samples dynamically
# 1. dataloader = load only sample of training data
# 1. dataloader = convert sample to ModelArrays
# 1. dataloader =
# -----------------

# dynamic data
# get samples from the data


# -------------
# engineering
# -------------
# 1. LOAD PROCESSED DATA in
from src.engineer import DynamicEngineer
from src.engineer.dynamic_engineer import DynamicEngineer

# data_dir = Path('/Volumes/Lees_Extend/data/ecmwf_sowc/data')
data_dir = Path('/lustre/soge1/projects/crop_yield/ml_drought/data')
de = DynamicEngineer(data_dir, process_static=True)

de.engineer(
    augment_static=False,
    static_ignore_vars=static_ignore_vars,
    dynamic_ignore_vars=dynamic_ignore_vars,
    logy=True
)

# load in the raw data (not-engineered)
# dynamic_ds = de._make_dataset(static=False, latlon=False)
# static_ds = de._make_dataset(static=True, latlon=False)
# static_ds_base = static_ds_master = static_ds.copy()


# pseudo tests!
assert de.output_folder.exists()
assert de.static_output_folder.exists()
assert all(np.isin(['data.nc', 'normalizing_dict.pkl'], [d.name for d in de.output_folder.iterdir()]))
assert all(np.isin(['data.nc', 'normalizing_dict.pkl'], [d.name for d in de.static_output_folder.iterdir()]))
test_dynamic = xr.open_dataset([d for d in de.output_folder.glob('*.nc')][0])
test_static = xr.open_dataset([d for d in de.static_output_folder.glob('*.nc')][0])

assert all(
    np.isin(
        ["peti", "precipitation", "discharge_spec", "target_var_original"],
        list(test_dynamic.data_vars))
)

assert all(
    np.isin(
        ["dpsbar", "aridity", "frac_snow", 'crop_perc'],
        list(test_static.data_vars)
    )
)

# -------------
# dataloading
# -------------
from src.models.data import DynamicDataLoader


# data_times = [pd.to_datetime(t) for t in test_dynamic.time.values]
target_var = 'discharge_spec'
seq_length = 365
data_dir = Path('/Volumes/Lees_Extend/data/ecmwf_sowc/data')

dl = DynamicDataLoader(
    target_var=target_var,
    test_years=np.arange(2011, 2016),
    data_path=data_dir,
    seq_length=seq_length,
    static_ignore_vars=static_ignore_vars,
    dynamic_ignore_vars=dynamic_ignore_vars,
)
X, y = dl.__iter__().__next__()

assert isinstance(X, tuple)
assert isinstance(X[0], np.ndarray)
assert X[0].shape[1] == seq_length, "Dynamic data: Should be (#non-nan stations, seq_length, n_predictors)"
assert X[0].shape[-1] == 2, "Dynamic data: Should be (#non-nan stations, seq_length, n_predictors)"

valid_static_vars = ['aridity',
                     'frac_snow',
                     'surfacewater_abs',
                     'groundwater_abs',
                     'reservoir_cap',
                     'dwood_perc',
                     'ewood_perc',
                     'crop_perc',
                     'urban_perc',
                     'porosity_hypres',
                     'conductivity_hypres',
                     'dpsbar']
assert X[5].shape[-1] == len(valid_static_vars), "Static Data Should be (#non-nan stations, n_predictors)"
assert X[0].shape[0] == y.shape[0], "Expect the same number of instances in X, y"
assert y.shape[1] == 1, "Expect only one feature in the target data (y)"

assert isinstance(dl.static_ds, xr.Dataset)
assert isinstance(dl.dynamic_ds, xr.Dataset)
assert len(dl) == 16070

# TODO: check that correctly shuffle the loaded data by target_timestep (which sample pulled)
# TODO: check the ModelArrays created correctly
dl.__iter__().__next__()

# ------------------------------------------------------------------------------------------
# MODELS
# ------------------------------------------------------------------------------------------
# TODO: check how to get the models to work!!
# TODO: update `evaluate` / `predict` / `get_dataloader` / `train`
# TODO: do for EALSTM first and get some results asap rocky
data_dir = Path('/Volumes/Lees_Extend/data/ecmwf_sowc/data')
dynamic_ignore_vars = ['temperature', 'discharge_vol', 'discharge_spec',
                       'pet', 'humidity', 'shortwave_rad', 'longwave_rad', 'windspeed']

# import cProfile
# import profile

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
# test the training functionality
ealstm.train()

# test the prediction functionality
ealstm.predict()

#
captured = capsys.readouterr()
expected_stdout = "`include_yearly_aggs` does not yet work for dynamic dataloder. Setting to False"
assert (
    captured.out == expected_stdout
), f"Expected stdout to be {expected_stdout}, got {captured.out}"

# test getting the dataloader
dl = ealstm.get_dataloader(mode='train')
X, y = dl.__iter__().__next__()

# the dataloader loaded is the dynamic ?
test_years = np.arange(2011, 2017)
assert isinstance(dl, DynamicDataLoader)
assert all([pd.to_datetime(t).year in [y for y in test_years] for t in dl.valid_test_times]), "Test times are validly chosen"
assert all([pd.to_datetime(t).year not in [y for y in test_years]
            for t in dl.valid_train_times]), "Train times are validly chosen"

# the dataloder data is legit?
assert isinstance(X, tuple)
assert isinstance(X[0], np.ndarray)
assert isinstance(y, np.ndarray)
assert y.shape[-1] == 1




# ------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------

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

# ------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------

