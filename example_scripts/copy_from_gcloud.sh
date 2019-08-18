# copy_from_gcloud.sh

rsync -Pavu -e "ssh -i ~/.ssh/gcloud_drought" gabrieltseng95@35.202.115.34:ml_drought/data/interim/* .
