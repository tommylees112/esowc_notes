import matplotlib.pyplot as plt
import xarray as xr
from src.analysis.plot import Plotter
%matplotlib

chirps = xr.open_dataset('data/interim/chirps_preprocessed/chirps_19812019_kenya.nc')
vhi = xr.open_dataset('data/interim/vhi_preprocessed/vhi_preprocess_kenya.nc')

p = Plotter(chirps)
p.plot_histogram('precip', return_axes=True)


p2 = Plotter(vhi)

fig,ax = plt.subplots()
p.plot_histogram('precip', save=False, ax=ax, return_axes=False)
p2.plot_histogram('VHI', save=False, ax=ax, title='VHI vs. Precip', return_axes=True)
