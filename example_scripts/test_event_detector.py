from pathlib import Path
from src.analysis import EventDetector

data_dir = Path('data')
interim_dir = data_dir / 'interim'
p_dir = interim_dir / 'chirps_preprocessed' / 'chirps_19812019_kenya.nc'
v_dir = interim_dir / 'vhi_preprocessed' / 'vhi_preprocess_kenya.nc'

e = EventDetector(p_dir)
e.detect(
    variable='precip', time_period='dayofyear', hilo='low', method='std'
)

runs = e.calculate_runs()
