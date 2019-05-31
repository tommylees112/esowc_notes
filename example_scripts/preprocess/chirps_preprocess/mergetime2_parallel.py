# mergetime2_parallel.py

import glob
import os
import multiprocessing

def merge_nc_files(dir_):
  """ merge all of the daily nc files in the directory into one file"""
  location = dir_.split("/")[-1] if dir_.split("/")[-1] != "" else dir_.split("/")[-2]
  location = location.upper()
  output_dir = "/scratch/chri4118/chirps/final"

  print(f"** MERGING {location} in {dir_} - MERGETIME **")
  os.system(f"cdo -f nc2 mergetime {dir_}/*.nc {output_dir}/{location}_chirps_daily_mergetime.nc")

  print(f"** MERGING {location} in {dir_} - CAT **")
  os.system(f"cdo cat {dir_}/*.nc {output_dir}/{location}_chirps_daily_cat.nc")
  print(f"** {location} merged **")

  return

if __name__ == "__main__":
  os.system("mkdir -p /scratch/chri4118/chirps/final/")

  awash_dir = "/scratch/chri4118/chirps/africa/awash"
  ea_dir = "/scratch/chri4118/chirps/africa/ea"
  dirs = [awash_dir, ea_dir]

  pool = multiprocessing.Pool(processes=100)
  pool.map(merge_nc_files, dirs)



