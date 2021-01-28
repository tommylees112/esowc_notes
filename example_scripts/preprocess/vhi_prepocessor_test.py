from src.preprocess.vhi import VHIPreprocesser
from pathlib import Path

v = VHIPreprocesser()

# test that collect the filenames correctly
demo_raw_folder = v.raw_folder / "vhi" / "1981"
demo_raw_folder.mkdir(parents=True, exist_ok=True)

fnames = [
    "VHP.G04.C07.NC.P1981035.VH.nc",
    "VHP.G04.C07.NC.P1981036.VH.nc",
    "VHP.G04.C07.NC.P1981037.VH.nc",
    "VHP.G04.C07.NC.P1981038.VH.nc",
    "VHP.G04.C07.NC.P1981039.VH.nc",
]

[(demo_raw_folder / fname).touch() for fname in fnames]


from src.exporters.vhi import VHIExporter, batch_ftp_request
import xarray as xr

fname = "VHP.G04.C07.NC.P1981035.VH.nc"

# download 1981
fnames = e.get_ftp_filenames([1981])
e = VHIExporter()
# raw_folder = e.raw_folder
raw_folder = Path("data/raw/")
batch_ftp_request({"raw_folder": raw_folder}, fnames)
ds = xr.open_dataset("data/raw/vhi/1981/VHP.G04.C07.NC.P1981035.VH.nc")

# make a dummy netcdf file
HEIGHT = list(range(0, 3616))
WIDTH = list(range(0, 10000))
VCI = TCI = VHI = np.random.randint(1000, size=(3616, 10000)) * 0.1

raw_ds = xr.Dataset(
    {
        "VCI": (["HEIGHT", "WIDTH"], VCI),
        "TCI": (["HEIGHT", "WIDTH"], TCI),
        "VHI": (["HEIGHT", "WIDTH"], VHI),
    },
    # coords = {
    #     'HEIGHT': (HEIGHT),
    #     'WIDTH': (WIDTH),
    # }
)


# test extract_timestamp(ds, netcdf_filepath, use_filepath=True)
