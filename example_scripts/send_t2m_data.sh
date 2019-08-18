# send_t2m_data.sh
# /era5_hourly_2m_temperature*.nc
t2m_dir='/ouce-home/data/analysis/era5/0.28125x0.28125/hourly/t2m/nc/'
t2m_dir='/ouce-home/data/analysis/era5/0.28125x0.28125/daily/t2m/nc/'
t2m_dir='/ouce-home/data/analysis/era5/0.28125x0.28125/monthly/t2m/nc/'

for filename in $t2m_dir; do
    rsync -Pavu -e "ssh -i ~/.ssh/gcloud_drought" $filename  gabrieltseng95@35.202.115.34:ml_drought/data/raw/ouce
done

wait
echo "\n\n------- DONE 2m_temperature -------\n\n"
