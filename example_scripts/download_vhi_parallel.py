from ftplib import FTP
from pathlib import Path
import multiprocessing
import ipdb

OUTPUT_DIR = Path(f'/soge-home/projects/crop_yield/esowc_notes/data/vhi2')

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
    """ by having context manager INSIDE function
    TODO: is this sensible? or have the FTP as an argument to be supplied ?
    """
    print(f"Downloading {output_filename}")
    with open(output_filename,'wb') as lf:
        ftp.retrbinary("RETR " + filename, lf.write)
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


def chunks(l, n):
    """ return a generator object which chunks list into sublists of size n
    https://chrisalbon.com/python/data_wrangling/break_list_into_chunks_of_equal_size/
    """
    # For item i in a range that is a length of l,
    for i in range(0, len(l), n):
        # Create an index range for l of n items:
        yield l[i:i+n]


def main():
    # get the filenames
    vhi_files = get_ftp_filenames()

    # split the filenames into batches of 100 (21 batches)?
    batches = [batch for batch in chunks(vhi_files,100)][0]

    # run in parallel for multiple file downloads
    pool = multiprocessing.Pool(processes=100)
    ris = pool.map(batch_ftp_request, batches)

    # write the output (TODO: turn into logging behaviour)
    print("\n\n*************************\n\n")
    print("Script Run")
    print("*************************")
    print("Errors:")
    print("\nError: ",[ri for ri in ris if ri != None])


def test():
    """ run for a single file """
    # get the filenames
    vhi_files = get_ftp_filenames()[:1]
    batches = [batch for batch in chunks(vhi_files,100)][0]
    pool = multiprocessing.Pool(processes=100)

    ipdb.set_trace()
    ris = pool.map(batch_ftp_request, batches)
    # write the output (TODO: turn into logging behaviour)
    print("\n\n*************************\n\n")
    print("Script Run")
    print("*************************")
    print("Errors:")
    print("\nError: ",[ri for ri in ris if ri != None])

if __name__ == "__main__":
    # main()
    test()
