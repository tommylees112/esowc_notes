import numpy as np
import pandas as pd
import xarray as xr

from pathlib import Path


class ThresholdCounter:
    def __init__(
        self, data_folder: Path = Path("data"), hilo: str = "low", thresh: str = "std"
    ) -> Path:
        self.data_folder = data_folder
        self.interim_folder = data_folder / "interim"
