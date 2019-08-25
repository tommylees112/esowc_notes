#
true_da_shape = (true_da.lat.shape[0], true_da.lon.shape[0])
pred_da_shape = (pred_da.lat.shape[0], pred_da.lon.shape[0])
assert true_da_shape == pred_da_shape
vals = np.sqrt(
    np.nansum((true_da.values - pred_da.values)**2, axis=0) /
pred_da.shape[0]
)
da = xr.ones_like(pred_da).isel(time=0)
da.values = vals
# reapply the mask
da = da.where(~get_ds_mask(pred_da))

#
from sklearn.metrics import r2_score


# fit values, and mean
pred = p(x)                         # or [p(z) for z in x]
true_mean = numpy.sum(y)/len(y)          # or sum(y)/len(y)
ssreg = numpy.sum((pred-true_mean)**2)   # or sum([ (yihat - true_mean)**2 for yihat in pred])
sstot = numpy.sum((y - true_mean)**2)    # or sum([ (yi - true_mean)**2 for yi in y])
results['determination'] = ssreg / sstot




def spatial_r2(true_da: xr.DataArray,
               pred_da: xr.DataArray) -> xr.DataArray:
    true_da_shape = (true_da.lat.shape[0], true_da.lon.shape[0])
    pred_da_shape = (pred_da.lat.shape[0], pred_da.lon.shape[0])
    assert true_da_shape == pred_da_shape

    r2_vals = 1 - (
        np.nansum((true_da.values - pred_da.values)**2, axis=0)
    ) / (
        np.nansum((true_da.values - np.nanmean(pred_da.values))**2, axis=0)
    )

    da = xr.ones_like(pred_da).isel(time=0)
    da.values = r2_vals

    # reapply the mask
    da = da.where(~get_ds_mask(pred_da))
    return da
