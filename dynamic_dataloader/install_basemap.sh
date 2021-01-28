# Set up a place for these new environments:
# make environments directory
mkdir /home/jovyan/envs
# initialize bash
conda init bash
# restart shell
exec $SHELL


# Then, for each environment you want to add:
# in this case, we'll install Python 3.6
conda create -p /home/jovyan/envs/py3.6 python=3.6
# use this new environment
conda activate /home/jovyan/env-test/py3.6
# enable kernel under the name py3.6
pip install --user ipykernel
python -m ipykernel install --user --name=py3.6
# leave environment
conda deactivate


# PYMC
mkdir -p /home/jovyan/envs
conda init bash
exec $SHELL

conda create -p /home/jovyan/envs/pymc
conda activate /home/jovyan/env/pymc
conda install -c conda-forge pymc3 --yes

# enable kernel under the name pymc
pip install --user ipykernel
python -m ipykernel install --user --name=pymc
