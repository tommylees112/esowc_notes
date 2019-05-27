from pathlib import Path
from src.exporters import CHIRPSExporter

data_dir = Path('data')
c = CHIRPSExporter(data_dir)

c.export(region='africa')
