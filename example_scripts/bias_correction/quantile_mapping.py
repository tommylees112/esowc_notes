#!/usr/bin/python
"""programme to make quantile(CDF)-mapping bias correction"""
"""Adrian Tompkins tompkins@ictp.it - please feel free to use"""

import numpy as np
import matplotlib.pyplot as plt

def map(vals):
    """ CDF mapping for bias correction
    note that values exceeding the range of the training set
    are set to -999 at the moment - possibly could leave unchanged?"""
    # calculate exact CDF values using linear interpolation
    cdf1 = np.interp(vals, xbins, cdfmod, left=0.0, right=999.0)
    # now use interpol again to invert the obsCDF, hence reversed x,y
    corrected = np.interp(cdf1, cdfobs, xbins, left=0.0, right=-999.0)
    return corrected


#----------------
# MAIN CODE START
#----------------

global cdfobs, cdfmod, xbins
n=100
cdfn=10

#----------------
# make raw data
#----------------
# make some fake observations(obs) and model (mod) data:
obs = np.random.uniform(low=0.5, high=13.3, size=(n,))
mod = np.random.uniform(low=1.4, high=19.3, size=(n,))

# sort the arrays
obs = np.sort(obs)
mod = np.sort(mod)

# plot the raw data
fig,ax = plt.subplots()
ax.set_title('Plot the raw data')
plt.plot(range(len(obs)), obs, label='observations')
plt.plot(range(len(obs)), mod, label='model')
plt.legend()
plt.show()

#----------------
# calculate pdf
#----------------
# calculate the global max and bins.
global_max = max(np.amax(obs), np.amax(mod))
wide = global_max / cdfn
xbins = np.arange(0.0, global_max + wide, wide)

# create PDF
pdfobs, bins = np.histogram(obs, bins=xbins)
pdfmod, bins = np.histogram(mod, bins=xbins)

# numpy + matplotlib
obs_width = 0.5 * (bins[1] - bins[0])
mod_width = 1 * (bins[1] - bins[0])
bincentres = [(bins[i]+bins[i+1])/2. for i in range(len(bins)-1)]
center = (bins[:-1] + bins[1:]) / 2

# plot the PDF
fig,ax = plt.subplots()
ax.set_title('Histogram of Observations vs. Model')
plt.bar(bincentres, pdfobs, align='center', width=mod_width, label='observations', alpha=0.6)
plt.bar(bincentres, pdfmod, align='center', width=mod_width, label='model', alpha=0.6)
plt.legend()

# seaborn plot PDF
fig,ax = plt.subplots()
ax.set_title('Histogram of Observations vs. Model')
sns.distplot(obs, label='observations', ax=ax)
sns.distplot(mod, label='model', ax=ax)
plt.legend()

#----------------
# calculate cdf
#----------------
# create CDF with zero in first entry.
cdfobs = np.insert(np.cumsum(pdfobs), 0, 0.0)
cdfmod = np.insert(np.cumsum(pdfmod), 0, 0.0)

# plot the CDF
fig, ax = plt.subplots()
ax.set_title('CDF of Observation vs. Model')
plt.plot(bins, cdfobs, label='observations')
plt.plot(bins, cdfmod, label='model')
plt.legend()

# plot the CDF ontop of the PDF
fig, ax = plt.subplots()
ax.set_title('CDF & Histogram of Observation vs. Model')
plt.bar(bincentres, pdfobs, align='center', width=mod_width, label='observations', alpha=0.6)
plt.bar(bincentres, pdfmod, align='center', width=mod_width, label='model', alpha=0.6)
ax.set_ylabel('N Observations (PDF)')
ax2 = ax.twinx()
plt.plot(bins, cdfobs, label='observations')
plt.plot(bins, cdfmod, label='model')
ax2.set_ylabel('Cumsum (CDF)')
plt.legend()


#----------------
# mini dashboard
#----------------
# plot the raw data with cdf/pdf below
fig = plt.figure(constrained_layout=True)
gs = fig.add_gridspec(2, 2)
# raw data
ax1 = fig.add_subplot(gs[0, :])
ax1.set_title('Raw Data')
plt.plot(range(len(obs)), obs, label='observations')
plt.plot(range(len(obs)), mod, label='model')
# pdf
ax2 = fig.add_subplot(gs[1, 0])
ax2.set_title('PDF')
plt.bar(bincentres, pdfobs, align='center', width=mod_width, label='observations', alpha=0.6)
plt.bar(bincentres, pdfmod, align='center', width=mod_width, label='model', alpha=0.6)
# cdf
ax3 = fig.add_subplot(gs[1, 1])
ax3.set_title('CDF')
plt.plot(bins, cdfobs, label='observations')
plt.plot(bins, cdfmod, label='model')
# cleanups
plt.legend()

#---------------------
# compute quantile map
#---------------------
# dummy model data list to be bias corrected
raindata = [2.0, 5.0]
print(raindata)
print(map(raindata))
