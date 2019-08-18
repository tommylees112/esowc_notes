for filename in data/raw/reanalysis-era5-single-levels/total_precipitation/*/*.nc; do
    echo $filename
    year=$(echo $filename| cut -d'/' -f 5)
    echo "${}"
done

PYTHON:
------
'''
fps = p.get_filepaths(p.raw_folder, variable='total_precipitation')
years = [f.parents[0].name for f in fps]

dsts = [f.parent / (years[ix] + "_" + f.name)
    for ix, f in enumerate(fps)
]

from shutil import move
[move(src, dsts[ix]) for ix, src in enumerate(fps)]

'''
