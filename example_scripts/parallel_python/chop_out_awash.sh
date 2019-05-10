#! bin/bash
# chop_out_awash.sh

new_dir_name="$1"
start_year="$2"
end_year="$3"
variable="$4"
base_data_dir="$5"

echo "-------- chop_out_awash.sh ----------"
echo "2. ${new_dir_name} - ${start_year} - ${end_year} - ${variable} - ${base_data_dir}"

# START TIME
start_seconds=$(date +%s)

working_dir=/home/mpim/m300690/drought_eda2
output_dir=/scratch/m/m300690/${new_dir_name}

# ------------------------------------------------------------------------------

mkdir -p $output_dir
for year in `seq $start_year $end_year`; do

  # for each year chop out the AWASH/EAST AFRICA and put into SCRATCH file
  cdo sellonlatbox,35,46,5,15 $base_data_dir/Ep_${year}_GLEAM_v3.1a.nc $output_dir/pet_awash_$year.nc &

done
wait

# ------------------------------------------------------------------------------

# How long did the script take to run?
end_seconds=$(date +%s)
seconds_elapsed=$(($end_seconds - $start_seconds))

echo "${variable} East Africa Chopped!!"
echo "${variable} Chop time taken: "`date -u -d @${seconds_elapsed} +"%T"`
