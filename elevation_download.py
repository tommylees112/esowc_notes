from .base import BaseExporter


class ElevationExporter(BaseExporter):
    """Exports a digital elevation model (DEM) using the
    elevation package

    """

    def __init__(self, data_folder: Path = Path("data")) -> None:
        super().__init__(data_folder)
