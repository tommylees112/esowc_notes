    def create_valid_time_ds(self, ds: xr.Dataset) -> xr.Dataset:
        """"""
        # calculate the valid times from the FH/ID
        forecast_horizon = ds.forecast_horizon.values
        initialisation_date = ds.initialisation_date.values
        valid_time = initialisation_date[:, np.newaxis] + forecast_horizon

        # create new dimension in the dataset object
        stacked = ds.stack(
            time=('initialisation_date', 'forecast_horizon')
        )
        stacked['time'] = (['initialisation_date', 'forecast_horizon'], valid_time)
        stacked['forecast_horizon'] = forecast_horizon
        stacked['initialisation_date'] = initialisation_date
        ds['_time'] = (['initialisation_date', 'forecast_horizon'], valid_time)
        ds = ds.assign_coords(valid_time=ds._time)
        ds = ds.drop('_time')

        return ds
