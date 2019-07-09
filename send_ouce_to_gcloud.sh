# send_ouce_to_gcloud.sh
# '2m_temperature'
# 'mean_sea_level_pressure'
# 'sea_surface_temperature'

s5_dir='/lustre/soge1/data/incoming/seas5/1.0x1.0/6-hourly'

for filename in $s5_dir/2m_temperature/*/*.nc; do
    rsync -Pavu -e "ssh -i ~/.ssh/gcloud_drought" $filename  gabrieltseng95@35.202.115.34:ml_drought/data/raw/ouce
done

wait
echo "\n\n------- DONE 2m_temperature -------\n\n"

for filename in $s5_dir/mean_sea_level_pressure/*/*.nc; do
    rsync -Pavu -e "ssh -i ~/.ssh/gcloud_drought" $filename  gabrieltseng95@35.202.115.34:ml_drought/data/raw/ouce
done

wait
echo "\n\n------- DONE mean_sea_level_pressure -------\n\n"

for filename in $s5_dir/sea_surface_temperature/*/*.nc; do
    rsync -Pavu -e "ssh -i ~/.ssh/gcloud_drought" $filename  gabrieltseng95@35.202.115.34:ml_drought/data/raw/ouce
done

wait
echo "\n\n------- DONE sea_surface_temperature -------\n\n"
