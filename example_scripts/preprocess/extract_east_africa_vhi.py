from Pathlib import Path

from src.api_helpers import Region
from src.preprocess import VHIPreprocessor

ea_region = Region(
    name='ea_region',
    lonmin=21,
    lonmax=51.8,
    latmin=-11,
    latmax=23,
)

data_dir = Path('/scratch/data/')

v = VHIPreprocessor(data_folder=data_dir)
v.preprocess(subset_kenya=False)
"""
# L64
(
# 5. chop out EastAfrica
if subset_kenya:
    kenya_region = get_kenya()
    new_ds = select_bounding_box(new_ds, kenya_region)
)
### =>
(
region = ea_region
new_ds = select_bounding_box(new_ds, region)
)
"""

lookup_regions = dict(
    'kenya'=kenya_region,
    'ea_region'=ea_region,
)
