from pathlib import Path
import calendar

import xarray as xr
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from typing import Optional, Tuple, List, Union

if 'tommylees' in Path('.').absolute().parts:
    data_dir = Path('/Volumes/Lees_Extend/data/ecmwf_sowc/data')
out_dir = data_dir / 'analysis' / 'region_analysis'

# -----------------------
# read in data
# -----------------------

chirps = xr.open_dataset(
    data_dir / 'interim' /
    'chirps_preprocessed' / 'data_kenya.nc'
)
vci = xr.open_dataset(
    data_dir / 'interim' /
    'VCI_preprocessed' / 'data_kenya.nc'
)



from src.analysis.region_analysis.groupby_region import KenyaGroupbyRegion


# -----------------------
#
# -----------------------


# -----------------------
#
# -----------------------


# -----------------------
#
# -----------------------


# -----------------------
#
# -----------------------
