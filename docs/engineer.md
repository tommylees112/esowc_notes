```python

@staticmethod
def stratify_xy(ds: xr.Dataset,
                year: int,
                target_variable: str,
                target_month: int,
                pred_months: int,
                expected_length: Optional[int],
                ) -> Tuple[Optional[Dict[str, xr.Dataset]], date]:

```

Returns
- a dict with two `xarray.Dataset` objects. An `x` object, and a `y` object.
- a datetime object of the minimum test date (how many months before?)

```python
max_date = date(year, target_month, calendar.monthrange(year, target_month)[-1])
```
- get the date of the final day of the month for that month


```python
# from src/utils.py
def minus_months(cur_year: int, cur_month: int, diff_months: int,
                 to_endmonth_datetime: bool = True) -> Tuple[int, int, Optional[date]]:
    """Given a year-month pair (e.g. 2018, 1), and a number of months subtracted
    from that  (e.g. 2), return the new year-month pair (e.g. 2017, 11).

    Optionally, a date object representing the end of that month can be returned too
    """

    new_month = cur_month - diff_months
    if new_month < 1:
        new_month += 12
        new_year = cur_year - 1
    else:
        new_year = cur_year

    if to_endmonth_datetime:
        newdate: Optional[date] = date(new_year, new_month,
                                       calendar.monthrange(new_year, new_month)[-1])
    else:
        newdate = None
    return new_year, new_month, newdate

mx_year, mx_month, max_train_date = minus_months(year, target_month, diff_months=1)
_, _, min_date = minus_months(mx_year, mx_month, diff_months=pred_months)
```
- Get the max training months (t-1) for that target month/year
- get the minimum training months (t-n) for that target month/year


```python
#
```
- each iteration count down one month (02 -> 01 -> 12 ...)
-  because the `y` month becomes the `cur_pred_month` and `x`
-  becomes the month before `cur_pred_month`
```python
#
```

```python
#
```
