"""
identify periods when

1. get the climatology (for the time period of interest)
2. calculate thresholds of interest
3. 
"""

import numpy as np
import scipy as sp
from scipy import linalg
from scipy import stats
import scipy.ndimage as ndimage
from datetime import date
from typing import List, Optional, Dict, Tuple


# ------------------------------------------------------------------------------
# MAIN FUNCTION
# ------------------------------------------------------------------------------

def detect(t: np.ndarray,
           temp: np.ndarray,
           climatologyPeriod= [None, None],
           pctile=90,
           windowHalfWidth=5,
           smoothPercentile=True,
           smoothPercentileWidth=31,
           minDuration=5,
           joinAcrossGaps=True,
           maxGap=2,
           maxPadLength=False,
           coldSpells=False,
           alternateClimatology: Optional[List] = False):
    """Hobday et al. (2016) marine heat wave definition

    Arguments:
    ---------

      climatologyPeriod      Period over which climatology is calculated, specified
                             as list of start and end years. Default is to calculate
                             over the full range of years in the supplied time series.
                             Alternate periods suppled as a list e.g. [1983,2012].

      pctile                 Threshold percentile (%) for detection of extreme values
                             (DehEFAULT = 90)

      windowHalfWidth        Width of window (one sided) about day-of-year used for
                             the pooling of values and calculation of threshold percentile
                             (DEFAULT = 5 [days])

      smoothPercentile       Boolean switch indicating whether to smooth the threshold
                             percentile timeseries with a moving average (DEFAULT = True)

      smoothPercentileWidth  Width of moving average window for smoothing threshold
                             (DEFAULT = 31 [days])

      minDuration            Minimum duration for acceptance detected MHWs
                             (DEFAULT = 5 [days])

      joinAcrossGaps         Boolean switch indicating whether to join MHWs
                             which occur before/after a short gap (DEFAULT = True)

      maxGap                 Maximum length of gap allowed for the joining of MHWs
                             (DEFAULT = 2 [days])

      maxPadLength           Specifies the maximum length [days] over which to interpolate
                             (pad) missing data (specified as nans) in input temp time series.
                             i.e., any consecutive blocks of NaNs with length greater
                             than maxPadLength will be left as NaN. Set as an integer.
                             (DEFAULT = False, interpolates over all missing values).

      coldSpells             Specifies if the code should detect cold events instead of
                             heat events. (DEFAULT = False)

      alternateClimatology   Specifies an alternate temperature time series to use for the
                             calculation of the climatology. Format is as a list of numpy
                             arrays: (1) the first element of the list is a time vector,
                             in datetime format (e.g., date(1982,1,1).toordinal())
                             [1D numpy array of length TClim] and (2) the second element of
                             the list is a temperature vector [1D numpy array of length TClim].
                             (DEFAULT = False)

    Notes:
    -----

      1. This function assumes that the input time series consist of continuous daily values
         with few missing values. Time ranges which start and end part-way through the calendar
         year are supported.

      2. This function supports leap years. This is done by ignoring Feb 29s for the initial
         calculation of the climatology and threshold. The value of these for Feb 29 is then
         linearly interpolated from the values for Feb 28 and Mar 1.

      3. The calculation of onset and decline rates assumes that the heat wave started a half-day
         before the start day and ended a half-day after the end-day. (This is consistent with the
         duration definition as implemented, which assumes duration = end day - start day + 1.)

      4. For the purposes of MHW detection, any missing temp values not interpolated over (through
         optional maxPadLLength) will be set equal to the seasonal climatology. This means they will
         trigger the end/start of any adjacent temp values which satisfy the MHW criteria.


    """
    mhw = initialise_output()
    T, year, month, day, doy, month_leapYear, day_leapYear, doy_leapYear, feb28, feb29 = generate_time_vectors(t)

    # Calculate threshold and seasonal climatology (varying with day-of-year)
    climatologyPeriod = set_climatology_period(climatologyPeriod)

    tempClim, TClim, yearClim, monthClim, dayClim, doyClim = initialise_climatology_arrays(
        alternateClimatology, temp, T, year, month,
        day, doy, month_leapYear, day_leapYear, doy_leapYear
    )

    # Flip temp time series if detecting cold spells
    if coldSpells:
        temp = -1.*temp
        tempClim = -1.*tempClim

    # Pad missing values for all consecutive missing blocks of length <= maxPadLength
    if maxPadLength:
        temp = pad(temp, maxPadLength=maxPadLength)
        tempClim = pad(tempClim, maxPadLength=maxPadLength)

    clim_start, clim_end, thresh_climYear, seas_climYear, clim = initialise_climatology_dict(yearClim, climatologyPeriod, lenClimYear, TClim)

    clim = calculate_daily_climatology(
        pctile, windowHalfWidth, lenClimYear, smoothPercentile,
        smoothPercentileWidth, thresh_climYear,  seas_climYear,  clim,
        feb29, doyClim, clim_start, clim_end, tempClim, temp
    )

    temp = fill_missing_temp_vals_with_climatology(temp, clim)

    events, n_events = find_exceedences(temp, clim)
    mhw = find_consecutive_exceedences_above_threshold(events, n_events, mhw, joinAcrossGaps, maxGap)

    mhw = calculate_event_characteristics(mhw, t, clim, temp)
    if coldSpells:
        clim, mhw = flip_for_cold_spells(clim, mhw)


    return mhw, clim


