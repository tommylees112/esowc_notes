from pathlib import Path
import xarray as xr
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

if 'tommylees' in Path('.').absolute().parts:
    data_dir = Path('/Volumes/Lees_Extend/data/ecmwf_sowc/data')
out_dir = data_dir / 'analysis' / 'region_analysis'

chirps = xr.open_dataset(
    data_dir / 'interim' /
    'chirps_preprocessed' / 'data_kenya.nc'
)


from src.analysis.exploration import (
    calculate_seasonal_anomalies, create_anomaly_df,
    plot_bar_anomalies
)

# ---------------------------
#
# ---------------------------

# Plot the indices over same time series
from sklearn.preprocessing import scale

indices_df = pd.read_csv('data/flow_and_indices.csv').drop(columns=['flow', 'flow_std'])
indices_df = indices_df.astype({'date': 'datetime64[ns]'}).set_index('date')

# Resample to SEASONAL timesteps
seasonal_metrics = indices_df[['NINO34', 'AMO', 'PDO']].resample('Q-DEC').mean()

# standardize (x - mean / std)
seasonal_metrics['NINO34'] = scale(seasonal_metrics['NINO34'].values)
seasonal_metrics['AMO'] = scale(seasonal_metrics['AMO'].values)
seasonal_metrics['PDO'] = scale(seasonal_metrics['PDO'].values)

# select same time slice
seasonal_metrics_df = seasonal_metrics.loc['1995': '2017']
seasonal_metrics_df = seasonal_metrics_df.reset_index().rename(columns={'date': 'time'})


def plot_index(df: pd.DataFrame, index_name: str, title: str) -> None:
    fig, ax = plot_bar_anomalies(
        df, variable=index_name
    )
    ax.set_xlabel('Time')
    ax.set_ylabel(f'{title} Index')
    ax.set_title(title)
    fig.savefig(f'/Users/tommylees/Downloads/{index_name}_seasonal_anomaly.png')


plot_index(seasonal_metrics_df, index_name='NINO34', title='El Nino Index (NINO34)')
plot_index(seasonal_metrics_df, index_name='AMO', title='Atlantic Multi-Decadal Oscillation Index')
plot_index(seasonal_metrics_df, index_name='PDO', title='Pacific Decadal Oscillation')
