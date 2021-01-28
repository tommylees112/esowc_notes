# read_nc_file.py

import argparse
import os


def main(file):
    """"""

    import xarray as xr
    import numpy as np

    assert os.path.isfile(file), "{} DOES NOT EXIST".format(file)

    print("Opening Dataset: {}".format(file))
    # OPEN the netcdf file
    ds = xr.open_dataset(file)
    print("**** SUMMARY ****")
    print(ds)
    print("")

    try:
        print("**** TIME RANGE ****")
        print("{} - {}".format(ds.time.min().values, ds.time.max().values))
        print("")
    except:
        print("... time not found ...")

    try:
        print("**** LONGITUDE RANGE ****")
        print("{} - {}".format(ds.longitude.min().values, ds.longitude.max().values))
        print("")
    except:
        print("... longitude not found ...")

    try:
        print("**** LATITUDE RANGE ****")
        print("{} - {}".format(ds.latitude.min().values, ds.latitude.max().values))
        print("")
    except:
        print("... latitude not found ...")

    # extract the datavariables
    variables = [
        var for var in ds.data_vars.keys() if var not in ["latitude", "longitude"]
    ]

    for var in variables:
        print("**** {} VARIABLE ****".format(var))

        # What % of values are nan / missing?
        print("Missing Values: {}%".format(100 * (np.isnan(ds[var].values).mean())))

        if np.isnan(ds[var].values).mean() < 1.0:
            print("Min Value: {}".format(ds[var].min().values))
            print("Max Value: {}".format(ds[var].max().values))

        print("")

    return ds


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Use xarray to extract info about .nc file"
    )
    parser.add_argument("-f", dest="file")

    args = parser.parse_args()

    file = args.file
    assert file is not None, "You must pass in a file to inspect via the -f command!"

    main(file)
