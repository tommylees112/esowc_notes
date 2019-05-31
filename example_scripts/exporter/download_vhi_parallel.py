"""
# NOTE: this file has to be run with ipython

ipython example_scripts/download_vhi_parallel.py

TODO:
- add the output_dir as an argument
- figure out how to pass multiple arguments through the pool.map() function
- so unstable - it has to be run from your root esowc_notes directory (FIX THIS)
"""
from ftplib import FTP
from pathlib import Path
import multiprocessing
import ipdb

# to pickle more than multiprocessing can
# https://stackoverflow.com/a/21345423/9940782
from pathos.multiprocessing import ProcessingPool as Pool

# ------------------------------------------------------------------------------
# TODO: NEED to put inside one of the functions
# OUTPUT_DIR = Path(f'/soge-home/projects/crop_yield/esowc_notes/data/vhi2')
OUTPUT_DIR = Path('data/vhi_demo').absolute()
if not OUTPUT_DIR.exists():
    OUTPUT_DIR.mkdir()
# ------------------------------------------------------------------------------

def get_ftp_filenames():
    """  get the filenames of interest """
    with FTP('ftp.star.nesdis.noaa.gov') as ftp:
        ftp.login()
        ftp.cwd('/pub/corp/scsb/wguo/data/Blended_VH_4km/VH/')

        # append the filenames to a list
        listing = []
        ftp.retrlines("LIST", listing.append)
        # extract the filename
        filepaths = [f.split(' ')[-1] for f in listing]
        # extract only the filenames of interest
        vhi_files = [f for f in filepaths if ".VH.nc" in f]

    return vhi_files


def download_file_from_ftp(ftp_instance, filename, output_filename):
    """ download a single file from the `ftp_instance`
    """
    print(f"Downloading {output_filename}")
    with open(output_filename,'wb') as lf:
        ftp_instance.retrbinary("RETR " + filename, lf.write)
    if output_filename.exists():
        print(f"Successful Download! {output_filename}")
    else:
        print(f"Error Downloading file: {output_filename}")

    return


def batch_ftp_request(filenames, output_dir=OUTPUT_DIR):
    """ This has the context manager to avoid overloading ftp server """
    with FTP('ftp.star.nesdis.noaa.gov') as ftp:
        ftp.login()
        ftp.cwd('/pub/corp/scsb/wguo/data/Blended_VH_4km/VH/')

        for filename in filenames:
            output_filename = output_dir / filename
            download_file_from_ftp(ftp, filename, output_filename)

    return


def each_file_individually(filenames, output_dir=OUTPUT_DIR):
    """ individual context for each file (will that overload that poor server?)"""
    assert False, "Is this irresponsible?"
    with FTP('ftp.star.nesdis.noaa.gov') as ftp:
        ftp.login()
        ftp.cwd('/pub/corp/scsb/wguo/data/Blended_VH_4km/VH/')
        for filename in filenames:
            output_filename = output_dir / filename
            download_file_from_ftp(ftp, filename, output_filename)
    return



def chunks(l, n):
    """ return a generator object which chunks list into sublists of size n
    https://chrisalbon.com/python/data_wrangling/break_list_into_chunks_of_equal_size/
    """
    # For item i in a range that is a length of l,
    for i in range(0, len(l), n):
        # Create an index range for l of n items:
        yield l[i:i+n]


def main(pool, subset=False):
    # get the filenames
    if subset:
        vhi_files = get_ftp_filenames()[:15]
    else:
        vhi_files = get_ftp_filenames()

    # split the filenames into batches of 100 (21 batches)?
    batches = [batch for batch in chunks(vhi_files,100)]

    # run in parallel for multiple file downloads
    # pool = multiprocessing.Pool(processes=100)
    ris = pool.map(batch_ftp_request, batches)

    # write the output (TODO: turn into logging behaviour)
    print("\n\n*************************\n\n")
    print("Script Run")
    print("*************************")
    print("Errors:")
    print("\nError: ",[ri for ri in ris if ri != None])


def test(parallel=True, pool=None):
    """ run for a single file """
    # get the filenames
    vhi_files = get_ftp_filenames()[:1]
    batches = [batch for batch in chunks(vhi_files,100)][0]


    if parallel:
        assert pool != None, "pool argument must be provided when using parallel"
        # https://stackoverflow.com/a/8805244/9940782
        print("Downloading file in `parallel`")
        # pool = multiprocessing.Pool(processes=100)
        ris = pool.map(batch_ftp_request, batches)
        # ris = pool.apply_async(batch_ftp_request,args=(batches,))

        # write the output (TODO: turn into logging behaviour)
        print("\n\n*************************\n\n")
        print("Script Run")
        print("*************************")
        print("Errors:")
        print("\nError: ",[ri for ri in ris if ri != None])
    else:
        # initialise ftp connection
        ftp = FTP('ftp.star.nesdis.noaa.gov')
        ftp.login()
        ftp.cwd('/pub/corp/scsb/wguo/data/Blended_VH_4km/VH/')
        # download the file individually
        print("Downloading file individually")
        filename = batches[0]
        output_filename = OUTPUT_DIR / filename
        download_file_from_ftp(ftp, filename, output_filename)
        ftp.quit()
        # ipdb.set_trace()
    return


if __name__ == "__main__":
    # pool = multiprocessing.Pool(processes=100)
    pool = Pool(processes=100)
    # test(pool=pool)

    # main(pool)

    # GABI RUN THIS OPTION:
    main(pool, subset=True)
