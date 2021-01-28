from matplotlib import colors as c
import matplotlib.pyplot as plt

# >>>>>>>>>>>>>>>>>
# need to be able to SET colors for particular values!
# https://stackoverflow.com/a/8391452/9940782
for pred_month in cluster_ds.time.values[:2]:
    # plot xr.Dataset
    month_abbr = m_abbrs[pred_month + 1]
data = cluster_ds.cluster_5.sel(time=pred_month).drop('time')  # .plot(color=sns.color_palette("Set1"))

cmap = c.ListedColormap(sns.color_palette("Set1"))
pmesh = plt.pcolormesh(data, cmap=cmap);
cax = plt.colorbar(pmesh)

# >>>>>>>>>>>>>>>>>
# YOU CAN CHOOSE THE VALUES BY THE ORDER!
print(len(sns.color_palette("viridis")))

colorpalette_1 = np.array(sns.color_palette("viridis", 10))[[0, 2, 5, 7, -1]]
colorpalette_2 = np.array(sns.color_palette("viridis", 10))[[-1, 7, 5, 2, 0]]

for colorpalette in [colorpalette_1, colorpalette_2]:
    fig, ax = plt.subplots()
    cmap = c.ListedColormap(colorpalette)
    pmesh = plt.pcolormesh(data, cmap=cmap);
    cax = plt.colorbar(pmesh)

# >>>>>>>>>>>>>>>>>>>
# Kratzert code:
def get_label_2_color(lstm_clusters: Dict, raw_clusters: Dict) -> defaultdict:
    """Helper function to match colors between cluster results.
    This function tries to match the colors of different cluster results, by comparing the number of
    shared basins between to clusters. This is not a bullet-proof algorithm but works for our plots.
    Basically what is does is to take the results of one clusterer and then compare a second one by
    finding the cluster label of the second clusterer that has the most basins in common. Then
    assigning both labels the same color.

    TODO: generalise this for PIXELS
    1) get the pixel ids (stacked -> Tuple: (lat, lon))
    2) get the

    Parameters
    ----------
    lstm_feats : Dict
        Cluster labels for the LSTM embeddings
    raw_feats : Dict
        Cluster labels for the raw catchment attributes

    Returns
    -------
    defaultdict
        Dictionary that contains a mapping from label number to color for both cluster results.
    """
    color_list = ['#1b9e77', '#d95f02', '#7570b3',
        '#e7298a', '#e6ab02', '#66a61e']
    label_2_color = defaultdict(dict)
    basin_in_cluster = {'lstm': defaultdict(list), 'raw': defaultdict(list)}
    for basin, label in lstm_clusters.items():
        basin_in_cluster["lstm"][label].append(basin)
    for basin, label in raw_clusters.items():
        basin_in_cluster["raw"][label].append(basin)

    for label, basins in basin_in_cluster["lstm"].items():
        label_2_color["lstm"][label] = color_list[label]

        max_count = -1
        color_label = None
        for label2, basins2 in basin_in_cluster["raw"].items():
            intersect = set(basins).intersection(basins2)
            if len(intersect) > max_count:
                max_count = len(intersect)
                color_label = label2

        label_2_color["raw"][color_label] = color_list[label]

    return label_2_color


# get the cluster labels for both feature sets and both k values
clusters = get_clusters(lstm_embedding, df_norm, ks=[5, 6], basins=basins)
]

    # draw the maps
    attributes = load_attributes(db_path=str(BASE_RUN_DIR / "attributes.db"),
                             basins = basins,
                             drop_lat_lon = False)

fig, ax=plt.subplots(nrows = 2, ncols = 2, figsize = (12, 10))

                                 for i, k in enumerate(clusters.keys()):
    label_2_color=get_label_2_color(clusters[k]["lstm"], clusters[k]["raw"])
    for j, name in enumerate(clusters[k].keys()):
        collection=get_shape_collections(us_states)
        ax[j, i].add_collection(collection)

        data=defaultdict(list)
        for basin, label in clusters[k][name].items():
            data["lat"].append(
                attributes.loc[attributes.index == basin, 'gauge_lat'][0])
            data["lon"].append(
                attributes.loc[attributes.index == basin, 'gauge_lon'][0])
            data["color"].append(label_2_color[name][label])

        points = ax[j,i].scatter(x =data["lon"],
                                 y = data["lat"],
                                 c = data["color"],
                                 s = 30,
                                 zorder = 2,
                                 edgecolor = '#333333',
                                 linewidth =0.5)
        ax[j, i].axis(False)
                                     if name == "lstm":
            ax[j, i].set_title(f"Using LSTM embeddings with k={k}")
                                     else:
            ax[j, i].set_title(f"Using raw catchment attributes with k={k}")
                                     plt.tight_layout()
