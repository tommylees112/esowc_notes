"""
paramiko - https://stackoverflow.com/a/3635163/9940782
"""
from pathlib import Path
import paramiko

data_dir = Path('data')

# ------------------------------------------------------------------------------
# Open a transport
host = "hydras.ugent.be"
port = 2225
transport = paramiko.Transport((host, port))

# Auth
password = "v33_GLEAM2019#aw"
username = "gleamuser"
transport.connect(username = username, password = password)

# Connect!
sftp = paramiko.SFTPClient.from_transport(transport)

# Navigate through the sftp server
years = [y for y in range(1980,2018)]

year = years[0]  # TODO: loop through these years

granularity = 'monthly'

base_sftp_path = f'/data/v3.3a/{granularity}'

if granularity == 'daily':
    sftp.chdir(f'{base_sftp_path}/{year}')
    annual_files = [
        f'Eb_{year}_GLEAM_v3.3a.nc',
        f'Ei_{year}_GLEAM_v3.3a.nc',
        f'Ep_{year}_GLEAM_v3.3a.nc',
        f'Es_{year}_GLEAM_v3.3a.nc',
        f'Et_{year}_GLEAM_v3.3a.nc',
        f'Ew_{year}_GLEAM_v3.3a.nc',
        f'E_{year}_GLEAM_v3.3a.nc',
        f'SMroot_{year}_GLEAM_v3.3a.nc',
        f'SMsurf_{year}_GLEAM_v3.3a.nc',
        f'S_{year}_GLEAM_v3.3a.nc'
    ]

    assert sftp.listdir() == annual_files, f'Should have created the same filenames\
        `annual_files` as those found in the sftp directory `sftp.listdir()`'


    # Download
    for file in annual_files:
        filepath = f'{base_sftp_path}/{year}/{file}'
        localpath = (data_dir / 'raw' / 'gleam' / year)

        # check the directory exists and make it if necesary
        if not localpath.exists():
            localpath.mkdir(parents=True, exist_ok=True)
            print(f'mkdir -p {localpath}')
        localpath = (localpath / file).as_posix()

        # send the sftp GET request
        sftp.get(filepath, localpath)


if granularity == 'monthly':
    sftp.chdir(f'{base_sftp_path}')

    monthly_files = [
        'Eb_1980_2018_GLEAM_v3.3a_MO.nc',
        'Ei_1980_2018_GLEAM_v3.3a_MO.nc',
        'Ep_1980_2018_GLEAM_v3.3a_MO.nc',
        'Es_1980_2018_GLEAM_v3.3a_MO.nc',
        'Et_1980_2018_GLEAM_v3.3a_MO.nc',
        'Ew_1980_2018_GLEAM_v3.3a_MO.nc',
        'E_1980_2018_GLEAM_v3.3a_MO.nc',
        'SMroot_1980_2018_GLEAM_v3.3a_MO.nc',
        'SMsurf_1980_2018_GLEAM_v3.3a_MO.nc',
        'S_1980_2018_GLEAM_v3.3a_MO.nc'
    ]
    assert sftp.listdir() == monthly_files, f'Should have created the same filenames\
        `monthly_files` as those found in the sftp directory `sftp.listdir()`'

    for file in monthly_files:
        filepath = f'{base_sftp_path}/{file}'
        localpath = (data_dir / 'raw' / 'gleam' / 'monthly')

        if not localpath.exists():
            localpath.mkdir(parents=True, exist_ok=True)
            print(f'mkdir -p {localpath}')
        localpath = (localpath / file).as_posix()

        sftp.get(filepath, localpath)
        assert Path(localpath).exists(), f'Should have downloaded data to: \
            {localpath} but doesnt exist!'
        print(f'** Completed for {localpath.split('/')[-1]} **')
