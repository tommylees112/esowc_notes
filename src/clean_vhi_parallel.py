import glob
import os
import multiprocessing
import sys

if os.getcwd().split('/')[-2] == "eswoc_notes":
    sys.path.append('..')
from src.clean_vhi_data import preprocess_VHI_data

IN_FILE_DIR="/soge-home/projects/crop_yield/ESoWC_dummy/data/vhi/ftp.star.nesdis.noaa.gov/pub/corp/scsb/wguo/data/Blended_VH_4km/VH/"
# OUT_FILE_DIR="/soge-home/projects/crop_yield/ESoWC_dummy/data/vhi/clean2"
OUT_FILE_DIR="/scratch/chri4118/vhi_chop"

def add_coordinates(netcdf_filepath):
    """ function to be run in parallel & safely catch errors

    https://stackoverflow.com/a/24683990/9940782
    """
    print(f"Starting work on {netcdf_filepath}")
    try:
        return preprocess_VHI_data(netcdf_filepath, OUT_FILE_DIR)
    except Exception as e:
        print(f"### FAILED: {netcdf_filepath}")
        return e, netcdf_filepath


if __name__ == "__main__":

  print(f"Writing data to: {OUT_FILE_DIR}")
  nc_files = glob.glob(IN_FILE_DIR+"*VH.nc")[:5]
  os.system(f"mkdir -p {OUT_FILE_DIR}")
  assert os.path.isdir(OUT_FILE_DIR), f"The output file {OUT_FILE_DIR} does not exist!"

  pool = multiprocessing.Pool(processes=100)
  pool.map(add_coordinates, nc_files)
  # ris = pool.map(add_coordinates, nc_files)
  # pool.close()
  # pool.join()
  #
  # # print the errors
  # print("\n\n*************************\n\n")
  # print("Script Run")
  # print("\n\n*************************\n\n")
  # print("Errors")
  # [print(f"\n{result}") for result in ris]
