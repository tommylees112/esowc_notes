from pathlib import Path
import os
import json
from src import DictWithDefaults, Run
from src.preprocess import VHIPreprocessor


base_dir = Path(os.path.dirname(os.path.abspath("./ml_drought")))
default_config_file = base_dir / "pipeline_config/minimal.json"
with open(default_config_file, "r") as f:
    default_config = json.load(f)

user_config = {}
config = DictWithDefaults(user_config, default_config)
data_path = Path(config["data"])


preprocess_args = config["preprocess"]
dataset2preprocessor = {"vhi": VHIPreprocessor}

r = Run(data_path)
dataset, variables = [(d, v) for d, v in preprocess_args.items()][0]
preprocessor = dataset2preprocessor[dataset](r.data)
preprocessor.preprocess(**variables[0])
