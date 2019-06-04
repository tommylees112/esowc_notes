from src.exporters.cds import (CDSExporter, ERA5Exporter)
from src.exporters.s5 import (S5Exporter)
from src.exporters.all_valid_s5 import datasets as dataset_reference

from pathlib import Path
from src.utils import get_kenya
import numpy as np

%load_ext autoreload
%autoreload 2

data_dir = Path('data')



# ------------------------------------------------------------------------------
# S5 Exporter
# ------------------------------------------------------------------------------


#### TEST 1 - wrong granularity
# assert RaisedError
s5 = S5Exporter(data_dir)
s5.get_s5_initialisation_times('daily')




#### TEST 2 - get_s5_initialisation_times produces the correct keys
s5 = S5Exporter(data_dir)
selection_request = s5.get_s5_initialisation_times(
    'hourly', min_year=2017, max_year=2018,
    min_month=1, max_month=1
)

expected_keys = ['year', 'month', 'day']
assert all(np.isin(expected_keys, [k for k in selection_request.keys()])), f"\
    Expecting keys: {expected_keys}. Got: {[k for k in selection_request.keys()]}"




#### TEST 3 - get_s5_leadtimes produces the correct keys & values for dataset
# `seasonal-original-single-level`
granularity = 'hourly'
max_leadtime=5
pressure_level=False

s5 = S5Exporter(data_dir)

selection_request = s5.get_s5_leadtimes(
                    granularity=granularity,
                    max_leadtime=max_leadtime,
                    pressure_level=pressure_level
)
expected_keys = ['leadtime_hour']
assert all(np.isin(expected_keys, [k for k in selection_request.keys()])), f"\
    Expecting keys: {expected_keys}. Got: {[k for k in selection_request.keys()]}"


assert isinstance(selection_request['leadtime_hour'][0], str), f"Expected a list of str, got: {type(selection_request['leadtime_hour'][0])}"

leadtimes_int = [int(lt) for lt in selection_request['leadtime_hour']]
assert max(leadtimes_int) == 120, f"Expected max leadtime to be 120hrs\
Got: {max(leadtimes_int)}hrs"




#### TEST 4 - get_s5_leadtimes produces the correct keys & values for dataset
# `seasonal-monthly-pressure-levels`
granularity = 'monthly'
max_leadtime=5
pressure_level=True

s5 = S5Exporter(data_dir)

selection_request = s5.get_s5_leadtimes(
                    granularity=granularity,
                    max_leadtime=max_leadtime,
                    pressure_level=pressure_level
)
expected_keys = ['leadtime_month']
assert all(np.isin(expected_keys, [k for k in selection_request.keys()])), f"\
    Expecting keys: {expected_keys}. Got: {[k for k in selection_request.keys()]}"


assert isinstance(selection_request['leadtime_month'][0], str), f"Expected a list of str, got: {type(selection_request['leadtime_hour'][0])}"

leadtimes_int = [int(lt) for lt in selection_request['leadtime_month']]
assert max(leadtimes_int) == 5, f"Expected max leadtime to be 5 months\
Got: {max(leadtimes_int)} months"




#### TEST 5 - test dataset_reference creation
s5 = S5Exporter(data_dir)

expected_dataset_reference = dataset_reference['seasonal-original-single-levels']




#### Test 6 - get_product_type for pressure levels hourly
s5 = S5Exporter(data_dir)

s5.dataset = 'seasonal-original-single-levels'
s5.dataset_reference = dataset_reference[s5.dataset]
assert s5.get_product_type(None) is None, f"Expecting the product_type for \
seasonal-original-single-levels dataset to be None. Returned:\
 {s5.get_product_type(None)}"




#### Test 7 - get_product_type for single levels monthly
s5 = S5Exporter(data_dir)

s5.dataset = 'seasonal-monthly-single-levels'
s5.dataset_reference = dataset_reference[s5.dataset]
assert s5.get_product_type(None) is 'monthly_mean', f"\
Expecting `product_type` for `seasonal-original-single-levels` \
 dataset to be 'monthly_mean'. Returned: {s5.get_product_type(None)}"

assert s5.get_product_type('hindcast_climate_mean') is 'hindcast_climate_mean', f"\
Expecting `product_type` for `seasonal-original-single-levels` dataset to be\
 'hindcast_climate_mean' Returned: {s5.get_product_type('hindcast_climate_mean')}"

