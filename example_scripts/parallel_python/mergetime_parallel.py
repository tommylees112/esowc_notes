import glob
import os
import multiprocessing

def merge_nc_files(dir_):
  """ merge all of the daily nc files in the directory into one file"""
  year = dir_.split('/')[-1] if dir_.split('/')[-1] != '' else dir_.split('/')[-2]
  output_dir = "/scratch/chri4118/chirps/daily"

  print(f"** MERGING year: {year} in {dir_} **")
  # os.system(f"cdo -f nc2 mergetime {dir_}/*.nc {output_dir}/chirps_{year}.nc")
  os.system(f"cdo cat {dir_}/*.nc {output_dir}/chirps_daily_{year}.nc")
  print(f"** year {year} merged **")

  return

if __name__ == "__main__":
  year_dirs = glob.glob("/scratch/chri4118/nc/*")
  os.system("mkdir -p /scratch/chri4118/chirps/daily/")

  assert os.path.isdir("/scratch/chri4118/chirps/daily/"), f"The output file /scratch/chri4118/chirps/daily/ does not exist!"
  pool = multiprocessing.Pool(processes=100)
  pool.map(merge_nc_files, year_dirs)

