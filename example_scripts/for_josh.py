"""
Testing the ERA5ExporterPOS class.

See the notebooks here:
https://github.com/planet-os/notebooks/blob/master/aws/era5-pds.md
https://github.com/planet-os/notebooks/blob/master/aws/era5-s3-via-boto.ipynb

Run the lines starting with "$" using bash

1. Download the repository

    $ git clone https://github.com/esowc/ml_drought.git

2. change to the repository directory

    $ cd ml_drought

3. create the environment with the necessary packages

    $ conda env create -f environment.ubuntu.cpu.yml

4. activate the python environment with the packages installed

    $ conda activate esowc-drought

5. then run the lines below (perhaps copying them into
    an ipython console or however you run your code)

"""

from pathlib import Path

assert (
    Path(".").absolute().name == "ml_drought"
), f"You have to run this script from the ml_drought repository"


from src.exporters import ERA5ExporterPOS

# initialise the ERA5 exporter object
e = ERA5ExporterPOS()

# download precip for 2010 - 2018 (the download should start)
e.export(
    "precipitation_amount_1hour_Accumulation", years=[y for y in range(2010, 2019)]
)

####
# your code analysing the downloaded data