# ------------------------------------------------------------------------------
# SUB FUNCTIONS
# ------------------------------------------------------------------------------


def initialise_output() -> Dict:
    """
    Output Keys:
        'time_start'           Start time of MHW [datetime format]
        'time_end'             End time of MHW [datetime format]
        'time_peak'            Time of MHW peak [datetime format]
        'date_start'           Start date of MHW [datetime format]
        'date_end'             End date of MHW [datetime format]
        'date_peak'            Date of MHW peak [datetime format]
        'index_start'          Start index of MHW
        'index_end'            End index of MHW
        'index_peak'           Index of MHW peak
        'duration'             Duration of MHW [days]
        'intensity_max'        Maximum (peak) intensity [deg. C]
        'intensity_mean'       Mean intensity [deg. C]
        'intensity_var'        Intensity variability [deg. C]
        'intensity_cumulative' Cumulative intensity [deg. C x days]
        'rate_onset'           Onset rate of MHW [deg. C / days]
        'rate_decline'         Decline rate of MHW [deg. C / days]
    """
    mhw = {}
    mhw['time_start'] = [] # datetime format
    mhw['time_end'] = [] # datetime format
    mhw['time_peak'] = [] # datetime format
    mhw['date_start'] = [] # datetime format
    mhw['date_end'] = [] # datetime format
    mhw['date_peak'] = [] # datetime format
    mhw['index_start'] = []
    mhw['index_end'] = []
    mhw['index_peak'] = []
    mhw['duration'] = [] # [days]
    mhw['duration_moderate'] = [] # [days]
    mhw['duration_strong'] = [] # [days]
    mhw['duration_severe'] = [] # [days]
    mhw['duration_extreme'] = [] # [days]
    mhw['intensity_max'] = [] # [deg C]
    mhw['intensity_mean'] = [] # [deg C]
    mhw['intensity_var'] = [] # [deg C]
    mhw['intensity_cumulative'] = [] # [deg C]
    mhw['intensity_max_relThresh'] = [] # [deg C]
    mhw['intensity_mean_relThresh'] = [] # [deg C]
    mhw['intensity_var_relThresh'] = [] # [deg C]
    mhw['intensity_cumulative_relThresh'] = [] # [deg C]
    mhw['intensity_max_abs'] = [] # [deg C]
    mhw['intensity_mean_abs'] = [] # [deg C]
    mhw['intensity_var_abs'] = [] # [deg C]
    mhw['intensity_cumulative_abs'] = [] # [deg C]
    mhw['category'] = []
    mhw['rate_onset'] = [] # [deg C / day]
    mhw['rate_decline'] = [] # [deg C / day]

    return mhw


