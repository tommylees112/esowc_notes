# download_cci_landcover.sh
# args:
#     - base_data_dir

base_data_dir=$1
cd $base_data_dir

# wget --header 'Host: data.ceda.ac.uk' --user-agent 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:65.0) Gecko/20100101 Firefox/65.0' --header 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8' --header 'Accept-Language: en-GB,en;q=0.5' --referer 'http://data.ceda.ac.uk/neodc/esacci/land_cover/data/land_cover_maps/v1.6.1/' --header 'Cookie: hs_beacon_shown=1' --header 'Upgrade-Insecure-Requests: 1' 'http://data.ceda.ac.uk/neodc/esacci/land_cover/data/land_cover_maps/v1.6.1/ESACCI-LC-L4-LCCS-Map-300m-P5Y-2005-v1.6.1.nc' --output-document 'ESACCI-LC-L4-LCCS-Map-300m-P5Y-2005-v1.6.1.nc'

# get the legend
# wget --output-document 'ESACCI-LC-Legend.csv' http://data.ceda.ac.uk/neodc/esacci/land_cover/data/land_cover_maps/v1.6.1/ESACCI-LC-Legend.csv

# http://maps.elie.ucl.ac.be/CCI/viewer/download.php
wget ftp://geo10.elie.ucl.ac.be/v207/ESACCI-LC-L4-LCCS-Map-300m-P1Y-2015-v2.0.7b.nc.zip

wget http://maps.elie.ucl.ac.be/CCI/viewer/download/ESACCI-LC-Legend.csv

unzip ESACCI-LC-L4-LCCS-Map-300m-P1Y-2015-v2.0.7b.nc.zip

echo '**** Data Downloaded ****'

# lonmin=32.6
# lonmax=51.8
# latmin=-5.0
# latmax=15.2
# in_file=$base_data_path/ESACCI-LC-L4-LCCS-Map-300m-P5Y-2005-v1.6.1.nc
# mid_file=$base_data_path/ESACCI_LC_L4-Map_300m.nc
# out_file=$base_data_path/EA_ESACCI_LC.nc
#
# # too big to select subset so choose one
# cdo selvar,lccs_class $in_file $mid_fibrele
#
# #
# cdo sellonlatbox,$lonmin,$lonmax,$latmin,$latmax $mid_file $out_file
#
# echo '**** EA Selected and written to $out_file ****'
