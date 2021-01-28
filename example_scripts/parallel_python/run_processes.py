# run_processes.py

from lookup_files import datasources
import os


def check_separator(filepath):
    """ append a slash to the end of the filepath if doesn't already exist """
    if filepath[-1] != os.sep:
        filepath += os.sep

    return filepath


print("******* Process Started **********")

for ds in datasources:
    # for each datasource
    base_data_dir = check_separator(ds.path)
    new_dir_name = ds.dir_name
    start_year = ds.date_range[0]
    end_year = ds.date_range[1]
    variable = ds.variable
    print(f"------ {ds.name} Started -----")

    # 1. chop out awash
    # print(f"------ {ds.name} running chop_out_awash.sh -----")
    # os.system(f"bash chop_out_awash.sh {new_dir_name} {start_year} {end_year} {variable} {base_data_dir} {end_year}")
    print(f"------ {ds.name} running chop_out_east_africa.sh -----")
    os.system(
        f"bash chop_out_east_africa.sh {new_dir_name} {start_year} {end_year} {variable} {base_data_dir} {end_year}"
    )

    # 2.
    # print(f"------ {ds.name} running mergetime_awash.sh -----")
    # os.system(f"bash mergetime_awash.sh {new_dir_name} {start_year} {end_year} {variable} {base_data_dir} {end_year}")

    print(f"------ {ds.name} running mergetime_EA.sh -----")
    os.system(
        f"bash mergetime_EA.sh {new_dir_name} {start_year} {end_year} {variable} {base_data_dir} {end_year}"
    )


print("******* Process Finished **********")
