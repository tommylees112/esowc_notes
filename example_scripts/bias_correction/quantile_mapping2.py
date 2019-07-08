# -*- coding: utf-8 -*-
"""
@author: eilan_dk (dirk.eilander@deltares.nl)
v0.1 18/08/2016

"""

import numpy as np
from scipy.stats.mstats import mquantiles
from scipy.interpolate import interp1d


def bias_correction(obs, p, s, method='delta', nbins=10, extrapolate=None):
    """Bias Correction techniques for correcting simulated output based on differences between the CDFs of
    observed and simulated output for a training period.

    three different methods are available
    'delta'   This is the simplest bias correction method, which consists on adding the mean change signal
              to the observations (delta method). This method corresponds to case g=1 and f=0 in Amengual
              et al. (2012). This method is applicable to any kind of variable but it is preferable not to
              apply it to bounded variables (e.g. precipitation, wind speed, etc.) because values out of
              range could be obtained.
    'scaling' This method is very similar to the delta method but, in this case, the correction consist on
              scaling the simulation with the difference (additive: 'scaling_add') or quotient
              (multiplicative: 'scaling_multi') between the mean of the observations and the simulation in
              the train period.
    'eqm'     Empirical Quantile Mapping (eQM) This is the most popular bias correction method which consists
              on calibrating the simulated Cumulative Distribution Function (CDF) by adding to the observed
              quantiles both the mean delta change and the individual delta changes in the corresponding
              quantiles. This is equivalent to f=g=1 in Amengual et al. (2012). This method is applicable to
              any kind of variable.

    input args
    obs:      observed climate data for the training period
    p:        simulated climate by the model for the same variable obs for the training period.
    s:        simulated climate for the variables used in p, but considering the test/projection period.
    method:   'delta', 'scaling_add', 'scaling_multi', 'eqm', see explenation above
    nbins:    for 'eqm' method only: number of quantile bins in case of 'eqm' method (default = 10)
    extrapolate: for 'eqm' method only: None (default) or 'constant' indicating the extrapolation method to
              be applied to correct values in 's' that are out of the range of lowest and highest quantile of 'p'

    output
    c:        bias corrected series for s


    ref:
    Amengual, A., Homar, V., Romero, R., Alonso, S., & Ramis, C. (2012). A statistical adjustment of regional
    climate model outputs to local scales: application to Platja de Palma, Spain. Journal of Climate, 25(3), 939-957.
    http://journals.ametsoc.org/doi/pdf/10.1175/JCLI-D-10-05024.1

    based on R-package downscaleR, source:
    https://github.com/SantanderMetGroup/downscaleR/wiki/Bias-Correction-and-Model-Output-Statistics-(MOS)

    TODO: include conditioning on weather types to alleviate the problem that arise when the dry day frequency changes.
    """

    if (method == 'eqm') and (nbins > 1):
        binmid = np.arange((1./nbins)*0.5, 1., 1./nbins)
        qo = mquantiles(obs[np.isfinite(obs)], prob=binmid)
        qp = mquantiles(p[np.isfinite(p)], prob=binmid)
        p2o = interp1d(qp, qo, kind='linear', bounds_error=False)
        c = p2o(s)
        if extrapolate is None:
            c[s > np.max(qp)] = qo[-1]
            c[s < np.min(qp)] = qo[0]
        elif extrapolate == 'constant':
            c[s > np.max(qp)] = s[s > np.max(qp)] + qo[-1] - qp[-1]
            c[s < np.min(qp)] = s[s < np.min(qp)] + qo[0] - qp[0]

    elif method == 'delta':
        c = obs + (np.nanmean(s) - np.nanmean(p))

    elif method == 'scaling_add':
        c = s - np.nanmean(p) + np.nanmean(obs)

    elif method == 'scaling_multi':
        c = (s/np.nanmean(p)) * np.nanmean(obs)

    else:
        raise ValueError("incorrect method, choose from 'delta', 'scaling_add', 'scaling_multi' or 'eqm'")

    return c