def generate_time_vectors(t) -> Tuple:
    """Generate vectors for year, month, day-of-month, and day-of-year

    create vectors of length = `len(t)` for DAY, MONTH, YEAR
    """
    T = len(t)
    year = np.zeros((T))
    month = np.zeros((T))
    day = np.zeros((T))
    doy = np.zeros((T))
    for i in range(T):
        year[i] = date.fromordinal(t[i]).year
        month[i] = date.fromordinal(t[i]).month
        day[i] = date.fromordinal(t[i]).day
    # Leap-year baseline for defining day-of-year values
    year_leapYear = 2012 # This year was a leap-year and therefore doy in range of 1 to 366
    t_leapYear = np.arange(date(year_leapYear, 1, 1).toordinal(),date(year_leapYear, 12, 31).toordinal()+1)
    dates_leapYear = [date.fromordinal(tt.astype(int)) for tt in t_leapYear]
    month_leapYear = np.zeros((len(t_leapYear)))
    day_leapYear = np.zeros((len(t_leapYear)))
    doy_leapYear = np.zeros((len(t_leapYear)))
    for tt in range(len(t_leapYear)):
        month_leapYear[tt] = date.fromordinal(t_leapYear[tt]).month
        day_leapYear[tt] = date.fromordinal(t_leapYear[tt]).day
        doy_leapYear[tt] = t_leapYear[tt] - date(date.fromordinal(t_leapYear[tt]).year,1,1).toordinal() + 1
    # Calculate day-of-year values
    for tt in range(T):
        doy[tt] = doy_leapYear[(month_leapYear == month[tt]) * (day_leapYear == day[tt])]

    # Constants (doy values for Feb-28 and Feb-29) for handling leap-years
    feb28 = 59
    feb29 = 60

    return  (
        T, year, month, day, doy,
        month_leapYear, day_leapYear, doy_leapYear,
        feb28, feb29
    )

def set_climatology_period(climatologyPeriod: List) -> List:
    # Set climatology period, if unset use full range of available data
    if (climatologyPeriod[0] is None) or (climatologyPeriod[1] is None):
        climatologyPeriod[0] = year[0]
        climatologyPeriod[1] = year[-1]

    return climatologyPeriod


def initialise_climatology_arrays(alternateClimatology: bool,
                          temp: List,
                          T: List,
                          year,
                          month,
                          day,
                          doy,
                          month_leapYear: Optional,
                          day_leapYear: Optional,
                          doy_leapYear: Optional,):
    """Initialise the climatology vectors:
        tempClim, TClim, yearClim, monthClim, dayClim, doyClim
        with either
    """
    # if alternate temperature time series is supplied for the calculation of the climatology
    if alternateClimatology:
        tClim = alternateClimatology[0]
        tempClim = alternateClimatology[1]
        TClim = len(tClim)
        yearClim = np.zeros((TClim))
        monthClim = np.zeros((TClim))
        dayClim = np.zeros((TClim))
        doyClim = np.zeros((TClim))
        for i in range(TClim):
            yearClim[i] = date.fromordinal(tClim[i]).year
            monthClim[i] = date.fromordinal(tClim[i]).month
            dayClim[i] = date.fromordinal(tClim[i]).day
            doyClim[i] = doy_leapYear[(month_leapYear == monthClim[i]) * (day_leapYear == dayClim[i])]

    else:
        tempClim = temp.copy()
        TClim = np.array([T]).copy()[0]
        yearClim = year.copy()
        monthClim = month.copy()
        dayClim = day.copy()
        doyClim = doy.copy()

    return tempClim, TClim, yearClim, monthClim, dayClim, doyClim


def initialise_climatology_dict(yearClim, climatologyPeriod, lenClimYear, TClim):
    # Length of climatological year
    lenClimYear = 366

    # Start and end indices for calculation of climatology
    clim_start = np.where(yearClim == climatologyPeriod[0])[0][0]
    clim_end = np.where(yearClim == climatologyPeriod[1])[0][-1]

    # Inialize arrays for DAILY climatology (len==366)
    thresh_climYear = np.NaN*np.zeros(lenClimYear)
    seas_climYear = np.NaN*np.zeros(lenClimYear)
    clim = {}
    clim['thresh'] = np.NaN*np.zeros(TClim)
    clim['seas'] = np.NaN*np.zeros(TClim)


    return clim_start, clim_end, thresh_climYear, seas_climYear, clim


