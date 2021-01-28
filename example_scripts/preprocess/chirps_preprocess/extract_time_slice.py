import argparse
import os


def main(file_in, time_start, time_end, file_out):
    """
    Extract a time slice (BY INDEX!) from a netcdf object
  """
    print(
        "**** Extract timesteps: {} - {} from {}****".format(
            time_start, time_end, file_in
        )
    )

    # load the modules inside here (because do the error checking first!)
    import numpy as np
    import xarray as xr

    # read in the dataset
    ds = xr.open_dataset(file_in)

    # check if it's a valid time index
    if time_start > 0:
        assert (
            time_start < len(ds.time) - 1
        ), "You must provide a valid time_start. The max is {}. You supplied {}".format(
            len(ds.time) - 1, time_start
        )
    else:
        # if a negative index it is selecting FROM THE END
        # assert that the POSITIVE is less than the length of the time dimension
        assert -time_start <= len(
            ds.time
        ), "You must provide a valid time_start. When counting from the back of the array, the min is {}. You supplied {}".format(
            len(ds.time), time_start
        )

    if time_start == -1:
        # if start at -1 then the user ONLY wants the most recent timeslice
        ds.isel(time=time_start).to_netcdf(file_out)
    else:
        ds.isel(time=slice(time_start, time_end)).to_netcdf(file_out)

    print("**** File written to {} ****".format(file_out))

    return ds


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Use xarray to extract info about .nc file"
    )
    parser.add_argument(
        "-f", dest="file_in", type=str, help="input netcdf to extract the timeslice"
    )
    parser.add_argument(
        "-o", dest="file_out", type=str, help="output filename to save the timeslice"
    )
    parser.add_argument(
        "-ts", dest="time_start", type=int, help="The starting time_slice"
    )
    parser.add_argument(
        "-te",
        dest="time_end",
        type=int,
        help="The ending (upper limit) time_slice, defaults to time_start + 1",
    )

    args = parser.parse_args()

    file_in = args.file_in
    assert file_in is not None, "You must pass in a file to inspect via the -f command!"

    file_out = args.file_out
    assert (
        file_out is not None
    ), "You must pass in an output filepath via the -o command!"

    time_start = int(args.time_start)
    assert (
        time_start is not None
    ), "You must pass in a starting time_slice via the -ts command!"

    try:
        time_end = int(args.time_end)
    except:
        # has the user passed in a time end? If not then assign it to the next timeslice
        if time_start != -1:
            time_end = time_start + 1
        else:
            # if pass in -1 as the start time user ONLY wants the final timestep (time=-1)
            time_end = -1

    assert (
        time_end is not None
    ), "The ending time_slice can be passed in with the -te command!"

    main(file_in, time_start, time_end, file_out)
