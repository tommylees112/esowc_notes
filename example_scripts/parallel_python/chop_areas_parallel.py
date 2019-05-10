import glob
import os
import multiprocessing

in_file_dir="/soge-home/projects/crop_yield/ESoWC_dummy/data/vhi/ftp.star.nesdis.noaa.gov/pub/corp/scsb/wguo/data/Blended_VH_4km/VH/"

out_file_dir="/soge-home/projects/crop_yield/ESoWC_dummy/data/vhi_chop"

def chop_nc_files(file):
  """ merge all of the daily nc files in the directory into one file"""
  output_dir = out_file_dir
  year = file.split("_")[-1].split(".")[0]

  print(f"** CHOPPING file: {file} - {year} **")

  os.system(f"cdo sellonlatbox,26,56,-12,18 {file} {output_dir}/EA_{year}.nc")
  # os.system(f"cdo sellonlatbox,35,46,5,15 {file} {output_dir}/awash/AWASH_{year}.nc")
  print(f"** {file} - {year} CHOPPED **")
  return

if __name__ == "__main__":

  nc_files = glob.glob(in_file_dir+"*VH.nc")
  os.system(f"mkdir -p {out_file_dir}")
  # os.system("mkdir -p /scratch/chri4118/chirps/africa/awash")

  assert os.path.isdir(out_file_dir), f"The output file {out_file_dir} does not exist!"
  pool = multiprocessing.Pool(processes=100)
  pool.map(chop_nc_files, nc_files)
