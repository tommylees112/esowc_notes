import pandas as pd
import numpy as np
import torch

from pathlib import Path
import seaborn as sns
import matplotlib.pyplot as plt
import os
import re
import xarray as xr
import pickle

main_dir = Path("/Volumes/Lees_Extend/data/ecmwf_sowc")

dynamic = xr.open_dataset(main_dir / "features/one_timestep_forecast/data.nc")
static = xr.open_dataset(main_dir / "features/static/data.nc")
