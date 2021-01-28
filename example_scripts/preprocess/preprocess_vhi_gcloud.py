from pathlib import Path
from src.preprocess import VHIPreprocessor


data_path = Path("data")
processor = VHIPreprocessor(data_path)
regrid_path = data_path / "interim/chirps_preprocessed/chirps_kenya.nc"
# processor.preprocess(
#     subset_str='kenya', regrid=regrid_path,
#     parallel=False, resample_time='M', upsampling=False
# )

processor.merge_files(subset_str="kenya", resample_time="M", upsampling=False)
