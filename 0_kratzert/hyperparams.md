camels_attributes:
- num_reservoir
- reservoir_cap
- sand_perc
- silt_perc
- clay_perc
- organic_perc
- bulkdens
- bulkdens_5
- bulkdens_50
- bulkdens_95
- tawc
- tawc_5
- tawc_50
- tawc_95
- porosity_cosby
- porosity_cosby_5
- porosity_cosby_50
- porosity_cosby_95
- porosity_hypres
- porosity_hypres_5
- porosity_hypres_50
- porosity_hypres_95
- conductivity_cosby
- conductivity_cosby_5
- conductivity_cosby_50
- conductivity_cosby_95
- conductivity_hypres
- conductivity_hypres_5
- conductivity_hypres_50
- conductivity_hypres_95
- root_depth
- root_depth_5
- root_depth_50
- root_depth_95
- soil_depth_pelletier
- soil_depth_pelletier_5
- soil_depth_pelletier_50
- soil_depth_pelletier_95
- inter_high_perc
- inter_mod_perc
- inter_low_perc
- frac_high_perc
- frac_mod_perc
- frac_low_perc
- no_gw_perc
- low_nsig_perc
- nsig_low_perc
- gauge_elev
- area
- elev_min
- elev_10
- elev_50
- elev_90
- elev_max
- dwood_perc
- ewood_perc
- grass_perc
- shrub_perc
- crop_perc
- urban_perc
- inwater_perc
- bares_perc
- p_mean
- pet_mean
- aridity
- p_seasonality
- frac_snow
- high_prec_freq
- high_prec_dur
- low_prec_freq
- low_prec_dur


dynamic_inputs:
- precipitation
- peti
- temperature

seq_length: 365

target_variable:
- discharge_spec
