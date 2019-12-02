from pathlib import Path
from src.preprocess import (S5Preprocessor)
%load_ext autoreload
%autoreload 2

data_path = Path('data')
regrid_path = data_path / 'interim/chirps_preprocessed/data_kenya.nc'

datasets = [
        d.name 
        for d in (data_path / 'raw').iterdir() 
        if 'seasonal' in d.name
]
for dataset in datasets:
    variables = [
        v.name for v in (data_path / 'raw' / dataset).glob('*')
    ]

    for variable in variables:
        processor = S5Preprocessor(data_path)
        processor.preprocess(subset_str='kenya', regrid=regrid_path,
                            resample_time='M', upsampling=False,
                            variable=variable)
        break
