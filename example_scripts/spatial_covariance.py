# spatial_covariance.py
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt


def plot_point(ax, lat, lon):
    ax.plot(lon, lat, color='cyan', marker='o',
                 markersize=20, mew=4, markerfacecolor='none',
                 )  # transform=self.transform)


def spatial_cov(da, lat=48, lon=15, time_constraint=None):
    """
    Calculates the spatial covariance for the specified point (lat, lon) under the specified time constraint.
    """
    import numpy as np
    if not isinstance(da, xr.core.dataarray.DataArray):
        print('data input has to be a xarray data array')
    # set nans to zero, or else the dot function will return nans
    da = da.where(~np.isnan(da), 0)
    da = da.load()

    # calculate anomaly
    anomalies = da - da.mean('time')
    point = dict(latitude=lat, longitude=lon)
    scal_prod = (anomalies.loc[point].dot(anomalies)).compute()
    stds = (da.loc[point].std(dim='time') * da.std(dim='time')).compute()
    total_num = da.time.shape[0]
    return scal_prod / stds / total_num


def spatial_cov_2var(da_point, da):
    """
    Calculates the spatial covariance for the point series da_point
    and the 3D data array da.
    """
    import numpy as np
    if not isinstance(da, xr.core.dataarray.DataArray):
        print('data input has to be a xarray data array')
    # set nans to zero, or else the dot function will return nans
    da = da.where(~np.isnan(da), 0)
    da_point = da_point.where(~np.isnan(da_point), 0)
    da = da.load()
    da_point = da_point.load()
    anomalies = (da - da.mean('time'))#/da.std(dim='time')
    anomalies_point = (da_point - da_point.mean('time'))#/da_point.std(dim='time')
    scal_prod = (anomalies_point.dot(anomalies)).compute()
    stds = (da_point.std(dim='time') * da.std(dim='time')).compute()
    total_num = da.time.shape[0]
    return scal_prod / stds / total_num


def plot_spatial_covariance(spatial_cov):
    assert np.isin(['lat', 'lon'], list(spatial_cov.coords)).all()
    assert isinstance(spatial_cov, xr.DataArray)

    spatial_cov.plot()
    plot_point(plt.gca(), lat, lon)
