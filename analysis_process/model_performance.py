from src.analysis import annual_scores


# ------ SEASONALITY ------
# load the monthly scores dictionary
monthly_scores = annual_scores(
    data_path=data_dir,
    models=['previous_month', 'rnn',
            'linear_regression', 'linear_network', 'ealstm'],
    metrics=['rmse', 'r2'],
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


# ------ SEASONALITY ------
