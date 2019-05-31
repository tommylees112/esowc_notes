from pathlib import Path
from src.preprocess import VHIPreprocessor

data_dir = Path('data')
v = VHIPreprocessor(data_dir)
v.preprocess(subset_kenya=True)
