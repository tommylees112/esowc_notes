# bash script to download the natural earth countries shapefile
# https://www.naturalearthdata.com/downloads/50m-cultural-vectors/

cd data

# wget the online file to countries_shp.zip
wget -O countries_shp.zip https://www.naturalearthdata.com/http//www.naturalearthdata.com/download/50m/cultural/ne_50m_admin_0_countries.zip

mkdir -p countries_shp
cd countries_shp

# unzip the different files into the data directory
unzip ../countries_shp.zip
