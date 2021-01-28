from pathlib import Path

import xarray as xr
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from typing import Optional, Tuple, List, Union

if "tommylees" in Path(".").absolute().parts:
    data_dir = Path("/Volumes/Lees_Extend/data/ecmwf_sowc/data")
out_dir = data_dir / "analysis" / "region_analysis"


# -----------------------
# Calculate the 3Month VCI in PREDICTED / TRUE data
# -----------------------
from src.analysis.region_analysis import GroupbyRegion, KenyaGroupbyRegion
from src.analysis import VegetationDeficitIndex

# predicted data
# pred_ds = xr.open_mfdataset((data_dir / 'models' / 'one_month_forecast' / 'previous_month' / '*.nc').as_posix())


def get_datetimes_from_files(files: List[Path]) -> List:
    datetimes = []
    for path in files:
        year = path.name.replace(".nc", "").split("_")[-2]
        month = path.name.replace(".nc", "").split("_")[-1]
        day = calendar.monthrange(int(year), int(month))[-1]
        dt = pd.to_datetime(f"{year}-{month}-{day}")
        datetimes.append(dt)
    return datetimes


def open_pred_data(model: str, experiment: str = "one_month_forecast"):
    import calendar

    files = [
        f for f in (data_dir / "models" / "one_month_forecast" / "ealstm").glob("*.nc")
    ]
    files.sort(key=lambda path: int(path.name.split("_")[-1][:-3]))
    times = get_datetimes_from_files(files)

    pred_ds = xr.merge(
        [
            xr.open_dataset(f).assign_coords(time=times[i]).expand_dims("time")
            for i, f in enumerate(files)
        ]
    )

    return pred_ds


model = "ealstm"
pred_ds = open_pred_data(model)
pred_ds = pred_ds.sortby("time")
pred_ds.to_netcdf(out_dir / f"{model}_prediction_VHI.nc")
pred_da = pred_ds.preds

# fit the index (necessary? Only for the VCI3M value)
index = VegetationDeficitIndex(
    out_dir / f"{model}_prediction_VHI.nc", resample_str=None
)
index.fit("preds")
pred_VCI3M_da = index.index.preds3_moving_average
pred_VDI_da = index.index.VCI3M_index

# true data
true_paths = [
    f for f in (data_dir / "features" / "one_month_forecast" / "test").glob("*/y.nc")
]
true_ds = xr.open_mfdataset(true_paths).sortby("time").compute()
true_ds.to_netcdf(out_dir / "true_VCI_data.nc")
true_da = true_ds.VCI

# fit the index (necessary? Only for the VCI3M value)
index = VegetationDeficitIndex(out_dir / "true_VCI_data.nc", resample_str=None)
index.fit("VHI")
try:
    true_VCI3M_da = index.index.VCI3_moving_average
except AttributeError:
    true_VCI3M_da = index.index.VHI3_moving_average
true_VDI_da = index.index.VCI3M_index

#

# -----------------------
# groupby region
# -----------------------
# preds
grouper = KenyaGroupbyRegion(data_dir)
grouper.analyze(da=pred_VCI3M_da, mean=True, selection="level_2")
pred_gdf = grouper.gdf.rename(columns={"mean_value": "pred_value"}).drop(
    columns="DISTNAME"
)

# true
grouper = KenyaGroupbyRegion(data_dir)
grouper.analyze(da=true_VCI3M_da, mean=True, selection="level_2")
true_gdf = grouper.gdf.rename(columns={"mean_value": "true_value"}).drop(
    columns="DISTNAME"
)

# join the values from true / pred WHERE datetime-region_names match
gdf = (
    pd.merge(pred_gdf, true_gdf, on=["datetime", "region_name"], how="inner")
    .drop(columns="geometry_y")
    .rename(columns={"geometry_x": "geometry"})
    .astype({"true_value": "float", "true_value": "float"})
)

# -----------------------
# calculate true/pred VDI
# -----------------------


def VDI(df: pd.DataFrame, values_column: str, new_column: str = "VDI") -> pd.DataFrame:
    """ pandas implementation of the VDI """
    bins = [0.0, 10.0, 20.0, 35.0, 50.0]
    df[new_column] = np.digitize(df[values_column], bins)
    return df


gdf = VDI(gdf, values_column="pred_value", new_column="pred_VDI")
gdf = VDI(gdf, values_column="true_value", new_column="true_VDI")


# # (do the same for the mean in each county)
# if np.isin(['pred_VDI', 'true_VDI'], gdf.columns).all():
#     mean_gdf = gdf.drop(columns=['pred_VDI', 'true_VDI'])
# else:

# -----------------------
# calculate performance
# -----------------------
# confusion matrix
from sklearn.metrics import confusion_matrix
from sklearn.metrics import roc_curve
from sklearn.metrics import classification_report

