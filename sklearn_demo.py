import xarray as xr
import pandas as pd
import numpy as np
from geopandas import GeoDataFrame
import pickle
from pathlib import Path

data_dir = Path('/Volumes/Lees_Extend/data/ecmwf_sowc/data')
gdf = pickle.load(open(data_dir / 'analysis' / 'all_gdf.pkl', 'rb'))

# --------------------
# scikit learn modules
# --------------------

# Some sklearn tools for preprocessing and building a pipeline.
# ColumnTransformer was introduced in 0.20 so make sure you have this version
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction import DictVectorizer

from sklearn.model_selection import train_test_split, GridSearchCV
# from sklearn.metrics import accuracy_score, classification_report
from sklearn.metrics import mean_squared_error, r2_score

# Our algorithms, by from the easiest to the hardest to intepret.
from sklearn.linear_model import LogisticRegression
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from xgboost.sklearn import XGBClassifier, XGBRegressor

# feature engineering and selecting variables
df = gdf.copy()
# df = gdf.drop(columns='geometry_x')
df['month'] = df.datetime.dt.month
df['year'] = df.datetime.dt.year
datetimes = df.datetime
# df = df.drop(columns='datetime')
df = df.dropna(axis=0, how='any')

# PICKLE load/save
with open(data_dir / 'analysis' / 'clean_df.pkl', 'wb') as f:
    pickle.dump(pd.DataFrame(df), f)

df = pickle.load(open(data_dir / 'analysis' / 'clean_df.pkl', 'rb'))

#

# X, y split
X = df.drop("VCI", axis=1)

scaler = StandardScaler()
y = df.VCI.values.reshape(-1, 1)
y = scaler.fit_transform(y)

# train, test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=.3, random_state=42)

# preprocessing pipeline
cat_features = ['region_name', 'month', 'year']
num_features = ['SMsurf', 'precip', 'E']

# create a sklearn pipeline
preprocessor = ColumnTransformer([("numerical", StandardScaler(), num_features),
                                  ("categorical", OneHotEncoder(sparse=False, handle_unknown="ignore"),
                                   cat_features)])

rf_model = Pipeline(
    [('preprocessor', preprocessor), ('model', RandomForestRegressor(n_estimators=100, n_jobs=-1))]
)

# search for best parameters
# gs = GridSearchCV(rf_model, {"model__max_depth": [10, 15],
#                              "model__min_samples_split": [5, 10]},
#                   n_jobs=-1, cv=5, scoring="accuracy")

# gs.fit(X_train, y_train)

# fit the model
rf_model.fit(X_train, y_train)
y_pred = rf_model.predict(X_test)
mean_squared_error(y_test, y_pred)

r2_score(y_test, y_pred)

#
# d = df.to_dict()
# vec = DictVectorizer()
# vec.fit_transform(d).to_array()
# vec.get_feature_names()


# ---------------------
# without pipeline
# ---------------------

# PREPROCESS all features
cat_features = ['region_name', 'month', 'year']
num_features = ['SMsurf', 'precip', 'E', 'VCI']

preprocessor = ColumnTransformer([("numerical", StandardScaler(), num_features),
                                  ("categorical", OneHotEncoder(sparse=False, handle_unknown="ignore"),
                                   cat_features)])

_processed_features = preprocessor.fit_transform(df)

ohe_categories = preprocessor.named_transformers_['categorical'].categories_
new_ohe_features = [
    f"{col}__{val}"
    for col, vals in zip(cat_features, ohe_categories)
    for val in vals
]
all_features = num_features + new_ohe_features

clean_df = pd.DataFrame(data=_processed_features, columns=all_features)
