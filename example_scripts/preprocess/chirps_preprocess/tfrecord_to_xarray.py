import xarray as xr
import tensorflow as tf
from pathlib import Path
from scipy import stats
import numpy as np
import pandas as pd
from typing import Dict, Tuple, List
import re

from tensorflow.core.example.feature_pb2 import Feature as tf_Feature


def find_timestep(string: str) -> str:
    # find the first string pattern matching
    ts_regex = re.compile(r"\d{4}_\d{2}_\d{2}")
    ts = ts_regex.findall(string)[0]

    # return either empty string or the captured year
    ts = ts if ts != [] else ''

    return ts





def dict_to_ds(dict_: Dict) -> xr.Dataset:
    df = pd.DataFrame(dict_)
    try:
        df = df.set_index(['latitude', 'longitude', 'time'])
    except KeyError:
        df = df.set_index(['lat', 'lon', 'time'])

    ds = df.to_xarray()

    return ds


def get_dict_from_tf_feature(result: tf_Feature, idx: int, keys: List) -> dict:
    # iterate over each key in the image (lat, lon, values)
    out = {}
    for i in range(len(keys)):
        data = result.features.feature[keys[i]]

        # extract the data as EITHER float OR int (varies by resource)
        list_of_values = np.array(data.float_list.value)
        if list_of_values.size == 0:
            list_of_values = np.array(data.int64_list.value)
        out[keys[i]] = list_of_values

    out, n_pixels = make_dict_keys_same_length(out)
    # parsed_time = pd.to_datetime(find_timestep(string))

    # if none of the timestamps can be found
    if all([find_timestep(key) == '' for key in out.keys()]):
        times = [idx for _ in range(n_pixels)]
    out['time'] = times

    return out


def tf_feature_to_dataset(data: tf_Feature, idx: int, keys: List) -> xr.Dataset:
    out = get_dict_from_tf_feature(data, idx, keys)
    ds = dict_to_ds(out)
    return ds


def tfrecord_to_xarray(file: str) -> List[xr.Dataset]:
    """Turn `tfrecord` datatype into a dictionary of equal length
    lists (pixels).

    """
    ds_timesteps = []
    # iterate over each `example` in the dataset (observation/image)
    for i, example in enumerate(tf.python_io.tf_record_iterator(file)):
        # read as a dict-like object
        result = tf.train.Example.FromString(example)
        keys = [k for k in result.features.feature.keys()]

        ds = tf_feature_to_dataset(result, i, keys)
        ds_timesteps.append(ds)

    return ds_timesteps
