import numpy as np
from pathlib import Path
from sklearn import linear_model
from sklearn.metrics import mean_squared_error

from typing import Dict, Tuple, Optional

from src.models.base import ModelBase
from src.models.data import DataLoader, train_val_mask
