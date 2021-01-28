# -------------
# static preprocessing
# -------------
#  climatic_attributes
#  humaninfluence_attributes
#  hydrogeology_attributes
#  hydrologic_attributes
#  hydrometry_attributes
#  landcover_attributes
#  soil_attributes
#  topographic_attributes


def replace_val_in_da(
    da: xr.DataArray, value: Any, replace_val: Any = np.nan
) -> xr.DataArray:
    """set all of the instances where da == value to `replace_val`
    e.g. strings with value of ''
    """
    return da.where(da != value, replace_val)


for variable in ["high_prec_timing", "low_prec_timing"]:
    static_ds[variable] = replace_val_in_da(static_ds[variable], "", np.nan)


def preprocess_static(static_ds: xr.Dataset) -> xr.Dataset:
    """preprocess the static data"""
    # set 'station_id' to an integer
    reference_coord = list(static_ds.coords)[0]
    static_ds[reference_coord] = static_ds[reference_coord].astype(int)

    # convert into float
    vars_to_convert_to_float = ["num_reservoir", "reservoir_cap"]
    for v in vars_to_convert_to_float:
        static_ds[v] = static_ds[v].astype(np.dtype("float64"))

    # turn into boolean
    static_ds["benchmark_catch"] = (
        ("station_id"),
        [True if b == "Y" else False for b in static_ds["benchmark_catch"]],
    )

    # to time dtype
    static_ds["flow_period_start"] = (
        ("station_id"),
        [pd.to_datetime(str(ts.values)) for ts in static_ds["flow_period_start"]],
    )
    static_ds["flow_period_end"] = (
        ("station_id"),
        [pd.to_datetime(str(ts.values)) for ts in static_ds["flow_period_end"]],
    )
    return static_ds
