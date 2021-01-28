import numpy as np
import torch
from pathlib import Path
from typing import Optional, List, Tuple, Dict, Any
from torch.utils.data import DataLoader, TensorDataset
import random
import pickle

from src.engineer.basin import CamelsCSV
from src.engineer.runoff import RunoffEngineer, CamelsDataLoader
from src.engineer.runoff_utils import get_basins, load_static_data

from src.models.kratzert.nseloss import NSELoss
from src.models.kratzert import Model
import tqdm
import pandas as pd
from torch import nn
import sys
import time

from src.engineer.runoff_utils import get_basins

# SETTINGS
data_dir = Path("data")
basins = get_basins(data_dir)
train_dates = [2000, 2010]
with_basin_str = True
val_dates = [2011, 2020]
target_var = "discharge_spec"
x_variables = ["precipitation", "peti"]
static_variables = ["pet_mean", "aridity", "p_seasonality"]
ignore_static_vars = None
seq_length = 365
dropout = 0.4
hidden_size = 256
seed = 10101
cache = True
use_mse = True
batch_size = 50  # 256
num_workers = 4
initial_forget_gate_bias = 5
learning_rate = 1e-3
epochs = 30

# EALSTM
concat_static = False
with_static = True

DEVICE = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

## TRAIN dataloader

data = CamelsDataLoader(
    data_dir=data_dir,
    basins=basins,
    concat_static=concat_static,
    cache=cache,
    with_static=with_static,
    train_dates=train_dates,
)
train_loader = DataLoader(
    data, batch_size=batch_size, shuffle=True, num_workers=num_workers
)

## VAL dataloader
val_data = CamelsDataLoader(
    data_dir=data_dir,
    basins=basins,
    concat_static=concat_static,
    cache=cache,
    with_static=with_static,
    train_dates=val_dates,
)
val_loader = DataLoader(
    val_data, batch_size=batch_size, shuffle=True, num_workers=num_workers
)

## TEST dataloader
test_data = CamelsDataLoader(
    data_dir=data_dir,
    basins=basins,
    concat_static=concat_static,
    cache=cache,
    with_static=with_static,
    train_dates=[1999],
)
test_loader = DataLoader(
    test_data, batch_size=batch_size, shuffle=True, num_workers=num_workers
)


# LSTM model
class LSTMModel(pl.LightningModule):
    def __init__(
        self, hidden_size: int,
        train_ds: TensorDataset,
        val_ds: TensorDataset,
        test_ds: TensorDataset,
        dropout_rate: float = 0.0,
        n_features: int = 2,
        learning_rate: float = 0.02
    ):
        super(LSTMModel, self).__init__()

        # initialise the parameters of the model
        self.hidden_size = hidden_size
        self.dropout_rate = dropout_rate
        self.learning_rate = learning_rate

        # initialise the loss function
        self.loss_func = F.mse_loss

        # create LSTM layer
        self.lstm = nn.LSTM(input_size=n_features, hidden_size=self.hidden_size,
                            num_layers=1, bias=True, batch_first=True)

        # fully connected final layer with dropout
        self.dropout = nn.Dropout(p=self.dropout_rate)
        self.fully_connected = nn.Linear(
            in_features=self.hidden_size, out_features=1)

        # initialise dataloaders
        self.train_ds: TensorDataset = train_ds
        self.val_ds: TensorDataset = val_ds
        self.test_ds: TensorDataset = test_ds

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass through the Network.

        :param x: Tensor of shape [batch size, seq length, num features]
            containing the input data for the LSTM network.

        :return: Tensor containing the network predictions

        Same as torch.nn.Module.forward(), however in Lightning you want this
            to define the operations you want to use for prediction
            (ie: on a server or as a feature extractor).

        Normally you’d call self.forward() from your
            training_step() method.  This makes it easy to write a
            complex system for training with the outputs you’d want
            in a prediction setting.
        """
        output, (h_n, c_n) = self.lstm(x)
        state = (h_n, c_n)

        # perform prediction only at the end of the input sequence
        pred = self.fully_connected(self.dropout(h_n[-1, :, :]))

        return pred

    def my_loss(self, y_hat, y):
        loss = F.mse_loss(y_hat, y)
        return loss

    def training_step(self, batch, batch_idx):
        """
        for epoch in range(10):
            for batch in data:
              # training_step above is what happens here
              # lightning handles the rest (backward, gradient clip, etc...)
        """
        x, y = batch
        y_hat = self.forward(x)
        return {'loss': self.my_loss(y_hat, y)}

    def validation_step(self, batch, batch_idx):
        """
        for val_batch in data:
            # validation_step above is what happens here
            # with no grad, eval, etc... all handled for you automatically
        """
        # OPTIONAL
        x, y = batch
        y_hat = self.forward(x)
        return {'val_loss': self.my_loss(y_hat, y).cpu()}

    def validation_end(self, outputs):
        # OPTIONAL
        val_loss_mean = torch.stack([x['val_loss'] for x in outputs]).mean()
        return {'val_loss': val_loss_mean}

    def test_step(self, batch, batch_idx):
        # OPTIONAL
        x, y = batch
        y_hat = self.forward(x)
        return {'test_loss': self.my_loss(y_hat, y)}

    def test_end(self, outputs):
        # OPTIONAL
        test_loss_mean = torch.stack([x['test_loss'] for x in outputs]).mean()
        return {'test_loss': test_loss_mean}

    def configure_optimizers(self):
        # REQUIRED
        return torch.optim.Adam(self.parameters(), lr=self.learning_rate)

    @pl.data_loader
    def train_dataloader(self):
        return DataLoader(self.train_ds, batch_size=1000, num_workers=3)

    @pl.data_loader
    def val_dataloader(self):
        # OPTIONAL
        # can also return a list of val dataloaders
        return DataLoader(self.val_ds, batch_size=2048, num_workers=3)

    @pl.data_loader
    def test_dataloader(self):
        # OPTIONAL
        # can also return a list of test dataloaders
        return DataLoader(self.test_ds, batch_size=2048, num_workers=3)
