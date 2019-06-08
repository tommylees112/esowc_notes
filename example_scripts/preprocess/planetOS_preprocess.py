from pathlib import Path

from src.preprocess import PlanetOSPreprocessor
data_path = Path('data')

regrid_path = data_path / 'interim/chirps_preprocessed/chirps_kenya.nc'
assert regrid_path.exists(), f'{regrid_path} not available'

processor = PlanetOSPreprocessor(data_path)
processor.preprocess(subset_kenya=True, regrid=regrid_path,
                     parallel=False, resample_time='M', upsampling=False)
