# send_dummy_era5.sh
era5_dir='/soge-home/projects/crop_yield/ml_drought/data/raw/reanalysis-era5-single-levels'

for filename in $era5_dir; do
    rsync -Pavu -e "ssh -i ~/.ssh/gcloud_drought" $filename  gabrieltseng95@35.202.115.34:ml_drought/data/raw/
done

wait
echo "\n\n------- DONE ERA5 Data -------\n\n"
