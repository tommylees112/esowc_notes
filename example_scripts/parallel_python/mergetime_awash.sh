#! bin/bash
# bash mergetime.sh &

new_dir_name="$1"
start_year="$2"
end_year="$3"
variable="$4"
base_data_dir="$5"

echo "-------- mergetime.sh ----------"
echo "3. ${new_dir_name} - ${start_year} - ${end_year} - ${variable} - ${base_data_dir}"

# START TIME
start_seconds=$(date +%s)

working_dir=/home/mpim/m300690/drought_eda2
output_dir=/scratch/m/m300690/${new_dir_name}

# ------------------------------------------------------------------------------

final_data=/scratch/m/m300690/EA_data/

mkdir -p $final_data

cdo -f nc2 mergetime ${output_dir}/pet_awash_*.nc $final_data/awash_GLEAM_pet.nc

# ------------------------------------------------------------------------------

# How long did the script take to run?
end_seconds=$(date +%s)
seconds_elapsed=$(($end_seconds - $start_seconds))

echo "${variable} data merged!"
echo "${variable} Merge time taken: "`date -u -d @${seconds_elapsed} +"%T"`