def calculate_daily_climatology(pctile,
                                windowHalfWidth,
                                lenClimYear,
                                smoothPercentile,
                                smoothPercentileWidth,
                                thresh_climYear,  # empty array
                                seas_climYear,  # empty array
                                clim,  # empty dict
                                feb29,
                                doyClim,
                                clim_start,
                                clim_end,
                                tempClim,
                                temp):
    """Calculate the climatology (mean) for each day and threshold (90pctile)

    Arguments:
    ---------
      pctile                 Threshold percentile (%) for detection of extreme values
                             (DehEFAULT = 90)

      windowHalfWidth        Width of window (one sided) about day-of-year used for
                             the pooling of values and calculation of threshold percentile
                             (DEFAULT = 5 [days])

      smoothPercentile       Boolean switch indicating whether to smooth the threshold
                             percentile timeseries with a moving average (DEFAULT = True)

      smoothPercentileWidth  Width of moving average window for smoothing threshold
                             (DEFAULT = 31 [days])

    """
    # Loop over all day-of-year values, and calculate threshold and seasonal climatology across years
    for d in range(1, lenClimYear + 1):
        # Special case for Feb 29
        if d == feb29:
            continue
        # find all indices for each day of the year +/- windowHalfWidth and from them calculate the threshold
        tt0 = np.where(doyClim[clim_start:clim_end+1] == d)[0]  # the index for that day each year
        # If this doy value does not exist (i.e. in 360-day calendars) then skip it
        if len(tt0) == 0:
            continue
        tt = np.array([])
        for w in range(-windowHalfWidth, windowHalfWidth+1):  # -5 : 5 default
            tt = np.append(tt, clim_start + tt0 + w)  # append the daily values 5days before and 5days after
        tt = tt[tt>=0] # Reject indices "before" the first element
        tt = tt[tt<TClim] # Reject indices "after" the last element
        thresh_climYear[d-1] = np.percentile(nonans(tempClim[tt.astype(int)]), pctile)
        seas_climYear[d-1] = np.mean(nonans(tempClim[tt.astype(int)]))

    # Special case for Feb 29 (LEAP YEAR)
    thresh_climYear[feb29-1] = 0.5*thresh_climYear[feb29-2] + 0.5*thresh_climYear[feb29]
    seas_climYear[feb29-1] = 0.5*seas_climYear[feb29-2] + 0.5*seas_climYear[feb29]

    if smoothPercentile:
        thresh_climYear, seas_climYear = smooth_climatologies(thresh_climYear, seas_climYear, smoothPercentileWidth)

    # Generate threshold for full time series
    clim["thresh"] = thresh_climYear[doy.astype(int) - 1]
    clim["seas"] = seas_climYear[doy.astype(int) - 1]
    # Save vector indicating which points in temp are missing values
    clim["missing"] = np.isnan(temp)

    return clim


def smooth_climatologies(thresh_climYear, seas_climYear, smoothPercentileWidth):
    """Calculate a smoothed time series.
    Uses a running average of an input time series using uniform window.
    """
    # If the climatology contains NaNs, then assume it is a <365-day year and deal accordingly
    if np.sum(np.isnan(seas_climYear)) + np.sum(np.isnan(thresh_climYear)):
        valid = ~np.isnan(thresh_climYear)
        thresh_climYear[valid] = runavg(
            thresh_climYear[valid], smoothPercentileWidth
        )
        valid = ~np.isnan(seas_climYear)
        seas_climYear[valid] = runavg(seas_climYear[valid], smoothPercentileWidth)
    else:  # >= 365-day year (no nans)
        thresh_climYear = runavg(thresh_climYear, smoothPercentileWidth)
        seas_climYear = runavg(seas_climYear, smoothPercentileWidth)

    return thresh_climYear, seas_climYear



def fill_missing_temp_vals_with_climatology(temp: List, clim: Dict):
    """Set all remaining missing temp values equal to the climatology """
    temp[np.isnan(temp)] = clim["seas"][np.isnan(temp)]

    return temp


def find_exceedences(temp, clim):
    """Calculate a time series of "True" when threshold is exceeded, "False" otherwise

    NOTE: WHY is exceed bool different from events?
    """
    exceed_bool = temp - clim["thresh"]
    exceed_bool[exceed_bool <= 0] = False
    exceed_bool[exceed_bool > 0] = True

    # Find contiguous regions of exceed_bool = True
    events, n_events = ndimage.label(exceed_bool)
    return events, n_events


