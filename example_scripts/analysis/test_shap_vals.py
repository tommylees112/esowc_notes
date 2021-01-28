# train models
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from src.models import LinearRegression, LinearNetwork, Persistence
from src.models.data import DataLoader

data_path = Path("data")
l = LinearRegression(data_path)
l.train()

ln = LinearNetwork(layer_sizes=[100], data_folder=data_path)
ln.train(num_epochs=10)

# ------------------------------------------------------------------------------
# try and explain the LinearRegression model
# ------------------------------------------------------------------------------
test_arrays_loader = DataLoader(
    data_path=data_path, batch_file_size=1, shuffle_data=False, mode="test"
)
key, val = list(next(iter(test_arrays_loader)).items())[0]
explanations = l.explain(val.x)

# plot the SHAP explanations

# 1. mean spatial and temporal response
mean_expl = explanations.mean(axis=0).mean(axis=0)
x_vars = val.x_vars
df = pd.DataFrame(dict(variables=x_vars, values=mean_expl))

sns.barplot(x="variables", y="values", data=df)
fig = plt.gcf()
plt.title(f"{key} {val.y_var} mean SHAP Values for Linear Regression")
fig.savefig("scripts/mean_variable_importance_linear_regression.png", dpi=300)

# 2. mean spatial response
values = explanations.mean(axis=0).T.flatten()
x_vars = np.repeat(val.x_vars, 11)
df = pd.DataFrame(
    dict(variable=x_vars, month=np.tile(np.arange(1, 12), 5), value=values)
)

fig, axs = plt.subplots(3, 2, sharex=True, sharey=True)
for i, var in enumerate(val.x_vars):
    d = df.loc[df.variable == var]
    ax_ix = np.unravel_index(i, (3, 2))
    ax = axs[ax_ix]
    d.plot(x="month", y="value", ax=ax, label=var, color=sns.color_palette()[i])
    ax.axhline(0, "k--", alpha=0.7)

fig.savefig("scripts/ts_variable_importance_linear_regression.png", dpi=300)

# ------------------------------------------------------------------------------
# Explain the Linear Network
# ------------------------------------------------------------------------------

test_arrays_loader = DataLoader(
    data_path=data_path,
    batch_file_size=1,
    shuffle_data=False,
    mode="test",
    to_tensor=True,
)
key, val = list(next(iter(test_arrays_loader)).items())[0]
explanations = ln.explain(val.x)

#
