def get_matching_groups(
    reference_ds: xr.DataArray, comparison_ds: xr.DataArray
) -> Tuple[Dict[float, float], pd.DataFrame]:
    # get the unique values from the reference_ds
    group_vals = np.unique(reference_ds.values[~np.isnan(reference_ds.values)])

    # calculate the number of matching pixels
    df = convert_counts_dict_to_dataframe(
        count_matching_pixels(reference_ds, comparison_ds)
    )

    # check that the groups are matching / all groups are included
    assert all(np.isin(np.unique(df.group_0.values), group_vals))
    assert all(np.isin(np.unique(df.group_1.values), group_vals))

    # calculate_the remap_dict
    remap_dict = most_overlapping_pixels_algorithm(df)

    # check all values in group_vals are in the dict keys
    assert all(np.isin([k for k in remap_dict.keys()], group_vals))

    return remap_dict, df


def count_matching_pixels(reference_ds: xr.Dataset, comparison_ds: xr.Dataset) -> Dict[float, Dict[float, float]]:
    """Count the number of pixels for each value
        in comparison_ds for each reference value
        in reference_ds

    Returns:
    -------
     Dict[float, Dict[float, float]]
        keys = reference_ds values
        values = {comparison_ds values: count of matches}
    """
    unique_counts = dict()

    # for each reference value in reference_ds
    # excluding np.nan
    for value in np.unique(reference_ds.values[~np.isnan(reference_ds.values)]):
        # get the pixels from Comparison corresponding to `value` in Reference
        np_arr = comparison_ds.where(reference_ds == value).values
        # drop nans from matching values
        np_arr = np_arr[~np.isnan(np_arr)]
        # calculate the number of group_1 pixels
        counts = np.unique(np_arr, return_counts=True)
        unique_counts[value] = dict(zip(counts[0], counts[1]))

    return unique_counts


def convert_counts_dict_to_dataframe(unique_counts: dict) -> pd.DataFrame:
    """create long format dataframe from counts in unique_counts"""
    df = pd.DataFrame(unique_counts)  # rows = group_1_values, cols = group_0_values
    df.columns = df.columns.rename('group_0')
    df.index = df.index.rename('group_1')
    # 2D -> 1D idx, group_0, group_1, count
    df = df.unstack().reset_index().rename(columns={0:'count'})

    counts = df.groupby('group_1')['count'].sum()
    df['pct'] = df.apply(lamba x: x['count'] / counts.iloc[x.group_1], axis=1)
    assert False

    return df


def get_max_count_row(df: pd.DataFrame) -> pd.Series:
    """Get the row with the largest count from df"""
    return df.loc[df['count'].idxmax()]


def drop_already_assigned_values(
    df: pd.DataFrame,
    assigned_group_values: List[float],
) -> pd.DataFrame:
    """drop the values that have been assigned (added to the lists)
    """
    # remove the matches from group_1
    df = df.loc[~np.isin(df.group_1, assigned_group_values)]
    # remove the matches from group_0
#     df = df.loc[~np.isin(df.group_0, assigned_group_values)]
    return df


def calculate_remap_dict(group_0_list: List[float], group_1_list: List[float]) -> Dict[float, float]:
    """create dictionary object containing the mapping from reference_group -> comparison_group"""
    remap_dict = dict()
    # TODO: THis assumption is not true it's not symmetrical
    # remap dict is symmetrical:
    # values in group_0->group_1 are the same mapping as group_1-> group_0
    remap_dict.update(dict(zip(group_0_list, group_1_list)))
    remap_dict.update(dict(zip(remap_dict.values(), remap_dict.keys())))

    # sort the remap_dict
    remap_dict = {k :remap_dict[k]  for k in sorted(remap_dict)}

    return remap_dict