def find_consecutive_exceedences_above_threshold(events, n_events, mhw, joinAcrossGaps, maxGap):
    """Find all MHW events of duration >= minDuration
    Updates the mhw dictionary object.
    """
    for ev in range(1, n_events + 1):  # for each event
        event_duration = (events == ev).sum()
        if event_duration < minDuration:  # is it longer than threshold?
            continue
        # extract the t where event starts and ends
        mhw["time_start"].append(t[np.where(events == ev)[0][0]])
        mhw["time_end"].append(t[np.where(events == ev)[0][-1]])

    # Link heat waves that occur before and after a short gap
    if joinAcrossGaps:
        mhw = join_events_across_gaps(maxGap, mhw)



    return mhw


def join_events_across_gaps(maxGap, mhw):
    """Link heat waves that occur before and after a short gap
    (gap must be no longer than maxGap)
    """
    # Calculate gap length for each consecutive pair of events
    # from the start of the NEXT EVENT to the end of the PRIOR EVENT
    gaps = np.array(mhw["time_start"][1:]) - np.array(mhw["time_end"][0:-1]) - 1
    if len(gaps) > 0:
        while gaps.min() <= maxGap:
            # Find first short gap
            ev = np.where(gaps <= maxGap)[0][0]
            # Extend first MHW to encompass second MHW (including gap)
            mhw["time_end"][ev] = mhw["time_end"][ev + 1]
            # Remove second event from record
            del mhw["time_start"][ev + 1]
            del mhw["time_end"][ev + 1]
            # Calculate gap length for each consecutive pair of events
            gaps = (
                np.array(mhw["time_start"][1:])
                - np.array(mhw["time_end"][0:-1])
                - 1
            )
            if len(gaps) == 0:
                break
    return mhw


def calculate_event_characteristics(mhw, t, clim, temp):
    """Calculate marine heat wave properties """
    mhw["n_events"] = len(mhw["time_start"])

    # for each event caclulate the characteristics
    for ev in range(mhw["n_events"]):
        mhw["date_start"].append(date.fromordinal(mhw["time_start"][ev]))
        mhw["date_end"].append(date.fromordinal(mhw["time_end"][ev]))

        # get the start/end indices
        tt_start = np.where(t == mhw["time_start"][ev])[0][0]
        tt_end = np.where(t == mhw["time_end"][ev])[0][0]
        mhw["index_start"].append(tt_start)
        mhw["index_end"].append(tt_end)

        # extract the data (temp, threshold, seasonality) for that event
        temp_mhw = temp[tt_start : tt_end + 1]
        thresh_mhw = clim["thresh"][tt_start : tt_end + 1]
        seas_mhw = clim["seas"][tt_start : tt_end + 1]

        # what are the relative differences (from thresholds) / absolute values
        mhw_relSeas = temp_mhw - seas_mhw
        mhw_relThresh = temp_mhw - thresh_mhw
        mhw_relThreshNorm = (temp_mhw - thresh_mhw) / (thresh_mhw - seas_mhw)
        mhw_abs = temp_mhw

        # Find peak
        mhw, tt_peak = find_peak(mhw, mhw_relSeas, ev, tt_start)

        # MHW Duration
        mhw["duration"].append(len(mhw_relSeas))

        # MHW Intensity metrics
        mhw["intensity_max"].append(mhw_relSeas[tt_peak])
        mhw["intensity_mean"].append(mhw_relSeas.mean())
        mhw["intensity_var"].append(np.sqrt(mhw_relSeas.var()))
        mhw["intensity_cumulative"].append(mhw_relSeas.sum())
        mhw["intensity_max_relThresh"].append(mhw_relThresh[tt_peak])
        mhw["intensity_mean_relThresh"].append(mhw_relThresh.mean())
        mhw["intensity_var_relThresh"].append(np.sqrt(mhw_relThresh.var()))
        mhw["intensity_cumulative_relThresh"].append(mhw_relThresh.sum())
        mhw["intensity_max_abs"].append(mhw_abs[tt_peak])
        mhw["intensity_mean_abs"].append(mhw_abs.mean())
        mhw["intensity_var_abs"].append(np.sqrt(mhw_abs.var()))
        mhw["intensity_cumulative_abs"].append(mhw_abs.sum())

        # Fix categories
        mhw = set_categories(mhw, mhw_relThreshNorm)

        # Rates of onset and decline
        mhw = rates_of_onset_and_decline(
            mhw, tt_start, tt_end, tt_peak, mhw_relSeas,
            temp, clim
        )

    return mhw


