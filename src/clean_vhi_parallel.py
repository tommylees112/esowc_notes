import glob
import os
import multiprocessing
from clean_vhi_data import preprocess_VHI_data

IN_FILE_DIR="/soge-home/projects/crop_yield/ESoWC_dummy/data/vhi/ftp.star.nesdis.noaa.gov/pub/corp/scsb/wguo/data/Blended_VH_4km/VH/"
OUT_FILE_DIR="/soge-home/projects/crop_yield/ESoWC_dummy/data/vhi/clean"


def add_coordinates(netcdf_filepath):
    """ function to be run in parallel & safely catch errors

    https://stackoverflow.com/a/24683990/9940782
    """
    try:
        return preprocess_VHI_data(netcdf_filepath, OUT_FILE_DIR)
    except Exception as e:
        return e, netcdf_filepath


if __name__ == "__main__":

  nc_files = glob.glob(IN_FILE_DIR+"*VH.nc")
  os.system(f"mkdir -p {OUT_FILE_DIR}")
  assert os.path.isdir(OUT_FILE_DIR), f"The output file {out_file_dir} does not exist!"

  pool = multiprocessing.Pool(processes=100)
  ris = pool.map(add_coordinates, nc_files)
  pool.close()
  pool.join()

  # print the errors
  print("\n\n*************************\n\n")
  print("Script Run")
  print("\n\n*************************\n\n")
  print("Errors")
  [print(f"\n{result}") for result in ris]
