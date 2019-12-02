from pathlib import Path
%load_ext autoreload
%autoreload 2

from src.exporters import ERA5LandExporter

def export_era5_land(variable, years):
    # if the working directory is alread ml_drought don't need ../data
    if Path('.').absolute().as_posix().split('/')[-1] == 'ml_drought':
        data_path = Path('data')
    else:
        data_path = Path('../data')
    exporter = ERA5LandExporter(data_path)

    exporter.export(variable=variable,
                    selection_request={'year': years} if years is not None else None,
                    break_up='yearly')

data_path = Path('data')
e = ERA5LandExporter(data_path)
e.print_valid_vars()

export_era5_land(variable='total_precipitation', years=None)
# export_era5_land(variable='volumetric_soil_water_layer_1', years=None)
# export_era5_land(variable='volumetric_soil_water_layer_2', years=None)
# export_era5_land(variable='volumetric_soil_water_layer_3', years=None)
# export_era5_land(variable='volumetric_soil_water_layer_4', years=None)