def most_overlapping_pixels_algorithm(df: pd.DataFrame) -> Dict[float, float]:
    """match the 'closest' group from group_0 in group_1"""
    assert all(np.isin(["group_0", "group_1"], [c for c in df.columns])), f"Need columns group_0 group_1. Found: {df.columns}"
    # get the counts of each pixel value/group (excl. nans) and select the most cross-overs
    # order is important so we do the BEST match first
    # get the largest first
    group_0_list = []
    group_1_list = []

    # match each reference_group to closest matching comparison_group
    # track progress by removing the matches that have already been made
    # from the dataframe
    while df.shape[0] > 0:
        # IF only one group-value left, assign it to the final remaining group (itself)
        if len(df.group_1.unique()) == 1:
            # final value is itself
            # remap_dict[df.group_1.unique()[0]] = df.group_1.unique()[0]
            group_0_list.append(df.group_1.unique()[0])
            group_1_list.append(df.group_1.unique()[0])
            df = drop_already_assigned_values(
                df, group_1_list + group_0_list
            )

        else:
            # otherwise match to the closest remaining match (most overlapping pixels)
            max_count_row = get_max_count_row(df)
            group_0_list.append(
                max_count_row.group_0
            )
            group_1_list.append(
                max_count_row.group_1
            )

            # drop_already_assigned_values
            df = drop_already_assigned_values(
                df, group_1_list+group_0_list
            )

    remap_dict = calculate_remap_dict(group_0_list, group_1_list)

    return remap_dict


# Plotting helper functions
def plot_colors_remapping(colors, remap_dict) -> None:
    colors_remapped = [[int(v) for v in remap_dict.values()]]
    sns.palplot(colors)
    sns.palplot(colors_remapped)


def replace_with_dict2(ar: np.array, dic: Dict) -> np.array:
    """Replace the values in an np.ndarray with a dictionary

    https://stackoverflow.com/a/47171600/9940782
    """
    # Extract out keys and values
    k = np.array(list(dic.keys()))
    v = np.array(list(dic.values()))

    # Get argsort indices
    sidx = k.argsort()

    ks = k[sidx]
    vs = v[sidx]
    warnings.warn("We are taking one from the index. need to check this is true!!!")
    return vs[np.searchsorted(ks, ar) - 1]


def remap_xarray_values(
    xr_obj: Union[xr.Dataset, xr.DataArray],
    lookup_dict: Dict,
    new_variable: str,
    overwrite: bool = True,
    variable: Optional[str] = None,
) -> Union[xr.Dataset, xr.DataArray]:
    """ remap values in xr_obj using lookup_dict.
    Arguments:
    ---------
    : xr_obj (xr.Dataset, xr.DataArray)
        the xarray object we want to look values up from
    : variable (str)
        the INPUT variable we are hoping to look the values up from (the dictionary keys)
    : new_variable (str)
        the name of the OUTPUT variable we want to put the dictionary values in
    : lookup_dict (dict)
        the dictionary we want to lookup the values of 'variable' in to return values to 'new_variable'
    : overwrite (bool)
        True = return a new xr_obj with the remapped values
        False = Assign a new Variable to the xr_obj
    """
    # get the values as a numpy array
    if isinstance(xr_obj, xr.Dataset):
        assert variable is not None
        assert variable in list(ds.data_vars), f"variable is not in {list(ds.data_vars)}"
        ar = xr_obj[variable].values
    elif isinstance(xr_obj, xr.DataArray):
        ar = xr_obj.values
    else:
        assert (
            False
        ), "This function only works with xarray objects." \
        f"Currently xr_obj is type: {type(xr_obj)}"

    assert isinstance(ar, np.ndarray), f"ar should be a numpy array!"
    assert isinstance(lookup_dict, dict), f"lookup_dict should be a dictionary object!"

    # replace values in a numpy array with the values from the lookup_dict
    new_ar = replace_with_dict2(ar, lookup_dict)

    # assign the values looked up from the dictionary to a new variable in the xr_obj
    new_da = xr.DataArray(new_ar, coords=[xr_obj.lat, xr_obj.lon], dims=["lat", "lon"])
    if new_variable is not None:
        new_da.name = new_variable
    if not overwrite:
        new_da = xr.merge([xr_obj, new_da])

    return new_da


remap_dict, matches_df = get_matching_groups(reference_ds, comparison_ds)

print(remap_dict)

# remap_xarray_values(
#     comparison_ds, new_variable='cluster_5',
#     lookup_dict=remap_dict,
#     overwrite=True
# )