"""
# precision
Precision is the ability of a classiifer not to label an instance positive that is actually negative. For each class it is defined as as the ratio of true positives to the sum of true and false positives. Said another way, “for all instances classified positive, what percent was correct?” {COLUMNS in the confusion matrix}

# recall
Recall is the ability of a classifier to find all positive instances. For each class it is defined as the ratio of true positives to the sum of true positives and false negatives. Said another way, “for all instances that were actually positive, what percent was classified correctly?” {ROWS in the confusion matrix}

# f1 score
The F1 score is a weighted harmonic mean of precision and recall such that the best score is 1.0 and the worst is 0.0. Generally speaking, F1 scores are lower than accuracy measures as they embed precision and recall into their computation. As a rule of thumb, the weighted average of F1 should be used to compare classifier models, not global accuracy.

# support
Support is the number of actual occurrences of the class in the specified dataset. Imbalanced support in the training data may indicate structural weaknesses in the reported scores of the classifier and could indicate the need for stratified sampling or rebalancing. Support doesn’t change between models but instead diagnoses the evaluation process.
"""

# accuracy
accuracy = (gdf.pred_VDI == gdf.true_VDI).sum() / len(gdf)

# multiclass roc
# https://stackoverflow.com/questions/45332410/sklearn-roc-for-multiclass-classification

# classification_report
labels = ["Extreme", "Severe", "Moderate", "Normal", "Above normal"]
print(classification_report(gdf.true_VDI, gdf.pred_VDI))

# confusion_matrix
vals = gdf.true_VDI.unique()
vals.sort()
confusion_matrix(gdf.true_VDI, gdf.pred_VDI)


# https://scikit-learn.org/stable/auto_examples/model_selection/plot_confusion_matrix.html#sphx-glr-auto-examples-model-selection-plot-confusion-matrix-py
def plot_confusion_matrix(
    y_true, y_pred, classes, normalize=False, title=None, cmap=plt.cm.Blues
):
    """
    This function prints and plots the confusion matrix.
    Normalization can be applied by setting `normalize=True`.
    """
    if not title:
        if normalize:
            title = "Normalized confusion matrix"
        else:
            title = "Confusion matrix, without normalization"

    # Compute confusion matrix
    cm = confusion_matrix(y_true, y_pred)
    # Only use the labels that appear in the data
    # classes = classes[unique_labels(y_true, y_pred)]
    if normalize:
        cm = cm.astype("float") / cm.sum(axis=1)[:, np.newaxis]
        print("Normalized confusion matrix")
    else:
        print("Confusion matrix, without normalization")

    print(cm)

    fig, ax = plt.subplots()
    im = ax.imshow(cm, interpolation="nearest", cmap=cmap)
    ax.figure.colorbar(im, ax=ax)
    # We want to show all ticks...
    ax.set(
        xticks=np.arange(cm.shape[1]),
        yticks=np.arange(cm.shape[0]),
        # ... and label them with the respective list entries
        xticklabels=classes,
        yticklabels=classes,
        title=title,
        ylabel="True label",
        xlabel="Predicted label",
    )

    # Rotate the tick labels and set their alignment.
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

    # Loop over data dimensions and create text annotations.
    fmt = ".2f" if normalize else "d"
    thresh = cm.max() / 2.0
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(
                j,
                i,
                format(cm[i, j], fmt),
                ha="center",
                va="center",
                color="white" if cm[i, j] > thresh else "black",
            )
    fig.tight_layout()
    return ax


from sklearn.utils.multiclass import unique_labels

vals = gdf.true_VDI.unique()
vals.sort()
y_true = gdf.true_VDI
y_pred = gdf.pred_VDI
# Plot normalized confusion matrix
plot_confusion_matrix(
    gdf.true_VDI,
    gdf.pred_VDI,
    classes=vals,
    normalize=True,
    title="Normalized confusion matrix",
)


# -----------------------
# make plots
# -----------------------

# plot regions
from src.analysis.plot_regions import get_vrange, plot_comparison_maps

model = "ealstm"
metric = "value"
datetime = "2018-03-31"
if metric == "VDI":
    vmin = 1
    vmax = 5
else:
    # automatically set from data across all of the plots
    vmin, vmax = get_vrange(gdf[f"true_{metric}"], gdf[f"pred_{metric}"])


for datetime in gdf.datetime.unique():
    gdf_dt = gpd.GeoDataFrame(gpd.GeoDataFrame(gdf[gdf.datetime == datetime]))

    month_name = gdf_dt.datetime.dt.month_name().unique()[0]
    suptitle = f"{metric} for Month: {month_name}\nModel: {model}"
    fig, ax = plot_comparison_maps(
        gdf=gdf_dt, metric=metric, suptitle=suptitle, vmin=vmin, vmax=vmax
    )
    fig.savefig(Path(f"/Users/tommylees/Downloads/{model}_{metric}_{month_name}.png"))
