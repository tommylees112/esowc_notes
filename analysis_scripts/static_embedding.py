import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr
import calendar

embedding1 = np.random.random((1402, 64))
embedding2 = np.random.random((1402, 64))
latlons = [i for i in product(np.arange(100), np.arange(15))][:1402]
all_e = [embedding1, embedding2]
pred_months = [2]


def plot_embedding_matrix(pred_month: int, embedding: np.array):
    fig, ax = plt.subplots(figsize=(12, 5))

    # make the matrix plot
    img = ax.pcolor(embedding.T, cmap="plasma")

    # label axes
    month = [m for m in calendar.month_abbr][pred_month]
    ax.set_title(f"Input gate activations {month}")
    ax.set_xlabel("Pixels")
    ax.set_ylabel("Input gate neuron")

    # colorbar
    cbar = plt.colorbar(img, ax=ax)
    cbar.ax.set_ylabel("Activation")

    return fig, ax


### k means clustering
from collections import defaultdict
from typing import List, Dict, Union
from sklearn.cluster import KMeans


def fit_kmeans(array: np.array, ks: List[int] = [5]) -> Dict[int, Dict[int, int]]:
    """return the results of k-means clustering algorithm.
    Wraps: `sklearn.cluster.KMeans`

    Returns:
    -------
    : Dict[int, Dict[int, int]]
        key = 'k' paramter for kmeans
        inner_key =

    """
    clusters = {k: {} for k in ks}
    for k in ks:
        # fit the clustering algorithm
        clusterer = KMeans(
            n_clusters=k, random_state=0, init="k-means++", n_init=200
        ).fit(array)
        # for each row (pixel) in the matrix predict the cluster
        for pixel in range(array.shape[0]):
            arr = array[pixel, :]
            clusters[k][pixel] = clusterer.predict(arr.reshape(1, -1))[0]
    return clusters


def convert_clusters_to_ds(
    ks: List[int],
    static_clusters: Dict[int, np.array],
    pixels: np.ndarray,
    latitudes: np.ndarray,
    longitudes: np.ndarray,
    time: Union[pd.Timestamp, int] = 1,
) -> xr.Dataset:
    """calculate a spatial xr.Dataset object with the lat, lon, time
    coordinates restored (for plotting KMeans results on a map).
    """
    out = []
    for k in ks:
        cluster = np.array([v for v in static_clusters[k].values()])
        coords = {"pixel": pixels}
        dims = ["pixel"]
        cluster_ds = xr.Dataset(
            {
                f"cluster_{k}": (dims, cluster),
                "lat": (dims, latitudes),
                "lon": (dims, longitudes),
                "time": (dims, [time for _ in range(len(latitudes))]),
            }
        )
        out.append(cluster_ds)

    static_cluster_ds = xr.auto_combine(out)
    static_cluster_ds = (
        static_cluster_ds.to_dataframe().set_index(["time", "lat", "lon"]).to_xarray()
    )

    return static_cluster_ds


def plot_cluster_ds(ks: List[int], static_cluster_ds: xr.Dataset, month_abbr: str = ""):
    """Plot the static_cluster_ds calculated from `convert_clusters_to_ds`"""
    for k in ks:
        fig, ax = plt.subplots(figsize=(12, 8))
        static_cluster_ds[f"cluster_{k}"].plot(ax=ax)
        ax.set_title(f"Output of Static Embedding Clustering [k={k}]\n{month_abbr}")

        #  + ax.get_xticklabels() + ax.get_yticklabels()):
        for item in [ax.title, ax.xaxis.label, ax.yaxis.label]:
            item.set_fontsize(20)


### workflow
clusters = fit_kmeans(embedding, ks=[5])
cluster_ds = convert_clusters_to_ds(
    ks=[5],
    static_clusters=clusters,
    pixels=latlons,
    latitudes=latlons[:, 0],
    longitudes=latlons[:, 1],
    time=[0, 1],
)