def find_peak(mhw, mhw_relSeas, ev, tt_start):
    """find the peak time for that event (INTENSITY)"""
    tt_peak = np.argmax(mhw_relSeas)
    mhw["time_peak"].append(mhw["time_start"][ev] + tt_peak)
    mhw["date_peak"].append(date.fromordinal(mhw["time_start"][ev] + tt_peak))
    mhw["index_peak"].append(tt_start + tt_peak)

    return mhw, tt_peak


def set_categories(mhw, mhw_relThreshNorm):
    """Assign categories"""
    categories = np.array(["Moderate", "Strong", "Severe", "Extreme"])

    tt_peakCat = np.argmax(mhw_relThreshNorm)
    cats = np.floor(1.0 + mhw_relThreshNorm)
    mhw["category"].append(
        categories[np.min([cats[tt_peakCat], 4]).astype(int) - 1]
    )
    mhw["duration_moderate"].append(np.sum(cats == 1.0))
    mhw["duration_strong"].append(np.sum(cats == 2.0))
    mhw["duration_severe"].append(np.sum(cats == 3.0))
    mhw["duration_extreme"].append(np.sum(cats >= 4.0))

    return mhw


def rates_of_onset_and_decline(mhw,
                               tt_start,
                               tt_end,
                               tt_peak,
                               mhw_relSeas,
                               temp,
                               clim,):
    """
    Requires getting MHW strength at "start" and "end"
     of event (continuous: assume start/end half-day
     before/after first/last point).
    """
    ## For START of event
    if tt_start > 0:
        mhw_relSeas_start = 0.5 * (
            mhw_relSeas[0] + temp[tt_start - 1] - clim["seas"][tt_start - 1]
        )
        mhw["rate_onset"].append(
            (mhw_relSeas[tt_peak] - mhw_relSeas_start) / (tt_peak + 0.5)
        )
    else:  # MHW starts at beginning of time series
        if (
            tt_peak == 0
        ):  # Peak is also at begining of time series, assume onset time = 1 day
            mhw["rate_onset"].append((mhw_relSeas[tt_peak] - mhw_relSeas[0]) / 1.0)
        else:
            mhw["rate_onset"].append(
                (mhw_relSeas[tt_peak] - mhw_relSeas[0]) / tt_peak
            )

    ## For END of event
    if tt_end < T - 1:
        mhw_relSeas_end = 0.5 * (
            mhw_relSeas[-1] + temp[tt_end + 1] - clim["seas"][tt_end + 1]
        )
        mhw["rate_decline"].append(
            (mhw_relSeas[tt_peak] - mhw_relSeas_end)
            / (tt_end - tt_start - tt_peak + 0.5)
        )
    else:  # MHW finishes at end of time series
        if (
            tt_peak == T - 1
        ):  # Peak is also at end of time series, assume decline time = 1 day
            mhw["rate_decline"].append(
                (mhw_relSeas[tt_peak] - mhw_relSeas[-1]) / 1.0
            )
        else:
            mhw["rate_decline"].append(
                (mhw_relSeas[tt_peak] - mhw_relSeas[-1])
                / (tt_end - tt_start - tt_peak)
            )

    return mhw


def flip_for_cold_spells(clim, mhw):
    clim["seas"] = -1.0 * clim["seas"]
    clim["thresh"] = -1.0 * clim["thresh"]
    for ev in range(len(mhw["intensity_max"])):
        mhw["intensity_max"][ev] = -1.0 * mhw["intensity_max"][ev]
        mhw["intensity_mean"][ev] = -1.0 * mhw["intensity_mean"][ev]
        mhw["intensity_cumulative"][ev] = -1.0 * mhw["intensity_cumulative"][ev]
        mhw["intensity_max_relThresh"][ev] = (
            -1.0 * mhw["intensity_max_relThresh"][ev]
        )
        mhw["intensity_mean_relThresh"][ev] = (
            -1.0 * mhw["intensity_mean_relThresh"][ev]
        )
        mhw["intensity_cumulative_relThresh"][ev] = (
            -1.0 * mhw["intensity_cumulative_relThresh"][ev]
        )
        mhw["intensity_max_abs"][ev] = -1.0 * mhw["intensity_max_abs"][ev]
        mhw["intensity_mean_abs"][ev] = -1.0 * mhw["intensity_mean_abs"][ev]
        mhw["intensity_cumulative_abs"][ev] = (
            -1.0 * mhw["intensity_cumulative_abs"][ev]
        )

    return clim, mhw


