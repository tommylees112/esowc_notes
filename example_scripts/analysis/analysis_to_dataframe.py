"""
Note: for wide format
https://stackoverflow.com/a/30512931/9940782
for metric in monthly_scores.keys():
    ...
    keys_ = [c for c in metric_df.columns if c != 'month']
    vals_ = [f'{c}_{metric}' for c in metric_df.columns if c != 'month']
    metric_df = metric_df.rename(columns=dict(zip(keys_, vals_)))
    ...
df = reduce(lambda left, right: pd.merge(left, right, on='month'),
            metric_dfs)

"""
def annual_scores_to_dataframe(monthly_scores: Dict) -> pd.DataFrame:
    """Convert the dictionary from annual_scores to a pd.DataFrame
    """
    df = pd.DataFrame(monthly_scores)

    metric_dfs = []
    # rename columns by metric
    for metric in monthly_scores.keys():
        metric_df = df[metric].apply(pd.Series).T
        keys_ = [c for c in metric_df.columns if c != 'month']
        vals_ = [f'{c}_{metric}' for c in metric_df.columns if c != 'month']
        metric_df = metric_df.rename(columns=dict(zip(keys_, vals_)))
        metric_dfs.append(metric_df)

    # join columns into one dataframe
    df = reduce(lambda left, right: pd.merge(left, right, on='month'),
                metric_dfs)

    return df
