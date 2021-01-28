import cdsapi

c = cdsapi.Client()

c.retrieve(
    "seasonal-original-single-levels",
    {
        "format": "grib",
        "originating_centre": "ecmwf",
        "system": "5",
        "variable": "total_precipitation",
        "year": ["2018"],
        "month": ["01"],
        "day": "01",
        "leadtime_hour": ["24"],
        "area": "6.002/33.501/-5.202/42.283",
    },
    "S5_2018_01_01_+24h_kenya.grib",
)
