"""
1. https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html
2. https://docs.aws.amazon.com/cli/latest/userguide/install-linux.html#install-linux-path
3.

nohup python -c "from src.exporters import ERA5ExporterPOS; e = ERA5ExporterPOS(); e.export('precipitation_amount_1hour_Accumulation')"> planetOS.out

nohup python -c "from src.exporters import ERA5ExporterPOS; e = ERA5ExporterPOS(); e.export('air_temperature_at_2_metres')"> planetOS_temp.out &

nohup python -c "from src.exporters import ERA5ExporterPOS; e = ERA5ExporterPOS();  e.export('air_temperature_at_2_metres_1hour_Maximum')"> planetOS_tempMAX.out &

nohup python -c "from src.exporters import ERA5ExporterPOS; e = ERA5ExporterPOS();  e.export('air_pressure_at_mean_sea_level')"> planetOS_airP.out &

nohup python -c "from src.exporters import ERA5ExporterPOS; e = ERA5ExporterPOS(); e.export('sea_surface_temperature')"> planetOS_sst.out &

nohup python -c "from src.exporters import ERA5ExporterPOS; e = ERA5ExporterPOS(); e.export('surface_air_pressure')"> planetOS_slp.out &


air_temperature_at_2_metres
air_temperature_at_2_metres_1hour_Maximum
air_pressure_at_mean_sea_level
sea_surface_temperature
surface_air_pressure
"""
from src.exporters import ERA5ExporterPOS

e = ERA5ExporterPOS()

# download precip for 2010 - 2018
e.export(
    "precipitation_amount_1hour_Accumulation", years=[y for y in range(2010, 2019)]
)

variables = [
    "air_pressure_at_mean_sea_level",
    "air_temperature_at_2_metres",
    "air_temperature_at_2_metres_1hour_Maximum",
    "air_temperature_at_2_metres_1hour_Minimum",
    "dew_point_temperature_at_2_metres",
    "eastward_wind_at_100_metres",
    "eastward_wind_at_10_metres",
    "integral_wrt_time_of_surface_direct_downwelling_shortwave_flux_in_air_1hour_Accumulation",
    "lwe_thickness_of_surface_snow_amount",
    "northward_wind_at_100_metres",
    "northward_wind_at_10_metres",
    "precipitation_amount_1hour_Accumulation",
    "sea_surface_temperature",
    "snow_density",
    "surface_air_pressure",
]


import xarray as xr

ds = xr.open_mfdataset(
    "data/raw/era5POS/2018/12/precipitation_amount_1hour_Accumulation.nc"
)

"""
<xarray.Dataset>
Dimensions:                                  (lat: 640, lon: 1280, nv: 2, time1: 744)
Coordinates:
  * lon                                      (lon) float32 0.0 ... 359.718
  * lat                                      (lat) float32 89.784874 ... -89.784874
  * time1                                    (time1) datetime64[ns] 2018-12-01T07:00:00 ... 2019-01-01T06:00:00
Dimensions without coordinates: nv
Data variables:
    time1_bounds                             (time1, nv) datetime64[ns] ...
    precipitation_amount_1hour_Accumulation  (time1, lat, lon) float32 ...
Attributes:
    source:       Reanalysis
    institution:  ECMWF
    tilte:        ERA5 forecasts
"""
