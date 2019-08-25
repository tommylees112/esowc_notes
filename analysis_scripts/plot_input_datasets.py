from pathlib import Path
import calendar

import xarray as xr
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from typing import Optional, Tuple, List, Union


def plot_input_data(da: xr.DataArray, dataset: str):
    fig, ax = plt.subplots(figsize=(12, 8))
    da.plot(cmap='gist_earth', ax=ax)
    ax.set_title(f'{dataset}')
    ax.set_xlabel('')
    ax.set_ylabel('')
    ax.set_xticklabels('')
    ax.set_yticklabels('')
    ax.set_xticks([])
    ax.set_yticks([])
    fig.savefig(f'/Users/tommylees/Downloads/raw_input_data_{dataset}.png')


srtm = xr.open_dataset(data_dir / 'interim/static/srtm_preprocessed/kenya.nc')
srtm.topography.attrs['long_name'] = 'Height above sea level [m]'
plot_input_data(da=srtm.topography, dataset='topography')
