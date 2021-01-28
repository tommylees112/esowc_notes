from pathlib import Path
import xarray as xr
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

if "tommylees" in Path(".").absolute().parts:
    data_dir = Path("/Volumes/Lees_Extend/data/ecmwf_sowc/data")
out_dir = data_dir / "analysis" / "region_analysis"


vci = xr.open_dataset(data_dir / "interim" / "VCI_preprocessed" / "data_kenya.nc")

from src.analysis.exploration import (
    calculate_seasonal_anomalies,
    create_anomaly_df,
    plot_bar_anomalies,
    calculate_seasonal_anomalies_spatial,
)


# ------------------------
# timeseries plotting
# ------------------------

vci_anom_ts = calculate_seasonal_anomalies(vci, variable="VCI")
vci_anom_df = create_anomaly_df(vci_anom_ts, mintime="1995", maxtime="2017-09")
fig, ax = plot_bar_anomalies(vci_anom_df)
ax.set_title("VCI Anomalies for Kenya")
ax.set_ylabel("VCI Anomaly")
fig.savefig("/Users/tommylees/Downloads/vci_seasonal_anomalies_ts.png")

# ------------------------
# spatial plotting
# ------------------------
vci_anom = calculate_seasonal_anomalies_spatial(vci, variable="VCI")


def plot_time_anomaly(vci_anom: xr.DataArray, time_str: str):
    fig, ax = plt.subplots()
    vci_anom.sel(time=time_str).plot(cmap="RdBu", ax=ax, vmin=-65, vmax=65)
    ax.set_title(f"VCI Anomaly {time_str}")
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.set_xticklabels("")
    ax.set_yticklabels("")
    ax.set_xticks([])
    ax.set_yticks([])
    fig.savefig(f"/Users/tommylees/Downloads/vci_anomaly_{time_str}.png")


plot_time_anomaly(vci_anom, "2017-06")
plot_time_anomaly(vci_anom, "2017-03")
plot_time_anomaly(vci_anom, "2000-12")
plot_time_anomaly(vci_anom, "2017-03")
plot_time_anomaly(vci_anom, "2001-03")
plot_time_anomaly(vci_anom, "2006-09")
