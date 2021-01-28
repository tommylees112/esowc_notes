import glob
import os
import multiprocessing


def unzip_file(file):
    os.system(f"gunzip {file}")
    return


def unzip_all_files(dir):
    if dir[-1] != "/":
        dir += "/"

    files = glob.glob(f"{dir}/*")

    for file in files:
        unzip_file(file)

    return


all_dirs = glob.glob("/scratch/chri4118/tiff/*")

pool = multiprocessing.Pool(processes=30)
pool.map(unzip_all_files, all_dirs)
