from pathlib import Path
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt

import torch
from torch import nn
from torch.nn import functional as F

from src.models.linear_network import LinearNetwork, LinearModel, LinearBlock
from src.models.data import DataLoader, train_val_mask
from src.models.utils import chunk_array

from typing import cast, Dict, List, Optional, Tuple, Union

data_path = Path("data")
l = LinearNetwork(layer_sizes=[100], data_folder=data_path)

# l.evaluate()
# dense layers
# l.dense_layers
layer_sizes = [100]
dense_layers = nn.ModuleList(
    [
        LinearBlock(
            in_features=layer_sizes[i - 1], out_features=layer_sizes[i], dropout=dropout
        )
        for i in range(1, len(layer_sizes))
    ]
)


# final dense
# l.final_dense

final_dense = nn.Linear(in_features=layer_sizes[-1], out_features=1)

# DataLoader
len_mask = len(DataLoader._load_datasets(data_path, mode="train", shuffle_data=False))
train_mask, val_mask = train_val_mask(len_mask, 0.3)
batch_size = 256
# batch_size=5
train_dataloader = DataLoader(
    data_path=data_path,
    batch_file_size=batch_size,
    shuffle_data=True,
    mode="train",
    mask=train_mask,
    to_tensor=True,
)
val_dataloader = DataLoader(
    data_path=data_path,
    batch_file_size=batch_size,
    shuffle_data=True,
    mode="train",
    mask=val_mask,
    to_tensor=True,
)
test_arrays_loader = DataLoader(
    data_path=data_path,
    batch_file_size=batch_size,
    shuffle_data=False,
    mode="test",
    to_tensor=True,
)


# lm.model = LinearModel()

input_size = 55
layer_sizes = [55, 55, 55, 55, 55, 100]
dropout = 0.25
lm = LinearModel(input_size=input_size, layer_sizes=layer_sizes, dropout=dropout)


# input_size = torch.Size([175670, 55])
# layer_sizes = [torch.Size([175670, 55]), 55, 55, 55, torch.Size([175670, 55]), 100]
# droput = 0.25
# LinearModel(input_size=input_size,
#             layer_sizes=l.layer_sizes,
#             dropout=dropout)
#
lm.init_weights()
learning_rate = 1e-3
optimizer = torch.optim.Adam([pam for pam in lm.parameters()], lr=learning_rate)

# ------------------------------------------------------------------------------
# TRAINING and testing the NN model
# ------------------------------------------------------------------------------

num_epochs = 1
early_stopping = None
batch_size = 5
learning_rate = 1e-3


train_rmse = []
# set in training mode
lm.train()
# use the split training mode
for x, y in train_dataloader:
    for x_batch, y_batch in chunk_array(x, y, batch_size):
        break

# EPOCH = number of times going through the network
# For one BATCH of data zero the gradient
optimizer.zero_grad()
pred = lm(x_batch)
loss = F.smooth_l1_loss(pred, y_batch)
loss.backward()
optimizer.step()
train_rmse.append(loss.item())

# evaluate on the validation data (EARLY STOPPING)
lm.eval()
val_rmse = []
with torch.no_grad():  # whenever validating on test/validation datasets
    for x, y in val_dataloader:
        break

val_pred_y = lm(x)
val_loss = F.mse_loss(val_pred_y, y)

val_rmse.append(val_loss.item())

# get the training RMSE
print(f"Epoch {epoch + 1}, train RMSE: {np.mean(train_rmse)}")

# STOP early if early_stopping
epoch_val_rmse = np.mean(val_rmse)
print(f"Val RMSE: {epoch_val_rmse}")
if epoch_val_rmse < best_val_score:
    batches_without_improvement = 0
    best_val_score = epoch_val_rmse
else:
    batches_without_improvement += 1
    if batches_without_improvement == early_stopping:
        print("Early stopping!")
        return None

# ------------------------------------------------------------------------------
#
# ------------------------------------------------------------------------------
preds_dict: Dict[str, np.ndarray] = {}
test_arrays_dict: Dict[str, Dict[str, np.ndarray]] = {}

with torch.no_grad():
    for dict in test_arrays_loader:
        for key, val in dict.items():

            preds = lm(val.x)
            preds_dict[key] = preds.numpy()
            test_arrays_dict[key] = {"y": val.y.numpy(), "latlons": val.latlons}
            break
