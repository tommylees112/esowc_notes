import xarray as xr
import numpy as np
from datetime import datetime

from src.preprocess import CAMELSGBPreprocessor
from src.utils import get_kenya, get_ethiopia

from ..utils import _make_dataset


def _copy_runoff_data_to_tmp_path(tmp_path: Path) -> None:
    # get the base directory
    cwd = Path(os.getcwd())
    if cwd.name == "ml_drought":
        pass
    elif cwd.parents[0].name == "ml_drought":
        cwd = cwd.parents[0]
    elif cwd.parents[1].name == "ml_drought":
        cwd = cwd.parents[1]
    elif cwd.parents[2].name == "ml_drought":
        cwd = cwd.parents[2]
    else:
        assert False, "Current working directory cannot find base path"

    # copy the data to tmp_path
    source = cwd / "tests/test_data/raw/CAMELS_GB_DATASET"
    assert source.exists()
    source_str = source.as_posix()
    destination = (tmp_path / "raw/CAMELS_GB_DATASET").as_posix()

    shutil.copytree(source_str, destination)


class TestCAMELSGBPreprocessor:
    def test(tmp_path):
        processor = CAMELSGBPreprocessor(tmp_path)
        assert False
