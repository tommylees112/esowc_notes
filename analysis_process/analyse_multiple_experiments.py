from typing import Tuple

# -------- FUNCTIONS ---------


def get_experiment_static(experiment: str) -> bool:
    """
    one_month_forecast_VCI_YESstatic => True
    one_month_forecast_VCI_NOstatic => False
    """
    import re
    rgx = re.compile(r'(YES)|(NO)')
    try:
        static = rgx.search(experiment.split('_')[-1]).group()
    except AttributeError:
        static = None

    return static == 'YES'


def append_auxillary_columns(df: pd.DataFrame) -> pd.DataFrame:
    df['static'] = df.experiment.apply(lambda x: get_experiment_static(x))
    df['var'] = df.experiment.apply(lambda x: x.split('_')[-2])
    df.loc[df.experiment == 'one_month_forecast', ['static', 'var']] = np.nan
    df['static'] = df.static.astype(bool)
    return df


def get_performance_metrics(metric: str,
                            score_dict: Dict[str, pd.DataFrame]) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Arguments:
    ---------
    metric: str,
        one of {'rmse', 'r2}
    score_dict: Dict[str, pd.DataFrame]
        output of `load_experiment_annual_scores()` function
    """
    total_errors = {}
    error_seasonality = []
    for experiment, df in zip(score_dict.keys(), score_dict.values()):
        df = df.drop_duplicates(subset=['month', 'metric', 'year'])
        df = df.where(df.metric == metric).dropna()
        seasonality_of_error = (
            df.drop(columns=['year', 'metric'])
            .groupby('month')
            .mean()
            .reset_index()
        )
        total_error = df.drop(columns=['year', 'metric', 'month']).mean()
        total_errors[experiment] = total_error

        seasonality_of_error = seasonality_of_error.melt(id_vars=['month'])
        seasonality_of_error['experiment'] = experiment
        seasonality_of_error = seasonality_of_error.rename(
            columns={'variable': 'model'})
        error_seasonality.append(seasonality_of_error)

    seasonality = pd.concat(error_seasonality)
    errors = pd.DataFrame(total_errors).T.reset_index().rename(
        columns={'index': 'experiment'})

    seasonality = append_auxillary_columns(seasonality)
    errors = append_auxillary_columns(errors)

    return errors, seasonality


def create_experiment_dataset(pred_dict: Dict[str, xr.DataArray]) -> xr.Dataset:
    """Create new dataset with `static`/`predictor_variables`
    defined as dimensions in the output xr.Dataset object.

    Returns:
    --------
    <xarray.Dataset>
    Dimensions:
    Coordinates:
    * predictor_variables  (predictor_variables) object
    * lat                  (lat) float64
    * lon                  (lon) float64
    * time                 (time) datetime64[ns]
    * static               (static) object
    """
    all_ds = []
    for name, dict_of_ds in zip(pred_dict.keys(), pred_dict.values()):
        datasets = []
        if name == 'one_month_forecast':
            continue

        for model, da in zip(dict_of_ds.keys(), dict_of_ds.values()):
            static = get_experiment_static(name)
            variable = name.split("_")[-2]

            # create dataset
            ds = da.to_dataset(model)
            ds = ds.assign_coords(static=static)
            ds = ds.assign_coords(predictor_variables=variable)
            ds = ds.expand_dims({'static': [static]})
            ds = ds.expand_dims({'predictor_variables': [variable]})
            datasets.append(ds)

        expt_ds = xr.merge(datasets)
        all_ds.append(expt_ds)

    expt_ds = xr.auto_combine(all_ds)

    return expt_ds


# -------- SCRIPT ---------
# read in other experiment predictions
experiments = [
    'one_month_forecast_VCI_YESstatic',
    'one_month_forecast_VCI_NOstatic',
    'one_month_forecast_precip_YESstatic',
    'one_month_forecast_precip_NOstatic',
    'one_month_forecast_t2m_YESstatic',
    'one_month_forecast_t2m_NOstatic',
    'one_month_forecast_pev_YESstatic',
    'one_month_forecast_pev_NOstatic',
    'one_month_forecast_E_YESstatic',
    'one_month_forecast_E_NOstatic',
    'one_month_forecast'
]


# pred_dict = read_experiments_pred_data(experiments)
# score_dict = load_experiment_annual_scores(experiments)

# Plot the error metrics for different experiments
r2_errors, r2_seasonality = get_performance_metrics(
    metric='r2', score_dict=score_dict
)
rmse_errors, rmse_seasonality = get_performance_metrics(
    metric='rmse', score_dict=score_dict
)

def plot_metrics(model: str):
    fig, ax = plt.subplots()
    sns.barplot(x='var', y=model, hue='static', data=rmse_errors, ax=ax)
    ax.set_xlabel('rmse')
    ax.axhline(14.722749710083)

    return fig, ax



plot_metrics('rnn')


# fig, ax = plt.subplots()
# sns.barplot(x='var', y='ealstm', hue='static', data=rmse_errors, ax=ax)
# ax.set_xlabel('rmse')

# fig, ax = plt.subplots()
# sns.barplot(x='var', y='rnn', hue='static', data=r2_errors, ax=ax)
# ax.set_xlabel('r2')

# # CREATE new dataset
# expt_ds = create_experiment_dataset(pred_dict)

