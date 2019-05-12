# #! bin/bash
# get_data_witout_year.sh
# bash commands:

# parse command line arguments
new_dir_name="$1"
start_year="$2"
end_year="$3"
variable="$4"
base_data_dir="$5"

echo "-------- get_data_witout_year.sh ----------"
echo "1. ${new_dir_name} - ${start_year} - ${end_year} - ${variable} - ${base_data_dir}"

# START TIME
start_seconds=$(date +%s)

working_dir=/home/mpim/m300690/drought_eda2
output_dir=/scratch/m/m300690/${new_dir_name}

# make the new directory
mkdir -p ${output_dir}

# 1. GET THE DATA INTO ONE PLACE
for year in `seq ${start_year} ${end_year}`; do
# for year in 2000 2001; do

  echo $year" ${variable} data being merged"

  cd $base_data_dir

  cdo -f nc2 mergetime *.nc $output_dir/$variable_$year.nc &

done
wait

# How long did the script take to run?
end_seconds=$(date +%s)
seconds_elapsed=$(($end_seconds - $start_seconds))

echo "${variable} data merged!"
echo "${variable} Merge time taken: "`date -u -d @${seconds_elapsed} +"%T"`
