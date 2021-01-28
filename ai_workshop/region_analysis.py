"""
I want to be able to turn a xr.Dataset into a Geopandas
DataFrame with all of the timestep data in a row format
(requires ALOT of space ... many rows)
"""

da = ds.ndvi
region_names = []
true_mean_value = []
datetimes = [pd.to_datetime(t) for t in da.time.values]

region_data_dict = {}
region_data_dict["datetime"] = datetimes
all_region_vals = np.array([])

for valid_region_id in valid_region_ids:
    region_vals = da.where(region_da == valid_region_id).mean(dim=["lat", "lon"]).values
    #     region_data_dict[region_lookup[valid_region_id]] = region_vals
    region_names = np.repeat(region_lookup[valid_region_id], len(region_vals))
    datetimes = np.repeat(datetimes, len(region_vals))
    all_region_vals = np.append(all_region_vals, region_vals)
