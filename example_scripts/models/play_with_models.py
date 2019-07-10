import xarray as xr

from pathlib import Path
from src.models import Persistence, LinearRegression

data_path = Path('data')

# high level api
predictor = Persistence(data_path)
predictor.evaluate(save_preds=True)

predictor = LinearRegression(data_path)
predictor.evaluate(save_preds=True)

# 1 LOAD_TRAIN_DATA get into the guts
x, y = predictor.load_train_arrays()

# 2 ds_folder_to_np (load x/y from the train data)
train_data_path = predictor.data_path / 'features/train'
out_x, out_y = [], []
for subtrain in train_data_path.iterdir():
    if (subtrain / 'x.nc').exists() and (subtrain / 'y.nc').exists():
        arrays = predictor.ds_folder_to_np(subtrain, clear_nans=True,
                                      return_latlons=False)
        out_x.append(arrays.x)
        out_y.append(arrays.y)

# 3
x, y = xr.open_dataset(folder / 'x.nc'), xr.open_dataset(folder / 'y.nc')
x_np, y_np = x.to_array().values, y.to_array().values
# first, x
x_np = x_np.reshape(x_np.shape[0], x_np.shape[1], x_np.shape[2] * x_np.shape[3])
x_np = np.moveaxis(np.moveaxis(x_np, 0, 1), -1, 0)
# then, y
y_np = y_np.reshape(y_np.shape[0], y_np.shape[1], y_np.shape[2] * y_np.shape[3])
y_np = np.moveaxis(y_np, -1, 0).reshape(-1, 1)


# 4
if clear_nans:
    # remove nans if they are in the x or y data
    x_nans, y_nans = np.isnan(x_np), np.isnan(y_np)
    x_nans_summed = x_nans.reshape(x_nans.shape[0],
                                   x_nans.shape[1] * x_nans.shape[2]).sum(axis=-1)
    y_nans_summed = y_nans.sum(axis=-1)
    notnan_indices = np.where((x_nans_summed == 0) & (y_nans_summed == 0))[0]
    x_np, y_np = x_np[notnan_indices], y_np[notnan_indices]

# 5
@dataclass
class ModelArrays:
    x: np.ndarray
    y: np.ndarray
    x_vars: List[str]
    y_var: str
    latlons: Optional[np.ndarray] = None

if return_latlons:
    lons, lats = np.meshgrid(x.lon.values, x.lat.values)
    flat_lats, flat_lons = lats.reshape(-1, 1), lons.reshape(-1, 1)
    latlons = np.concatenate((flat_lats, flat_lons), axis=-1)
    if clear_nans:
        latlons = latlons[notnan_indices]
    arrays = ModelArrays(x=x_np, y=y_np, x_vars=list(x.data_vars),
                         y_var=list(y.data_vars)[0], latlons=latlons)

arrays = ModelArrays(x=x_np, y=y_np, x_vars=list(x.data_vars),
                     y_var=list(y.data_vars)[0])


# 1 Fit the model
x = x.reshape(x.shape[0], x.shape[1] * x.shape[2])  # flatten latlon
predictor.model = linear_model.LinearRegression()
predictor.model.fit(x, y)
train_pred_y = predictor.model.predict(x)
train_rmse = np.sqrt(mean_squared_error(y, train_pred_y))
