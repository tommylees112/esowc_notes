from collections import namedtuple

DataSource = namedtuple(
    'DataSource',
    ['variable', 'dir_name', 'name', 'date_range', 'year_subfolder', 'path', 'file', 'notes']
)

GLEAM_et = DataSource(
    variable = "PET",
    dir_name = "gleam_pet",
    name = "gleam_pet",
    date_range = [1980,2016],
    year_subfolder = False,
    path = "/work/mj0060/m300157/drought_east_africa/",
    file = "Ep_{YYYY}_GLEAM_v3.1a.nc",
    notes = ""
)

datasources = [GLEAM_et]

""" Marginalia:
    ----------

ouce
et = ["data_not_backed_up/satellite/modis/8kmx8km/monthly/et/nc"]
sm = ["data_not_backed_up/satellite/esa_cci_sm/0.25x0.25/daily/sm/nc/alldata/",
      "data_not_backed_up/satellite/esa_cci_sm/0.25x0.25/daily/sm/nc/alldata/combined",
      "soge-home/projects/land_surface_climate/gleam_global/"]
ndvi = ["data_not_backed_up/satellite/avhrr_gimms/1.0x1.0/monthly/ndvi/ascii"]
precip = ["data_not_backed_up/satellite/cmorph/0.07x0.07/3-hourly/adv_precip/nc/"]


# use a named tuple!
lookup = {"et":{"variable":"et",
  "name":"gleam",
  "date_range":[1980,2017],
  "year_subfolder":True,
  "path":"/pool/data/ICDC/land/gleam_evaporation/DATA",
  "file":"GLEAM_v3.2a__EvaporationParameters__0.25deg__DAILY__UHAM-ICDC__{YYYYMMDD}__fv0.01.nc",
  "notes":""},
"sm":{"variable":"sm",
  "name":"esa_cci_sm",
  "date_range":[1978,2016],
  "year_subfolder":True,
  "path":"/pool/data/ICDC/land/esa_cci_soilmoisture/DATA",
  "file":"ESACCI-SOILMOISTURE-L3S-SSMV-COMBINED-{YYYYMMDD}000000-fv04.2.nc",
  "notes":""},
"lai":{"variable":"lai",
  "name":"avhrr_lai",
  "date_range":[1981,2017],
  "year_subfolder":False,
  "path":"/pool/data/ICDC/land/avhrr_modis_lai/DATA",
  "file":"GlobMap_V01_LAI__{YYYY}{***}__UHAM-ICDC.nc",
  "notes": "the second section of three numbers is a range from 001 - 350 \
  at intervals of 15 days"},
"lst":{"variable":"lst",
  "name":"modis_lst",
  "date_range":[2000,2018],
  "year_subfolder":True,
  "path":"/pool/data/ICDC/land/modis_terra_landsurfacetemperature/DATA/MONTHLY",
  "file":"MODIS-C06__MOD11C3__MONTHLY__LandSurfaceTemperature__0.05deg__UHAM-ICDC__{YYYYMM}__fv0.01.nc",
  "notes":""},
"ndvi":{"variable":"ndvi",
  "name":"modis_ndvi",
  "date_range":[2000,2018],
  "year_subfolder":True,
  "path":"/pool/data/ICDC/land/modis_terra_vegetationindex/DATA",
  "file":"MODIS-C006_MOD13C2_NDVI__LPDAAC__0.05deg__MONTHLY__UHAM-ICDC__{YYYYMM}__fv0.01.nc",
  "notes":""}}

"""

