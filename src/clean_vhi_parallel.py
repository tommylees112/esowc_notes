"""
# from command line
>>> python src/clean_vhi_parallel.py

# TODO
- for the filepaths that fail run them again, not in parallel but sequentially
-
"""

import glob
import os
import multiprocessing
import sys
from pathlib import Path
import pathlib
import pickle

if os.getcwd().split("/")[-2] == "eswoc_notes":
    sys.path.append("..")
if os.getcwd().split("/")[-1] == "eswoc_notes":
    sys.path.append(".")
print(os.getcwd())
from clean_vhi_data import preprocess_VHI_data, add_coordinates_to_multiple_files

# IN_FILE_DIR=Path("/soge-home/projects/crop_yield/esowc_notes/data/vhi/ftp.star.nesdis.noaa.gov/pub/corp/scsb/wguo/data/Blended_VH_4km/VH")
IN_FILE_DIR = Path("/soge-home/projects/crop_yield/esowc_notes/data/vhi2")
# OUT_FILE_DIR="/soge-home/projects/crop_yield/ESoWC_dummy/data/vhi/clean2"
OUT_FILE_DIR = "/soge-home/projects/crop_yield/esowc_notes/data/vhi2/vhi_chop"


def add_coordinates(netcdf_filepath):
    """ function to be run in parallel & safely catch errors

    https://stackoverflow.com/a/24683990/9940782
    """
    print(f"Starting work on {netcdf_filepath}")
    if isinstance(netcdf_filepath, pathlib.PosixPath):
        netcdf_filepath = netcdf_filepath.as_posix()

    try:
        return preprocess_VHI_data(netcdf_filepath, OUT_FILE_DIR)
    except Exception as e:
        print(f"### FAILED: {netcdf_filepath}")
        return e, netcdf_filepath


def retry_failed_vhi_files(out_file_dir):
    """ for the failed filenames in `vhi_errors.pkl` try again sequentially """
    # load failed filenames
    nc_files = pickle.load(open("vhi_errors.pkl", "rb"))
    # add coordinates to downloaded `.nc` files sequentially
    add_coordinates_to_multiple_files(nc_files, out_file_dir)

    return


def main():
    print(f"Writing data to: {OUT_FILE_DIR}")
    nc_files = [f.as_posix() for f in IN_FILE_DIR.glob("*VH.nc")]

    os.system(f"mkdir -p {OUT_FILE_DIR}")
    assert os.path.isdir(
        OUT_FILE_DIR
    ), f"The output file {OUT_FILE_DIR} does not exist!"

    pool = multiprocessing.Pool(processes=100)
    # pool.map(add_coordinates, nc_files)
    outputs = pool.map(add_coordinates, nc_files)

    print("\n\n*************************\n\n")
    print("Script Run")
    print("*************************")
    print("Errors:")
    print("\nError: ", [error for error in outputs if error != None])
    print("\n__Failed File List:", [error[-1] for error in outputs if error != None])

    # write output of failed files to python.txt
    with open("vhi_errors.pkl", "wb") as f:
        pickle.dump([error[-1] for error in outputs if error != None], f)


if __name__ == "__main__":
    main()
