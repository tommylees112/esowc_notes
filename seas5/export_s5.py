from pathlib import Path

import sys
sys.path.append('..')
from src.exporters import S5Exporter


def export_s5():
    # if the working directory is alread ml_drought don't need ../data
    if Path('.').absolute().as_posix().split('/')[-1] == 'ml_drought':
        data_path = Path('data')
    else:
        data_path = Path('../data')

    granularity = 'monthly'
    pressure_level = False

    exporter = S5Exporter(
        data_folder=data_path,
        granularity=granularity,
        pressure_level=pressure_level,
    )
    variables = ['total_precipitation', '2m_temperature', 'evaporation']
    min_year = 1993
    max_year = 2019
    min_month = 1
    max_month = 12
    max_leadtime = None
    pressure_levels = None
    n_parallel_requests = 1

    for variable in variables:
        print(f"\n\nWORKING ON: {variable}\n\n")
        exporter.export(
            variable=variable,
            min_year=min_year,
            max_year=max_year,
            min_month=min_month,
            max_month=max_month,
            max_leadtime=max_leadtime,
            pressure_levels=pressure_levels,
            n_parallel_requests=n_parallel_requests,
            break_up=False
        )


if __name__ == '__main__':
    export_s5()