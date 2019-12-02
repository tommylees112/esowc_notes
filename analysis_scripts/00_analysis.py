import xarray as xr
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pickle
import seaborn as sns

%load_ext autoreload
%autoreload 2
%matplotlib

data_dir = Path('/Volumes/Lees_Extend/data/ecmwf_sowc/data/')

# [f.name for f in (data_dir / 'features/one_month_forecast/test').iterdir()]
# [f.name for f in (data_path / 'features' / 'one_month_forecast' / 'train' / '2017_03').iterdir()]

# --------------------------------
# READ in dataArrays
# --------------------------------
from src.analysis.evaluation import annual_scores
from src.analysis.evaluation import read_pred_data, read_true_data

ealstm_pred_ds, ealstm_pred_da = read_pred_data('ealstm', data_dir=data_dir)
persistence_pred_ds, persistence_pred_da = read_pred_data('previous_month', data_dir=data_dir)

true_da = read_true_data(data_dir=data_dir)

assert (persistence_pred_da.time == true_da.time).all()
assert (ealstm_pred_da.time == true_da.time).all()

# --------------------------------
# read in models
# --------------------------------
# READ in model (maybe want to do more predictions on historical data)
from src.models import load_model, Persistence

ealstm_path = data_dir / 'models/one_month_forecast/ealstm/model.pt'
assert ealstm_path.exists(), \
    'Expected the unzipped file to have the model.pt file saved'

persistence = Persistence(data_folder=data_dir)
ealstm = load_model(model_path=ealstm_path)

# --------------------------------
# Create comparison over time barchart
# --------------------------------

scores = annual_scores(
    data_path=data_dir,
    models=['ealstm', 'previous_month'],
    metrics=['rmse', 'r2'],
    verbose=False,
    to_dataframe=True
)

# create long format dataframe
scores_long = pd.melt(
    scores, id_vars=['month', 'metric'],
    value_vars=['ealstm', 'previous_month']
)

# get the separate metrics for plotting
rmse = scores_long.loc[scores_long.metric=='rmse']
r2 = scores_long.loc[scores_long.metric=='r2']

scores_long.head()

g = sns.catplot(x="month", y="value", hue="variable", data=rmse,
                height=6, kind="bar", palette="muted")
g.despine(left=True)
ax = plt.gca()
ax.set_title('RMSE Comparison for EALSTM vs. Baseline');

# TODO: we should include the variability of these estimates too!

# --------------------------------
# Region Analysis
# --------------------------------
from src.analysis import MovingAverage
from src.analysis.region_analysis import KenyaGroupbyRegion

grouper = KenyaGroupbyRegion(data_dir)



# --------------------------------
# Landcover Analysis
# --------------------------------


# --------------------------------
# Make new predictions on other timesteps
# --------------------------------
"""
ealstm = load_model(model_path=ealstm_path)
ealstm.evaluate(year=np.arange(1990, 2010), month=3)

[f.name for f in (data_path / 'features' / 'one_month_forecast' / 'test' / 'hello').iterdir()]
"""
ealstm.evaluate_train_timesteps(years=[1991, 1992], months=[3], save_preds=True)


# test_arrays_dict, preds_dict = ealstm.predict()
