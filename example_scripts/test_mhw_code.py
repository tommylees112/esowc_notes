from pathlib import Path
import xarray as xr

data_dir = Path('data')
p_dir = data_dir / 'interim' / 'chirps_preprocessed' / 'chirps_19812019_kenya.nc'
v_dir = data_dir / 'interim' / 'vhi_preprocessed' / 'vhi_preprocess_kenya.nc'

p = xr.open_dataset(p_dir)
v = xr.open_dataset(v_dir)

## test mhw
detect(
    t,
    temp,
    climatologyPeriod=[None, None],
    pctile=90,
    windowHalfWidth=5,
    smoothPercentile=True,
    smoothPercentileWidth=31,
    minDuration=5,
    joinAcrossGaps=True,
    maxGap=2,
    maxPadLength=False,
    coldSpells=False,
    alternateClimatology=False
)