# assert ERROR
assert s5.get_product_type('dsgdfgdfh') is Error, f"\
Expecting `product_type` for `seasonal-original-single-levels` dataset to return\
 '' Error. Returned: {s5.get_product_type('dsgdfgdfh')}"



#### TEST 8 - get_dataset
s5 = S5Exporter(data_dir)

expected_dataset = 'seasonal-original-single-levels'
granularity = 'hourly'
pressure_level=False

s5.pressure_level = pressure_level
s5.granularity = granularity
dataset = s5.get_dataset(s5.granularity, s5.pressure_level)

assert dataset == expected_dataset, f"Expected dataset attribute to be: \
 {expected_dataset}. Got: {dataset}"

## b
expected_dataset = 'seasonal-original-pressure-levels'
granularity = 'hourly'
pressure_level=True

s5.pressure_level = pressure_level
s5.granularity = granularity
dataset = s5.get_dataset(s5.granularity, s5.pressure_level)

assert dataset == expected_dataset, f"Expected dataset attribute to be: \
 {expected_dataset}. Got: {dataset}"



#### TEST 9 - create_selection_request
s5 = S5Exporter(data_dir)

granularity = 'monthly'
pressure_level=False
variable = 'total_precipitation'
max_leadtime = 5
min_year=2017
max_year=2018
min_month=1
max_month=12

s5.pressure_level = pressure_level
s5.granularity = granularity

s5.dataset = s5.get_dataset(s5.granularity, s5.pressure_level)
s5.dataset_reference = dataset_reference[s5.dataset]
s5.product_type = s5.get_product_type(product_type = None)

processed_selection_request = s5.create_selection_request(
    variable=variable, max_leadtime=max_leadtime, min_year=min_year,
    max_year=max_year, min_month=min_month, max_month=max_month,
)

# CHECK default arguments
assert processed_selection_request['originating_centre'] == 'ecmwf', "\
Expected originating_centre to be: {'ecmwf'}. Got:\
{processed_selection_request['originating_centre']}"

assert processed_selection_request['system'] == '5', f"\
Expected 'system' to be '5'. Got:\
{processed_selection_request['system']}"

# CHECK time arguments
assert processed_selection_request['year'] == ['2017','2018'], f"\
Expected 'year' to be ['2017','2018']. Got:\
{processed_selection_request['year']}"

exp_months = [
    '{:02d}'.format(month)
    for month in range(min_month, max_month + 1)
]
assert processed_selection_request['month'] == exp_months, f"\
Expected 'month' to be {exp_months}. Got:\
{processed_selection_request['month']}"


##### test the parent class export

processed_selection_request
s5._export(
    dataset=dataset,
    selection_request=processed_selection_request,
    show_api_request=True,
)

##### test the filepath created
expected_filepath = 'data/raw/seasonal-monthly-single-levels/total_precipitation/2017_2018/01_12.nc'

filepath = s5.make_filename(
    dataset=s5.dataset,
    selection_request=processed_selection_request
)

assert expected_filepath == filepath.as_posix(), f"\
    Expected: {expected_filepath}. Got: {filepath.as_posix()}"


########
from pprint import pprint
for year, month in itertools.product(processed_selection_request['year'],
                                     processed_selection_request['month']):
    updated_request = processed_selection_request.copy()
    updated_request['year'] = [year]
    updated_request['month'] = [month]
    pprint("\n\n", updated_request)

# ==============================================================================
###### TEST test the export works
# ==============================================================================
granularity = 'monthly'
pressure_level=False

s5 = S5Exporter(
    data_folder=data_dir,
    granularity=granularity,
    pressure_level=pressure_level,
)
s5.get_valid_variables()

variable = 'total_precipitation'
min_year = 2017
max_year = 2017
min_month = 1
max_month = 5
max_leadtime = None
pressure_levels = None
selection_request = None
N_parallel_requests = None
show_api_request = True

s5.export(
    variable=variable,
    min_year=min_year,
    max_year=max_year,
    min_month=min_month,
    max_month=max_month,
    max_leadtime=max_leadtime,
    pressure_levels=pressure_levels,
)
