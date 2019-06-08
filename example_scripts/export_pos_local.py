from pathlib import Path

import sys
Path('~/github/ml_drought').absolute().as_posix()
sys.path.append('..')
from src.exporters import ERA5ExporterPOS


def export_era5POS():
    # if the working directory is alread ml_drought don't need ../data
    if Path('.').absolute().as_posix().split('/')[-1] == 'ml_drought':
        data_path = Path('data')
    else:
        data_path = Path('~/github/ml_drought')
    exporter = ERA5ExporterPOS(data_path)

    exporter.export(variable='precipitation_amount_1hour_Accumulation',
    years=[2018])


if __name__ == '__main__':
    export_era5POS()
