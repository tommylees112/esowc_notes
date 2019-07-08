from pathlib import Path
from src.analysis.indices.spi import SPI

from tests.utils import _make_dataset, _create_dummy_precip_data

tmp_path = Path('/Users/tommylees/Downloads/')
def _create_dummy_precip_data(tmp_path):
    data_dir = tmp_path / 'data' / 'interim' / 'chirps_preprocessed'
    if not data_dir.exists():
        data_dir.mkdir(parents=True, exist_ok=True)

    precip, _, _ = _make_dataset((30, 30), variable_name='precip')
    precip.to_netcdf(data_dir / 'chirps_kenya.nc')

    return data_dir / 'chirps_kenya.nc'


class TestSPI:

    def test_initialisation(tmp_path):
        data_path = _create_dummy_precip_data(tmp_path)

        s = SPI(data_path)

        assert s
