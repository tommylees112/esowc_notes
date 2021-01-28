import xarray as xr
import pandas as pd
from pathlib import Path
import sqlite3

base_dir = Path("/home/jovyan/ealstm_regional_modeling/")
data_dir = base_dir / "runs/run_1305_1437_seed472410"

# ------------------------
# CONNECT TO DATABASE:
# ------------------------
# connect to database
con = sqlite3.connect(data_dir / "attributes.db")
cur = con.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
db_name = cur.fetchall()[0][0]

# attrs = pd.read_sql_table('basin_attributes', con)
df = pd.read_sql(f"SELECT * FROM {db_name}", con)

# OR
with sqlite3.connect(data_dir / "attributes.db") as conn:
    df = pd.read_sql("SELECT * FROM 'basin_attributes'", conn, index_col="gauge_id")


# ------------------------
# Dynamic Data
# ------------------------
basins = get_basin_list()
ds = CamelsH5(
    h5_file=data_dir / "data/train/train_data.h5",
    basins=basins,
    db_path=data_dir / "attributes.db",
    concat_static=False,
    cache=False,
    no_static=False,
)
"""PyTorch data set to work with pre-packed hdf5 data base files.

    Should be used only in combination with the files processed from `create_h5_files` in the
    `papercode.utils` module.

    Parameters
    ----------
    h5_file : PosixPath
        Path to hdf5 file, containing the bundled data
    basins : List
        List containing the 8-digit USGS gauge id
    db_path : str
        Path to sqlite3 database file, containing the catchment characteristics
    concat_static : bool
        If true, adds catchment characteristics at each time step to the meteorological forcing
        input data, by default False
    cache : bool, optional
        If True, loads the entire data into memory, by default False
    no_static : bool, optional
        If True, no catchment attributes are added to the inputs, by default False
    """
