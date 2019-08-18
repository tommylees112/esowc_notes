from pathlib import Path
import xarray as xr
%load_ext autoreload
%autoreload 2

from src.preprocess import ERA5LandPreprocessor

data_dir = Path('/Volumes/Lees_Extend/data/ecmwf_sowc/data')

e = ERA5LandPreprocessor(data_dir)

# get filepaths
e.get_filepaths()
