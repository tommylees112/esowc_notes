from src.analysis import annual_scores
from typing import Dict, List
import pandas as pd


# ------ FUNCTIONS ------
def load_experiment_annual_scores(experiments: List[str] = ['one_month_forecast'],
                                  true_data_experiment: str = 'one_month_forecast') -> Dict[str, pd.DataFrame]:
    out_dict = {}
    for experiment in experiments:
        if experiment == 'one_month_forecast':
            models = ['previous_month', 'rnn',
                      'linear_regression', 'linear_network', 'ealstm']
        else:
            models = ['rnn', 'linear_regression',
                      'linear_network', 'ealstm']
        monthly_scores = annual_scores(
            data_path=data_dir,
            models=models,
            metrics=['rmse', 'r2'],
            pred_years=[y for y in range(2011, 2019)],
            experiment=experiment,
            true_data_experiment=true_data_experiment,
            target_var='VCI',
            verbose=False,
            to_dataframe=True
        )
        out_dict[experiment] = monthly_scores

    return out_dict


# ------ SCRIPTS ------
# load the monthly scores dictionary
experiment = 'one_month_forecast'
monthly_scores = annual_scores(
    data_path=data_dir,
    models=['previous_month', 'rnn',
            'linear_regression', 'linear_network', 'ealstm'],
    metrics=['rmse', 'r2'],
    pred_years=[y for y in range(2011, 2019)],
    experiment=experiment,
    true_data_experiment=experiment,
    target_var='VCI',
    verbose=False,
    to_dataframe=True
)


# ALL MODELS
fig, ax = plt.subplots(figsize=(12, 8))
for model in ['previous_month', 'linear_regression', 'linear_network', 'rnn', 'ealstm']:
    (
        monthly_scores
        .where(monthly_scores.metric == 'rmse')
        .plot(x='month', y=model, label=model, ax=ax)
    )
plt.legend()
ax.set_title('Seasonality of Model Performance')
ax.set_ylabel('RMSE')

# BASELINE vs. EALSTM MODELS
fig, ax = plt.subplots(figsize=(12, 8))
for model in ['previous_month', 'ealstm']:
    (
        monthly_scores
        .where(monthly_scores.metric == 'rmse')
        .plot(x='month', y=model, label=model, ax=ax)
    )
plt.legend()
ax.set_title('Seasonality of Model Performance')
ax.set_ylabel('RMSE')


