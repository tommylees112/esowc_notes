"""
conda activate esowc-drought

nohup python run.py --config pipeline_config/vhi.json > nohup_vhi_download.out &

wait

nohup python -c "from src.run import Run; from pathlib import Path; data = Path('data'); r = Run(data); preprocess_args = {'vhi':[{'subset_kenya':True}]}; r.process(preprocess_args)" > nohup_vhi.out &
"""


from src.run import Run
from pathlib import Path

data = Path("data")
r = Run(data)


preprocess_args = {"vhi": [{"subset_kenya": True}]}

r.process(preprocess_args)