# ------------------------------------------------------------------------------
# UTILS
# ------------------------------------------------------------------------------


def nonans(array):
    """
    Return input array [1D numpy array] with
    all nan values removed
    """
    return array[~np.isnan(array)]


def pad(data, maxPadLength=False):
    """
    Linearly interpolate over missing data (NaNs) in a time series.

    Inputs:

      data	     Time series [1D numpy array]
      maxPadLength   Specifies the maximum length over which to interpolate,
                     i.e., any consecutive blocks of NaNs with length greater
                     than maxPadLength will be left as NaN. Set as an integer.
                     maxPadLength=False (default) interpolates over all NaNs.

    Written by Eric Oliver, Institue for Marine and Antarctic Studies, University of Tasmania, Jun 2015

    """
    data_padded = data.copy()
    bad_indexes = np.isnan(data)
    good_indexes = np.logical_not(bad_indexes)
    good_data = data[good_indexes]
    interpolated = np.interp(
        bad_indexes.nonzero()[0], good_indexes.nonzero()[0], good_data
    )
    data_padded[bad_indexes] = interpolated
    if maxPadLength:
        blocks, n_blocks = ndimage.label(np.isnan(data))
        for bl in range(1, n_blocks + 1):
            # if greater than max pad length then keep as nan
            # i.e. don't interpolate over too large a range
            if (blocks == bl).sum() > maxPadLength:
                data_padded[blocks == bl] = np.nan

    return data_padded


def runavg(ts, w):
    """

    Performs a running average of an input time series using uniform window
    of width w. This function assumes that the input time series is periodic.

    Inputs:

      ts            Time series [1D numpy array]
      w             Integer length (must be odd) of running average window

    Outputs:

      ts_smooth     Smoothed time series

    Written by Eric Oliver, Institue for Marine and Antarctic Studies, University of Tasmania, Feb-Mar 2015

    """
    # Original length of ts
    N = len(ts)
    # make ts three-fold periodic
    ts = np.append(ts, np.append(ts, ts))
    # smooth by convolution with a window of equal weights
    ts_smooth = np.convolve(ts, np.ones(w) / w, mode="same")
    # Only output central section, of length equal to the original length of ts
    ts = ts_smooth[N : 2 * N]

    return ts


# ------------------------------------------------------------------------------
# TEST CODE
# ------------------------------------------------------------------------------
# import matplotlib.pyplot as plt
#
# # default arguments
# climatologyPeriod= [None, None]
# pctile=90
# windowHalfWidth=5
# smoothPercentile=True
# smoothPercentileWidth=31
# minDuration=5
# joinAcrossGaps=True
# maxGap=2
# maxPadLength=False
# coldSpells=False
# alternateClimatology=False
#
#
# # Generate time vector using datetime format (January 1 of year 1 is day 1)
# t = np.arange(date(1982,1,1).toordinal(),date(2014,12,31).toordinal()+1)
# dates = [date.fromordinal(tt.astype(int)) for tt in t]
#
# # Generate synthetic temperature time series
# sst = np.zeros(len(t))
# sst[0] = 0 # Initial condition
# a = 0.85 # autoregressive parameter
# for i in range(1,len(t)):
#     sst[i] = a*sst[i-1] + 0.75*np.random.randn() + 0.5*np.cos(t[i]*2*np.pi/365.25)
# sst = sst - sst.min() + 5.
#
#
#
#
#
# plt.plot([_ for _ in range(len(thresh_climYear[valid]))], thresh_climYear[valid])
# plt.plot([_ for _ in range(len(thresh_climYear[valid]))], runavg(thresh_climYear[valid], smoothPercentileWidth))
#
#
# def find_window_of_events(events: List, event: int, window: int, exceed_bool: List[bool]):
#     """ Return the index of events """
#     ixs = np.where(events==event)[0]
#     min_ix, max_ix = ixs.min(), ixs.max()
#     bools = exceed_bool[min_ix - window : max_ix + 1 + window]
#
#     return ixs, bools

detect(t,sst)
