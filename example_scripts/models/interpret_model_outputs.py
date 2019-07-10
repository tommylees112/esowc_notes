from pathlib import Path
import xarray as xr
import pandas as pd
from typing import Dict, List, Optional
from scripts.eng_utils import drop_nans_and_flatten
import salem


data_dir = Path('/Volumes/Lees_Extend/data/ecmwf_sowc/data')
test_dir = data_dir / 'features/test'
model_dir = data_dir / 'models/linear_regression'

# ------------------------------------------------------------------------------
# Plotting functions
# ------------------------------------------------------------------------------

# TODO: where to save the plots?
# 'analysis/evaluation/{model}/plots'

def plot_spatial_preds_vs_true(ds: xr.Dataset,
                               var_name: str,
                               cmap: str = 'viridis',
                               unsaturate: bool = False,
                               savefig: bool = False,
                               vmin: Optional[Union[int, float]] = None,
                               vmax: Optional[Union[int, float]] = None,
                               title: Optional[str] = None):
    """plot the spatial patterns of the predicted vs. true values

    TODO: Make them take up the same space (colorbar means that predicted is bigger)
    """
    fig, (ax1,ax2) = plt.subplots(1,2,sharex=True, sharey=True, figsize=(15,6))

    # get the colorbar min/max from the values in the `ds` from `truth` var
    if vmin is None and vmax is None:
        if unsaturate:
            vmax = np.quantile(drop_nans_and_flatten(ds[var_name]), 0.9)
            vmin = np.quantile(drop_nans_and_flatten(ds[var_name]), 0.1)
        else:
            vmax = max(drop_nans_and_flatten(ds[var_name]))
            vmin = min(drop_nans_and_flatten(ds[var_name]))

    kwargs = {'vmin': vmin, 'vmax': vmax, 'cmap': cmap}

    # ds.preds.plot(ax=ax1, add_colorbar=True, **kwargs)
    ds.preds.salem.quick_map(ax=ax1, **kwargs)
    ax1.set_title('Predicted')
    # ds[var_name].plot(ax=ax2, add_colorbar=True, **kwargs)
    ds[var_name].salem.quick_map(ax=ax2, **kwargs)
    ax2.set_title('Truth')
    ax2.set_ylabel('')

    try:
        time = pd.to_datetime(ds.time.values).strftime('%Y-%m-%d')
    except:
        time = ''

    if title is None:
        title = f'{var_name} Evaluation {time}'

    fig.suptitle(title)

    target = f'{var_name}_{time.replace("-", "_")}'

    plt.tight_layout()

    if savefig:
        plt.savefig(f'{target}_comparison.png', dpi=300, bbox_inches='tight')

    return fig,(ax1,ax2)

# ------------------------------------------------------------------------------
# comparison dictionary
# ------------------------------------------------------------------------------

def create_true_predicted_dictionary(model_dir: Path, ) -> Dict:
    pred_files = [file for file in model_dir.iterdir() if file.suffix == '.nc']
    pred_dirs = [f.stem.replace('preds_', '') for f in pred_files]
    true_files = [test_dir / dir / 'y.nc' for dir in pred_dirs]

    assert len(pred_files) == len(true_files), f'The predicted times should\
    also be present in the `features/[experiment]/test/[time]` \
    {len(pred_files)} {len(true_files)}'

    y_hat_ds_list = [xr.open_dataset(f) for f in pred_files]
    y_ds_list = [xr.open_dataset(f) for f in true_files]
    dates = [pd.to_datetime(xr.open_dataset(f).time.values[0]) for f in true_files]
    evaluation_times = [dt.strftime('%Y-%m-%d') for dt in dates]

    evaluation_dict = {
        date: {'y': y_ds_list[ix], 'y_hat': y_hat_ds_list[ix]}
        for ix, date in enumerate(evaluation_times)
    }

    return evaluation_dict


def create_list_comparison_ds(model_dir: Path, ) -> List[xr.Dataset]:
    """
    Arguments:
    ---------
    model_dir: Path
        models/{model_name}
    """
    pred_files = [file for file in model_dir.iterdir() if file.suffix == '.nc']
    pred_dirs = [f.stem.replace('preds_', '') for f in pred_files]
    true_files = [test_dir / dir / 'y.nc' for dir in pred_dirs]

    assert len(pred_files) == len(true_files), f'The predicted times should\
    also be present in the `features/[experiment]/test/[time]` \
    {len(pred_files)} {len(true_files)}'

    #
    ds = xr.open_dataset(pred_files[0])
    ds.merge(true_files[0])

    comparison_list = []
    for ix, pred_file in enumerate(pred_files):
        y_hat_ds = xr.open_dataset(pred_file)
        y_ds = xr.open_dataset(true_files[ix])
        ds = y_hat_ds.merge(y_ds)
        comparison_list.append(ds)

    return comparison_list


# ------------------------------------------------------------------------------
# Plotting the truth vs. the predicted values
# ------------------------------------------------------------------------------

evaluation_dict = create_true_predicted_dictionary(model_dir)
comparison_list = create_comparison_ds(model_dir)
comparison_ds = comparison_list[0]

ds = xr.auto_combine(comparison_list)

plot_spatial_preds_vs_true(
    ds.mean(dim='time'), var_name='VHI',
    vmin=0, vmax=100, title='VHI 1994-01 : 1994-05 Mean'.title(),
)

# ------------------------------------------------------------------------------
# calculating the error (pred - true) (+ve = too large, -ve = too small)
# ------------------------------------------------------------------------------

fig,(ax1,ax2,ax3) = plt.subplots(1,3,figsize=(18,5))

(ds.preds - ds.VHI).plot(ax=ax1,vmin=-0.2,vmax=0.2,cmap='RdBu_r')
(ds.preds - ds.VHI).plot(ax=ax2,vmin=-0.2,vmax=0.2,cmap='RdBu_r')
abs(ds.rec_preds - ds.lin_preds).plot(ax=ax3,vmin=0,vmax=0.2)

ax1.set_title('RNN Error ($\hat{y_{RNN}} - y$)')
ax2.set_title('Linear Error ($\hat{y_{linear}} - y$)')
ax3.set_title('Absolute Difference (Recurrent - Linear)')



#
