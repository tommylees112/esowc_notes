import glob
import os
import multiprocessing

def to_netcdf(file):
  """ """
  # extract the file name from the string
  filename = file.split('/')[-1] if file.split('/')[-1] != '' else file.split('/')[-2]
  filename = filename.replace(".tif", ".nc")
  year = file.split('/')[-2]
  outfile = f"/scratch/chri4118/nc/{year}/{filename}"

  # https://gis.stackexchange.com/questions/199570/how-to-prepare-tiffs-to-create-a-netcdf-file
  # https://stackoverflow.com/questions/52133969/convert-tiff-to-netcdf
  # os.system(f"gdal_translate -of netCDF -co 'FOMRAT=NC4' {file} {outfile}")
  os.system(f"gdal_translate -of netcdf {file} {outfile}")

  return

def make_folder_structure():
  """ make the folder structure for the .nc files to be written to"""
  for year in range(1981, 2019):
    os.system(f"mkdir -p /scratch/chri4118/nc/{year}")

  return

if __name__ == "__main__":
  make_folder_structure()

  pool = multiprocessing.Pool(processes=100)

  all_files = glob.glob("/scratch/chri4118/tiff/*/*.tif")
  pool.map(to_netcdf, all_files)

