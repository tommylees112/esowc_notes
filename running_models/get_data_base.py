from pathlib import Path
import numpy as np
import pandas as pd
import xarray as xr

data_dir = Path("/data/ml_drought/data")
models_dir = data_dir / "models" / self.experiment
dict(
    experiment="one_month_forecast",
    pred_months=None,
    include_pred_month=True,
    include_latlons=False,
    include_monthly_aggs=True,
    include_yearly_aggs=True,
    surrounding_pixels=None,
    ignore_vars=None,
    static="embedding",
    predict_delta=False,
)
