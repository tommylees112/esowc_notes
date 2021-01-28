import xarray as xr
import pandas as pd
import numpy as np

# from geopandas import GeoDataFrame
import pickle
from pathlib import Path

from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer


data_dir = Path("/Volumes/Lees_Extend/data/ecmwf_sowc/data")
# gdf = pickle.load(open(data_dir / 'analysis' / 'all_gdf.pkl', 'rb'))
df = pickle.load(open(data_dir / "analysis" / "clean_df.pkl", "rb"))


# ---------------
# clean up the dataframe
# ---------------

# feature engineering and selecting variables
df = gdf.copy()
# df = gdf.drop(columns='geometry_x')
df["month"] = df.datetime.dt.month
df["year"] = df.datetime.dt.year
datetimes = df.datetime
# df = df.drop(columns='datetime')
df = df.dropna(axis=0, how="any")


# ---------------
# work with one region
# ---------------

d = df.loc[df.region_name == "KITUI"]
d = d.set_index("datetime")

num_features = ["SMsurf", "precip", "E", "VCI"]

# create a sklearn pipeline
preprocessor = ColumnTransformer([("numerical", StandardScaler(), num_features)])
vals_ = preprocessor.fit_transform(d)

final = pd.DataFrame(data=vals_, columns=num_features, index=d.index)

# ---------------
#
# ---------------

# ---------------
#
# ---------------

# ---------------
#
# ---------------

# ---------------
#
# ---------------
