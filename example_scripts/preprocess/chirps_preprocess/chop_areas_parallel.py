import glob
import os
import multiprocessing

def chop_nc_files(file):
  """ merge all of the daily nc files in the directory into one file"""
  output_dir = "/scratch/chri4118/chirps/africa"
  year = file.split("_")[-1].split(".")[0]

  print(f"** CHOPPING file: {file} - {year} **")

  os.system(f"cdo sellonlatbox,26,56,-12,18 {file} {output_dir}/EA_{year}.nc")
  os.system(f"cdo sellonlatbox,35,46,5,15 {file} {output_dir}/AWASH_{year}.nc")
  print(f"** {file} - {year} CHOPPED **")
  return

if __name__ == "__main__":
  nc_files = glob.glob("/scratch/chri4118/chirps/daily/*.nc")
  os.system("mkdir -p /scratch/chri4118/chirps/africa/")

  assert os.path.isdir("/scratch/chri4118/chirps/africa/"), f"The output file /scratch/chri4118/chirps/africa/ does not exist!"
  pool = multiprocessing.Pool(processes=100)
  pool.map(chop_nc_files, nc_files)


