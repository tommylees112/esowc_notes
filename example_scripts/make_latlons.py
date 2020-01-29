import numpy as np

def make_latlons(y)
    lats = lons = np.array([i for i in range(len(y))])
    latitudes, longitudes = np.meshgrid(lats, lons)
    latitudes, longitudes = latitudes.reshape(-1, 1), longitudes.reshape(-1, 1)
    latlons = np.concatenate((latitudes, longitudes), axis=-1)
    return latlons[:len(y)]
