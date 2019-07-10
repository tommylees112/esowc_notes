from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import pickle

from src.analysis import plot_shap_values
from src.models import Persistence, LinearRegression, LinearNetwork
from src.models.data import DataLoader

%load_ext autoreload
%autoreload 2

data_dir = Path('/Volumes/Lees_Extend/data/ecmwf_sowc/data')
predictor = LinearRegression(data_folder=data_dir, experiment='nowcast')
predictor.train()
