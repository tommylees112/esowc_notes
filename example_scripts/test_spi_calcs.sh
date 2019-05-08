# testing use of climate_indices package from the command line

process_climate_indices --index spi --periodicity monthly --netcdf_precip kenya_rainfall2.nc --var_name_precip tp --output_file_base ./kenya_monthly_spi --scales 1 3 6 --calibration_start_year 1980 --calibration_end_year 2017 --multiprocessing all
