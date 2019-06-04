from src.exporters.cds import (CDSExporter, ERA5Exporter)
from src.exporters.s5 import (S5Exporter)
from pathlib import Path
from src.utils import get_kenya

%load_ext autoreload
%autoreload 2

data_dir = Path('data')

# Initialise the ERA5 exporter
e = ERA5Exporter(data_dir)

# valid SEAS5 exporters
valid_datasets = [
    'seasonal-original-single-levels', 'seasonal-original-pressure-levels',
    'seasonal-monthly-single-levels', 'seasonal-monthly-pressure-levels',
]

kenya_region = get_kenya()

variable = 'total_precipitation'
dataset = 'seasonal-original-single-levels'
area = e.create_area(kenya_region)


# times
years = [_ for _ in range(2017,2019)]
months = [_ for _ in range(1,13)]

# leadtime_hour (0 - 215 days)
leadtime_hours = [days * 24 for days in range(1, 20)]
all_leadtimes = [days * 24 for days in range(1, 216)]

\
assert all([lt in all_leadtimes for lt in leadtime_hours]), f"\
    You have specified an illegal leadtime_hour. Must be an \
    integer where int % 24 == 0"

selection_request = {
    'originating_centre': 'ecmwf',
    'system': '5',
    'day': '1',
    'variable': variable,
    'format': 'netcdf',
    'year': years,
    'month': months,
    'leadtime_hour': leadtime_hours,
    'area': area,
}

granularity = 'monthly'

assert dataset in valid_datasets, f"Dataset must be one of: {valid_datasets}. Got: {dataset}"
e.create_selection_request(
    variable, selection_request, granularity
)
