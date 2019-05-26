# to be sourced from various scripts
# my database of field info, listing GrADS .ctl file or netCDF file,
# full name, and special mappings or colour properties.
file=""
LSMASK=""
flipcolor=0
if [ -z "$FORM_field" ]; then
  echo;echo "Please select a field"
  exit
fi
if [ "$EMAIL" = ec8907341dfc63c526d08e36d06b7ed8 ]; then
    lwrite=false # true
fi
if [ "$lwrite" = true ]; then
    echo "queryfield: FORM_field=$FORM_field<br>"
fi
if [ ${FORM_field#Rapid} != $FORM_field ]; then
    # Gerard's data
    [ "$lwrite" = true ] && echo "queryfield.cgi: calling queryfield_rapid.cgi<br>"
    . ./queryfield_rapid.cgi
else
[ "$lwrite" = true ] && echo "queryfield.cgi: entering case switch with FORM_field=$FORM_field<br>"
NPERYEAR=12 # default

case $FORM_field in

knmi14pcglob*)
    field=$FORM_field
    dataset=${field%%_*}
    field=${field#*_}
    var=${field%%_*}
    field=${field#*_}
    type=${field%%_*}
    field=${field#*_}
    model=${field%%_*}
    scen=${field#*_}
    if [ $var = evappot ]; then
        file=UUData/$var/${var}_d_ECEarth_RCP85_s%%_mo.nc
    else
        file=UUData/$var/${var}_${type}_${model}_${scen}_%%.nc
    fi
    LSMASK=UUData/lsmask.nc
    ;;

cmip5*|thor*|knmi14*|eucleia*|futureweather*|hiwaves*) # expecting cmip5_var_Amon_model_exp
    field=$FORM_field
    dataset=${field%%_*}
    field=${field#*_}
    var=${field%%_*}
    field=${field#*_}
    type=${field%%_*}
    field=${field#*_}
    model=${field%%_*}
    field=${field#*_}
    if [ ${field#p?_} != $field ]; then
        physics=${field%%_*}
        model=${model}_${physics}
        field=${field#*_}
    fi
    if [ ${field#decadal} != $field ]; then
       exp=${field%%_*}
       field=${field#*_}
       lead=${field%%_*}
       field=${field#*_}
       ip=${field%%_*}
       field=${field#*_}
       ensave=$field
    elif [ ${field%_*} = $field ]; then
       exp=$field
       rip=""
    else
       exp=${field%_*}
       rip=${field#*_}
       if [ $rip = 144 ]; then # special case
          rip=ave_144
       fi
       if [ $rip = 288 ]; then # special case
          rip=ave_288
       fi
    fi
    [ "$lwrite" = true ] && echo "dataset=$dataset var=$var type=$type model=$model exp=$exp rip=$rip lead=$lead ip=$ip ensave=$ensave<br>"
    alttype=$type
    if [ "${type%mon}" != "$type" ]; then
        if [ $dataset = knmi14 ]; then
            dir=mon/atmos
            type=Amon
        else
            dir=monthly
        fi
        NPERYEAR=12
    elif [ "${type%day}" != "$type" ]; then
        if [ $dataset = knmi14 ]; then
            dir=day/atmos
            type=day
            export splitfield=true
        elif [ $dataset = eucleia ]; then
            dir=day
            type=day
            export splitfield=true
        else
            dir=daily
        fi
        if [ ${model#Had} != ${model} ]; then
            NPERYEAR=360
        else
            NPERYEAR=366
        fi
    elif [ $type = yr ]; then
        dir=annual
        NPERYEAR=1
        alttype=year
    else
       echo "$0: cannot handle type $type yet"
       exit -1
    fi
    case $dataset in
         cmip5) datasetname=CMIP5;decdir=CMIP5/decadal;;
         thor) datasetname=THOR;decdir=THOR;;
         knmi14) datasetname=KNMI14;;
         eucleia) datasetname=EUCLEIA;;
         futureweather) datasetname=FutureWeather;;
         hiwaves3) datasetname=HIWAVES3;;
         *) echo "unknown dataset $dataset"; exit -1;;
    esac
    if [ $var = pr -o $var = pme -o $var = huss -o $var = hurs -o \
         $var = tp ]; then
        flipcolor=11
    fi
    if [ $exp = decadal ]; then
           if [ $model = modmean -o $model = mod -o $model = ens ]; then
          if [ $ip = i0p1 ]; then
             file=$decdir/${var}_${type}_${model}0_yr${lead}_%%.nc
          elif [ $ip = i1p1 ]; then
             file=$decdir/${var}_${type}_${model}_yr${lead}_%%.nc
          else
             exit -1
          fi
       elif [ $ensave = ens ]; then
          file=$decdir/${var}_${type}_${model}_yr${lead}_${ip}_%%.nc
       else
          file=$decdir/${var}_${type}_${model}_yr${lead}_${ip}_ave.nc
       fi
    else
        if [ $dataset = knmi14 ]; then
            if [ $model = RACMO22E ]; then
                period=1950-2100
                file=${var}_WEU-11i_KNMI-EC-EARTH_historical-${exp}_KNMI-${model}_v1_${alttype#A}_${period}_%%.nc
                file=KNMI14Data/CMIP5/output/KNMI/$model/$exp/$dir/$var/$file
                LSMASK=KNMI14Data/CMIP5/output/KNMI/RACMO22E/rcp85/fixed/sftlf_WEU-11_KNMI-EC-EARTH_historical_r0i0p0_KNMI-RACMO22E_v1_fx_latlon.nc
            else
                if [ "$splitfield" = true ]; then
                    file=${var}_${type}_${model}_${exp}_????????-????????_%%.nc
                else
                    file=${var}_${type}_${model}_${exp}_186001-210012_%%.nc
                fi
                file=KNMI14Data/CMIP5/output/KNMI/$model/$exp/$dir/$type/$var/$file
            fi
            ###echo "file=$file"
        elif [ $dataset = futureweather ]; then
            period=$exp
            exp=FutureWeather
            if [ $period = alldays ]; then
                export splitfield=true
                period='????????-????????'
            elif [ $period = allmonths ]; then
                export splitfield=true
                period='??????-??????'
            else
                type=yr
                NPERYEAR=1
            fi
            if [ "$splitfield" = true ]; then
                file=${var}_${type}_${model}_${exp}_${period}_%%%.nc
            else
                file=${var}_${type}_${model}_${exp}_%%%.nc
            fi
            file=ECEARTH23/FutureWeather/${type#A}/$var/$file
            LSMASK=ECEARTH23/FutureWeather/fixed/lsmask_ecearth23_t799.nc
            ###echo "file=$file"
        elif [ $dataset = hiwaves3 ]; then
            ###[ $type == Aday ] && export splitfield=true
            file=${var}_${type}_${model}_${exp}_%%%.nc
            file=HIWAVES3/${type}/$var/$file
            ###echo "file=$file"
            LSMASK=KNMI14Data/sftlf_ns.nc
        elif [ $dataset = eucleia ]; then
            if [ "$splitfield" = true ]; then
                file=${var}_${type}_${model}_${exp}_????????-????????_%%%.nc
            else
                file=${var}_${type}_${model}_${exp}_%%%.nc
            fi
            file=EUCLEIA/${model}/$dir/$var/$file
            ###echo "file=$file"
        elif [ -z "$rip" ]; then
            file=CMIP5/$dir/$var/${var}_${type}_${model}_${exp}_000.nc
            if [ -e $file -o -L $file ]; then
                file=CMIP5/$dir/$var/${var}_${type}_${model}_${exp}_%%%.nc
            else
                oldfile=$file
                file=CMIP5/$dir/$var/${var}_${type}_${model}_${exp}_00.nc
                if [ -e $file -o -L $file ]; then
                    file=CMIP5/$dir/$var/${var}_${type}_${model}_${exp}_%%.nc
                else
                    echo "queryfield: error: cannot locate CMIP5 file $oldfile or $file"
                    exit -1
                fi
            fi
        else
            file=CMIP5/$dir/$var/${var}_${type}_${model}_${exp}_${rip}.nc
        fi
    fi
    ###echo "file=$file<br>"
    if [ $exp = decadal ]; then
       if [ $ip = i1p1 ]; then
          kindname="$model $dataset $exp yr$lead $ensave"
       elif [ $ip = i0p1 ]; then
          kindname="$model no-assim $exp yr$lead $ensave"
       else
          kindname="$model $ip $exp yr$lead $ensave"
       fi
    elif [ "${model#mod}" != $model -o $model = ens -o $model = one ]; then
       if [ 0 = 1 ]; then # use date of file
          ensfile=`echo $file | tr '%' '0'`
          if [ `uname` = Darwin ]; then
             datum=`stat -t '%Y%m%d' -f '%Sm' $ensfile`
          else
             datum=`stat --printf="%y" $ensfile | cut -d ' ' -f 1`
          fi
          kindname="${model}_$datum $exp"
       else # use number of models
          modname=`echo $file | sed -e 's/modmean/mod/' -e 's/%%%/???/' -e 's/%%/??/'`
          ###echo "modname=$modname<br>"
          nmod=`echo $modname | wc -w | tr -d ' '`
          kindname="${model}$nmod $exp"
       fi
       # first rough approximation
       if [ $var = sic -o $var = tos -o $var = sos ]; then
          LSMASK=CMIP5/monthly/lsmask_cmip3_288.nc
       else
          LSMASK=CMIP5/monthly/lsmask_cmip3_144.nc
       fi
    else
       kindname="$model $exp"
       if [ -z "$LSMASK" ]; then
           if [ $type = Amon -o $type = Lmon -o $type = day ]; then
               case $model in
                    HadGEM3-A-N216) trylsmask=EUCLEIA/HadGEM3-A-N216/fx/sftlf_fx_HadGEM3-A-N216_historical_r0i0p0.nc;;
                    ECEARTH23) trylsmask=KNMI14Data/sftlf_ns.nc;;
                    EC-EARTH) trylsmask=CMIP5/monthly/sftlf.nc;;
                    FIO-ESM)  trylsmask=CMIP5/fixed/sftlf.FIO-ESM.nc;;
                    GISS-E2-H-CC) trylsmask=CMIP5/fixed/sftlf_fx_GISS-E2-H_historical_r0i0p0.nc;; # tmp
                    GISS-E2-R-CC) trylsmask=CMIP5/fixed/sftlf_fx_GISS-E2-R_historical_r0i0p0.nc;; # tmp
                    HadGEM2*)  trylsmask=CMIP5/fixed/sftlf_fx_HadGEM2-ES_historical_r1i1p1.nc;;
                    inmcm4)    trylsmask=CMIP5/fixed/sftlf_fx_${model}_rcp45_r0i0p0.nc;;
                    *)         trylsmask=CMIP5/fixed/sftlf_fx_${model%_p?}_historical_r0i0p0.nc;;
               esac
           fi
           if [ -n "$trylsmask" -a \( -s "$trylsmask" -o -s $HOME/climexp/$trylsmask \) ]; then
               LSMASK=$trylsmask
           else
               trylsmask=""
           fi
       fi
    fi
    [ -n "$rip" ] && kindname="$kindname $rip"
    climfield="$var"
    ;;

cordex*)
    # expecting cordex_${domain}_${var}_${gcm}_${exp}_${rip}_${rcm}_${timescale}
    field=${FORM_field#cordex_}
    domain=${field%%_*}
    field=${field#*_}
    var=${field%%_*}
    field=${field#*_}
    gcm=${field%%_*}
    field=${field#*_}
    exp=${field%%_*}
    field=${field#*_}
    rip=${field%%_*}
    field=${field#*_}
    rcm=${field%%_*}
    timescale=${field#*_}
    version=v1
    case $gcm in
        ave) file=CORDEX/$domain/$timescale/$var/${var}_${domain}_cordex_${exp}_${timescale}_ave.nc
        climfield=$var
        kindname="CORDEX $domain ave $exp"
        LSMASK=CORDEX/$domain/fx/lsmask_EUR-44_cordex_ave.nc
        ;;
        ens) file=CORDEX/$domain/$timescale/$var/${var}_${domain}_cordex_${exp}_${timescale}_%%%.nc
        climfield=$var
        kindname="CORDEX $domain $exp"
        LSMASK=CORDEX/$domain/fx/lsmask_EUR-44_cordex_ave.nc
        ;;
        *)
file=CORDEX/$domain/$timescale/$var/${var}_${domain}_${gcm}_${exp}_${rip}_${rcm}_${version}_${timescale}_*latlon.nc
        ###echo $file
        file=`ls $file 2> /dev/null | head -1`
        climfield=$var
        if [ $rcm = MPI-CSC-REMO2009 ]; then
            kindname="$gcm/$rcm $rip $exp"
        else
            kindname="$gcm/$rcm $exp"
        fi
        LSMASK=CORDEX/$domain/fx/lsmask_${domain}_${gcm}_historical_r0i0p0_${rcm}_${version}_fx_latlon.nc
        ;;
    esac
    case $file in
        *%.nc) ensfile=`echo $file | tr '%' '0'`;;
        *) ensfile=$file;;
    esac
    [ ! -f "$ensfile" ] && file=
    case $timescale in
        day) case $gcm in
                MOHC*) NPERYEAR=360;;
                NOAA_GFDL*|NCC-NorESM1*|CSIRO-QCCCE*|IPSL-IPSL-CM5A*|MIROC-MIROC5*) NPERYEAR=365;;
                *) NPERYEAR=366;;
             esac;;
        annual) NPERYEAR=1;;
    esac
    if [ -z "$file" ]; then
        echo
        echo "Cannot handle $FORM_field (yet)"
        exit -1
    fi

    ;;

rt2b_*)
    . ./ENSEMBLES_RCM/rt2b.cgi;;
rt3_*)
    . ./ENSEMBLES_RCM/rt3.cgi;;

ens_ecmwf4*|ecmwf4*)
    FORM_field=${FORM_field#ens_}
    mon=${FORM_field##*_}
    case $mon in
        01|jan) mon=01;month=1Jan;;
        02|feb) mon=02;month=1Feb;;
        03|mar) mon=03;month=1Mar;;
        04|apr) mon=04;month=1Apr;;
        05|may) mon=05;month=1May;;
        06|jun) mon=06;month=1Jun;;
        07|jul) mon=07;month=1Jul;;
        08|aug) mon=08;month=1Aug;;
        09|sep) mon=09;month=1Sep;;
        10|oct) mon=10;month=1Oct;;
        11|nov) mon=11;month=1Nov;;
        12|dec) mon=12;month=1Dec;;
        *) echo "$0: unknown field $FORM_field"; exit -1;;
    esac
    if [ ${FORM_field#ecmwf4_ave} != $FORM_field ]; then
        var=${FORM_field#ecmwf4_ave_}
        var=${var%_*}
        var=`echo "$var" | tr '[:lower:]' '[:upper:]'`
        file=ECMWF/S4/${var}_ECMWF-S4_ave_monthly-means_FCmon${mon}.nc
    else
        var=${FORM_field#*_}
        var=${var%_*}
        var=`echo "$var" | tr '[:lower:]' '[:upper:]'`
        file=ECMWF/S4/${var}_ECMWF-S4_mem%%_monthly-means_FCmon${mon}.nc
    fi
    kindname="ECMWF S4 $month"
    climfield=$var
    LSMASK=ECMWF/S4/lsmask07.nc
    ;;
isimip*)
    field=$FORM_field
    dataset=${field%%_*}
    field=${field#*_}
    var=${field%%_*}
    field=${field#*_}
    gcm=${field%%_*}
    field=${field#*_}
    hydro=${field%%_*}
    scen=${field#*_}
    if [ $gcm = all -a $hydro = all ]; then
        file=ISIMIP/$var/isimip_${var}_${scen}_%%%.nc
    else
        file=ISIMIP/$var/${gcm}_${hydro}_${var}.nc
    fi
    ;;

tempa) file=NCDCData/temp_anom.nc;kindname="NCDC v3";climfield="T2m anom";LSMASK=NCDCData/ls_temp_anom.nc;;
noaa_temp) file=NCDCData/NOAAGlobalTemp.gridded.nc;kindname="NOAA v4";climfield="SST/T2m anom";LSMASK=NCDCData/ls_noaatemp.nc;;
hadcrut4) file=UKMOData/HadCRUT.4.6.0.0.median.nc;kindname="HadCRUT4.6";climfield="SST/T2m anom";LSMASK=UKMOData/lsmask_5.nc;;
crutem1) file=CRUData/crutem1.ctl;kindname="CRUTEM1";climfield="T2m anom";;
ncrutem1) file=CRUData/ncrutem1.ctl;kindname="CRUTEM1";climfield="number of stations";;
crutem1v) file=CRUData/crutem1v.ctl;kindname="CRUTEM1v";climfield="T2m anom";;
crutem2) file=CRUData/crutem2.ctl;kindname="CRUTEM2";climfield="T2m anom";;
ncrutem2) file=CRUData/ncrutem2.ctl;kindname="CRUTEM2";climfield="number of stations";;
crutem2v) file=CRUData/crutem2v.ctl;kindname="CRUTEM2v";climfield="T2m anom";;
crutem3) file=CRUData/CRUTEM3_ce.nc;kindname="CRUTEM3";climfield="T2m anom";;
ncrutem3) file=CRUData/CRUTEM3_nobs_ce.nc;kindname="CRUTEM3";climfield="number of stations";;
crutem3v) file=CRUData/CRUTEM3v_ce.nc;kindname="CRUTEM3v";climfield="T2m anom";;
crutem4) file=UKMOData/CRUTEM.4.6.0.0.anomalies.nc;kindname="CRUTEM4.6";climfield="T2m anom";;
crutem4v) file=UKMOData/CRUTEM.4.6.0.0.variance_adjusted.nc;kindname="CRUTEM4.6v";climfield="T2m anom";;
giss_temp_250) file=NASAData/giss_temp_both_250.nc;kindname="GISS 250";climfield="T2m/SST anom";LSMASK=NASAData/lsmask.nc;;
giss_temp_land_250) file=NASAData/giss_temp_land_250.nc;kindname="GISS 250";climfield="T2m anom";LSMASK=NASAData/lsmask.nc;;
giss_temp_1200) file=NASAData/giss_temp_both_1200.nc;kindname="GISS 1200";climfield="T2m/SST anom";LSMASK=NASAData/lsmask.nc;;
giss_temp_land_1200) file=NASAData/giss_temp_land_1200.nc;kindname="GISS 1200";climfield="T2m anom";LSMASK=NASAData/lsmask.nc;;
had4_krig_v2) file=YorkData/had4_krig_v2_0_0.nc;kindname="HadCRUT4 filled-in";climfield="T2m/SST";LSMASK=UKMOData/lsmask_5.nc;;
ghcn_cams_05) file=NCEPData/ghcn_cams_05.nc;kindname="GHCN/CAMS";climfield="t2m";;
ghcn_cams_10) file=NCEPData/ghcn_cams_10.nc;kindname="GHCN/CAMS";climfield="t2m";;
ghcn_cams_25) file=NCEPData/ghcn_cams_25.nc;kindname="GHCN/CAMS";climfield="t2m";;
berkeley_tavg_daily_full) file=BerkeleyData/TAVG_Daily_LatLong1_full.nc;kindname="Berkeley";climfield="Tavg";NPERYEAR=366;LSMASK=BerkeleyData/land_mask.nc;;
berkeley_tmax_daily_full) file=BerkeleyData/TMAX_Daily_LatLong1_full.nc;kindname="Berkeley";climfield="Tmax";NPERYEAR=366;LSMASK=BerkeleyData/land_mask.nc;;
berkeley_tmin_daily_full) file=BerkeleyData/TMIN_Daily_LatLong1_full.nc;kindname="Berkeley";climfield="Tmin";NPERYEAR=366;LSMASK=BerkeleyData/land_mask.nc;;
berkeley_tavg_daily_full_e) file=BerkeleyData/TAVG_Daily_LatLong1_full_extended.nc;kindname="Berkeley+";climfield="Tavg";NPERYEAR=366;LSMASK=BerkeleyData/land_mask2.nc;;
berkeley_tmax_daily_full_e) file=BerkeleyData/TMAX_Daily_LatLong1_full_extended.nc;kindname="Berkeley+";climfield="Tmax";NPERYEAR=366;LSMASK=BerkeleyData/land_mask2.nc;;
berkeley_tmin_daily_full_e) file=BerkeleyData/TMIN_Daily_LatLong1_full_extended.nc;kindname="Berkeley+";climfield="Tmin";NPERYEAR=366;LSMASK=BerkeleyData/land_mask2.nc;;
berkeley_tavg_daily) file=BerkeleyData/TAVG_Daily_LatLong1.nc;kindname="Berkeley";climfield="Tavg anom";NPERYEAR=366;LSMASK=BerkeleyData/land_mask.nc;;
berkeley_tmax_daily) file=BerkeleyData/TMAX_Daily_LatLong1.nc;kindname="Berkeley";climfield="Tmax anom";NPERYEAR=366;LSMASK=BerkeleyData/land_mask.nc;;
berkeley_tmin_daily) file=BerkeleyData/TMIN_Daily_LatLong1.nc;kindname="Berkeley";climfield="Tmin anom";NPERYEAR=366;LSMASK=BerkeleyData/land_mask.nc;;
berkeley_tavg) file=BerkeleyData/TAVG_LatLong1.nc;kindname="Berkeley";climfield="Tavg";LSMASK=BerkeleyData/land_mask.nc;;
berkeley_tmax) file=BerkeleyData/TMAX_LatLong1.nc;kindname="Berkeley";climfield="Tmax";LSMASK=BerkeleyData/land_mask.nc;;
berkeley_tmin) file=BerkeleyData/TMIN_LatLong1.nc;kindname="Berkeley";climfield="Tmin";LSMASK=BerkeleyData/land_mask.nc;;
berkeley_txx) file=BerkeleyData/$FORM_field.nc;kindname="Berkeley";climfield="Txx";NPERYEAR=1;LSMASK=BerkeleyData/land_mask.nc;;
clsat_tavg) file=SYSUData/CLSAT_13_tavg.nc;kindname="CL-SAT 1.3";climfield="T2m anom";;
clsat_tmin) file=SYSUData/CLSAT_13_tmin.nc;kindname="CL-SAT 1.3";climfield="Tmin anom";;
clsat_tmax) file=SYSUData/CLSAT_13_tmax.nc;kindname="CL-SAT 1.3";climfield="Tmax anom";;
cmst) file=SYSUData/CMST.nc;kindname="CMST";climfield="T2m/SST anom";;

hadghcnd_tx) file=UKMOData/hadghcnd_tx.ctl;kindname="HadGHCND";climfield="Tmax";NPERYEAR=366;;
hadghcnd_tn) file=UKMOData/hadghcnd_tn.ctl;kindname="HadGHCND";climfield="Tmin";NPERYEAR=366;;
rtg_sst_5dy) file=NCEPData/rtg_sst_5dy.ctl;kindname="RTG";climfield="SST";NPERYEAR=73;;
rtg_sst_month) file=NCEPData/rtg_sst_month.ctl;kindname="RTG";climfield="SST";;
sstoi_v2) file=NCEPData/sstoi_v2.nc;kindname="NCEP OI v2";climfield="SST";;
sstoiv2_monthly_mean) file=NCEPData/oisst_v2_mean_monthly.nc;kindname="NCEP OIv2 1/4";climfield="SST";;
sstoiv2_monthly_anom) file=NCEPData/oisst_v2_anom_monthly.nc;kindname="NCEP OIv2 1/4";climfield="SST anom";;
sstoiv2_daily_mean) file=NCEPData/oisst_v2_mean_daily.nc;kindname="NCEP OIv2 1/4";climfield="SST";NPERYEAR=366;;
sstoiv2_daily_anom) file=NCEPData/oisst_v2_anom_daily.nc;kindname="NCEP OIv2 1/4";climfield="SST anom";NPERYEAR=366;;
iceoi_v2) file=NCEPData/iceoi_v2.nc;kindname="Reynolds v2";climfield="ice cover";;
sstoi) file=NCEPData/sstoi.ctl;kindname="Reynolds";climfield="SST";;
ersstv3b) file=NCDCData/ersstv3b.ctl;kindname="ERSST v3b2";climfield="SST";;
ersstv4) file=NCDCData/ersstv4.nc;kindname="ERSST v4";climfield="SST";;
ersstv4a) file=NCDCData/ersstv4a.nc;kindname="ERSST v4";climfield="SSTa";;
ersstv5) file=NCDCData/ersstv5.nc;kindname="ERSST v5";climfield="SST";;
ersstv5a) file=NCDCData/ersstv5a.nc;kindname="ERSST v5";climfield="SSTa";;
ssmi_sst) file=SSMIData/ssmi_sst.ctl;kindname="SSMI";climfield="SST";;
tlt_60) file=UAHData/tlt_60.nc;kindname="UAH MSU v6.0";climfield="Tlt anomaly";LSMASK=UAHData/lsmask_25_180.nc;;
tlt_56) file=UAHData/tlt_56.nc;kindname="UAH MSU v5.6";climfield="Tlt anomaly";LSMASK=UAHData/lsmask_25_180.nc;;
tlt_55) file=UAHData/tlt_55.nc;kindname="UAH MSU v5.5";climfield="Tlt anomaly";LSMASK=UAHData/lsmask_25_180.nc;;
rss_tlt) file=SSMIData/rss_tlt_v4_0.nc;kindname="RSS MSU 4.0";climfield="TlT";;
rss_tlt_anom) file=SSMIData/rss_tlt_anom_v4_0.nc;kindname="RSS MSU 4.0";climfield="TlT anomaly";;
rss_tlt_old) file=SSMIData/rss_tlt_v3_3.nc;kindname="RSS MSU 3.3";climfield="TlT";;
rss_tlt_anom_old) file=SSMIData/rss_tlt_anom_v3_3.nc;kindname="RSS MSU 3.3";climfield="TlT anomaly";;
prca) file=NCDCData/prcp_anom.nc;kindname="NCDC";climfield="precip anom";LSMASK=NCDCData/lsmask_5.nc;flipcolor=11;;
ncdc_prcp) file=NCDCData/prcp_total.nc;kindname="NCDC";climfield="prcp";flipcolor=11;;
prcp_trmm) file=TRMMData/prcp_trmm.nc;kindname="TRMM+GPCC";climfield="precipitation";flipcolor=11;;
prcp_trmm_lo) file=TRMMData/prcp_trmm_lo.nc;kindname="TRMM+GPCC";climfield="precipitation";flipcolor=11;;
prcp_trmm_1) file=TRMMData/prcp_trmm_1.nc;kindname="TRMM";climfield="precipitation";flipcolor=11;;
prcp_trmm_1_lo) file=TRMMData/prcp_trmm_1_lo.nc;kindname="TRMM";climfield="precipitation";flipcolor=11;LSMASK=TRMMData/lsmask_trmm_1.nc;;
cmorph_daily_05) file=NCEPData/cmorph_daily_05.nc;kindname="CMORPH";climfield="precipitation";flipcolor=11;LSMASK=NCEPData/lsmask_05.nc;NPERYEAR=366;;
cmorph_daily) file=NCEPData/cmorph_daily.nc;kindname="CMORPH";climfield="precipitation";flipcolor=11;LSMASK=NCEPData/lsmask_025.nc;NPERYEAR=366;;
cmorph_monthly) file=NCEPData/cmorph_monthly.nc;kindname="CMORPH";climfield="precipitation";LSMASK=NCEPData/lsmask_025.nc;flipcolor=11;;
knmi_radar_daily) file=KNMIRadarData/radar_sum.nc;kindname="KNMI radar";climfield="precipitation";flipcolor=11;NPERYEAR=366;map='set lon 3 7.5
set lat 50.5 54';;
knmi_radar_maxhourly) file=KNMIRadarData/radar_max.nc;kindname="KNMI radar";climfield="max hourly precip";flipcolor=11;NPERYEAR=366;map='set lon 3 7.5
set lat 50.5 54';;
imerg_daily) file=GPMData/imerg_daily.nc;kindname="IMERG";climfield=precipitation;flipcolor=11;NPERYEAR=366;;
imerg_daily_02) file=GPMData/imerg_daily_02.nc;kindname="IMERG";climfield=precipitation;flipcolor=11;NPERYEAR=366;;
imerg_daily_05) file=GPMData/imerg_daily_05.nc;kindname="IMERG";climfield=precipitation;flipcolor=11;NPERYEAR=366;;
ssmi_1) file=NCDCData/ssmi_1.ctl;kindname="NCDC SSMI/I";climfield="precipitation";flipcolor=11;;
hulme) file=CRUData/hulme23.ctl;kindname="CRU";climfield="precipitation";flipcolor=11;;
hulme-nino3) file=CRUData/hulme23-nino3.ctl;kindname="CRU";climfield="precipitation - nino3";flipcolor=11;;
cru4_tmp) file=CRUData/cru_ts4.02.1901.2017.tmp.dat.nc;kindname="CRU TS4.02";climfield="temperature";LSMASK=CRUData/lsmask_05.nc;;
cru4_tmp_stn) file=CRUData/cru_ts4.02.1901.2017.tmp.stn.nc;kindname="CRU TS4.02 stn";climfield="#temperature";LSMASK=CRUData/lsmask_05.nc;;
cru4_tmp_10) file=CRUData/cru_ts4.02.1901.2017.tmp.dat_1.nc;kindname="CRU TS4.02";climfield="temperature";LSMASK=CRUData/lsmask_10.nc;;
cru4_tmp_25) file=CRUData/cru_ts4.02.1901.2017.tmp.dat_25.nc;kindname="CRU TS4.02";climfield="temperature";LSMASK=CRUData/lsmask_25.nc;;
cru4_tmx) file=CRUData/cru_ts4.02.1901.2017.tmx.dat.nc;kindname="CRU TS4.02";climfield="Tmax";LSMASK=CRUData/lsmask_05.nc;;
cru4_tmx_stn) file=CRUData/cru_ts4.02.1901.2017.tmx.stn.nc;kindname="CRU TS4.02 stn";climfield="#Tmax";LSMASK=CRUData/lsmask_05.nc;;
cru4_tmx_10) file=CRUData/cru_ts4.02.1901.2017.tmx.dat_1.nc;kindname="CRU TS4.02";climfield="Tmax";LSMASK=CRUData/lsmask_10.nc;;
cru4_tmx_25) file=CRUData/cru_ts4.02.1901.2017.tmx.dat_25.nc;kindname="CRU TS4.02";climfield="Tmax";LSMASK=CRUData/lsmask_25.nc;;
cru4_tmn) file=CRUData/cru_ts4.02.1901.2017.tmn.dat.nc;kindname="CRU TS4.02";climfield="Tmin";LSMASK=CRUData/lsmask_05.nc;;
cru4_tmn_stn) file=CRUData/cru_ts4.02.1901.2017.tmn.stn.nc;kindname="CRU TS4.02 stn";climfield="#Tmin";LSMASK=CRUData/lsmask_05.nc;;
cru4_tmn_10) file=CRUData/cru_ts4.02.1901.2017.tmn.dat_1.nc;kindname="CRU TS4.02";climfield="Tmin";LSMASK=CRUData/lsmask_10.nc;;
cru4_tmn_25) file=CRUData/cru_ts4.02.1901.2017.tmn.dat_25.nc;kindname="CRU TS4.02";climfield="Tmin";LSMASK=CRUData/lsmask_25.nc;;
cru4_dtr) file=CRUData/cru_ts4.02.1901.2017.dtr.dat.nc;kindname="CRU TS4.02";climfield="Tmax-Tmin";LSMASK=CRUData/lsmask_05.nc;;
cru4_dtr_stn) file=CRUData/cru_ts4.02.1901.2017.dtr.stn.nc;kindname="CRU TS4.02";climfield="#Tmax-Tmin";LSMASK=CRUData/lsmask_05.nc;;
cru4_dtr_10) file=CRUData/cru_ts4.02.1901.2017.dtr.dat_1.nc;kindname="CRU TS4.02";climfield="Tmax-Tmin";LSMASK=CRUData/lsmask_10.nc;;
cru4_dtr_25) file=CRUData/cru_ts4.02.1901.2017.dtr.dat_25.nc;kindname="CRU TS4.02";climfield="Tmax-Tmin";LSMASK=CRUData/lsmask_25.nc;;
cru4_pre) file=CRUData/cru_ts4.02.1901.2017.pre.dat.nc;kindname="CRU TS4.02";climfield="precipitation";flipcolor=11;LSMASK=CRUData/lsmask_05.nc;;
cru4_pre_stn) file=CRUData/cru_ts4.02.1901.2017.pre.stn.nc;kindname="CRU TS4.02 stn";climfield="#precipitation";flipcolor=11;LSMASK=CRUData/lsmask_05.nc;;
cru4_pre_10) file=CRUData/cru_ts4.02.1901.2017.pre.dat_1.nc;kindname="CRU TS4.02";climfield="precipitation";flipcolor=11;LSMASK=CRUData/lsmask_10.nc;;
cru4_pre_25) file=CRUData/cru_ts4.02.1901.2017.pre.dat_25.nc;kindname="CRU TS4.02";climfield="precipitation";flipcolor=11;LSMASK=CRUData/lsmask_25.nc;;
cru4_cld) file=CRUData/cru_ts4.02.1901.2017.cld.dat.nc;kindname="CRU TS4.02";climfield="cloud fraction";flipcolor=11;LSMASK=CRUData/lsmask_05.nc;;
cru4_cld_stn) file=CRUData/cru_ts4.02.1901.2017.cld.stn.nc;kindname="CRU TS4.02";climfield="#cloud fraction";flipcolor=11;LSMASK=CRUData/lsmask_05.nc;;
cru4_cld_10) file=CRUData/cru_ts4.02.1901.2017.cld.dat_1.nc;kindname="CRU TS4.02";climfield="cloud fraction";flipcolor=11;LSMASK=CRUData/lsmask_10.nc;;
cru4_cld_25) file=CRUData/cru_ts4.02.1901.2017.cld.dat_25.nc;kindname="CRU TS4.02";climfield="cloud fraction";flipcolor=11;LSMASK=CRUData/lsmask_25.nc;;
cru4_vap) file=CRUData/cru_ts4.02.1901.2017.vap.dat.nc;kindname="CRU TS4.02";climfield="vapour pressure";flipcolor=11;LSMASK=CRUData/lsmask_05.nc;;
cru4_vap_stn) file=CRUData/cru_ts4.02.1901.2017.vap.stn.nc;kindname="CRU TS4.02";climfield="#vapour pressure";flipcolor=11;LSMASK=CRUData/lsmask_05.nc;;
cru4_vap_10) file=CRUData/cru_ts4.02.1901.2017.vap.dat_1.nc;kindname="CRU TS4.02";climfield="vapour pressure";flipcolor=11;LSMASK=CRUData/lsmask_10.nc;;
cru4_vap_25) file=CRUData/cru_ts4.02.1901.2017.vap.dat_25.nc;kindname="CRU TS4.02";climfield="vapour pressure";flipcolor=11;LSMASK=CRUData/lsmask_25.nc;;

hadex2_ann_*) var=${FORM_field#hadex2_ann_};file=UKMOData/HadEX2_${var}_ann.nc;kindname="HadEX2";climfield=$var;NPERYEAR=1;;
hadex2_*) var=${FORM_field#hadex2_};file=UKMOData/HadEX2_${var}_mo.nc;kindname="HadEX2";climfield=$var;;

hadcruh_q) file=CRUData/CRU_blendnewjul08_q_7303cf.nc;kindname="HadCRUH";climfield="specific humidity";flipcolor=11;;
hadcruh_rh) file=CRUData/CRU_blendnewjul08_RH_7303cf.nc;kindname="HadCRUH";climfield="relative humidity";flipcolor=11;;

ensembles_025_tg) file=ENSEMBLES/tg_0.25deg_reg_v19.0eu.nc;kindname="E-OBS 19.0e";climfield="Tmean";NPERYEAR=366;map='set lon -30 50
set lat 30 75';;
ensembles_025_tg_e) file=ENSEMBLES/tg_0.25deg_reg_v19.0ee.nc;kindname="E-OBS 19.0e+";climfield="Tmean";NPERYEAR=366;map='set lon -30 50
set lat 30 75';;
ensembles_025_tg_mo) file=ENSEMBLES/tg_0.25deg_reg_v19.0eu_mo.nc;kindname="E-OBS 19.0e";climfield="Tmean";map='set lon -30 50
set lat 30 75';;
ensembles_025_tn) file=ENSEMBLES/tn_0.25deg_reg_v19.0eu.nc;kindname="E-OBS 19.0e";climfield="Tmin";NPERYEAR=366;map='set lon -30 50
set lat 30 75';;
ensembles_025_tn_e) file=ENSEMBLES/tn_0.25deg_reg_v19.0ee.nc;kindname="E-OBS 19.0e+";climfield="Tmin";NPERYEAR=366;map='set lon -30 50
set lat 30 75';;
ensembles_025_tn_mo) file=ENSEMBLES/tn_0.25deg_reg_v19.0eu_mo.nc;kindname="E-OBS 19.0e";climfield="Tmin";map='set lon -30 50
set lat 30 75';;
ensembles_025_tx) file=ENSEMBLES/tx_0.25deg_reg_v19.0eu.nc;kindname="E-OBS 19.0e";climfield="Tmax";NPERYEAR=366;map='set lon -30 50
set lat 30 75';;
ensembles_025_tx_e) file=ENSEMBLES/tx_0.25deg_reg_v19.0ee.nc;kindname="E-OBS 19.0e+";climfield="Tmax";NPERYEAR=366;map='set lon -30 50
set lat 30 75';;
ensembles_025_tx_mo) file=ENSEMBLES/tx_0.25deg_reg_v19.0eu_mo.nc;kindname="E-OBS 19.0e";climfield="Tmax";map='set lon -30 50
set lat 30 75';;
ensembles_025_rr) file=ENSEMBLES/rr_0.25deg_reg_v19.0eu.nc;kindname="E-OBS 19.0e";climfield="prcp";NPERYEAR=366;flipcolor=11;map='set lon -30 50
set lat 30 75';;
ensembles_025_rr_e) file=ENSEMBLES/rr_0.25deg_reg_v19.0ee.nc;kindname="E-OBS 19.0e+";climfield="prcp";NPERYEAR=366;flipcolor=11;map='set lon -30 50
set lat 30 75';;
ensembles_025_rr_mo) file=ENSEMBLES/rr_0.25deg_reg_v19.0eu_mo.nc;kindname="E-OBS 19.0e";climfield="prcp";flipcolor=11;map='set lon -30 50
set lat 30 75';;
ensembles_025_pp_mo) file=ENSEMBLES/pp_0.25deg_reg_v19.0eu_mo.nc;kindname="E-OBS 19.0e";climfield="slp";map='set lon -30 50
set lat 30 75';;
ensembles_025_elev) file=ENSEMBLES/elev_0.25deg_reg_v4.0.nc;kindname="E-OBS 4.0";climfield="elev";NPERYEAR=0;map='set lon -30 50
set lat 30 75';;

prism_ppt*) ext=${FORM_field#prism_ppt};file=PRISMData/ppt_prism$ext.nc;kindname="PRISM";climfield="prcp";flipcolor=11;map='set lon -125 -66.5
set lat 24.1 49.9';;
prism_tmax*) ext=${FORM_field#prism_tmax};file=PRISMData/tmax_prism$ext.nc;kindname="PRISM";climfield="Tmax";map='set lon -125 -66.5
set lat 24.1 49.9';;
prism_tmin*) ext=${FORM_field#prism_tmin};file=PRISMData/tmin_prism$ext.nc;kindname="PRISM";climfield="Tmin";map='set lon -125 -66.5
set lat 24.1 49.9';;
prism_tmean*) ext=${FORM_field#prism_tmean};file=PRISMData/tmean_prism$ext.nc;kindname="PRISM";climfield="temperature";map='set lon -125 -66.5
set lat 24.1 49.9';;
prism_tdmean*) ext=${FORM_field#prism_tdmean};file=PRISMData/tdmean_prism$ext.nc;kindname="PRISM";climfield="dew point";map='set lon -125 -66.5
set lat 24.1 49.9';;
prism_vpdmax*) ext=${FORM_field#prism_vpdmax};file=PRISMData/tdmean_prism$ext.nc;kindname="PRISM";climfield="max vapour pressure deficit";map='set lon -125 -66.5
set lat 24.1 49.9';;

scpdsi) file=CRUData/scPDSI.cru_ts3.26early.bams2018.GLOBAL.1901.2017.nc;kindname="CRU";climfield="scPDSI 3.26e";;
scpdsi_europe) file=CRUData/scpdsi_Europe_IJC.nc;kindname="CRU";climfield="scPDSI";;
scpdsi_alpine) file=CRUData/scpdsi_alpine.ctl;kindname="CRU";climfield="scPDSI";map='set lon 4 19
set lat 43 49
set mpdset hires';;
spei_*) n=${FORM_field#spei_};file=CSICData/SPEI_$n.nc;kindname="CSIC";climfield="SPEI $n";flipcolor=11;;
PSI_*) dataset=${FORM_field#PSI_};file=UCData/PSI_$dataset.nc;kindname="GIDMaPS";climfield="PSI $dataset";flipcolor=11;;
SPI_*) dataset=${FORM_field#SPI_};file=UCData/SPI_$dataset.nc;kindname="GIDMaPS";climfield="SPI $dataset";flipcolor=11;;
SSI_*) dataset=${FORM_field#SSI_};file=UCData/SSI_$dataset.nc;kindname="GIDMaPS";climfield="SSI $dataset";flipcolor=11;;
gpcc_25_8) file=GPCCData/gpcc_V8_25.nc;kindname="GPCC V8 2.5";climfield="precipitation";flipcolor=11;;
gpcc_10_8) file=GPCCData/gpcc_V8_10.nc;kindname="GPCC V8 1.0";climfield="precipitation";flipcolor=11;;
gpcc_05_8) file=GPCCData/gpcc_V8_05.nc;kindname="GPCC V8 0.5";climfield="precipitation";flipcolor=11;;
gpcc_25_n1_8) file=GPCCData/gpcc_V8_25_n1.nc;kindname="GPCC V8 2.5";climfield="precipitation";flipcolor=11;;
gpcc_10_n1_8) file=GPCCData/gpcc_V8_10_n1.nc;kindname="GPCC V8 1.0";climfield="precipitation";flipcolor=11;;
gpcc_05_n1_8) file=GPCCData/gpcc_V8_05_n1.nc;kindname="GPCC V8 0.5";climfield="precipitation";flipcolor=11;;
gpcc_25) file=GPCCData/gpcc_25.nc;kindname="GPCC 2.5";climfield="precipitation";flipcolor=11;;
gpcc_10) file=GPCCData/gpcc_10.nc;kindname="GPCC 1.0";climfield="precipitation";flipcolor=11;;
gpcc_05) file=GPCCData/gpcc_05.nc;kindname="GPCC 0.5";climfield="precipitation";flipcolor=11;LSMASK=GPCCData/lsmask_05.nc;;
gpcc_025) file=GPCCData/gpcc_025.nc;kindname="GPCC 0.25";climfield="precipitation";flipcolor=11;;
gpcc_25_n1) file=GPCCData/gpcc_25_n1.nc;kindname="GPCC 2.5";climfield="precipitation";flipcolor=11;;
gpcc_10_n1) file=GPCCData/gpcc_10_n1.nc;kindname="GPCC 1.0";climfield="precipitation";flipcolor=11;;
gpcc_05_n1) file=GPCCData/gpcc_05_n1.nc;kindname="GPCC 0.5";climfield="precipitation";flipcolor=11;;
gpcc_025_n1) file=GPCCData/gpcc_025_n1.nc;kindname="GPCC 0.25";climfield="precipitation";flipcolor=11;;
gpccall_10) file=GPCCData/gpcc_10_combined.nc;kindname="GPCC+monitoring";climfield="precipitation";flipcolor=11;;
gpccpatch_10) file=GPCCData/gpcc_10_patched.nc;kindname="GPCC+monitoring";climfield="precipitation";flipcolor=11;;
gpccall_10_n1) file=GPCCData/gpcc_10_n1_combined.nc;kindname="GPCC+monitoring";climfield="precipitation";flipcolor=11;;
gpccpatch_10_n1) file=GPCCData/gpcc_10_n1_patched.nc;kindname="GPCC+monitoring_var";climfield="precipitation";flipcolor=11;;
gpccall_25) file=GPCCData/gpcc_25_combined.nc;kindname="GPCC+monitoring";climfield="precipitation";flipcolor=11;;
gpccpatch_25) file=GPCCData/gpcc_25_patched.nc;kindname="GPCC+monitoring_var";climfield="precipitation";flipcolor=11;;
gpccall_25_n1) file=GPCCData/gpcc_25_n1_combined.nc;kindname="GPCC+monitoring";climfield="precipitation";flipcolor=11;;
gpccpatch_25_n1) file=GPCCData/gpcc_25_n1_patched.nc;kindname="GPCC+monitoring_var";climfield="precipitation";flipcolor=11;;
gpcc) file=GPCCData/gpcc_10_mon.nc;kindname="GPCC monitoring";climfield="precipitation";flipcolor=11;;
gpcc_n1) file=GPCCData/gpcc_10_n1_mon.nc;kindname="GPCC monitoring";climfield="precipitation";flipcolor=11;;
ngpcc) file=GPCCData/gpcc_10_n_mon.nc;kindname="GPCC monitoring";climfield="#gauges";;
ngpcc_025) file=GPCCData/ngpcc_025.nc;kindname="GPCC";climfield="#gauges";;
ngpcc_05) file=GPCCData/ngpcc_05.nc;kindname="GPCC";climfield="#gauges";;
ngpcc_10) file=GPCCData/ngpcc_10.nc;kindname="GPCC";climfield="#gauges";;
ngpcc_25) file=GPCCData/ngpcc_25.nc;kindname="GPCC";climfield="#gauges";;
gpcc_daily) file=GPCCData/gpcc_combined_daily.nc;kindname="GPCC daily V1";climfield="precipitation";NPERYEAR=366;;
gpcc_daily_n1) file=GPCCData/gpcc_combined_daily_n1.nc;kindname="GPCC daily V1";climfield="precipitation"NPERYEAR=366;;
ngpcc_daily) file=GPCCData/gpcc_combined_daily_n.nc;kindname="GPCC daily V1";climfield="#gauges"NPERYEAR=366;;
prcp_cpc_daily) file=NCEPData/prcp_GLB_daily.nc;kindname="CPC daily";climfield="precipitation";NPERYEAR=366;;
prcp_cpc_daily_us) file=NCEPData/prcp_CONUS_daily.nc;kindname="CPC daily";climfield="precipitation";NPERYEAR=366;;
prcp_cpc_daily_us_05) file=NCEPData/prcp_CONUS_daily_05.nc;kindname="CPC daily";climfield="precipitation";NPERYEAR=366;;
prcp_cpc_daily_us_10) file=NCEPData/prcp_CONUS_daily_10.nc;kindname="CPC daily";climfield="precipitation";NPERYEAR=366;;
prcp_cpc_daily_n1) file=NCEPData/prcp_GLB_daily_n1.nc;kindname="CPC daily";climfield="precipitation";NPERYEAR=366;;
prcp_cpc_daily_n1_us) file=NCEPData/prcp_CONUS_daily_n1.nc;kindname="CPC daily";climfield="precipitation";NPERYEAR=366;;
nprcp_cpc_daily) file=NCEPData/nprcp_GLB_daily.nc;kindname="CPC daily";climfield="#gauges";NPERYEAR=366;;
nprcp_cpc_daily_us) file=NCEPData/nprcp_CONUS_daily.nc;kindname="CPC daily";climfield="#gauges";NPERYEAR=366;;
gpcp_22) file=GPCPData/gpcp_22.ctl;kindname="GPCP v2.2";climfield="precipitation";flipcolor=11;LSMASK=GPCPData/gpcp_25_lsmask.nc;;
gpcp_23) file=GPCPData/gpcp.nc;kindname="GPCP v2.3";climfield="precipitation";flipcolor=11;LSMASK=GPCPData/gpcp_25_lsmask.nc;;
gpcp_daily) file=GPCPData/gpcp_daily.nc;kindname="GPCP v1.3";climfield="precipitation";flipcolor=11;NPERYEAR=366;;
gpcp_daily_12) file=GPCPData/gpcp_1dd_12.ctl;kindname="GPCP v1.2";climfield="precipitation";flipcolor=11;NPERYEAR=366;;
cmap) file=NCEPData/cmap.nc;kindname="CMAP";climfield="precipitation";flipcolor=11;;
cmaperr) file=NCEPData/cmaperr.ctl;kindname="CMAP";climfield="relative error on precipitation";;
cmapm) file=NCEPData/cmapm.ctl;kindname="CMAP incl model";climfield="precipitation";flipcolor=11;;
cmapmerr) file=NCEPData/cmapmerr.ctl;kindname="CPMAP (incl model)";climfield="relative error on precipitation";;
chirps_20_25) file=CHIRPSData/v2p0chirps_25.nc;kindname="CHIRPS";climfield="precipitation";flipcolor=11;NPERYEAR=366;map="set lon -20 55
set lat -40 40";;
CenTrendsv1) file=UCSBData/CenTrends_v1_monthly_ce.nc;kindname="CenTrends v1";climfield="precipitation";flipcolor=11;map="set lon 28 54
set lat -15 18";;
CenTrendsChirps) file=CHIRPSData/centrends_chirps.nc;kindname="CenTrends/CHIRPS";climfield="precipitation";flipcolor=11;map="set lon 28 54
set lat -15 18";;

clm_era_soil01) file=ETHData/SOILLIQ_era_clm_01.nc;kindname="CLM/ERAi";climfield="soil moisture 0-10cm";flipcolor=11;;
clm_era_soil1) file=ETHData/SOILLIQ_era_clm_1.nc;kindname="CLM/ERAi";climfield="soil moisture 0-1m";flipcolor=11;;
clm_era_rain) file=ETHData/RAIN_era_clm.nc;kindname="CLM/ERAi";climfield="rain";flipcolor=11;;
clm_era_et) file=ETHData/ET_era_clm.nc;kindname="CLM/ERAi";climfield="evapotranspiration";;
clm_era_etp) file=ETHData/ETp_era_clm.nc;kindname="CLM/ERAi";climfield="potential evaporation";;
clm_wfdei_soil01) file=ETHData/SOILLIQ_wfdei_clm_01.nc;kindname="CLM/WFDEI";climfield="soil moisture 0-10cm";flipcolor=11;;
clm_wfdei_soil1) file=ETHData/SOILLIQ_wfdei_clm_1.nc;kindname="CLM/WFDEI";climfield="soil moisture 0-1m";flipcolor=11;;
clm_wfdei_rain) file=ETHData/RAIN_wfdei_clm.nc;kindname="CLM/WFDEI";climfield="rain";flipcolor=11;;
clm_wfdei_et) file=ETHData/ET_wfdei_clm.nc;kindname="CLM/WFDEI";climfield="evapotranspiration";;
clm_wfdei_etp) file=ETHData/ETp_wfdei_clm.nc;kindname="CLM/WFDEI";climfield="potential evaporation";;

emulate) file=CRUData/emulate_3.2_1850-2003.nc;kindname="EMULATE 3.2";climfield="SLP";NPERYEAR=366;map="set lon -70 50
set lat 25 70";;
trenberthslp) file=UCARData/ds010_1.nc;kindname="Trenberth";climfield="SLP";map='set mproj nps';;
gmslp) file=UKMOData/gmslp.ctl;kindname="UKMO";climfield="SLP";;
hadslp2r) file=UKMOData/hadslp2r.nc;kindname="HadSLP2r";climfield="SLP";;
hadslp2.0) file=UKMOData/hadslp2_0.nc;kindname="HadSLP2.0";climfield="SLP";;
hadsst2) file=UKMOData/hadsst2.ctl;kindname="HadSST2";climfield="SSTa";;
hadsst3) file=UKMOData/HadSST.3.1.1.0.median.nc;kindname="HadSST3110";climfield="SSTa";;
hadisst1) file=UKMOData/HadISST_sst.nc;kindname="HadISST1";climfield="SST";;
hadisst1_ice) file=UKMOData/HadISST_ice.nc;kindname="HadISST1";climfield="ice";;
gisst22) file=UKMOData/gisst22_sst.ctl;kindname="GISST2.2";climfield="SST";;
gisst22_ice) file=UKMOData/gisst22_ice.ctl;kindname="GISST2.2";climfield="ice";;
mslpnh) file=CRUData/mslpnh.ctl;kindname="Jones";climfield="SLP";map='set mproj nps';;
slp_mm) file=BernData/slp_mm.ctl;kindname="Luterbacher Maunders";climfield="SLP";map="set lon -25 30";;
slp_mm_1) file=BernData/slp_mm_1.ctl;kindname="Luterbacher Modern";climfield="SLP";map="set lon -25 30";;
Luterbacherslp) file=RapidData/recon.1750.1849.hadslp2r.1850.2008.seasonal.nc;kindname="Kuettel et al.";climfield="Sea Level Pressure";NOMISSING=nomissing;NPERYEAR=4;map='set lat 20 70
set lon -40 50';;
fresco_cloud) file=FRESCO/fresco_cloud.nc;kindname="FRESCO";climfield="cloud fraction";flipcolor=11;;
fresco_cloud_1) file=FRESCO/fresco_cloud_1.nc;kindname="FRESCO";climfield="cloud fraction";flipcolor=11;;
fresco_cloud_5) file=FRESCO/fresco_cloud_5.nc;kindname="FRESCO";climfield="cloud fraction";flipcolor=11;LSMASK=FRESCO/lsmask_5.nc;;
fresco6_cloud) file=FRESCO/fresco_cloud_fraction.nc;kindname="FRESCO v6";climfield="cloud fraction";flipcolor=11;;
fresco6_cloud_1) file=FRESCO/fresco_cloud_fraction_1.nc;kindname="FRESCO v6";climfield="cloud fraction";flipcolor=11;;
fresco_pressure) file=FRESCO/fresco_pressure.nc;kindname="FRESCO";climfield="cloud pressure";;
fresco_pressure_1) file=FRESCO/fresco_pressure_1.nc;kindname="FRESCO";climfield="cloud pressure";;
fresco_pressure_5) file=FRESCO/fresco_pressure_5.nc;kindname="FRESCO";climfield="cloud pressure";LSMASK=FRESCO/lsmask_5.nc;;
fresco6_pressure) file=FRESCO/fresco_cloud_pressure.nc;kindname="FRESCO v6";climfield="cloud pressure";;
fresco6_pressure_1) file=FRESCO/fresco_cloud_pressure_1.nc;kindname="FRESCO v6";climfield="cloud pressure";;
fresco6_ssi) file=FRESCO/fresco_ssi_fullsky.nc;kindname="FRESCO v6";climfield="ssi fullsky";flipcolor=11;;
fresco6_ssi_1) file=FRESCO/fresco_ssi_fullsky_1.nc;kindname="FRESCO v6";climfield="ssi fullsky";flipcolor=11;;

mohmat42) file="UKMOData/mohmat42.ctl";kindname="MOHMAT 4.2";climfield="Tair";;
mohmat43) file="UKMOData/mohmat43.ctl";kindname="MOHMAT 4.3";climfield="Tair";;
mohmat43a) file="UKMOData/MOHMAT43_anm56xx_corrected.nc";kindname="MOHMAT 4.3";climfield="Tair anom";;
hadmat1) file="UKMOData/HadMAT1_anm56jan2002wrtM5_corrected.nc";kindname="HadMAT1";climfield="Tair anom";;
hadnmat2) file="UKMOData/HadNMAT2.nc";kindname="HadNMAT2";climfield="Tair night";;
hadnmat2a) file="UKMOData/HadNMAT2a.nc";kindname="HadNMAT2";climfield="Tair night anom";;
hadnmat2u) file="UKMOData/HadNMAT2u.nc";kindname="HadNMAT2";climfield="Tair night uncert";;

tc_sio) file=UCLData/tc_sio.ctl;kindname="JISAO";climfield="no.tc";map='set lat -50 0
set lon 10 140';;
tc_sio_monthly) file=UCLData/tc_sio_monthly.ctl;kindname="JISAO";climfield="no.tc";map='set lat -50 0
set lon 10 140';;
ts_ntracks) file="MITData/tstracks.ctl";kindname="MIT";climfield="#TS tracks";;
tc_ntracks) file="MITData/tctracks.ctl";kindname="MIT";climfield="#TC tracks";;
ts_vmax) file="MITData/vmax.ctl";kindname="MIT";climfield="vmax";;
ts_pdi) file="MITData/pdi.ctl";kindname="MIT";climfield="PDI";;
nts) file="MITData/nts.ctl";kindname="MIT";climfield="TS within 160km";NPERYEAR=1;;
ntc) file="MITData/ntc.ctl";kindname="MIT";climfield="TC within 160km";NPERYEAR=1;;
ts_heat) file="AOMLData/heat.nc";kindname="AOML";climfield="TC Heat Potential";;
ts_heat_1) file="AOMLData/heat_1.nc";kindname="AOML";climfield="TC Heat Potential";;
nhsnow) file=SnowData/nhsnow.ctl;kindname="NOAA";climfield="snowcover";map='set mproj nps';flipcolor=11;;
rutgers_nhsnow) file=RutgersData/snow_rucl.nc;kindname="Rutgers";climfield="snowcover";map='set mproj nps';flipcolor=11;;
rutgers_nhsnow_daily) file=RutgersData/snow_rucl_day.nc;kindname="Rutgers";climfield="snowcover";map='set mproj nps';flipcolor=11;NPERYEAR=366;;
ice_index_n) file=NSIDCData/conc_n.nc;kindname=NSIDC;climfield="ice concentration";map='set mproj nps';;
ice_index_s) file=NSIDCData/conc_s.nc;kindname=NSIDC;climfield="ice concentration";map='set mproj sps';;
ice_bootstrap_n) file=NSIDCData/conc_bt_n.nc;kindname=bootstrap;climfield="ice concentration";map='set mproj nps';;
ice_bootstrap_s) file=NSIDCData/conc_bt_s.nc;kindname=bootstrap;climfield="ice concentration";map='set mproj sps';;
frz_depth) file=NSIDCData/frz_depth.ctl;kindname=NSIDC;climfield="freeze depth";NPERYEAR=1;map='set mproj nps';;
thw_depth) file=NSIDCData/thw_depth.ctl;kindname=NSIDC;climfield="thaw depth";NPERYEAR=1;map='set mproj nps';;
frz_depth_m) file=NSIDCData/frz_depth_m.ctl;kindname=NSIDC;climfield="freeze depth";map='set mproj nps';;
thw_depth_m) file=NSIDCData/thw_depth_m.ctl;kindname=NSIDC;climfield="thaw depth";map='set mproj nps';;
camsopi) file=NCEPData/camsopi.nc;kindname="CAMSOPI";climfield="prcp";;
camsopi_perc) file=NCEPData/camsopi_perc.nc;kindname="CAMSOPI";climfield="perc";;
noaa_olr) file=NOAAData/olr.mon.mean.nc;kindname="NOAA";climfield="OLR";;
msla) file=CLSData/msla_merged_1deg.ctl;kindname="CLS merged";climfield="sea level anomalies";;
esa_sla) file=ESAData/esacci_sla.nc;kindname="ESA CCI";climfield="sea level anomalies";;
copernicus_sla_daily) file=CDSData/copernicus_sla_daily.nc;kindname="C3S";climfield="sea level anomalies";NPERYEAR=366;;
copernicus_adt_daily) file=CDSData/copernicus_adt_daily.nc;kindname="C3S";climfield="dynamic topography";NPERYEAR=366;;
copernicus_ugos_daily) file=CDSData/copernicus_ugos_daily.nc;kindname="C3S";climfield="geostrophic u";NPERYEAR=366;;
copernicus_vgos_daily) file=CDSData/copernicus_vgos_daily.nc;kindname="C3S";climfield="geostrophic v";NPERYEAR=366;;
copernicus_sla) file=CDSData/copernicus_sla.nc;kindname="C3S";climfield="sea level anomalies";;
copernicus_adt) file=CDSData/copernicus_adt.nc;kindname="C3S";climfield="dynamic topography";;
copernicus_ugos) file=CDSData/copernicus_ugos.nc;kindname="C3S";climfield="geostrophic u";;
copernicus_vgos) file=CDSData/copernicus_vgos.nc;kindname="C3S";climfield="geostrophic v";;
nodc_heat700) file=NODCData/heat700.nc;kindname="NODC";climfield="0-700m heat content";;
nodc_heat2000) file=NODCData/heat2000.nc;kindname="NODC";climfield="0-2000m heat content";;
nodc_temp100) file=NODCData/temp100.nc;kindname="NODC";climfield="0-100m mean temperature";;
nodc_temp700) file=NODCData/temp700.nc;kindname="NODC";climfield="0-700m mean temperature";;
nodc_temp2000) file=NODCData/temp2000.nc;kindname="NODC";climfield="0-2000m mean temperature";;
heat700_jma) file=JMAData/heat700_jma.nc;kindanme="JMA";climfield="0-700m heat content";;
soda_heat750) file=SODAData/soda_750int.nc;kindanme="SODA";climfield="0-750m heat content";;
grace_land) file=GRACEData/grace_land.nc;kindname="GRACE";climfield="LWE";;
grace_ocean) file=GRACEData/grace_ocean.nc;kindname="GRACE";climfield="LWE";;
luge_crop) file=McGillData/glcrop_1700-2007_05.nc;kindname="LUGE";climfield="cropland fraction";NPERYEAR=1;;
luge_past) file=McGillData/glpast_1700-2007_05.nc;kindname="LUGE";climfield="pasture fraction";NPERYEAR=1;;
en3_sos) file=UKMOData/salt_EN3_v2a_ObjectiveAnalysis_5m.nc;kindname="EN3";climfield="SSS";;
en3_osc*) depth=${FORM_field#en3_osc};file=UKMOData/salt_EN3_v2a_ObjectiveAnalysis_sal${depth}.nc;kindname="EN3";climfield="sal${depth}";;
en3_ohc*) depth=${FORM_field#en3_ohc};file=UKMOData/temp_EN3_v2a_ObjectiveAnalysis_ohc${depth}.nc;kindname="EN3";climfield="ohc${depth}";;
en4_sos) file=UKMOData/salt_EN.4.2.1_ObjectiveAnalysis_5m.nc;kindname="EN4.2.1";climfield="SSS";;
en4_osc*) depth=${FORM_field#en4_osc};file=UKMOData/salt_EN.4.2.1_ObjectiveAnalysis_sal${depth}.nc;kindname="EN4.2.1";climfield="sal${depth}";;
en4_ohc*) depth=${FORM_field#en4_ohc};file=UKMOData/temp_EN.4.2.1_ObjectiveAnalysis_ohc${depth}.nc;kindname="EN4.2.1";climfield="ohc${depth}";;
bmrc_d20) file=BMRCData/d20.nc;kindname="PEODAS";climfield="D20";;

sos_u)     file="SOS/u_mean12.ctl";kindname="KNMI ERS";climfield="u";;
sos_v)     file="SOS/v_mean12.ctl";kindname="KNMI ERS";climfield="v";;
sos_speed)     file="SOS/speed_mean12.ctl";kindname="KNMI ERS";climfield="|u|";;
sos_tx)     file="SOS/tx_mean12.ctl";kindname="KNMI ERS";climfield="tx";;
sos_ty)     file="SOS/ty_mean12.ctl";kindname="KNMI ERS";climfield="ty";;
erswindu) file=CERSATData/erswindu.ctl;kindname="ERS";climfield="zonal wind";;
erswindv) file=CERSATData/erswindv.ctl;kindname="ERS";climfield="meridional wind";;
ersstrsu) file=CERSATData/ersstrsu.ctl;kindname="ERS";climfield="zonal wind stress";;
ersstrsv) file=CERSATData/ersstrsv.ctl;kindname="ERS";climfield="meridional wind stress";;

tao_sst) file=TAOData/tao_sst.nc;kindname="TAO";climfield="SST";map='set lat -10 10
set lon 130 280';;
tao_airt) file=TAOData/tao_airt.nc;kindname="TAO";climfield="air temp";map='set lat -10 10
set lon 130 280';;
tao_windu) file=TAOData/tao_windu.nc;kindname="TAO";climfield="zonal wind";map='set lat -10 10
set lon 130 280';;
tao_windv) file=TAOData/tao_windv.nc;kindname="TAO";climfield="meridional wind";map='set lat -10 10
set lon 130 280';;
tao_xstrs) file=TAOData/tao_tau_x.nc;kindname="TAO";climfield="zonal windstress";map='set lat -10 10
set lon 130 280';;
tao_ystrs) file=TAOData/tao_tau_y.nc;kindname="TAO";climfield="meridional windstress";map='set lat -10 10
set lon 130 280';;
tao_curu) file=TAOData/tao_curu.nc;kindname="TAO";climfield="zonal current";map='set lat 0
set lev 1 42
set lon 130 280';;
tao_curv) file=TAOData/tao_curv.nc;kindname="TAO";climfield="meridional current";map='set lat 0
set lev 1 42
set lon 130 280';;
tao_rh) file=TAOData/tao_rh.nc;kindname="TAO";climfield="relative humidity";map='set lat -10 10
set lon 130 280';;
tao_z20) file=TAOData/tao_z20.nc;kindname="TAO";climfield="20C isotherm";map='set lat -10 10
set lon 130 280';;
tao_heat) file=TAOData/tao_heat400.nc;kindname="TAO";climfield="heat content";map='set lat -10 10
set lon 130 280';;

tao_sst-5dy) file=TAOData/tao_sst-5dy.nc;kindname="TAO";climfield="SST";NPERYEAR=73;map='set lat -10 10
set lon 130 280';;
tao_airt-5dy) file=TAOData/tao_airt-5dy.nc;kindname="TAO";climfield="air temp";NPERYEAR=73;map='set lat -10 10
set lon 130 280';;
tao_windu-5dy) file=TAOData/tao_windu-5dy.nc;kindname="TAO";climfield="zonal wind";NPERYEAR=73;map='set lat -10 10
set lon 130 280';;
tao_windv-5dy) file=TAOData/tao_windv-5dy.nc;kindname="TAO";climfield="meridional wind";NPERYEAR=73;map='set lat -10 10
set lon 130 280';;
tao_xstrs-5dy) file=TAOData/tao_tau_x-5dy.nc;kindname="TAO";climfield="zonal windstress";NPERYEAR=73;map='set lat -10 10
set lon 130 280';;
tao_ystrs-5dy) file=TAOData/tao_tau_y-5dy.nc;kindname="TAO";climfield="meridional windstress";NPERYEAR=73;map='set lat -10 10
set lon 130 280';;
tao_curu-5dy) file=TAOData/tao_curu-5dy.nc;kindname="TAO";climfield="zonal current";NPERYEAR=73;map='set lat 0
set lev 1 42
set lon 130 280';;
tao_curv-5dy) file=TAOData/tao_curv-5dy.nc;kindname="TAO";climfield="meridional current";NPERYEAR=73;map='set lat 0
set lev 1 42
set lon 130 280';;
tao_rh-5dy) file=TAOData/tao_rh-5dy.nc;kindname="TAO";climfield="relative humidity";NPERYEAR=73;map='set lat -10 10
set lon 130 280';;
tao_z20-5dy) file=TAOData/tao_z20-5dy.nc;kindname="TAO";climfield="20C isotherm";NPERYEAR=73;map='set lat -10 10
set lon 130 280';;
tao_heat-5dy) file=TAOData/tao_heat400-5dy.nc;kindname="TAO";climfield="heat content";NPERYEAR=73;map='set lat -10 10
set lon 130 280';;

tao_sst-dy) file=TAOData/tao_sst-dy.nc;kindname="TAO";climfield="SST";NPERYEAR=73;map='set lat -10 10
set lon 130 280';;
tao_airt-dy) file=TAOData/tao_airt-dy.nc;kindname="TAO";climfield="air temp";NPERYEAR=73;map='set lat -10 10
set lon 130 280';;
tao_windu-dy) file=TAOData/tao_windu-dy.nc;kindname="TAO";climfield="zonal wind";NPERYEAR=73;map='set lat -10 10
set lon 130 280';;
tao_windv-dy) file=TAOData/tao_windv-dy.nc;kindname="TAO";climfield="meridional wind";NPERYEAR=73;map='set lat -10 10
set lon 130 280';;
tao_xstrs-dy) file=TAOData/tao_tau_x-dy.nc;kindname="TAO";climfield="zonal windstress";NPERYEAR=73;map='set lat -10 10
set lon 130 280';;
tao_ystrs-dy) file=TAOData/tao_tau_y-dy.nc;kindname="TAO";climfield="meridional windstress";NPERYEAR=73;map='set lat -10 10
set lon 130 280';;
tao_curu-dy) file=TAOData/tao_curu-dy.nc;kindname="TAO";climfield="zonal current";NPERYEAR=73;map='set lat 0
set lev 1 42
set lon 130 280';;
tao_curv-dy) file=TAOData/tao_curv-dy.nc;kindname="TAO";climfield="meridional current";NPERYEAR=73;map='set lat 0
set lev 1 42
set lon 130 280';;
tao_rh-dy) file=TAOData/tao_rh-dy.nc;kindname="TAO";climfield="relative humidity";NPERYEAR=73;map='set lat -10 10
set lon 130 280';;
tao_z20-dy) file=TAOData/tao_z20-dy.nc;kindname="TAO";climfield="20C isotherm";NPERYEAR=73;map='set lat -10 10
set lon 130 280';;
tao_heat-dy) file=TAOData/tao_heat400-dy.nc;kindname="TAO";climfield="heat content";NPERYEAR=73;map='set lat -10 10
set lon 130 280';;

soda_sst) file=SODAData/SODA_temp_1.nc;kindname="SODA";climfield="SST";;
soda_sss) file=SODAData/SODA_salt_1.nc;kindname="SODA";climfield="surface salinity";;
soda_u_1) file=SODAData/SODA_u_1.nc;kindname="SODA";climfield="zonal surface current";;
soda_v_1) file=SODAData/SODA_v_1.nc;kindname="SODA";climfield="meridional surface current";;
soda_heat750) file=SODAData/SODA_750int.nc;kindname=SODA;climfield="heat content 750m";;
soda_heat300) file=SODAData/SODA_300int.nc;kindname=SODA;climfield="heat content 300m";;
soda_u_int750) file=SODAData/SODA_u_750int.nc;kindname=SODA;climfield="u 0-750m";;
soda_u_int300) file=SODAData/SODA_u_300int.nc;kindname=SODA;climfield="u 0-300m";;
soda_v_int750) file=SODAData/SODA_v_750int.nc;kindname=SODA;climfield="v 0-750m";;
soda_v_int300) file=SODAData/SODA_v_300int.nc;kindname=SODA;climfield="v 0-300m";;

ozon) file=TOMSData/toms.ctl;kindname="TOMS";climfield="ozone";;
tomsai) file=TOMSData/toms2.ctl;kindname="TOMS";climfield="aerosol";;
o3col) file=TEMISData/o3col1.nc;kindname="KNMI MSR";climfield="ozone";;
gacp_tau) file=NASAData/gacp_tau.ctl;kindname="GACP";climfield="aerosol optical depth";;
gacp_a) file=NASAData/gacp_a.ctl;kindname="GACP";climfield="aerosol Angstrom exponent";;
eac3_aod550) file=EAC3/AOD550_mon.nc;kindname="EAC3";climfield="AOD550";;
eac3_aod550_day) file=EAC3/AOD550_day.nc;kindname="EAC3";climfield="AOD550";NPERYEAR=366;;
emep_so2_1) file=EMEPData/so2_emissions_1.ctl;kindname="EMEP";climfield="SO2 emissions";NPERYEAR=1;map='set lon -45 75
set lat 25 80';NPERYEAR=1;;
emep_so2_25) file=EMEPData/so2_emissions_25.ctl;kindname="EMEP";climfield="SO2 emissions";NPERYEAR=1;map='set lon -45 75
set lat 25 80';NPERYEAR=1;;
emep_so2_5) file=EMEPData/so2_emissions_5.ctl;kindname="EMEP";climfield="SO2 emissions";NPERYEAR=1;map='set lon -45 75
set lat 25 80';NPERYEAR=1;;
emep_nox_1) file=EMEPData/nox_emissions_1.ctl;kindname="EMEP";climfield="NOX emissions";NPERYEAR=1;map='set lon -45 75
set lat 25 80';NPERYEAR=1;;
emep_nox_25) file=EMEPData/nox_emissions_25.ctl;kindname="EMEP";climfield="NOX emissions";NPERYEAR=1;map='set lon -45 75
set lat 25 80';NPERYEAR=1;;
emep_nox_5) file=EMEPData/nox_emissions_5.ctl;kindname="EMEP";climfield="NOX emissions";NPERYEAR=1;map='set lon -45 75
set lat 25 80';NPERYEAR=1;;
ndvi) file=UMDData/gimms_ndvi_mo.nc;kindname="GIMMS";climfield="ndvi";;
ndvi_old) file=NASAData/ndvi.ctl;kindname="pathfinder";climfield="vegetation";;
merra_refet) file=UCSBData/ETos_p05.monthly_01.nc;kindname="MERRA/ASCE";climfield="RefET";;
fldas_sm0_10) file=FLDASData/FLDAS_NOAH01_C_GL_M.A1982_2018_sm00_10.nc;kindname="FLDAS";climfield="soil moisture 0-10cm";;
fldas_sm0_40) file=FLDASData/FLDAS_NOAH01_C_GL_M.A1982_2018_sm00_40.nc;kindname="FLDAS";climfield="soil moisture 0-40cm";;
pdsi-old) file=UCARData/pdsi.ctl;kindname="UCAR";climfield="drought index";;
pdsi) file=UCARData/pdsi.mon.mean.nc;kindname="UCAR";climfield="PDSI";;
sc_pdsi) file=UCARData/pdsisc.monthly.maps.1850-now.fawc=1.r2.5x2.5.ipe=2.nc;kindname="UCAR";climfield="scPDSI";;

pdsi_anzda) file=UNSWData/anzda5.nc;kindname="UNSW";climield="scPDSI";NPERYEAR=1;map='set lon 136 178.5
set lat -47 -11
set mpdset hires';;

mm05_z100) file=FUBData/mm05_z100.ctl;kindname="FUB";climfield="z100";map='set mproj nps';;
mm05_z50) file=FUBData/mm05_z50.ctl;kindname="FUB";climfield="z50";map='set mproj nps';;
mm05_z30) file=FUBData/mm05_z30.ctl;kindname="FUB";climfield="z30";map='set mproj nps';;
mm05_z10) file=FUBData/mm05_z10.ctl;kindname="FUB";climfield="z10";map='set mproj nps';;
mm05_t100) file=FUBData/mm05_t100.ctl;kindname="FUB";climfield="t100";map='set mproj nps';;
mm05_t50) file=FUBData/mm05_t50.ctl;kindname="FUB";climfield="t50";map='set mproj nps';;
mm05_t30) file=FUBData/mm05_t30.ctl;kindname="FUB";climfield="t30";map='set mproj nps';;
mm05_t10) file=FUBData/mm05_t10.ctl;kindname="FUB";climfield="t10";map='set mproj nps';;
mm10_z100) file=FUBData/mm10_z100.ctl;kindname="FUB";climfield="z100";map='set mproj nps';;
mm10_z50) file=FUBData/mm10_z50.ctl;kindname="FUB";climfield="z50";map='set mproj nps';;
mm10_z30) file=FUBData/mm10_z30.ctl;kindname="FUB";climfield="z30";map='set mproj nps';;
mm10_z10) file=FUBData/mm10_z10.ctl;kindname="FUB";climfield="z10";map='set mproj nps';;
mm10_t100) file=FUBData/mm10_t100.ctl;kindname="FUB";climfield="t100";map='set mproj nps';;
mm10_t50) file=FUBData/mm10_t50.ctl;kindname="FUB";climfield="t50";map='set mproj nps';;
mm10_t30) file=FUBData/mm10_t30.ctl;kindname="FUB";climfield="t30";map='set mproj nps';;
mm10_t10) file=FUBData/mm10_t10.ctl;kindname="FUB";climfield="t10";map='set mproj nps';;

coads_sst) file=COADSData/sst.mean.nc;kindname="ICOADS v2.5";climfield="SST";;
coads_air) file=COADSData/air.mean.nc;kindname="ICOADS v2.5";climfield="Tair";;
coads_cldc) file=COADSData/cldc.mean.nc;kindname="ICOADS v2.5";climfield="cloudcover";;
coads_slp) file=COADSData/slp.mean.nc;kindname="ICOADS v2.5";climfield="SLP";;
coads_uwnd) file=COADSData/uwnd.mean.nc;kindname="ICOADS v2.5";climfield="zonal wind";;
coads_vwnd) file=COADSData/vwnd.mean.nc;kindname="ICOADS v2.5";climfield="meridional wind";;
coads_upstr) file=COADSData/upstr.mean.nc;kindname="ICOADS v2.5";climfield="zonal wind stress";;
coads_vpstr) file=COADSData/vpstr.mean.nc;kindname="ICOADS v2.5";climfield="meridional wind stress";;
coads_wspd) file=COADSData/wspd.mean.nc;kindname="ICOADS v2.5";climfield="wind speed";;
coads_wspd3) file=COADSData/wspd3.mean.nc;kindname="ICOADS v2.5";climfield="wind speed cubed";;

coads_sst_n) file=COADSData/sst.nobs1.nc;kindname="ICOADS v2.5";climfield="nobs SST";;
coads_air_n) file=COADSData/air.nobs1.nc;kindname="ICOADS v2.5";climfield="nobs Tair";;
coads_cldc_n) file=COADSData/cldc.nobs1.nc;kindname="ICOADS v2.5";climfield="nobs cloudcover";;
coads_slp_n) file=COADSData/slp.nobs1.nc;kindname="ICOADS v2.5";climfield="nobs SLP";;
coads_uwnd_n) file=COADSData/uwnd.nobs1.nc;kindname="ICOADS v2.5";climfield="nobs zonal wind";;
coads_vwnd_n) file=COADSData/vwnd.nobs1.nc;kindname="ICOADS v2.5";climfield="nobs meridional wind";;
coads_upstr_n) file=COADSData/upstr.nobs1.nc;kindname="ICOADS v2.5";climfield="nobs zonal wind stress";;
coads_vpstr_n) file=COADSData/vpstr.nobs1.nc;kindname="ICOADS v2.5";climfield="nobs meridional wind stress";;
coads_wspd_n) file=COADSData/wspd.nobs1.nc;kindname="ICOADS v2.5";climfield="nobs wind speed";;
coads_wspd3_n) file=COADSData/wspd3.nobs1.nc;kindname="ICOADS v2.5";climfield="nobs wind speed cubed";;

nslp) file=NCEPNCAR40/slp.mon.mean.nc;kindname="NCEP/NCAR";climfield="SLP";;
nslp_daily) file=NCEPNCAR40/slp.daily.nc;kindname="NCEP/NCAR";climfield="SLP";NPERYEAR=366;;
nz850) file=NCEPNCAR40/z850.nc;kindname="NCEP/NCAR";climfield="850mb height";;
nz700) file=NCEPNCAR40/z700.nc;kindname="NCEP/NCAR";climfield="700mb height";;
nz500) file=NCEPNCAR40/z500.nc;kindname="NCEP/NCAR";climfield="500mb height";;
nz300) file=NCEPNCAR40/z300.nc;kindname="NCEP/NCAR";climfield="300mb height";;
nz200) file=NCEPNCAR40/z200.nc;kindname="NCEP/NCAR";climfield="200mb height";;
nz500_var) file=NCEPNCAR40/hgt500var.nc;kindname="NCEP/NCAR";climfield="2-7dy 500mb height variance";;
nz200_var) file=NCEPNCAR40/hgt200var.nc;kindname="NCEP/NCAR";climfield="2-7dy 200mb height variance";;
nz500_daily) file=NCEPNCAR40/hgt500.daily.nc;kindname="NCEP/NCAR";climfield="500mb height";NPERYEAR=366;;
nz200_daily) file=NCEPNCAR40/hgt200.daily.nc;kindname="NCEP/NCAR";climfield="200mb height";NPERYEAR=366;;
ntaux) file=NCEPNCAR40/uflx.sfc.mon.mean.nc;kindname="NCEP/NCAR";climfield="zonal windstress";;
nu10m) file=NCEPNCAR40/uwnd.10m.mon.mean.nc;kindname="NCEP/NCAR";climfield="10m zonal wind";;
nu850) file=NCEPNCAR40/u850.nc;kindname="NCEP/NCAR";climfield="850mb zonal wind";;
nu700) file=NCEPNCAR40/u700.nc;kindname="NCEP/NCAR";climfield="700mb zonal wind";;
nu500) file=NCEPNCAR40/u500.nc;kindname="NCEP/NCAR";climfield="500mb zonal wind";;
nu300) file=NCEPNCAR40/u300.nc;kindname="NCEP/NCAR";climfield="300mb zonal wind";;
nu200) file=NCEPNCAR40/u200.nc;kindname="NCEP/NCAR";climfield="200mb zonal wind";;
ntauy) file=NCEPNCAR40/vflx.sfc.mon.mean.nc;kindname="NCEP/NCAR";climfield="meridional windstress";;
nv10m) file=NCEPNCAR40/vwnd.10m.mon.mean.nc;kindname="NCEP/NCAR";climfield="10m meridional wind";;
nv850) file=NCEPNCAR40/v850.nc;kindname="NCEP/NCAR";climfield="850mb meridional wind";;
nv700) file=NCEPNCAR40/v700.nc;kindname="NCEP/NCAR";climfield="700mb meridional wind";;
nv500) file=NCEPNCAR40/v500.nc;kindname="NCEP/NCAR";climfield="500mb meridional wind";;
nv300) file=NCEPNCAR40/v300.nc;kindname="NCEP/NCAR";climfield="300mb meridional wind";;
nv200) file=NCEPNCAR40/v200.nc;kindname="NCEP/NCAR";climfield="200mb meridional wind";;
nwspd) file=NCEPNCAR40/nwindspeed.ctl;kindname="NCEP/NCAR";climfield="10m wind speed";LSMASK=NCEPNCAR40/lsmask.nc;;
nt2m)  file=NCEPNCAR40/nt2m.ctl;kindname="R2";climfield="2m temperature";LSMASK=NCEPNCAR40/lsmask.nc;;
nair)  file=NCEPNCAR40/air.2m.mon.mean.nc;kindname="NCEP/NCAR";climfield="2m temperature";LSMASK=NCEPNCAR40/lsmask.nc;;
nt2m_daily)  file=NCEPNCAR40/air.2m.gauss.daily.nc;kindname="NCEP/NCAR";climfield="2m temperature";LSMASK=NCEPNCAR40/lsmask.nc;NPERYEAR=366;;
ntsfc) file=NCEPNCAR40/skt.sfc.mon.mean.nc;kindname="NCEP/NCAR";climfield="surface temp";LSMASK=NCEPNCAR40/lsmask.nc;;
nt850) file=NCEPNCAR40/t850.nc;kindname="NCEP/NCAR";climfield="850mb temperature";;
nt700) file=NCEPNCAR40/t700.nc;kindname="NCEP/NCAR";climfield="700mb temperature";;
nt500) file=NCEPNCAR40/t500.nc;kindname="NCEP/NCAR";climfield="500mb temperature";;
nt300) file=NCEPNCAR40/t300.nc;kindname="NCEP/NCAR";climfield="300mb temperature";;
nt200) file=NCEPNCAR40/t200.nc;kindname="NCEP/NCAR";climfield="200mb temperature";;
nprate) file=NCEPNCAR40/prate.sfc.mon.mean.nc;kindname="NCEP/NCAR";climfield="precipitation";flipcolor=11;;
nprate_daily) file=NCEPNCAR40/prate.sfc.gauss.daily.nc;kindname="NCEP/NCAR";climfield="precipitation";flipcolor=11;NPERYEAR=366;;
nprcp) file=NCEPNCAR40/nprcp.new.ctl;kindname="R2";climfield="precipitation";flipcolor=11;;
nq850) file=NCEPNCAR40/q850.nc;kindname="NCEP/NCAR";climfield="850mb humidity";flipcolor=11;;
nq700) file=NCEPNCAR40/q700.nc;kindname="NCEP/NCAR";climfield="700mb humidity";flipcolor=11;;
nq500) file=NCEPNCAR40/q500.nc;kindname="NCEP/NCAR";climfield="500mb humidity";flipcolor=11;;
nqrel850) file=NCEPNCAR40/qrel850.nc;kindname="NCEP/NCAR";climfield="850mb relative humidity";flipcolor=11;;
nqrel700) file=NCEPNCAR40/qrel700.nc;kindname="NCEP/NCAR";climfield="700mb relative humidity";flipcolor=11;;
nqrel500) file=NCEPNCAR40/qrel500.nc;kindname="NCEP/NCAR";climfield="500mb relative humidity";flipcolor=11;;
nw850) file=NCEPNCAR40/vvel850.ctl;kindname="NCEP/NCAR";climfield="850mb vertical velocity";;
nw700) file=NCEPNCAR40/vvel700.ctl;kindname="NCEP/NCAR";climfield="700mb vertical velocity";;
nw500) file=NCEPNCAR40/vvel500.ctl;kindname="NCEP/NCAR";climfield="500mb vertical velocity";;
nw200) file=NCEPNCAR40/vvel200.ctl;kindname="NCEP/NCAR";climfield="200mb vertical velocity";;
nrv10m) file=NCEPNCAR40/rv10m.ctl;kindname="NCEP/NCAR";climfield="10m relative vorticity";;
nrv850) file=NCEPNCAR40/rv850.ctl;kindname="NCEP/NCAR";climfield="850mb relative vorticity";;
nrv700) file=NCEPNCAR40/rv700.ctl;kindname="NCEP/NCAR";climfield="700mb relative vorticity";;
nrv500) file=NCEPNCAR40/rv500.ctl;kindname="NCEP/NCAR";climfield="500mb relative vorticity";;
nrv200) file=NCEPNCAR40/rv200.ctl;kindname="NCEP/NCAR";climfield="200mb relative vorticity";;
ncurl) file=NCEPNCAR40/ncurl.ctl;kindname="NCEP/NCAR";climfield="curl wind stress";;
nhordiv10m) file=NCEPNCAR40/hordiv10m.ctl;kindname="NCEP/NCAR";climfield="10m horizontal divergence";;
nhordiv850) file=NCEPNCAR40/hordiv850.ctl;kindname="NCEP/NCAR";climfield="850mb horizontal divergence";;
nhordiv700) file=NCEPNCAR40/hordiv700.ctl;kindname="NCEP/NCAR";climfield="700mb horizontal divergence";;
nhordiv500) file=NCEPNCAR40/hordiv500.ctl;kindname="NCEP/NCAR";climfield="500mb horizontal divergence";;
nhordiv200) file=NCEPNCAR40/hordiv200.ctl;kindname="NCEP/NCAR";climfield="200mb horizontal divergence";;
npsi1000) file=NCEPNCAR40/npsi1000.ctl;kindname="NCEP/NCAR";climfield="1000mb stream function";;
npsi850) file=NCEPNCAR40/npsi850.ctl;kindname="NCEP/NCAR";climfield="850mb stream function";;
npsi700) file=NCEPNCAR40/npsi700.ctl;kindname="NCEP/NCAR";climfield="700mb stream function";;
npsi500) file=NCEPNCAR40/npsi500.ctl;kindname="NCEP/NCAR";climfield="500mb stream function";;
npsi200) file=NCEPNCAR40/npsi200.ctl;kindname="NCEP/NCAR";climfield="200mb stream function";;
nvs925) file=NCEPNCAR40/vs925.ctl;kindname="NCEP/NCAR";climfield="10m-850mb vertical shear";;
nvs775) file=NCEPNCAR40/vs775.ctl;kindname="NCEP/NCAR";climfield="850mb-700mb vertical shear";;
nvs600) file=NCEPNCAR40/vs600.ctl;kindname="NCEP/NCAR";climfield="700mb-500mb vertical shear";;
nvs350) file=NCEPNCAR40/vs350.ctl;kindname="NCEP/NCAR";climfield="500mb-200mb vertical shear";;
nlhtfl) file=NCEPNCAR40/lhtfl.sfc.mon.mean.nc;kindname="NCEP/NCAR";climfield="latent heat flux";LSMASK=NCEPNCAR40/lsmask.nc;;
nshtfl) file=NCEPNCAR40/shtfl.sfc.mon.mean.nc;kindname="NCEP/NCAR";climfield="sensible heat flux";LSMASK=NCEPNCAR40/lsmask.nc;;
netflx) file=NCEPNCAR40/netflx.sfc.mon.mean.nc;kindname="NCEP/NCAR";climfield="net heat flux";LSMASK=NCEPNCAR40/lsmask.nc;;
nolr) file=NCEPNCAR40/ulwrf.ntat.mon.mean.nc;kindname="NCEP/NCAR";climfield="OLR";;
umd_olr) file=UMDData/umd_olr_mo.nc;kindname="NOAA/UMD";climfield="OLR";;
umd_olr_daily) file=UMDData/umd_olr_dy.nc;kindname="NOAA/UMD";climfield="OLR";NPERYEAR=366;;
nevap) file=NCEPNCAR40/evap.mon.mean.nc;kindname="NCEP/NCAR";climfield="evaporation";;
npme) file=NCEPNCAR40/pme.mon.mean.nc;kindname="NCEP/NCAR";climfield="P-E";flipcolor=11;;
nnsr) file=NCEPNCAR40/nswrs.sfc.mon.mean.nc;kindname="NCEP/NCAR";climfield="net surface shortwave";LSMASK=NCEPNCAR40/lsmask.nc;;
nnlr) file=NCEPNCAR40/nlwrs.sfc.mon.mean.nc;kindname="NCEP/NCAR";climfield="net surface longwave";LSMASK=NCEPNCAR40/lsmask.nc;;
nsoil) file=NCEPNCAR40/soilw.0-10cm.mon.mean.nc;kindname="NCEP/NCAR";climfield="soil moisture";flipcolor=11;;

cfsr_slp) file=CFSR/cfsr_slp.nc;kindname=CFSR;climfield=SLP;;
cfsr_z850) file=CFSR/cfsr_hgt850.nc;kindname=CFSR;climfield="850mb height";;
cfsr_z700) file=CFSR/cfsr_hgt700.nc;kindname=CFSR;climfield="700mb height";;
cfsr_z500) file=CFSR/cfsr_hgt500.nc;kindname=CFSR;climfield="500mb height";;
cfsr_z300) file=CFSR/cfsr_hgt300.nc;kindname=CFSR;climfield="300mb height";;
cfsr_z200) file=CFSR/cfsr_hgt200.nc;kindname=CFSR;climfield="200mb height";;
cfsr_z100) file=CFSR/cfsr_hgt100.nc;kindname=CFSR;climfield="100mb height";;
cfsr_ts) file=CFSR/cfsr_tmpsfc.nc;kindname=CFSR;climfield=Tsfc;;
cfsr_t2m) file=CFSR/cfsr_tmp2m.nc;kindname=CFSR;climfield=T2m;LSMASK=CFSR/lsmask_f.nc;;
cfsr_t850) file=CFSR/cfsr_t850.nc;kindname=CFSR;climfield="850mb temperature";;
cfsr_t700) file=CFSR/cfsr_t700.nc;kindname=CFSR;climfield="700mb temperature";;
cfsr_t500) file=CFSR/cfsr_t500.nc;kindname=CFSR;climfield="500mb temperature";;
cfsr_t300) file=CFSR/cfsr_t300.nc;kindname=CFSR;climfield="300mb temperature";;
cfsr_t200) file=CFSR/cfsr_t200.nc;kindname=CFSR;climfield="200mb temperature";;
cfsr_t100) file=CFSR/cfsr_t100.nc;kindname=CFSR;climfield="100mb temperature";;
cfsr_tmin) file=CFSR/cfsr_tmin2m.nc;kindname=CFSR;climfield=Tmin;LSMASK=CFSR/lsmask_f.nc;;
cfsr_tmax) file=CFSR/cfsr_tmax2m.nc;kindname=CFSR;climfield=Tmax;LSMASK=CFSR/lsmask_f.nc;;
cfsr_uflx) file=CFSR/cfsr_uflx.nc;kindname=CFSR;climfield="zonal wind stress";LSMASK=CFSR/lsmask_f.nc;;
cfsr_u10m) file=CFSR/cfsr_u10m.nc;kindname=CFSR;climfield="10m zonal wind";LSMASK=CFSR/lsmask_f.nc;;
cfsr_u850) file=CFSR/cfsr_u850.nc;kindname=CFSR;climfield="850mb zonal wind";;
cfsr_u700) file=CFSR/cfsr_u700.nc;kindname=CFSR;climfield="700mb zonal wind";;
cfsr_u500) file=CFSR/cfsr_u500.nc;kindname=CFSR;climfield="500mb zonal wind";;
cfsr_u300) file=CFSR/cfsr_u300.nc;kindname=CFSR;climfield="300mb zonal wind";;
cfsr_u200) file=CFSR/cfsr_u200.nc;kindname=CFSR;climfield="200mb zonal wind";;
cfsr_u100) file=CFSR/cfsr_u100.nc;kindname=CFSR;climfield="100mb zonal wind";;
cfsr_vflx) file=CFSR/cfsr_vflx.nc;kindname=CFSR;climfield="meridional wind stress";LSMASK=CFSR/lsmask_f.nc;;
cfsr_v10m) file=CFSR/cfsr_v10m.nc;kindname=CFSR;climfield="10m meridional wind";LSMASK=CFSR/lsmask_f.nc;;
cfsr_v850) file=CFSR/cfsr_v850.nc;kindname=CFSR;climfield="850mb meridional wind";;
cfsr_v700) file=CFSR/cfsr_v700.nc;kindname=CFSR;climfield="700mb meridional wind";;
cfsr_v500) file=CFSR/cfsr_v500.nc;kindname=CFSR;climfield="500mb meridional wind";;
cfsr_v300) file=CFSR/cfsr_v300.nc;kindname=CFSR;climfield="300mb meridional wind";;
cfsr_v200) file=CFSR/cfsr_v200.nc;kindname=CFSR;climfield="200mb meridional wind";;
cfsr_v100) file=CFSR/cfsr_v100.nc;kindname=CFSR;climfield="100mb meridional wind";;
cfsr_w850) file=CFSR/cfsr_w850.nc;kindname=CFSR;climfield="850mb vertical wind";;
cfsr_w700) file=CFSR/cfsr_w700.nc;kindname=CFSR;climfield="700mb vertical wind";;
cfsr_w500) file=CFSR/cfsr_w500.nc;kindname=CFSR;climfield="500mb vertical wind";;
cfsr_w300) file=CFSR/cfsr_w300.nc;kindname=CFSR;climfield="300mb vertical wind";;
cfsr_w200) file=CFSR/cfsr_w200.nc;kindname=CFSR;climfield="200mb vertical wind";;
cfsr_w100) file=CFSR/cfsr_w100.nc;kindname=CFSR;climfield="100mb vertical wind";;
cfsr_q850) file=CFSR/cfsr_q850.nc;kindname=CFSR;climfield="850mb humidity";;
cfsr_q700) file=CFSR/cfsr_q700.nc;kindname=CFSR;climfield="700mb humidity";;
cfsr_q500) file=CFSR/cfsr_q500.nc;kindname=CFSR;climfield="500mb humidity";;
cfsr_q300) file=CFSR/cfsr_q300.nc;kindname=CFSR;climfield="300mb humidity";;
cfsr_q200) file=CFSR/cfsr_q200.nc;kindname=CFSR;climfield="200mb humidity";;
cfsr_q100) file=CFSR/cfsr_q100.nc;kindname=CFSR;climfield="100mb humidity";;
cfsr_qrel850) file=CFSR/cfsr_qrel850.nc;kindname=CFSR;climfield="850mb relative humidity";;
cfsr_qrel700) file=CFSR/cfsr_qrel700.nc;kindname=CFSR;climfield="700mb relative humidity";;
cfsr_qrel500) file=CFSR/cfsr_qrel500.nc;kindname=CFSR;climfield="500mb relative humidity";;
cfsr_qrel300) file=CFSR/cfsr_qrel300.nc;kindname=CFSR;climfield="300mb relative humidity";;
cfsr_qrel200) file=CFSR/cfsr_qrel200.nc;kindname=CFSR;climfield="200mb relative humidity";;
cfsr_qrel100) file=CFSR/cfsr_qrel100.nc;kindname=CFSR;climfield="100mb relative humidity";;
cfsr_lhf) file=CFSR/cfsr_lhtfl.nc;kindname=CFSR;climfield="latent heat flux";LSMASK=CFSR/lsmask_f.nc;;
cfsr_shf) file=CFSR/cfsr_shtfl.nc;kindname=CFSR;climfield="sensible heat flux";LSMASK=CFSR/lsmask_f.nc;;
cfsr_tp) file=CFSR/cfsr_prate.nc;kindname=CFSR;climfield="prcp";LSMASK=CFSR/lsmask_f.nc;;
cfsr_ssr) file=CFSR/cfsr_swrf_sfc.nc;kindname=CFSR;climfield="net SW sfc";LSMASK=CFSR/lsmask_f.nc;;
cfsr_str) file=CFSR/cfsr_lwrf_sfc.nc;kindname=CFSR;climfield="net LW sfc";LSMASK=CFSR/lsmask_f.nc;;
cfsr_tsr) file=CFSR/cfsr_swrf_toa.nc;kindname=CFSR;climfield="net SW TOA";LSMASK=CFSR/lsmask_f.nc;;
cfsr_ttr) file=CFSR/cfsr_ulwrf_toa.nc;kindname=CFSR;climfield="net LW TOA";LSMASK=CFSR/lsmask_f.nc;;

jra_*) var=${FORM_field#jra_};file="JRA-55/jra_${var}_mo.nc";kindname="JRA-55";climfield="$var";;

gldas_mon_spi12) var=${FORM_field#gldas_mon_};file="CMCCData/spi_MON_GLDAS_0p25_deg_hist_1970_2016_3_6_12_mths.nc";kindname="GLDAS";climfield="$var";;
gldas_mon_spi48) var=${FORM_field#gldas_mon_};file="CMCCData/spi_MON_GLDAS_0p25_deg_hist_1970_2016_24_36_48_mths.nc";kindname="GLDAS";climfield="$var";;
gldas_mon_spei12) var=${FORM_field#gldas_mon_};file="CMCCData/spei_MON_GLDAS_0p25_deg_hist_1970_2016_3_6_12_mths.nc";kindname="GLDAS";climfield="$var";;
gldas_mon_spei48) var=${FORM_field#gldas_mon_};file="CMCCData/spei_MON_GLDAS_0p25_deg_hist_1970_2016_24_36_48_mths.nc";kindname="GLDAS";climfield="$var";;
gldas_ann_*) var=${FORM_field#gldas_ann_};file="CMCCData/${var}_ANN_GLDAS_0p25_deg_hist_1970_2016.nc";kindname="GLDAS";climfield="$var";;
gldas_mon_*) var=${FORM_field#gldas_mon_};file="CMCCData/${var}_MON_GLDAS_0p25_deg_hist_1970_2016.nc";kindname="GLDAS";climfield="$var";;

cslp|cpsl|cprmsl) file=20C/prmsl.mon.mean.nc;kindname="20C";climfield="SLP";LSMASK=20C/land.nc;;
cprmsl_daily) file=20C/prmsl_daily.nc;kindname="20C";climfield="SLP";NPERYEAR=366;LSMASK=20C/land.nc;;
cslp_extended) file=20C/prmsl.mon.mean_extended.nc;kindname="20C+";climfield="SLP";LSMASK=20C/land.nc;;
cz850) file=20C/hgt850.nc;kindname="20C";climfield="850mb height";;
cz700) file=20C/hgt700.nc;kindname="20C";climfield="700mb height";;
cz500_daily) file=20C/hgt500_daily.nc;kindname="20C";climfield="500mb height";NPERYEAR=366;;
cz500) file=20C/hgt500.nc;kindname="20C";climfield="500mb height";;
cz300) file=20C/hgt300.nc;kindname="20C";climfield="300mb height";;
cz200) file=20C/hgt200.nc;kindname="20C";climfield="200mb height";;
ctaux) file=20C/uflx.mon.mean.nc;kindname="20C";climfield="zonal windstress";LSMASK=20C/land.nc;;
cu10m) file=20C/uwnd.10m.mon.mean.nc;kindname="20C";climfield="10m zonal wind";LSMASK=20C/land.nc;;
cu850) file=20C/uwnd850.nc;kindname="20C";climfield="850mb zonal wind";;
cu700) file=20C/uwnd700.nc;kindname="20C";climfield="700mb zonal wind";;
cu500) file=20C/uwnd500.nc;kindname="20C";climfield="500mb zonal wind";;
cu300) file=20C/uwnd300.nc;kindname="20C";climfield="300mb zonal wind";;
cu200) file=20C/uwnd200.nc;kindname="20C";climfield="200mb zonal wind";;
ctauy) file=20C/vflx.mon.mean.nc;kindname="20C";climfield="meridional windstress";LSMASK=20C/land.nc;;
cv10m) file=20C/vwnd.10m.mon.mean.nc;kindname="20C";climfield="10m meridional wind";LSMASK=20C/land.nc;;
cwspd) file=20C/wspd.10m.mon.mean.nc;kindname="20C";climfield="10m wind speed";LSMASK=20C/land.nc;;
cwspd_daily) file=20C/wspd.10m.max.mean.nc;kindname="20C";climfield="daily max 10m wind speed";LSMASK=20C/land.nc;NPERYEAR=366;;
cv850) file=20C/vwnd850.nc;kindname="20C";climfield="850mb meridional wind";;
cv700) file=20C/vwnd700.nc;kindname="20C";climfield="700mb meridional wind";;
cv500) file=20C/vwnd500.nc;kindname="20C";climfield="500mb meridional wind";;
cv300) file=20C/vwnd300.nc;kindname="20C";climfield="300mb meridional wind";;
cv200) file=20C/vwnd200.nc;kindname="20C";climfield="200mb meridional wind";;
cwspd) file=20C/wspd.mon.mean.nc;kindname="20C";climfield="10m wind speed";LSMASK=20C/land.nc;;
cair|ctas)  file=20C/air.2m.mon.mean.nc;kindname="20C";climfield="2m temperature";LSMASK=20C/land.nc;;
ct2m_daily)  file=20C/air.2m_daily.nc;kindname="20C";climfield="2m temperature";LSMASK=20C/land.nc;NPERYEAR=366;;
ctsfc) file=20C/air.sfc.mon.mean.nc;kindname="20C";climfield="surface temp";LSMASK=20C/land.nc;;
ctmin|ctasmin)  file=20C/tmin.2m.mon.mean.nc;kindname="20C";climfield="Tmin";LSMASK=20C/land.nc;;
ctmin_daily)  file=20C/tmin.2m_daily.nc;kindname="20C";climfield="Tmin";LSMASK=20C/land.nc;NPERYEAR=366;;
ctmax|ctasmax)  file=20C/tmax.2m.mon.mean.nc;kindname="20C";climfield="Tmax";LSMASK=20C/land.nc;;
ctmax_daily)  file=20C/tmax.2m_daily.nc;kindname="20C";climfield="Tmax";LSMASK=20C/land.nc;NPERYEAR=366;;
ct850_daily)  file=20C/air850_daily.nc;kindname="20C";climfield="T850";LSMASK=20C/land.nc;NPERYEAR=366;;
ct850) file=20C/air850.nc;kindname="20C";climfield="850mb temperature";;
ct700) file=20C/air700.nc;kindname="20C";climfield="700mb temperature";;
ct500) file=20C/air500.nc;kindname="20C";climfield="500mb temperature";;
ct300) file=20C/air300.nc;kindname="20C";climfield="300mb temperature";;
ct200) file=20C/air200.nc;kindname="20C";climfield="200mb temperature";;
cprate|cpr) file=20C/prate.mon.mean.nc;kindname="20C";climfield="precipitation";flipcolor=11;LSMASK=20C/land.nc;;
cprate_daily) file=20C/prate_daily.nc;kindname="20C";climfield="precipitation";flipcolor=11;LSMASK=20C/land.nc;NPERYEAR=366;;
cevap) file=20C/evap.mon.mean.nc;kindname="20C";climfield="evaporation";LSMASK=20C/land.nc;;
cpme) file=20C/pme.mon.mean.nc;kindname="20C";climfield="P-E";flipcolor=11;LSMASK=20C/land.nc;;
clhtfl) file=20C/lhtfl.mon.mean.nc;kindname="20C";climfield="latent heat flux";LSMASK=20C/land.nc;;
cq850) file=20C/shum850.nc;kindname="20C";climfield="850mb humidity";flipcolor=11;;
cq700) file=20C/shum700.nc;kindname="20C";climfield="700mb humidity";flipcolor=11;;
cq500) file=20C/shum500.nc;kindname="20C";climfield="500mb humidity";flipcolor=11;;
cshum2m) file=20C/shum.2m.mon.mean.nc;kindname="20C";climfield="spec. humidity";flipcolor=11;LSMASK=20C/land.nc;;
crhum2m) file=20C/rhum.2m.mon.mean.nc;kindname="20C";climfield="rel. humidity";flipcolor=11;LSMASK=20C/land.nc;;
cqrel850) file=20C/rhum850.nc;kindname="20C";climfield="850mb relative humidity";flipcolor=11;LSMASK=20C/land.nc;;
cqrel700) file=20C/rhum700.nc;kindname="20C";climfield="700mb relative humidity";flipcolor=11;LSMASK=20C/land.nc;;
cqrel500) file=20C/rhum500.nc;kindname="20C";climfield="500mb relative humidity";flipcolor=11;LSMASK=20C/land.nc;;
csoil) file=20C/soilm.mon.mean.nc;kindname="20C";climfield="soil moisture";flipcolor=11;LSMASK=20C/land.nc;;
cshtfl) file=20C/shtfl.mon.mean.nc;kindname="20C";climfield="sensible heat flux";LSMASK=20C/land.nc;;
cdswrf) file=20C/dswrf.sfc.mon.mean.nc;kindname="20C";climfield="surface downward solar flux";LSMASK=20C/land.nc;;

ncep_z20) file=NCEPData/ncep_z20.ctl;kindname="NCEP";climfield="Z20";map="set lon 120 290";;
ncep_ucur0) file=NCEPData/ncep_ucur0.ctl;kindname="NCEP";climfield="U at 5m";map="set lon 120 290";;
ncep_vcur0) file=NCEPData/ncep_vcur0.ctl;kindname="NCEP";climfield="V at 5m";map="set lon 120 290";;

era5_prcp_daily) file=ERA5/era5_tp_????????-????????.nc;kindname="ERA5";climfield="pr";NPERYEAR=366;LSMASK=ERA5/era5_000000_lsm.nc;export splitfield=true;;
era5_prcp_daily_e) file=ERA5/era5_tp_daily_extended.nc;kindname="ERA5+";climfield="pr";NPERYEAR=366;LSMASK=ERA5/era5_000000_lsm.nc;;
era5_t2m_daily) file=ERA5/era5_t2m_????????-????????.nc;kindname="ERA5";climfield="T2m";NPERYEAR=366;LSMASK=ERA5/era5_000000_lsm.nc;export splitfield=true;;
era5_t2m_daily_e) file=ERA5/era5_t2m_daily_extended.nc;kindname="ERA5+";climfield="T2m";NPERYEAR=366;LSMASK=ERA5/era5_000000_lsm.nc;;
era5_tdew_daily) file=ERA5/era5_tdew_????????-????????.nc;kindname="ERA5";climfield="Tdew";NPERYEAR=366;LSMASK=ERA5/era5_000000_lsm.nc;export splitfield=true;;
era5_tdew_daily_e) file=ERA5/era5_tdew_daily_extended.nc;kindname="ERA5+";climfield="Tdew";NPERYEAR=366;LSMASK=ERA5/era5_000000_lsm.nc;;
era5_twet_daily) file=ERA5/era5_twetbulb_????????-????????.nc;kindname="ERA5";climfield="Twetbulb";NPERYEAR=366;LSMASK=ERA5/era5_000000_lsm.nc;export splitfield=true;;
era5_twet_daily_e) file=ERA5/era5_twetbulb_daily_extended.nc;kindname="ERA5+";climfield="Twetbulb";NPERYEAR=366;LSMASK=ERA5/era5_000000_lsm.nc;;
era5_slp_daily) file=ERA5/era5_msl_????????-????????.nc;kindname="ERA5";climfield="MSL";NPERYEAR=366;LSMASK=ERA5/era5_000000_lsm.nc;export splitfield=true;;
era5_sp_daily) file=ERA5/era5_sp_????????-????????.nc;kindname="ERA5";climfield="SP";NPERYEAR=366;LSMASK=ERA5/era5_000000_lsm.nc;export splitfield=true;;
era5_slp_daily_e) file=ERA5/era5_msl_daily_extended.nc;kindname="ERA5+";climfield="MSL";NPERYEAR=366;LSMASK=ERA5/era5_000000_lsm.nc;;
era5_z500_daily) file=ERA5/era5_z500_????????-????????.nc;kindname="ERA5";climfield="Z500";NPERYEAR=366;LSMASK=ERA5/era5_000000_lsm.nc;export splitfield=true;;
era5_z500_daily_e) file=ERA5/era5_z500_daily_extended.nc;kindname="ERA5+";climfield="Z500";NPERYEAR=366;LSMASK=ERA5/era5_000000_lsm.nc;;
era5_t500_daily) file=ERA5/era5_t500_????????-????????.nc;kindname="ERA5";climfield="t500";NPERYEAR=366;LSMASK=ERA5/era5_000000_lsm.nc;export splitfield=true;;
era5_t500_daily_e) file=ERA5/era5_t500_daily_extended.nc;kindname="ERA5+";climfield="t500";NPERYEAR=366;LSMASK=ERA5/era5_000000_lsm.nc;;
era5_q500_daily) file=ERA5/era5_q500_????????-????????.nc;kindname="ERA5";climfield="q500";NPERYEAR=366;LSMASK=ERA5/era5_000000_lsm.nc;export splitfield=true;;
era5_q500_daily_e) file=ERA5/era5_q500_daily_extended.nc;kindname="ERA5+";climfield="q500";NPERYEAR=366;LSMASK=ERA5/era5_000000_lsm.nc;;
era5_tmin_daily) file=ERA5/era5_tmin_????????-????????.nc;kindname="ERA5";climfield="Tmin";NPERYEAR=366;LSMASK=ERA5/era5_000000_lsm.nc;export splitfield=true;;
era5_tmin_daily_e) file=ERA5/era5_tmin_daily_extended.nc;kindname="ERA5+";climfield="Tmin";NPERYEAR=366;LSMASK=ERA5/era5_000000_lsm.nc;;
era5_tmax_daily) file=ERA5/era5_tmax_????????-????????.nc;kindname="ERA5";climfield="Tmax";NPERYEAR=366;LSMASK=ERA5/era5_000000_lsm.nc;export splitfield=true;;
era5_tmax_daily_e) file=ERA5/era5_tmax_daily_extended.nc;kindname="ERA5+";climfield="Tmax";NPERYEAR=366;LSMASK=ERA5/era5_000000_lsm.nc;;
era5_evap_daily) file=ERA5/era5_evap_????????-????????.nc;kindname="ERA5";climfield="evap";NPERYEAR=366;LSMASK=ERA5/era5_000000_lsm.nc;export splitfield=true;;
era5_rsds_daily) file=ERA5/era5_rsds_????????-????????.nc;kindname="ERA5";climfield="rsds";NPERYEAR=366;LSMASK=ERA5/era5_000000_lsm.nc;export splitfield=true;;
era5_wspd_daily) file=ERA5/era5_sfcWind_????????-????????.nc;kindname="ERA5";climfield="wspd";NPERYEAR=366;LSMASK=ERA5/era5_000000_lsm.nc;export splitfield=true;;
era5_maxwspd_daily) file=ERA5/era5_sfcWindmax_????????-????????.nc;kindname="ERA5";climfield="max wspd";NPERYEAR=366;LSMASK=ERA5/era5_000000_lsm.nc;export splitfield=true;;

era5_slp|era5_psl|era5_msl) file=ERA5/era5_msl.nc;kindname="ERA5";climfield="MSL";LSMASK=ERA5/era5_000000_lsm.nc;;
era5_taux) file=ERA5/era5_ustrs.nc;kindname="ERA5";climfield="taux";LSMASK=ERA5/era5_000000_lsm.nc;;
era5_tauy) file=ERA5/era5_vstrs.nc;kindname="ERA5";climfield="tauy";LSMASK=ERA5/era5_000000_lsm.nc;;
era5_u10m) file=ERA5/era5_u10.nc;kindname="ERA5";climfield="u10";LSMASK=ERA5/era5_000000_lsm.nc;;
era5_v10m) file=ERA5/era5_v10.nc;kindname="ERA5";climfield="v10";LSMASK=ERA5/era5_000000_lsm.nc;;
era5_ts) file=ERA5/era5_ts.nc;kindname="ERA5";climfield="Tsfc";LSMASK=ERA5/era5_000000_lsm.nc;;
era5_t2m|era5_tas) file=ERA5/era5_t2m.nc;kindname="ERA5";climfield="T2m";LSMASK=ERA5/era5_000000_lsm.nc;;
era5_tmin) file=ERA5/era5_tmin.nc;kindname="ERA5";climfield="Tmin";LSMASK=ERA5/era5_000000_lsm.nc;;
era5_tmax) file=ERA5/era5_tmax.nc;kindname="ERA5";climfield="Tmax";LSMASK=ERA5/era5_000000_lsm.nc;;
era5_t2msst) file=ERA5/era5_t2msst.nc;kindname="ERA5";climfield="T2m/SST";LSMASK=ERA5/era5_000000_lsm.nc;;
era5_wspd) file=ERA5/era5_wspd.nc;kindname="ERA5";climfield="wind speed";LSMASK=ERA5/era5_000000_lsm.nc;;
era5_wspd_daily) file=ERA5/era5_wspd_daily.nc;kindname="ERA5";climfield="wind speed";LSMASK=ERA5/era5_000000_lsm.nc;;
era5_maxwspd_daily) file=ERA5/era5_maxwspd_daily.nc;kindname="ERA5";climfield="max wind speed";LSMASK=ERA5/era5_000000_lsm.nc;;
era5_ci) file=ERA5/era5_ci.nc;kindname="ERA5";climfield="sea-ice cover";LSMASK=ERA5/era5_000000_lsm.nc;;
era5_snd) file=ERA5/era5_snd.nc;kindname="ERA5";climfield="swe";LSMASK=ERA5/era5_000000_lsm.nc;;
era5_snld) file=ERA5/era5_snld.nc;kindname="ERA5";climfield="swe";LSMASK=ERA5/era5_000000_lsm.nc;;
era5_vap) file=ERA5/era5_vap.nc;kindname="ERA5";climfield="column vapour";LSMASK=ERA5/era5_000000_lsm.nc;;
era5_lhf) file=ERA5/era5_lhtfl.nc;kindname="ERA5";climfield="latent heat flux";LSMASK=ERA5/era5_000000_lsm.nc;;
era5_shf) file=ERA5/era5_shtfl.nc;kindname="ERA5";climfield="sensible heat flux";LSMASK=ERA5/era5_000000_lsm.nc;;
era5_trbflx) file=ERA5/era5_trbflx.nc;kindname="ERA5";climfield="turbulent heat flux";LSMASK=ERA5/era5_000000_lsm.nc;;
era5_snetflx) file=ERA5/era5_snetflx.nc;kindname="ERA5";climfield="sfc net heat flux";LSMASK=ERA5/era5_000000_lsm.nc;;
era5_huss) file=ERA5/era5_huss.nc;kindname="ERA5";climfield="spec humidity";LSMASK=ERA5/lsmask075.nc;;
era5_evap) file=ERA5/era5_evap.nc;kindname="ERA5";climfield="evaporation";LSMASK=ERA5/era5_000000_lsm.nc;;
era5_pme) file=ERA5/era5_pme.nc;kindname="ERA5";climfield="P-E";LSMASK=ERA5/era5_000000_lsm.nc;;
era5_tp|era5_pr) file=ERA5/era5_tp.nc;kindname="ERA5";climfield="precipitation";LSMASK=ERA5/era5_000000_lsm.nc;;
era5_ssr) file=ERA5/era5_ssr.nc;kindname="ERA5";climfield="SSR";LSMASK=ERA5/era5_000000_lsm.nc;;
era5_str) file=ERA5/era5_str.nc;kindname="ERA5";climfield="STR";LSMASK=ERA5/era5_000000_lsm.nc;;
era5_z*) lev=${FORM_field#era5_z};file=ERA5/${FORM_field}.nc;kindname="ERA5";climfield="z$lev";;
era5_t*) lev=${FORM_field#era5_t};file=ERA5/${FORM_field}.nc;kindname="ERA5";climfield="t$lev";;
era5_u*) lev=${FORM_field#era5_u};file=ERA5/${FORM_field}.nc;kindname="ERA5";climfield="u$lev";;
era5_v*) lev=${FORM_field#era5_v};file=ERA5/${FORM_field}.nc;kindname="ERA5";climfield="v$lev";;
era5_w*) lev=${FORM_field#era5_w};file=ERA5/${FORM_field}.nc;kindname="ERA5";climfield="w$lev";;
era5_q*) lev=${FORM_field#era5_q};file=ERA5/${FORM_field}.nc;kindname="ERA5";climfield="q$lev";;
era5_rh*) lev=${FORM_field#era5_rh};file=ERA5/${FORM_field}.nc;kindname="ERA5";climfield="rh$lev";;


erai_prcp_daily) file=ERA-interim/erai_tp_daily.nc;kindname="ERA-int";climfield="pr";NPERYEAR=366;LSMASK=ERA-interim/lsmask07.nc;;
erai_prcp_daily_e) file=ERA-interim/erai_tp_daily_extended.nc;kindname="ERA-int+";climfield="pr";NPERYEAR=366;LSMASK=ERA-interim/lsmask07.nc;;
erai_t2m_daily) file=ERA-interim/erai_t2m_daily.nc;kindname="ERA-int";climfield="T2m";NPERYEAR=366;LSMASK=ERA-interim/lsmask07.nc;;
erai_t2m_daily_e) file=ERA-interim/erai_t2m_daily_extended.nc;kindname="ERA-int+";climfield="T2m";NPERYEAR=366;LSMASK=ERA-interim/lsmask07.nc;;
erai_tdew_daily) file=ERA-interim/erai_tdew_daily.nc;kindname="ERA-int";climfield="Tdew";NPERYEAR=366;LSMASK=ERA-interim/lsmask07.nc;;
erai_tdew_daily_e) file=ERA-interim/erai_tdew_daily_extended.nc;kindname="ERA-int+";climfield="Tdew";NPERYEAR=366;LSMASK=ERA-interim/lsmask07.nc;;
erai_twet_daily) file=ERA-interim/erai_twetbulb_daily.nc;kindname="ERA-int";climfield="Twetbulb";NPERYEAR=366;LSMASK=ERA-interim/lsmask07.nc;;
erai_twet_daily_e) file=ERA-interim/erai_twetbulb_daily_extended.nc;kindname="ERA-int+";climfield="Twetbulb";NPERYEAR=366;LSMASK=ERA-interim/lsmask07.nc;;
erai_slp_daily) file=ERA-interim/erai_msl_daily.nc;kindname="ERA-int";climfield="MSL";NPERYEAR=366;LSMASK=ERA-interim/lsmask07.nc;;
erai_sp_daily) file=ERA-interim/erai_sp_daily.nc;kindname="ERA-int";climfield="SP";NPERYEAR=366;LSMASK=ERA-interim/lsmask07.nc;;
erai_slp_daily_e) file=ERA-interim/erai_msl_daily_extended.nc;kindname="ERA-int+";climfield="MSL";NPERYEAR=366;LSMASK=ERA-interim/lsmask07.nc;;
erai_z500_daily) file=ERA-interim/erai_z500_daily.nc;kindname="ERA-int";climfield="Z500";NPERYEAR=366;LSMASK=ERA-interim/lsmask07.nc;;
erai_z500_daily_e) file=ERA-interim/erai_z500_daily_extended.nc;kindname="ERA-int+";climfield="Z500";NPERYEAR=366;LSMASK=ERA-interim/lsmask07.nc;;
erai_t500_daily) file=ERA-interim/erai_t500_daily.nc;kindname="ERA-int";climfield="t500";NPERYEAR=366;LSMASK=ERA-interim/lsmask07.nc;;
erai_t500_daily_e) file=ERA-interim/erai_t500_daily_extended.nc;kindname="ERA-int+";climfield="t500";NPERYEAR=366;LSMASK=ERA-interim/lsmask07.nc;;
erai_q500_daily) file=ERA-interim/erai_q500_daily.nc;kindname="ERA-int";climfield="q500";NPERYEAR=366;LSMASK=ERA-interim/lsmask07.nc;;
erai_q500_daily_e) file=ERA-interim/erai_q500_daily_extended.nc;kindname="ERA-int+";climfield="q500";NPERYEAR=366;LSMASK=ERA-interim/lsmask07.nc;;
erai_tmin_daily) file=ERA-interim/erai_tmin_daily.nc;kindname="ERA-int";climfield="Tmin";NPERYEAR=366;LSMASK=ERA-interim/lsmask07.nc;;
erai_tmin_daily_e) file=ERA-interim/erai_tmin_daily_extended.nc;kindname="ERA-int+";climfield="Tmin";NPERYEAR=366;LSMASK=ERA-interim/lsmask07.nc;;
erai_tmax_daily) file=ERA-interim/erai_tmax_daily.nc;kindname="ERA-int";climfield="Tmax";NPERYEAR=366;LSMASK=ERA-interim/lsmask07.nc;;
erai_tmax_daily_e) file=ERA-interim/erai_tmax_daily_extended.nc;kindname="ERA-int+";climfield="Tmax";NPERYEAR=366;LSMASK=ERA-interim/lsmask07.nc;;
erai_evap_daily) file=ERA-interim/erai_evap_daily.nc;kindname="ERA-int";climfield="evap";NPERYEAR=366;LSMASK=ERA-interim/lsmask07.nc;;
erai_evappot_daily) file=ERA-interim/erai_evappot_daily.nc;kindname="ERA-int";climfield="potential evaporation";NPERYEAR=366;LSMASK=ERA-interim/lsmask07.nc;;
erai_rsds_daily) file=ERA-interim/erai_rsds_daily.nc;kindname="ERA-int";climfield="rsds";NPERYEAR=366;LSMASK=ERA-interim/lsmask07.nc;;

erai_slp|erai_psl|erai_msl) file=ERA-interim/erai_msl.nc;kindname="ERA-int";climfield="MSL";LSMASK=ERA-interim/lsmask07.nc;;
erai_slp_e|erai_msl_e) file=ERA-interim/erai_msl_extended.nc;kindname="ERA-int+";climfield="MSL";LSMASK=ERA-interim/lsmask07.nc;;
erai_taux) file=ERA-interim/erai_ustrs.nc;kindname="ERA-int";climfield="taux";LSMASK=ERA-interim/lsmask07.nc;;
erai_tauy) file=ERA-interim/erai_vstrs.nc;kindname="ERA-int";climfield="tauy";LSMASK=ERA-interim/lsmask07.nc;;
erai_u10m) file=ERA-interim/erai_u10.nc;kindname="ERA-int";climfield="u10";LSMASK=ERA-interim/lsmask07.nc;;
erai_v10m) file=ERA-interim/erai_v10.nc;kindname="ERA-int";climfield="v10";LSMASK=ERA-interim/lsmask07.nc;;
erai_ts) file=ERA-interim/erai_ts.nc;kindname="ERA-int";climfield="Tsfc";LSMASK=ERA-interim/lsmask07.nc;;
erai_t2m|erai_tas) file=ERA-interim/erai_t2m.nc;kindname="ERA-int";climfield="T2m";LSMASK=ERA-interim/lsmask07.nc;;
erai_t2m_e) file=ERA-interim/erai_t2m_extended.nc;kindname="ERA-int+";climfield="T2m";LSMASK=ERA-interim/lsmask07.nc;;
erai_tmin) file=ERA-interim/erai_tmin.nc;kindname="ERA-int";climfield="Tmin";LSMASK=ERA-interim/lsmask07.nc;;
erai_tmin_e) file=ERA-interim/erai_tmin_extended.nc;kindname="ERA-int+";climfield="Tmin";LSMASK=ERA-interim/lsmask07.nc;;
erai_tmax) file=ERA-interim/erai_tmax.nc;kindname="ERA-int";climfield="Tmax";LSMASK=ERA-interim/lsmask07.nc;;
erai_tmax_e) file=ERA-interim/erai_tmax_extended.nc;kindname="ERA-int+";climfield="Tmax";LSMASK=ERA-interim/lsmask07.nc;;
erai_t2msst) file=ERA-interim/erai_t2msst.nc;kindname="ERA-int";climfield="T2m/SST";LSMASK=ERA-interim/lsmask07.nc;;
erai_wspd) file=ERA-interim/erai_wspd.nc;kindname="ERA-int";climfield="wind speed";LSMASK=ERA-interim/lsmask07.nc;;
erai_wspd_daily) file=ERA-interim/erai_wspd_daily.nc;kindname="ERA-int";climfield="wind speed";LSMASK=ERA-interim/lsmask07.nc;;
erai_maxwspd_daily) file=ERA-interim/erai_maxwspd_daily.nc;kindname="ERA-int";climfield="max wind speed";LSMASK=ERA-interim/lsmask07.nc;;
erai_ci) file=ERA-interim/erai_ci.nc;kindname="ERA-int";climfield="sea-ice cover";LSMASK=ERA-interim/lsmask07.nc;;
erai_snd) file=ERA-interim/erai_snd.nc;kindname="ERA-int";climfield="snow depth";LSMASK=ERA-interim/lsmask07.nc;;
erai_vap) file=ERA-interim/erai_vap.nc;kindname="ERA-int";climfield="column vapour";LSMASK=ERA-interim/lsmask07.nc;;
erai_lhf) file=ERA-interim/erai_lhtfl.nc;kindname="ERA-int";climfield="latent heat flux";LSMASK=ERA-interim/lsmask07.nc;;
erai_shf) file=ERA-interim/erai_shtfl.nc;kindname="ERA-int";climfield="sensible heat flux";LSMASK=ERA-interim/lsmask07.nc;;
erai_trbflx) file=ERA-interim/erai_trbflx.nc;kindname="ERA-int";climfield="turbulent heat flux";LSMASK=ERA-interim/lsmask07.nc;;
erai_snetflx) file=ERA-interim/erai_snetflx.nc;kindname="ERA-int";climfield="sfc net heat flux";LSMASK=ERA-interim/lsmask07.nc;;
erai_huss) file=ERA-interim/erai_huss.nc;kindname="ERA-int";climfield="spec humidity";LSMASK=ERA-interim/lsmask075.nc;;
erai_evap) file=ERA-interim/erai_evap.nc;kindname="ERA-int";climfield="evaporation";LSMASK=ERA-interim/lsmask07.nc;;
erai_evappot) file=ERA-interim/erai_evappot.nc;kindname="ERA-int";climfield="potential evaporation";LSMASK=ERA-interim/lsmask07.nc;;
erai_pme) file=ERA-interim/erai_pme.nc;kindname="ERA-int";climfield="P-E";LSMASK=ERA-interim/lsmask07.nc;;
erai_tp|erai_pr) file=ERA-interim/erai_tp.nc;kindname="ERA-int";climfield="precipitation";LSMASK=ERA-interim/lsmask07.nc;;
erai_ssr) file=ERA-interim/erai_ssr.nc;kindname="ERA-int";climfield="SSR";LSMASK=ERA-interim/lsmask07.nc;;
erai_str) file=ERA-interim/erai_str.nc;kindname="ERA-int";climfield="STR";LSMASK=ERA-interim/lsmask07.nc;;
erai_z*_e) lev=${FORM_field#erai_z};file=ERA-interim/${FORM_field}xtended.nc;kindname="ERA-int+";climfield="z$lev";;
erai_z*) lev=${FORM_field#erai_z};file=ERA-interim/${FORM_field}.nc;kindname="ERA-int";climfield="z$lev";;
erai_t*) lev=${FORM_field#erai_t};file=ERA-interim/${FORM_field}.nc;kindname="ERA-int";climfield="t$lev";;
erai_u*) lev=${FORM_field#erai_u};file=ERA-interim/${FORM_field}.nc;kindname="ERA-int";climfield="u$lev";;
erai_v*) lev=${FORM_field#erai_v};file=ERA-interim/${FORM_field}.nc;kindname="ERA-int";climfield="v$lev";;
erai_w*) lev=${FORM_field#erai_w};file=ERA-interim/${FORM_field}.nc;kindname="ERA-int";climfield="w$lev";;
erai_q*) lev=${FORM_field#erai_q};file=ERA-interim/${FORM_field}.nc;kindname="ERA-int";climfield="q$lev";;
erai_rh*) lev=${FORM_field#erai_rh};file=ERA-interim/${FORM_field}.nc;kindname="ERA-int";climfield="rh$lev";;

erai_txx|erai_tnn|erai_rx?day) file=ERA-interim/${FORM_field}.nc;kindname="ERA-int";climfield=${FORM_field#erai_};NPERYEAR=1;LSMASK=ERA-interim/lsmask07.nc;;

era20c_slp|era20c_psl|era20c_msl) file=ERA-20C/era20c_msl.nc;kindname="ERA-20C";climfield="MSL";LSMASK=ERA-20C/lsmask64.nc;;
era20c_slp_daily) file=ERA-20C/era20c_msl_daily.nc;kindname="ERA-20C";climfield="MSL";LSMASK=ERA-20C/lsmask64.nc;NPERYEAR=366;;
era20c_taux) file=ERA-20C/era20c_ustrs.nc;kindname="ERA-20C";climfield="taux";LSMASK=ERA-20C/lsmask64.nc;;
era20c_tauy) file=ERA-20C/era20c_vstrs.nc;kindname="ERA-20C";climfield="tauy";LSMASK=ERA-20C/lsmask64.nc;;
era20c_u10m) file=ERA-20C/era20c_u10.nc;kindname="ERA-20C";climfield="u10";LSMASK=ERA-20C/lsmask64.nc;;
era20c_v10m) file=ERA-20C/era20c_v10.nc;kindname="ERA-20C";climfield="v10";LSMASK=ERA-20C/lsmask64.nc;;
era20c_ts) file=ERA-20C/era20c_ts.nc;kindname="ERA-20C";climfield="Tsfc";LSMASK=ERA-20C/lsmask64.nc;;
era20c_t2m|era20c_tas) file=ERA-20C/era20c_t2m.nc;kindname="ERA-20C";climfield="T2m";LSMASK=ERA-20C/lsmask64.nc;;
era20c_t2m_daily) file=ERA-20C/era20c_t2m_daily.nc;kindname="ERA-20C";climfield="T2m";LSMASK=ERA-20C/lsmask64.nc;NPERYEAR=366;;
era20c_tmin) file=ERA-20C/era20c_tmin.nc;kindname="ERA-20C";climfield="Tmin";LSMASK=ERA-20C/lsmask64.nc;;
era20c_tmax) file=ERA-20C/era20c_tmax.nc;kindname="ERA-20C";climfield="Tmax";LSMASK=ERA-20C/lsmask64.nc;;
era20c_t2msst) file=ERA-20C/era20c_t2msst.nc;kindname="ERA-20C";climfield="T2m/SST";LSMASK=ERA-20C/lsmask64.nc;;
era20c_wspd) file=ERA-20C/era20c_wspd.nc;kindname="ERA-20C";climfield="wind speed";LSMASK=ERA-20C/lsmask64.nc;;
era20c_ci) file=ERA-20C/era20c_ci.nc;kindname="ERA-20C";climfield="sea-ice cover";LSMASK=ERA-20C/lsmask64.nc;;
era20c_snd) file=ERA-20C/era20c_snd.nc;kindname="ERA-20C";climfield="snow depth";LSMASK=ERA-20C/lsmask64.nc;;
era20c_lhf) file=ERA-20C/era20c_lhtfl.nc;kindname="ERA-20C";climfield="latent heat flux";LSMASK=ERA-20C/lsmask64.nc;;
era20c_shf) file=ERA-20C/era20c_shtfl.nc;kindname="ERA-20C";climfield="sensible heat flux";LSMASK=ERA-20C/lsmask64.nc;;
era20c_huss) file=ERA-20C/era20c_huss.nc;kindname="ERA-20C";climfield="spec humidity";LSMASK=ERA-20C/lsmask075.nc;;
era20c_evap) file=ERA-20C/era20c_evap.nc;kindname="ERA-20C";climfield="evaporation";LSMASK=ERA-20C/lsmask64.nc;;
era20c_pme) file=ERA-20C/era20c_pme.nc;kindname="ERA-20C";climfield="P-E";LSMASK=ERA-20C/lsmask64.nc;;
era20c_tp|era20c_pr) file=ERA-20C/era20c_tp.nc;kindname="ERA-20C";climfield="precipitation";LSMASK=ERA-20C/lsmask64.nc;;
era20c_prcp_daily) file=ERA-20C/era20c_tp_daily.nc;kindname="ERA-20C";climfield="precipitation";LSMASK=ERA-20C/lsmask64.nc;NPERYEAR=366;;
era20c_ssr) file=ERA-20C/era20c_ssr.nc;kindname="ERA-20C";climfield="SSR";LSMASK=ERA-20C/lsmask64.nc;;
era20c_str) file=ERA-20C/era20c_str.nc;kindname="ERA-20C";climfield="STR";LSMASK=ERA-20C/lsmask64.nc;;
era20c_z*_daily) lev=${FORM_field#era20c_z};lev=${lev%_daily};file=ERA-20C/${FORM_field}.nc;kindname="ERA-20C";climfield="z$lev";NPERYEAR=366;;
era20c_z*) lev=${FORM_field#era20c_z};file=ERA-20C/${FORM_field}.nc;kindname="ERA-20C";climfield="z$lev";;
era20c_t*) lev=${FORM_field#era20c_t};file=ERA-20C/${FORM_field}.nc;kindname="ERA-20C";climfield="t$lev";;
era20c_u*) lev=${FORM_field#era20c_u};file=ERA-20C/${FORM_field}.nc;kindname="ERA-20C";climfield="u$lev";;
era20c_v*) lev=${FORM_field#era20c_v};file=ERA-20C/${FORM_field}.nc;kindname="ERA-20C";climfield="v$lev";;
era20c_w*) lev=${FORM_field#era20c_w};file=ERA-20C/${FORM_field}.nc;kindname="ERA-20C";climfield="w$lev";;
era20c_q*) lev=${FORM_field#era20c_q};file=ERA-20C/${FORM_field}.nc;kindname="ERA-20C";climfield="q$lev";;

merra_slp) file=MERRA/merra_slp.nc;kindname="MERRA";climfield="SLP";LSMASK=MERRA/lsmask.nc;;
merra_taux) file=MERRA/merra_taux.nc;kindname="MERRA";climfield="taux";LSMASK=MERRA/lsmask.nc;;
merra_tauy) file=MERRA/merra_tauy.nc;kindname="MERRA";climfield="tauy";LSMASK=MERRA/lsmask.nc;;
merra_u10m) file=MERRA/merra_u10.nc;kindname="MERRA";climfield="u10";LSMASK=MERRA/lsmask.nc;;
merra_v10m) file=MERRA/merra_v10.nc;kindname="MERRA";climfield="v10";LSMASK=MERRA/lsmask.nc;;
merra_ts) file=MERRA/merra_ts.nc;kindname="MERRA";climfield="Tsfc";LSMASK=MERRA/lsmask.nc;;
merra_t2m) file=MERRA/merra_t2m.nc;kindname="MERRA";climfield="T2m";LSMASK=MERRA/lsmask.nc;;
merra_t2msst) file=MERRA/merra_t2msst.nc;kindname="MERRA";climfield="T2m/SST";LSMASK=MERRA/lsmask.nc;;
merra_wspd) file=MERRA/merra_wspd.nc;kindname="MERRA";climfield="wind speed";LSMASK=MERRA/lsmask.nc;;
merra_lhf) file=MERRA/merra_lhtfl.nc;kindname="MERRA";climfield="latent heat flux";LSMASK=MERRA/lsmask.nc;;
merra_shf) file=MERRA/merra_shtfl.nc;kindname="MERRA";climfield="sensible heat flux";LSMASK=MERRA/lsmask.nc;;
merra_pme) file=MERRA/merra_pme.nc;kindname="MERRA";climfield="P-E";LSMASK=MERRA/lsmask.nc;;
merra_evap) file=MERRA/merra_evap.nc;kindname="MERRA";climfield="evaporation";LSMASK=MERRA/lsmask.nc;;
merra_tp) file=MERRA/merra_tp.nc;kindname="MERRA";climfield="precipitation";LSMASK=MERRA/lsmask.nc;;
merra_ssr) file=MERRA/merra_ssr.nc;kindname="MERRA";climfield="SSR";LSMASK=MERRA/lsmask.nc;;
merra_str) file=MERRA/merra_str.nc;kindname="MERRA";climfield="STR";LSMASK=MERRA/lsmask.nc;;
merra_z*) lev=${FORM_field#merra_z};file=MERRA/${FORM_field}.nc;kindname="MERRA";climfield="z$lev";;
merra_t*) lev=${FORM_field#merra_t};file=MERRA/${FORM_field}.nc;kindname="MERRA";climfield="t$lev";;
merra_u*) lev=${FORM_field#merra_u};file=MERRA/${FORM_field}.nc;kindname="MERRA";climfield="u$lev";;
merra_v*) lev=${FORM_field#merra_v};file=MERRA/${FORM_field}.nc;kindname="MERRA";climfield="v$lev";;
merra_w*) lev=${FORM_field#merra_w};file=MERRA/${FORM_field}.nc;kindname="MERRA";climfield="w$lev";;
merra_q*) lev=${FORM_field#merra_q};file=MERRA/${FORM_field}.nc;kindname="MERRA";climfield="q$lev";;


ecmwf_t2m) file=ECMWFData/ecmwf_t2m.ctl;kindname="ECMWF";climfield="T2m";;
ecmwf_t2m_1) file=ECMWFData/ecmwf_t2m_1.ctl;kindname="ECMWF";climfield="+0 T2m";;
ecmwf_t2m_2) file=ECMWFData/ecmwf_t2m_2.ctl;kindname="ECMWF";climfield="+1 T2m";;
ecmwf_t2m_3) file=ECMWFData/ecmwf_t2m_3.ctl;kindname="ECMWF";climfield="+2 T2m";;
ecmwf_t2m_4) file=ECMWFData/ecmwf_t2m_4.ctl;kindname="ECMWF";climfield="+3 T2m";;
ecmwf_t2m_5) file=ECMWFData/ecmwf_t2m_5.ctl;kindname="ECMWF";climfield="+4 T2m";;
ecmwf_t2m_6) file=ECMWFData/ecmwf_t2m_6.ctl;kindname="ECMWF";climfield="+5 T2m";;
ecmwf_t2m_jan) file=ECMWFData/ecmwf_t2m_jan.ctl;kindname="ECMWF";climfield="1Jan T2m";;
ecmwf_t2m_feb) file=ECMWFData/ecmwf_t2m_feb.ctl;kindname="ECMWF";climfield="1Feb T2m";;
ecmwf_t2m_mar) file=ECMWFData/ecmwf_t2m_mar.ctl;kindname="ECMWF";climfield="1Mar T2m";;
ecmwf_t2m_apr) file=ECMWFData/ecmwf_t2m_apr.ctl;kindname="ECMWF";climfield="1Apr T2m";;
ecmwf_t2m_may) file=ECMWFData/ecmwf_t2m_may.ctl;kindname="ECMWF";climfield="1May T2m";;
ecmwf_t2m_jun) file=ECMWFData/ecmwf_t2m_jun.ctl;kindname="ECMWF";climfield="1Jun T2m";;
ecmwf_t2m_jul) file=ECMWFData/ecmwf_t2m_jul.ctl;kindname="ECMWF";climfield="1Jul T2m";;
ecmwf_t2m_aug) file=ECMWFData/ecmwf_t2m_aug.ctl;kindname="ECMWF";climfield="1Aug T2m";;
ecmwf_t2m_sep) file=ECMWFData/ecmwf_t2m_sep.ctl;kindname="ECMWF";climfield="1Sep T2m";;
ecmwf_t2m_oct) file=ECMWFData/ecmwf_t2m_oct.ctl;kindname="ECMWF";climfield="1Oct T2m";;
ecmwf_t2m_nov) file=ECMWFData/ecmwf_t2m_nov.ctl;kindname="ECMWF";climfield="1Nov T2m";;
ecmwf_t2m_dec) file=ECMWFData/ecmwf_t2m_dec.ctl;kindname="ECMWF";climfield="1Dec T2m";;
ecmwf_prcp) file=ECMWFData/ecmwf_prcp.ctl;kindname="ECMWF";climfield="precipitation";;
ecmwf_prcp_1) file=ECMWFData/ecmwf_prcp_1.ctl;kindname="ECMWF";climfield="+0 precipitation";;
ecmwf_prcp_2) file=ECMWFData/ecmwf_prcp_2.ctl;kindname="ECMWF";climfield="+1 precipitation";;
ecmwf_prcp_3) file=ECMWFData/ecmwf_prcp_3.ctl;kindname="ECMWF";climfield="+2 precipitation";;
ecmwf_prcp_4) file=ECMWFData/ecmwf_prcp_4.ctl;kindname="ECMWF";climfield="+3 precipitation";;
ecmwf_prcp_5) file=ECMWFData/ecmwf_prcp_5.ctl;kindname="ECMWF";climfield="+4 precipitation";;
ecmwf_prcp_6) file=ECMWFData/ecmwf_prcp_6.ctl;kindname="ECMWF";climfield="+5 precipitation";;
ecmwf_prcp_jan) file=ECMWFData/ecmwf_prcp_jan.ctl;kindname="ECMWF";climfield="1Jan precipitation";;
ecmwf_prcp_feb) file=ECMWFData/ecmwf_prcp_feb.ctl;kindname="ECMWF";climfield="1Feb precipitation";;
ecmwf_prcp_mar) file=ECMWFData/ecmwf_prcp_mar.ctl;kindname="ECMWF";climfield="1Mar precipitation";;
ecmwf_prcp_apr) file=ECMWFData/ecmwf_prcp_apr.ctl;kindname="ECMWF";climfield="1Apr precipitation";;
ecmwf_prcp_may) file=ECMWFData/ecmwf_prcp_may.ctl;kindname="ECMWF";climfield="1May precipitation";;
ecmwf_prcp_jun) file=ECMWFData/ecmwf_prcp_jun.ctl;kindname="ECMWF";climfield="1Jun precipitation";;
ecmwf_prcp_jul) file=ECMWFData/ecmwf_prcp_jul.ctl;kindname="ECMWF";climfield="1Jul precipitation";;
ecmwf_prcp_aug) file=ECMWFData/ecmwf_prcp_aug.ctl;kindname="ECMWF";climfield="1Aug precipitation";;
ecmwf_prcp_sep) file=ECMWFData/ecmwf_prcp_sep.ctl;kindname="ECMWF";climfield="1Sep precipitation";;
ecmwf_prcp_oct) file=ECMWFData/ecmwf_prcp_oct.ctl;kindname="ECMWF";climfield="1Oct precipitation";;
ecmwf_prcp_nov) file=ECMWFData/ecmwf_prcp_nov.ctl;kindname="ECMWF";climfield="1Nov precipitation";;
ecmwf_prcp_dec) file=ECMWFData/ecmwf_prcp_dec.ctl;kindname="ECMWF";climfield="1Dec precipitation";;
ecmwf_slp) file=ECMWFData/ecmwf_msl.ctl;kindname="ECMWF";climfield="SLP";;
ecmwf_slp_1) file=ECMWFData/ecmwf_msl_1.ctl;kindname="ECMWF";climfield="+0 SLP";;
ecmwf_slp_2) file=ECMWFData/ecmwf_msl_2.ctl;kindname="ECMWF";climfield="+1 SLP";;
ecmwf_slp_3) file=ECMWFData/ecmwf_msl_3.ctl;kindname="ECMWF";climfield="+2 SLP";;
ecmwf_slp_4) file=ECMWFData/ecmwf_msl_4.ctl;kindname="ECMWF";climfield="+3 SLP";;
ecmwf_slp_5) file=ECMWFData/ecmwf_msl_5.ctl;kindname="ECMWF";climfield="+4 SLP";;
ecmwf_slp_6) file=ECMWFData/ecmwf_msl_6.ctl;kindname="ECMWF";climfield="+5 SLP";;
ecmwf_slp_jan) file=ECMWFData/ecmwf_msl_jan.ctl;kindname="ECMWF";climfield="1Jan SLP";;
ecmwf_slp_feb) file=ECMWFData/ecmwf_msl_feb.ctl;kindname="ECMWF";climfield="1Feb SLP";;
ecmwf_slp_mar) file=ECMWFData/ecmwf_msl_mar.ctl;kindname="ECMWF";climfield="1Mar SLP";;
ecmwf_slp_apr) file=ECMWFData/ecmwf_msl_apr.ctl;kindname="ECMWF";climfield="1Apr SLP";;
ecmwf_slp_may) file=ECMWFData/ecmwf_msl_may.ctl;kindname="ECMWF";climfield="1May SLP";;
ecmwf_slp_jun) file=ECMWFData/ecmwf_msl_jun.ctl;kindname="ECMWF";climfield="1Jun SLP";;
ecmwf_slp_jul) file=ECMWFData/ecmwf_msl_jul.ctl;kindname="ECMWF";climfield="1Jul SLP";;
ecmwf_slp_aug) file=ECMWFData/ecmwf_msl_aug.ctl;kindname="ECMWF";climfield="1Aug SLP";;
ecmwf_slp_sep) file=ECMWFData/ecmwf_msl_sep.ctl;kindname="ECMWF";climfield="1Sep SLP";;
ecmwf_slp_oct) file=ECMWFData/ecmwf_msl_oct.ctl;kindname="ECMWF";climfield="1Oct SLP";;
ecmwf_slp_nov) file=ECMWFData/ecmwf_msl_nov.ctl;kindname="ECMWF";climfield="1Nov SLP";;
ecmwf_slp_dec) file=ECMWFData/ecmwf_msl_dec.ctl;kindname="ECMWF";climfield="1Dec SLP";;
ecmwf_z500) file=ECMWFData/ecmwf_z500.ctl;kindname="ECMWF";climfield="z500";;
ecmwf_z500_1) file=ECMWFData/ecmwf_z500_1.ctl;kindname="ECMWF";climfield="+0 z500";;
ecmwf_z500_2) file=ECMWFData/ecmwf_z500_2.ctl;kindname="ECMWF";climfield="+1 z500";;
ecmwf_z500_3) file=ECMWFData/ecmwf_z500_3.ctl;kindname="ECMWF";climfield="+2 z500";;
ecmwf_z500_4) file=ECMWFData/ecmwf_z500_4.ctl;kindname="ECMWF";climfield="+3 z500";;
ecmwf_z500_5) file=ECMWFData/ecmwf_z500_5.ctl;kindname="ECMWF";climfield="+4 z500";;
ecmwf_z500_6) file=ECMWFData/ecmwf_z500_6.ctl;kindname="ECMWF";climfield="+5 z500";;
ecmwf_z500_jan) file=ECMWFData/ecmwf_z500_jan.ctl;kindname="ECMWF";climfield="1Jan z500";;
ecmwf_z500_feb) file=ECMWFData/ecmwf_z500_feb.ctl;kindname="ECMWF";climfield="1Feb z500";;
ecmwf_z500_mar) file=ECMWFData/ecmwf_z500_mar.ctl;kindname="ECMWF";climfield="1Mar z500";;
ecmwf_z500_apr) file=ECMWFData/ecmwf_z500_apr.ctl;kindname="ECMWF";climfield="1Apr z500";;
ecmwf_z500_may) file=ECMWFData/ecmwf_z500_may.ctl;kindname="ECMWF";climfield="1May z500";;
ecmwf_z500_jun) file=ECMWFData/ecmwf_z500_jun.ctl;kindname="ECMWF";climfield="1Jun z500";;
ecmwf_z500_jul) file=ECMWFData/ecmwf_z500_jul.ctl;kindname="ECMWF";climfield="1Jul z500";;
ecmwf_z500_aug) file=ECMWFData/ecmwf_z500_aug.ctl;kindname="ECMWF";climfield="1Aug z500";;
ecmwf_z500_sep) file=ECMWFData/ecmwf_z500_sep.ctl;kindname="ECMWF";climfield="1Sep z500";;
ecmwf_z500_oct) file=ECMWFData/ecmwf_z500_oct.ctl;kindname="ECMWF";climfield="1Oct z500";;
ecmwf_z500_nov) file=ECMWFData/ecmwf_z500_nov.ctl;kindname="ECMWF";climfield="1Nov z500";;
ecmwf_z500_dec) file=ECMWFData/ecmwf_z500_dec.ctl;kindname="ECMWF";climfield="1Dec z500";;
ecmwf_u10) file=ECMWFData/ecmwf_u10.ctl;kindname="ECMWF";climfield="u10";;
ecmwf_u10_1) file=ECMWFData/ecmwf_u10_1.ctl;kindname="ECMWF";climfield="+0 u10";;
ecmwf_u10_2) file=ECMWFData/ecmwf_u10_2.ctl;kindname="ECMWF";climfield="+1 u10";;
ecmwf_u10_3) file=ECMWFData/ecmwf_u10_3.ctl;kindname="ECMWF";climfield="+2 u10";;
ecmwf_u10_4) file=ECMWFData/ecmwf_u10_4.ctl;kindname="ECMWF";climfield="+3 u10";;
ecmwf_u10_5) file=ECMWFData/ecmwf_u10_5.ctl;kindname="ECMWF";climfield="+4 u10";;
ecmwf_u10_6) file=ECMWFData/ecmwf_u10_6.ctl;kindname="ECMWF";climfield="+5 u10";;
ecmwf_u10_jan) file=ECMWFData/ecmwf_u10_jan.ctl;kindname="ECMWF";climfield="1Jan u10";;
ecmwf_u10_feb) file=ECMWFData/ecmwf_u10_feb.ctl;kindname="ECMWF";climfield="1Feb u10";;
ecmwf_u10_mar) file=ECMWFData/ecmwf_u10_mar.ctl;kindname="ECMWF";climfield="1Mar u10";;
ecmwf_u10_apr) file=ECMWFData/ecmwf_u10_apr.ctl;kindname="ECMWF";climfield="1Apr u10";;
ecmwf_u10_may) file=ECMWFData/ecmwf_u10_may.ctl;kindname="ECMWF";climfield="1May u10";;
ecmwf_u10_jun) file=ECMWFData/ecmwf_u10_jun.ctl;kindname="ECMWF";climfield="1Jun u10";;
ecmwf_u10_jul) file=ECMWFData/ecmwf_u10_jul.ctl;kindname="ECMWF";climfield="1Jul u10";;
ecmwf_u10_aug) file=ECMWFData/ecmwf_u10_aug.ctl;kindname="ECMWF";climfield="1Aug u10";;
ecmwf_u10_sep) file=ECMWFData/ecmwf_u10_sep.ctl;kindname="ECMWF";climfield="1Sep u10";;
ecmwf_u10_oct) file=ECMWFData/ecmwf_u10_oct.ctl;kindname="ECMWF";climfield="1Oct u10";;
ecmwf_u10_nov) file=ECMWFData/ecmwf_u10_nov.ctl;kindname="ECMWF";climfield="1Nov u10";;
ecmwf_u10_dec) file=ECMWFData/ecmwf_u10_dec.ctl;kindname="ECMWF";climfield="1Dec u10";;
ecmwf_v10) file=ECMWFData/ecmwf_v10.ctl;kindname="ECMWF";climfield="v10";;
ecmwf_v10_1) file=ECMWFData/ecmwf_v10_1.ctl;kindname="ECMWF";climfield="+0 v10";;
ecmwf_v10_2) file=ECMWFData/ecmwf_v10_2.ctl;kindname="ECMWF";climfield="+1 v10";;
ecmwf_v10_3) file=ECMWFData/ecmwf_v10_3.ctl;kindname="ECMWF";climfield="+2 v10";;
ecmwf_v10_4) file=ECMWFData/ecmwf_v10_4.ctl;kindname="ECMWF";climfield="+3 v10";;
ecmwf_v10_5) file=ECMWFData/ecmwf_v10_5.ctl;kindname="ECMWF";climfield="+4 v10";;
ecmwf_v10_6) file=ECMWFData/ecmwf_v10_6.ctl;kindname="ECMWF";climfield="+5 v10";;
ecmwf_v10_jan) file=ECMWFData/ecmwf_v10_jan.ctl;kindname="ECMWF";climfield="1Jan v10";;
ecmwf_v10_feb) file=ECMWFData/ecmwf_v10_feb.ctl;kindname="ECMWF";climfield="1Feb v10";;
ecmwf_v10_mar) file=ECMWFData/ecmwf_v10_mar.ctl;kindname="ECMWF";climfield="1Mar v10";;
ecmwf_v10_apr) file=ECMWFData/ecmwf_v10_apr.ctl;kindname="ECMWF";climfield="1Apr v10";;
ecmwf_v10_may) file=ECMWFData/ecmwf_v10_may.ctl;kindname="ECMWF";climfield="1May v10";;
ecmwf_v10_jun) file=ECMWFData/ecmwf_v10_jun.ctl;kindname="ECMWF";climfield="1Jun v10";;
ecmwf_v10_jul) file=ECMWFData/ecmwf_v10_jul.ctl;kindname="ECMWF";climfield="1Jul v10";;
ecmwf_v10_aug) file=ECMWFData/ecmwf_v10_aug.ctl;kindname="ECMWF";climfield="1Aug v10";;
ecmwf_v10_sep) file=ECMWFData/ecmwf_v10_sep.ctl;kindname="ECMWF";climfield="1Sep v10";;
ecmwf_v10_oct) file=ECMWFData/ecmwf_v10_oct.ctl;kindname="ECMWF";climfield="1Oct v10";;
ecmwf_v10_nov) file=ECMWFData/ecmwf_v10_nov.ctl;kindname="ECMWF";climfield="1Nov v10";;
ecmwf_v10_dec) file=ECMWFData/ecmwf_v10_dec.ctl;kindname="ECMWF";climfield="1Dec v10";;
ecmwf_ssr) file=ECMWFData/ecmwf_ssr.ctl;kindname="ECMWF";climfield="solar radiation";;
ecmwf_ssr_1) file=ECMWFData/ecmwf_ssr_1.ctl;kindname="ECMWF";climfield="+0 solar radiation";;
ecmwf_ssr_2) file=ECMWFData/ecmwf_ssr_2.ctl;kindname="ECMWF";climfield="+1 solar radiation";;
ecmwf_ssr_3) file=ECMWFData/ecmwf_ssr_3.ctl;kindname="ECMWF";climfield="+2 solar radiation";;
ecmwf_ssr_4) file=ECMWFData/ecmwf_ssr_4.ctl;kindname="ECMWF";climfield="+3 solar radiation";;
ecmwf_ssr_5) file=ECMWFData/ecmwf_ssr_5.ctl;kindname="ECMWF";climfield="+4 solar radiation";;
ecmwf_ssr_6) file=ECMWFData/ecmwf_ssr_6.ctl;kindname="ECMWF";climfield="+5 solar radiation";;
ecmwf_ssr_jan) file=ECMWFData/ecmwf_ssr_jan.ctl;kindname="ECMWF";climfield="1Jan solar radiation";;
ecmwf_ssr_feb) file=ECMWFData/ecmwf_ssr_feb.ctl;kindname="ECMWF";climfield="1Feb solar radiation";;
ecmwf_ssr_mar) file=ECMWFData/ecmwf_ssr_mar.ctl;kindname="ECMWF";climfield="1Mar solar radiation";;
ecmwf_ssr_apr) file=ECMWFData/ecmwf_ssr_apr.ctl;kindname="ECMWF";climfield="1Apr solar radiation";;
ecmwf_ssr_may) file=ECMWFData/ecmwf_ssr_may.ctl;kindname="ECMWF";climfield="1May solar radiation";;
ecmwf_ssr_jun) file=ECMWFData/ecmwf_ssr_jun.ctl;kindname="ECMWF";climfield="1Jun solar radiation";;
ecmwf_ssr_jul) file=ECMWFData/ecmwf_ssr_jul.ctl;kindname="ECMWF";climfield="1Jul solar radiation";;
ecmwf_ssr_aug) file=ECMWFData/ecmwf_ssr_aug.ctl;kindname="ECMWF";climfield="1Aug solar radiation";;
ecmwf_ssr_sep) file=ECMWFData/ecmwf_ssr_sep.ctl;kindname="ECMWF";climfield="1Sep solar radiation";;
ecmwf_ssr_oct) file=ECMWFData/ecmwf_ssr_oct.ctl;kindname="ECMWF";climfield="1Oct solar radiation";;
ecmwf_ssr_nov) file=ECMWFData/ecmwf_ssr_nov.ctl;kindname="ECMWF";climfield="1Nov solar radiation";;
ecmwf_ssr_dec) file=ECMWFData/ecmwf_ssr_dec.ctl;kindname="ECMWF";climfield="1Dec solar radiation";;

ecmwf_sst) file=ECMWFData/ecmwf_sst_o.ctl;kindname="ECMWF";climfield="SST";;
ecmwf_tsf_1) file=ECMWFData/ecmwf_tsf_1.ctl;kindname="ECMWF";climfield="+0 Tsfc";;
ecmwf_tsf_2) file=ECMWFData/ecmwf_tsf_2.ctl;kindname="ECMWF";climfield="+1 Tsfc";;
ecmwf_tsf_3) file=ECMWFData/ecmwf_tsf_3.ctl;kindname="ECMWF";climfield="+2 Tsfc";;
ecmwf_tsf_4) file=ECMWFData/ecmwf_tsf_4.ctl;kindname="ECMWF";climfield="+3 Tsfc";;
ecmwf_tsf_5) file=ECMWFData/ecmwf_tsf_5.ctl;kindname="ECMWF";climfield="+4 Tsfc";;
ecmwf_tsf_6) file=ECMWFData/ecmwf_tsf_6.ctl;kindname="ECMWF";climfield="+5 Tsfc";;
ecmwf_tsf_jan) file=ECMWFData/ecmwf_tsf_jan.ctl;kindname="ECMWF";climfield="1Jan Tsf";;
ecmwf_tsf_feb) file=ECMWFData/ecmwf_tsf_feb.ctl;kindname="ECMWF";climfield="1Feb Tsf";;
ecmwf_tsf_mar) file=ECMWFData/ecmwf_tsf_mar.ctl;kindname="ECMWF";climfield="1Mar Tsf";;
ecmwf_tsf_apr) file=ECMWFData/ecmwf_tsf_apr.ctl;kindname="ECMWF";climfield="1Apr Tsf";;
ecmwf_tsf_may) file=ECMWFData/ecmwf_tsf_may.ctl;kindname="ECMWF";climfield="1May Tsf";;
ecmwf_tsf_jun) file=ECMWFData/ecmwf_tsf_jun.ctl;kindname="ECMWF";climfield="1Jun Tsf";;
ecmwf_tsf_jul) file=ECMWFData/ecmwf_tsf_jul.ctl;kindname="ECMWF";climfield="1Jul Tsf";;
ecmwf_tsf_aug) file=ECMWFData/ecmwf_tsf_aug.ctl;kindname="ECMWF";climfield="1Aug Tsf";;
ecmwf_tsf_sep) file=ECMWFData/ecmwf_tsf_sep.ctl;kindname="ECMWF";climfield="1Sep Tsf";;
ecmwf_tsf_oct) file=ECMWFData/ecmwf_tsf_oct.ctl;kindname="ECMWF";climfield="1Oct Tsf";;
ecmwf_tsf_nov) file=ECMWFData/ecmwf_tsf_nov.ctl;kindname="ECMWF";climfield="1Nov Tsf";;
ecmwf_tsf_dec) file=ECMWFData/ecmwf_tsf_dec.ctl;kindname="ECMWF";climfield="1Dec Tsf";;

ecmwf_ssh) file=ECMWFData/ecmwf_ssh_o.ctl;kindname="ECMWF";climfield="SSH";;
ecmwf_ssh_1) file=ECMWFData/ecmwf_ssh_1_o.ctl;kindname="ECMWF";climfield="+0 SSH";;
ecmwf_ssh_2) file=ECMWFData/ecmwf_ssh_2_o.ctl;kindname="ECMWF";climfield="+1 SSH";;
ecmwf_ssh_3) file=ECMWFData/ecmwf_ssh_3_o.ctl;kindname="ECMWF";climfield="+2 SSH";;
ecmwf_ssh_4) file=ECMWFData/ecmwf_ssh_4_o.ctl;kindname="ECMWF";climfield="+3 SSH";;
ecmwf_ssh_5) file=ECMWFData/ecmwf_ssh_5_o.ctl;kindname="ECMWF";climfield="+4 SSH";;
ecmwf_ssh_6) file=ECMWFData/ecmwf_ssh_6_o.ctl;kindname="ECMWF";climfield="+5 SSH";;

ecmwf2_t2m_1) file=ECMWFData/monthly/ecmwf2_t2m_1.nc;kindname="ECMWF-2";climfield="+0 T2m";;
ecmwf2_t2m_2) file=ECMWFData/monthly/ecmwf2_t2m_2.nc;kindname="ECMWF-2";climfield="+1 T2m";;
ecmwf2_t2m_3) file=ECMWFData/monthly/ecmwf2_t2m_3.nc;kindname="ECMWF-2";climfield="+2 T2m";;
ecmwf2_t2m_4) file=ECMWFData/monthly/ecmwf2_t2m_4.nc;kindname="ECMWF-2";climfield="+3 T2m";;
ecmwf2_t2m_5) file=ECMWFData/monthly/ecmwf2_t2m_5.nc;kindname="ECMWF-2";climfield="+4 T2m";;
ecmwf2_t2m_6) file=ECMWFData/monthly/ecmwf2_t2m_6.nc;kindname="ECMWF-2";climfield="+5 T2m";;
ecmwf2_t2m_jan) file=ECMWFData/monthly/ecmwf2_t2m_jan.ensm.nc;kindname="ECMWF-2";climfield="1Jan T2m";;
ecmwf2_t2m_feb) file=ECMWFData/monthly/ecmwf2_t2m_feb.ensm.nc;kindname="ECMWF-2";climfield="1Feb T2m";;
ecmwf2_t2m_mar) file=ECMWFData/monthly/ecmwf2_t2m_mar.ensm.nc;kindname="ECMWF-2";climfield="1Mar T2m";;
ecmwf2_t2m_apr) file=ECMWFData/monthly/ecmwf2_t2m_apr.ensm.nc;kindname="ECMWF-2";climfield="1Apr T2m";;
ecmwf2_t2m_may) file=ECMWFData/monthly/ecmwf2_t2m_may.ensm.nc;kindname="ECMWF-2";climfield="1May T2m";;
ecmwf2_t2m_jun) file=ECMWFData/monthly/ecmwf2_t2m_jun.ensm.nc;kindname="ECMWF-2";climfield="1Jun T2m";;
ecmwf2_t2m_jul) file=ECMWFData/monthly/ecmwf2_t2m_jul.ensm.nc;kindname="ECMWF-2";climfield="1Jul T2m";;
ecmwf2_t2m_aug) file=ECMWFData/monthly/ecmwf2_t2m_aug.ensm.nc;kindname="ECMWF-2";climfield="1Aug T2m";;
ecmwf2_t2m_sep) file=ECMWFData/monthly/ecmwf2_t2m_sep.ensm.nc;kindname="ECMWF-2";climfield="1Sep T2m";;
ecmwf2_t2m_oct) file=ECMWFData/monthly/ecmwf2_t2m_oct.ensm.nc;kindname="ECMWF-2";climfield="1Oct T2m";;
ecmwf2_t2m_nov) file=ECMWFData/monthly/ecmwf2_t2m_nov.ensm.nc;kindname="ECMWF-2";climfield="1Nov T2m";;
ecmwf2_t2m_dec) file=ECMWFData/monthly/ecmwf2_t2m_dec.ensm.nc;kindname="ECMWF-2";climfield="1Dec T2m";;

ecmwf2_t2x_1) file=ECMWFData/monthly/ecmwf2_t2x_1.ctl;kindname="ECMWF-2";climfield="+0 T2max";;
ecmwf2_t2x_2) file=ECMWFData/monthly/ecmwf2_t2x_2.ctl;kindname="ECMWF-2";climfield="+1 T2max";;
ecmwf2_t2x_3) file=ECMWFData/monthly/ecmwf2_t2x_3.ctl;kindname="ECMWF-2";climfield="+2 T2max";;
ecmwf2_t2x_4) file=ECMWFData/monthly/ecmwf2_t2x_4.ctl;kindname="ECMWF-2";climfield="+3 T2max";;
ecmwf2_t2x_5) file=ECMWFData/monthly/ecmwf2_t2x_5.ctl;kindname="ECMWF-2";climfield="+4 T2max";;
ecmwf2_t2x_6) file=ECMWFData/monthly/ecmwf2_t2x_6.ctl;kindname="ECMWF-2";climfield="+5 T2max";;
ecmwf2_t2x_jan) file=ECMWFData/monthly/ecmwf2_t2x_jan.ensm.nc;kindname="ECMWF-2";climfield="1Jan T2max";;
ecmwf2_t2x_feb) file=ECMWFData/monthly/ecmwf2_t2x_feb.ensm.nc;kindname="ECMWF-2";climfield="1Feb T2max";;
ecmwf2_t2x_mar) file=ECMWFData/monthly/ecmwf2_t2x_mar.ensm.nc;kindname="ECMWF-2";climfield="1Mar T2max";;
ecmwf2_t2x_apr) file=ECMWFData/monthly/ecmwf2_t2x_apr.ensm.nc;kindname="ECMWF-2";climfield="1Apr T2max";;
ecmwf2_t2x_may) file=ECMWFData/monthly/ecmwf2_t2x_may.ensm.nc;kindname="ECMWF-2";climfield="1May T2max";;
ecmwf2_t2x_jun) file=ECMWFData/monthly/ecmwf2_t2x_jun.ensm.nc;kindname="ECMWF-2";climfield="1Jun T2max";;
ecmwf2_t2x_jul) file=ECMWFData/monthly/ecmwf2_t2x_jul.ensm.nc;kindname="ECMWF-2";climfield="1Jul T2max";;
ecmwf2_t2x_aug) file=ECMWFData/monthly/ecmwf2_t2x_aug.ensm.nc;kindname="ECMWF-2";climfield="1Aug T2max";;
ecmwf2_t2x_sep) file=ECMWFData/monthly/ecmwf2_t2x_sep.ensm.nc;kindname="ECMWF-2";climfield="1Sep T2max";;
ecmwf2_t2x_oct) file=ECMWFData/monthly/ecmwf2_t2x_oct.ensm.nc;kindname="ECMWF-2";climfield="1Oct T2max";;
ecmwf2_t2x_nov) file=ECMWFData/monthly/ecmwf2_t2x_nov.ensm.nc;kindname="ECMWF-2";climfield="1Nov T2max";;
ecmwf2_t2x_dec) file=ECMWFData/monthly/ecmwf2_t2x_dec.ensm.nc;kindname="ECMWF-2";climfield="1Dec T2max";;

ecmwf2_t2n_1) file=ECMWFData/monthly/ecmwf2_t2n_1.nc;kindname="ECMWF-2";climfield="+0 T2min";;
ecmwf2_t2n_2) file=ECMWFData/monthly/ecmwf2_t2n_2.nc;kindname="ECMWF-2";climfield="+1 T2min";;
ecmwf2_t2n_3) file=ECMWFData/monthly/ecmwf2_t2n_3.nc;kindname="ECMWF-2";climfield="+2 T2min";;
ecmwf2_t2n_4) file=ECMWFData/monthly/ecmwf2_t2n_4.nc;kindname="ECMWF-2";climfield="+3 T2min";;
ecmwf2_t2n_5) file=ECMWFData/monthly/ecmwf2_t2n_5.nc;kindname="ECMWF-2";climfield="+4 T2min";;
ecmwf2_t2n_6) file=ECMWFData/monthly/ecmwf2_t2n_6.nc;kindname="ECMWF-2";climfield="+5 T2min";;
ecmwf2_t2n_jan) file=ECMWFData/monthly/ecmwf2_t2n_jan.ensm.nc;kindname="ECMWF-2";climfield="1Jan T2min";;
ecmwf2_t2n_feb) file=ECMWFData/monthly/ecmwf2_t2n_feb.ensm.nc;kindname="ECMWF-2";climfield="1Feb T2min";;
ecmwf2_t2n_mar) file=ECMWFData/monthly/ecmwf2_t2n_mar.ensm.nc;kindname="ECMWF-2";climfield="1Mar T2min";;
ecmwf2_t2n_apr) file=ECMWFData/monthly/ecmwf2_t2n_apr.ensm.nc;kindname="ECMWF-2";climfield="1Apr T2min";;
ecmwf2_t2n_may) file=ECMWFData/monthly/ecmwf2_t2n_may.ensm.nc;kindname="ECMWF-2";climfield="1May T2min";;
ecmwf2_t2n_jun) file=ECMWFData/monthly/ecmwf2_t2n_jun.ensm.nc;kindname="ECMWF-2";climfield="1Jun T2min";;
ecmwf2_t2n_jul) file=ECMWFData/monthly/ecmwf2_t2n_jul.ensm.nc;kindname="ECMWF-2";climfield="1Jul T2min";;
ecmwf2_t2n_aug) file=ECMWFData/monthly/ecmwf2_t2n_aug.ensm.nc;kindname="ECMWF-2";climfield="1Aug T2min";;
ecmwf2_t2n_sep) file=ECMWFData/monthly/ecmwf2_t2n_sep.ensm.nc;kindname="ECMWF-2";climfield="1Sep T2min";;
ecmwf2_t2n_oct) file=ECMWFData/monthly/ecmwf2_t2n_oct.ensm.nc;kindname="ECMWF-2";climfield="1Oct T2min";;
ecmwf2_t2n_nov) file=ECMWFData/monthly/ecmwf2_t2n_nov.ensm.nc;kindname="ECMWF-2";climfield="1Nov T2min";;
ecmwf2_t2n_dec) file=ECMWFData/monthly/ecmwf2_t2n_dec.ensm.nc;kindname="ECMWF-2";climfield="1Dec T2min";;

ecmwf2_t850_1) file=ECMWFData/monthly/ecmwf2_t850_1.ctl;kindname="ECMWF-2";climfield="+0 T850";;
ecmwf2_t850_2) file=ECMWFData/monthly/ecmwf2_t850_2.ctl;kindname="ECMWF-2";climfield="+1 T850";;
ecmwf2_t850_3) file=ECMWFData/monthly/ecmwf2_t850_3.ctl;kindname="ECMWF-2";climfield="+2 T850";;
ecmwf2_t850_4) file=ECMWFData/monthly/ecmwf2_t850_4.ctl;kindname="ECMWF-2";climfield="+3 T850";;
ecmwf2_t850_5) file=ECMWFData/monthly/ecmwf2_t850_5.ctl;kindname="ECMWF-2";climfield="+4 T850";;
ecmwf2_t850_6) file=ECMWFData/monthly/ecmwf2_t850_6.ctl;kindname="ECMWF-2";climfield="+5 T850";;
ecmwf2_t850_jan) file=ECMWFData/monthly/ecmwf2_t850_jan.ensm.ctl;kindname="ECMWF-2";climfield="1Jan T850";;
ecmwf2_t850_feb) file=ECMWFData/monthly/ecmwf2_t850_feb.ensm.ctl;kindname="ECMWF-2";climfield="1Feb T850";;
ecmwf2_t850_mar) file=ECMWFData/monthly/ecmwf2_t850_mar.ensm.ctl;kindname="ECMWF-2";climfield="1Mar T850";;
ecmwf2_t850_apr) file=ECMWFData/monthly/ecmwf2_t850_apr.ensm.ctl;kindname="ECMWF-2";climfield="1Apr T850";;
ecmwf2_t850_may) file=ECMWFData/monthly/ecmwf2_t850_may.ensm.ctl;kindname="ECMWF-2";climfield="1May T850";;
ecmwf2_t850_jun) file=ECMWFData/monthly/ecmwf2_t850_jun.ensm.ctl;kindname="ECMWF-2";climfield="1Jun T850";;
ecmwf2_t850_jul) file=ECMWFData/monthly/ecmwf2_t850_jul.ensm.ctl;kindname="ECMWF-2";climfield="1Jul T850";;
ecmwf2_t850_aug) file=ECMWFData/monthly/ecmwf2_t850_aug.ensm.ctl;kindname="ECMWF-2";climfield="1Aug T850";;
ecmwf2_t850_sep) file=ECMWFData/monthly/ecmwf2_t850_sep.ensm.ctl;kindname="ECMWF-2";climfield="1Sep T850";;
ecmwf2_t850_oct) file=ECMWFData/monthly/ecmwf2_t850_oct.ensm.ctl;kindname="ECMWF-2";climfield="1Oct T850";;
ecmwf2_t850_nov) file=ECMWFData/monthly/ecmwf2_t850_nov.ensm.ctl;kindname="ECMWF-2";climfield="1Nov T850";;
ecmwf2_t850_dec) file=ECMWFData/monthly/ecmwf2_t850_dec.ensm.ctl;kindname="ECMWF-2";climfield="1Dec T850";;

ecmwf2_prcp) file=ECMWFData/monthly/ecmwf2_tp.ctl;kindname="ECMWF-2";climfield="precipitation";;
ecmwf2_prcp_1) file=ECMWFData/monthly/ecmwf2_prcp_1.ensm.ctl;kindname="ECMWF-2";climfield="+0 precipitation";;
ecmwf2_prcp_2) file=ECMWFData/monthly/ecmwf2_prcp_2.ensm.ctl;kindname="ECMWF-2";climfield="+1 precipitation";;
ecmwf2_prcp_3) file=ECMWFData/monthly/ecmwf2_prcp_3.ensm.ctl;kindname="ECMWF-2";climfield="+2 precipitation";;
ecmwf2_prcp_4) file=ECMWFData/monthly/ecmwf2_prcp_4.ensm.ctl;kindname="ECMWF-2";climfield="+3 precipitation";;
ecmwf2_prcp_5) file=ECMWFData/monthly/ecmwf2_prcp_5.ensm.ctl;kindname="ECMWF-2";climfield="+4 precipitation";;
ecmwf2_prcp_6) file=ECMWFData/monthly/ecmwf2_prcp_6.ensm.ctl;kindname="ECMWF-2";climfield="+5 precipitation";;
ecmwf2_prcp_jan) file=ECMWFData/monthly/ecmwf2_prcp_jan.ensm.ctl;kindname="ECMWF-2";climfield="1Jan precipitation";;
ecmwf2_prcp_feb) file=ECMWFData/monthly/ecmwf2_prcp_feb.ensm.ctl;kindname="ECMWF-2";climfield="1Feb precipitation";;
ecmwf2_prcp_mar) file=ECMWFData/monthly/ecmwf2_prcp_mar.ensm.ctl;kindname="ECMWF-2";climfield="1Mar precipitation";;
ecmwf2_prcp_apr) file=ECMWFData/monthly/ecmwf2_prcp_apr.ensm.ctl;kindname="ECMWF-2";climfield="1Apr precipitation";;
ecmwf2_prcp_may) file=ECMWFData/monthly/ecmwf2_prcp_may.ensm.ctl;kindname="ECMWF-2";climfield="1May precipitation";;
ecmwf2_prcp_jun) file=ECMWFData/monthly/ecmwf2_prcp_jun.ensm.ctl;kindname="ECMWF-2";climfield="1Jun precipitation";;
ecmwf2_prcp_jul) file=ECMWFData/monthly/ecmwf2_prcp_jul.ensm.ctl;kindname="ECMWF-2";climfield="1Jul precipitation";;
ecmwf2_prcp_aug) file=ECMWFData/monthly/ecmwf2_prcp_aug.ensm.ctl;kindname="ECMWF-2";climfield="1Aug precipitation";;
ecmwf2_prcp_sep) file=ECMWFData/monthly/ecmwf2_prcp_sep.ensm.ctl;kindname="ECMWF-2";climfield="1Sep precipitation";;
ecmwf2_prcp_oct) file=ECMWFData/monthly/ecmwf2_prcp_oct.ensm.ctl;kindname="ECMWF-2";climfield="1Oct precipitation";;
ecmwf2_prcp_nov) file=ECMWFData/monthly/ecmwf2_prcp_nov.ensm.ctl;kindname="ECMWF-2";climfield="1Nov precipitation";;
ecmwf2_prcp_dec) file=ECMWFData/monthly/ecmwf2_prcp_dec.ensm.ctl;kindname="ECMWF-2";climfield="1Dec precipitation";;
ecmwf2_msl) file=ECMWFData/monthly/ecmwf2_msl.ctl;kindname="ECMWF-2";climfield="SLP";;
ecmwf2_msl_1) file=ECMWFData/monthly/ecmwf2_msl_1.ctl;kindname="ECMWF-2";climfield="+0 SLP";;
ecmwf2_msl_2) file=ECMWFData/monthly/ecmwf2_msl_2.ctl;kindname="ECMWF-2";climfield="+1 SLP";;
ecmwf2_msl_3) file=ECMWFData/monthly/ecmwf2_msl_3.ctl;kindname="ECMWF-2";climfield="+2 SLP";;
ecmwf2_msl_4) file=ECMWFData/monthly/ecmwf2_msl_4.ctl;kindname="ECMWF-2";climfield="+3 SLP";;
ecmwf2_msl_5) file=ECMWFData/monthly/ecmwf2_msl_5.ctl;kindname="ECMWF-2";climfield="+4 SLP";;
ecmwf2_msl_6) file=ECMWFData/monthly/ecmwf2_msl_6.ctl;kindname="ECMWF-2";climfield="+5 SLP";;
ecmwf2_msl_jan) file=ECMWFData/monthly/ecmwf2_msl_jan.ensm.ctl;kindname="ECMWF-2";climfield="1Jan SLP";;
ecmwf2_msl_feb) file=ECMWFData/monthly/ecmwf2_msl_feb.ensm.ctl;kindname="ECMWF-2";climfield="1Feb SLP";;
ecmwf2_msl_mar) file=ECMWFData/monthly/ecmwf2_msl_mar.ensm.ctl;kindname="ECMWF-2";climfield="1Mar SLP";;
ecmwf2_msl_apr) file=ECMWFData/monthly/ecmwf2_msl_apr.ensm.ctl;kindname="ECMWF-2";climfield="1Apr SLP";;
ecmwf2_msl_may) file=ECMWFData/monthly/ecmwf2_msl_may.ensm.ctl;kindname="ECMWF-2";climfield="1May SLP";;
ecmwf2_msl_jun) file=ECMWFData/monthly/ecmwf2_msl_jun.ensm.ctl;kindname="ECMWF-2";climfield="1Jun SLP";;
ecmwf2_msl_jul) file=ECMWFData/monthly/ecmwf2_msl_jul.ensm.ctl;kindname="ECMWF-2";climfield="1Jul SLP";;
ecmwf2_msl_aug) file=ECMWFData/monthly/ecmwf2_msl_aug.ensm.ctl;kindname="ECMWF-2";climfield="1Aug SLP";;
ecmwf2_msl_sep) file=ECMWFData/monthly/ecmwf2_msl_sep.ensm.ctl;kindname="ECMWF-2";climfield="1Sep SLP";;
ecmwf2_msl_oct) file=ECMWFData/monthly/ecmwf2_msl_oct.ensm.ctl;kindname="ECMWF-2";climfield="1Oct SLP";;
ecmwf2_msl_nov) file=ECMWFData/monthly/ecmwf2_msl_nov.ensm.ctl;kindname="ECMWF-2";climfield="1Nov SLP";;
ecmwf2_msl_dec) file=ECMWFData/monthly/ecmwf2_msl_dec.ensm.ctl;kindname="ECMWF-2";climfield="1Dec SLP";;
ecmwf2_z500) file=ECMWFData/monthly/ecmwf2_z500.ctl;kindname="ECMWF-2";climfield="z500";;
ecmwf2_z500_1) file=ECMWFData/monthly/ecmwf2_z500_1.ctl;kindname="ECMWF-2";climfield="+0 z500";;
ecmwf2_z500_2) file=ECMWFData/monthly/ecmwf2_z500_2.ctl;kindname="ECMWF-2";climfield="+1 z500";;
ecmwf2_z500_3) file=ECMWFData/monthly/ecmwf2_z500_3.ctl;kindname="ECMWF-2";climfield="+2 z500";;
ecmwf2_z500_4) file=ECMWFData/monthly/ecmwf2_z500_4.ctl;kindname="ECMWF-2";climfield="+3 z500";;
ecmwf2_z500_5) file=ECMWFData/monthly/ecmwf2_z500_5.ctl;kindname="ECMWF-2";climfield="+4 z500";;
ecmwf2_z500_6) file=ECMWFData/monthly/ecmwf2_z500_6.ctl;kindname="ECMWF-2";climfield="+5 z500";;
ecmwf2_z500_jan) file=ECMWFData/monthly/ecmwf2_z500_jan.ensm.ctl;kindname="ECMWF-2";climfield="1Jan z500";;
ecmwf2_z500_feb) file=ECMWFData/monthly/ecmwf2_z500_feb.ensm.ctl;kindname="ECMWF-2";climfield="1Feb z500";;
ecmwf2_z500_mar) file=ECMWFData/monthly/ecmwf2_z500_mar.ensm.ctl;kindname="ECMWF-2";climfield="1Mar z500";;
ecmwf2_z500_apr) file=ECMWFData/monthly/ecmwf2_z500_apr.ensm.ctl;kindname="ECMWF-2";climfield="1Apr z500";;
ecmwf2_z500_may) file=ECMWFData/monthly/ecmwf2_z500_may.ensm.ctl;kindname="ECMWF-2";climfield="1May z500";;
ecmwf2_z500_jun) file=ECMWFData/monthly/ecmwf2_z500_jun.ensm.ctl;kindname="ECMWF-2";climfield="1Jun z500";;
ecmwf2_z500_jul) file=ECMWFData/monthly/ecmwf2_z500_jul.ensm.ctl;kindname="ECMWF-2";climfield="1Jul z500";;
ecmwf2_z500_aug) file=ECMWFData/monthly/ecmwf2_z500_aug.ensm.ctl;kindname="ECMWF-2";climfield="1Aug z500";;
ecmwf2_z500_sep) file=ECMWFData/monthly/ecmwf2_z500_sep.ensm.ctl;kindname="ECMWF-2";climfield="1Sep z500";;
ecmwf2_z500_oct) file=ECMWFData/monthly/ecmwf2_z500_oct.ensm.ctl;kindname="ECMWF-2";climfield="1Oct z500";;
ecmwf2_z500_nov) file=ECMWFData/monthly/ecmwf2_z500_nov.ensm.ctl;kindname="ECMWF-2";climfield="1Nov z500";;
ecmwf2_z500_dec) file=ECMWFData/monthly/ecmwf2_z500_dec.ensm.ctl;kindname="ECMWF-2";climfield="1Dec z500";;
ecmwf2_u10) file=ECMWFData/monthly/ecmwf2_u10.ctl;kindname="ECMWF-2";climfield="u10";;
ecmwf2_u10_1) file=ECMWFData/monthly/ecmwf2_u10_1.ctl;kindname="ECMWF-2";climfield="+0 u10";;
ecmwf2_u10_2) file=ECMWFData/monthly/ecmwf2_u10_2.ctl;kindname="ECMWF-2";climfield="+1 u10";;
ecmwf2_u10_3) file=ECMWFData/monthly/ecmwf2_u10_3.ctl;kindname="ECMWF-2";climfield="+2 u10";;
ecmwf2_u10_4) file=ECMWFData/monthly/ecmwf2_u10_4.ctl;kindname="ECMWF-2";climfield="+3 u10";;
ecmwf2_u10_5) file=ECMWFData/monthly/ecmwf2_u10_5.ctl;kindname="ECMWF-2";climfield="+4 u10";;
ecmwf2_u10_6) file=ECMWFData/monthly/ecmwf2_u10_6.ctl;kindname="ECMWF-2";climfield="+5 u10";;
ecmwf2_u10_jan) file=ECMWFData/monthly/ecmwf2_u10_jan.ensm.ctl;kindname="ECMWF-2";climfield="1Jan u10";;
ecmwf2_u10_feb) file=ECMWFData/monthly/ecmwf2_u10_feb.ensm.ctl;kindname="ECMWF-2";climfield="1Feb u10";;
ecmwf2_u10_mar) file=ECMWFData/monthly/ecmwf2_u10_mar.ensm.ctl;kindname="ECMWF-2";climfield="1Mar u10";;
ecmwf2_u10_apr) file=ECMWFData/monthly/ecmwf2_u10_apr.ensm.ctl;kindname="ECMWF-2";climfield="1Apr u10";;
ecmwf2_u10_may) file=ECMWFData/monthly/ecmwf2_u10_may.ensm.ctl;kindname="ECMWF-2";climfield="1May u10";;
ecmwf2_u10_jun) file=ECMWFData/monthly/ecmwf2_u10_jun.ensm.ctl;kindname="ECMWF-2";climfield="1Jun u10";;
ecmwf2_u10_jul) file=ECMWFData/monthly/ecmwf2_u10_jul.ensm.ctl;kindname="ECMWF-2";climfield="1Jul u10";;
ecmwf2_u10_aug) file=ECMWFData/monthly/ecmwf2_u10_aug.ensm.ctl;kindname="ECMWF-2";climfield="1Aug u10";;
ecmwf2_u10_sep) file=ECMWFData/monthly/ecmwf2_u10_sep.ensm.ctl;kindname="ECMWF-2";climfield="1Sep u10";;
ecmwf2_u10_oct) file=ECMWFData/monthly/ecmwf2_u10_oct.ensm.ctl;kindname="ECMWF-2";climfield="1Oct u10";;
ecmwf2_u10_nov) file=ECMWFData/monthly/ecmwf2_u10_nov.ensm.ctl;kindname="ECMWF-2";climfield="1Nov u10";;
ecmwf2_u10_dec) file=ECMWFData/monthly/ecmwf2_u10_dec.ensm.ctl;kindname="ECMWF-2";climfield="1Dec u10";;
ecmwf2_v10) file=ECMWFData/monthly/ecmwf2_v10.ctl;kindname="ECMWF-2";climfield="v10";;
ecmwf2_v10_1) file=ECMWFData/monthly/ecmwf2_v10_1.ctl;kindname="ECMWF-2";climfield="+0 v10";;
ecmwf2_v10_2) file=ECMWFData/monthly/ecmwf2_v10_2.ctl;kindname="ECMWF-2";climfield="+1 v10";;
ecmwf2_v10_3) file=ECMWFData/monthly/ecmwf2_v10_3.ctl;kindname="ECMWF-2";climfield="+2 v10";;
ecmwf2_v10_4) file=ECMWFData/monthly/ecmwf2_v10_4.ctl;kindname="ECMWF-2";climfield="+3 v10";;
ecmwf2_v10_5) file=ECMWFData/monthly/ecmwf2_v10_5.ctl;kindname="ECMWF-2";climfield="+4 v10";;
ecmwf2_v10_6) file=ECMWFData/monthly/ecmwf2_v10_6.ctl;kindname="ECMWF-2";climfield="+5 v10";;
ecmwf2_v10_jan) file=ECMWFData/monthly/ecmwf2_v10_jan.ensm.ctl;kindname="ECMWF-2";climfield="1Jan v10";;
ecmwf2_v10_feb) file=ECMWFData/monthly/ecmwf2_v10_feb.ensm.ctl;kindname="ECMWF-2";climfield="1Feb v10";;
ecmwf2_v10_mar) file=ECMWFData/monthly/ecmwf2_v10_mar.ensm.ctl;kindname="ECMWF-2";climfield="1Mar v10";;
ecmwf2_v10_apr) file=ECMWFData/monthly/ecmwf2_v10_apr.ensm.ctl;kindname="ECMWF-2";climfield="1Apr v10";;
ecmwf2_v10_may) file=ECMWFData/monthly/ecmwf2_v10_may.ensm.ctl;kindname="ECMWF-2";climfield="1May v10";;
ecmwf2_v10_jun) file=ECMWFData/monthly/ecmwf2_v10_jun.ensm.ctl;kindname="ECMWF-2";climfield="1Jun v10";;
ecmwf2_v10_jul) file=ECMWFData/monthly/ecmwf2_v10_jul.ensm.ctl;kindname="ECMWF-2";climfield="1Jul v10";;
ecmwf2_v10_aug) file=ECMWFData/monthly/ecmwf2_v10_aug.ensm.ctl;kindname="ECMWF-2";climfield="1Aug v10";;
ecmwf2_v10_sep) file=ECMWFData/monthly/ecmwf2_v10_sep.ensm.ctl;kindname="ECMWF-2";climfield="1Sep v10";;
ecmwf2_v10_oct) file=ECMWFData/monthly/ecmwf2_v10_oct.ensm.ctl;kindname="ECMWF-2";climfield="1Oct v10";;
ecmwf2_v10_nov) file=ECMWFData/monthly/ecmwf2_v10_nov.ensm.ctl;kindname="ECMWF-2";climfield="1Nov v10";;
ecmwf2_v10_dec) file=ECMWFData/monthly/ecmwf2_v10_dec.ensm.ctl;kindname="ECMWF-2";climfield="1Dec v10";;

ecmwf2_ssd) file=ECMWFData/monthly/ecmwf2_ssd.ctl;kindname="ECMWF-2";climfield="solar radiation";;
ecmwf2_ssd_1) file=ECMWFData/monthly/ecmwf2_ssd_1.ctl;kindname="ECMWF-2";climfield="+0 solar radiation";;
ecmwf2_ssd_2) file=ECMWFData/monthly/ecmwf2_ssd_2.ctl;kindname="ECMWF-2";climfield="+1 solar radiation";;
ecmwf2_ssd_3) file=ECMWFData/monthly/ecmwf2_ssd_3.ctl;kindname="ECMWF-2";climfield="+2 solar radiation";;
ecmwf2_ssd_4) file=ECMWFData/monthly/ecmwf2_ssd_4.ctl;kindname="ECMWF-2";climfield="+3 solar radiation";;
ecmwf2_ssd_5) file=ECMWFData/monthly/ecmwf2_ssd_5.ctl;kindname="ECMWF-2";climfield="+4 solar radiation";;
ecmwf2_ssd_6) file=ECMWFData/monthly/ecmwf2_ssd_6.ctl;kindname="ECMWF-2";climfield="+5 solar radiation";;
ecmwf2_ssd_jan) file=ECMWFData/monthly/ecmwf2_ssd_jan.ensm.ctl;kindname="ECMWF-2";climfield="1Jan solar radiation";;
ecmwf2_ssd_feb) file=ECMWFData/monthly/ecmwf2_ssd_feb.ensm.ctl;kindname="ECMWF-2";climfield="1Feb solar radiation";;
ecmwf2_ssd_mar) file=ECMWFData/monthly/ecmwf2_ssd_mar.ensm.ctl;kindname="ECMWF-2";climfield="1Mar solar radiation";;
ecmwf2_ssd_apr) file=ECMWFData/monthly/ecmwf2_ssd_apr.ensm.ctl;kindname="ECMWF-2";climfield="1Apr solar radiation";;
ecmwf2_ssd_may) file=ECMWFData/monthly/ecmwf2_ssd_may.ensm.ctl;kindname="ECMWF-2";climfield="1May solar radiation";;
ecmwf2_ssd_jun) file=ECMWFData/monthly/ecmwf2_ssd_jun.ensm.ctl;kindname="ECMWF-2";climfield="1Jun solar radiation";;
ecmwf2_ssd_jul) file=ECMWFData/monthly/ecmwf2_ssd_jul.ensm.ctl;kindname="ECMWF-2";climfield="1Jul solar radiation";;
ecmwf2_ssd_aug) file=ECMWFData/monthly/ecmwf2_ssd_aug.ensm.ctl;kindname="ECMWF-2";climfield="1Aug solar radiation";;
ecmwf2_ssd_sep) file=ECMWFData/monthly/ecmwf2_ssd_sep.ensm.ctl;kindname="ECMWF-2";climfield="1Sep solar radiation";;
ecmwf2_ssd_oct) file=ECMWFData/monthly/ecmwf2_ssd_oct.ensm.ctl;kindname="ECMWF-2";climfield="1Oct solar radiation";;
ecmwf2_ssd_nov) file=ECMWFData/monthly/ecmwf2_ssd_nov.ensm.ctl;kindname="ECMWF-2";climfield="1Nov solar radiation";;
ecmwf2_ssd_dec) file=ECMWFData/monthly/ecmwf2_ssd_dec.ensm.ctl;kindname="ECMWF-2";climfield="1Dec solar radiation";;

ecmwf2_snd_1) file=ECMWFData/monthly/ecmwf2_snd_1.ctl;kindname="ECMWF-2";climfield="+0 snow depth";;
ecmwf2_snd_2) file=ECMWFData/monthly/ecmwf2_snd_2.ctl;kindname="ECMWF-2";climfield="+1 snow depth";;
ecmwf2_snd_3) file=ECMWFData/monthly/ecmwf2_snd_3.ctl;kindname="ECMWF-2";climfield="+2 snow depth";;
ecmwf2_snd_4) file=ECMWFData/monthly/ecmwf2_snd_4.ctl;kindname="ECMWF-2";climfield="+3 snow depth";;
ecmwf2_snd_5) file=ECMWFData/monthly/ecmwf2_snd_5.ctl;kindname="ECMWF-2";climfield="+4 snow depth";;
ecmwf2_snd_6) file=ECMWFData/monthly/ecmwf2_snd_6.ctl;kindname="ECMWF-2";climfield="+5 snow depth";;
ecmwf2_snd_jan) file=ECMWFData/monthly/ecmwf2_snd_jan.ensm.ctl;kindname="ECMWF-2";climfield="1Jan snow depth";;
ecmwf2_snd_feb) file=ECMWFData/monthly/ecmwf2_snd_feb.ensm.ctl;kindname="ECMWF-2";climfield="1Feb snow depth";;
ecmwf2_snd_mar) file=ECMWFData/monthly/ecmwf2_snd_mar.ensm.ctl;kindname="ECMWF-2";climfield="1Mar snow depth";;
ecmwf2_snd_apr) file=ECMWFData/monthly/ecmwf2_snd_apr.ensm.ctl;kindname="ECMWF-2";climfield="1Apr snow depth";;
ecmwf2_snd_may) file=ECMWFData/monthly/ecmwf2_snd_may.ensm.ctl;kindname="ECMWF-2";climfield="1May snow depth";;
ecmwf2_snd_jun) file=ECMWFData/monthly/ecmwf2_snd_jun.ensm.ctl;kindname="ECMWF-2";climfield="1Jun snow depth";;
ecmwf2_snd_jul) file=ECMWFData/monthly/ecmwf2_snd_jul.ensm.ctl;kindname="ECMWF-2";climfield="1Jul snow depth";;
ecmwf2_snd_aug) file=ECMWFData/monthly/ecmwf2_snd_aug.ensm.ctl;kindname="ECMWF-2";climfield="1Aug snow depth";;
ecmwf2_snd_sep) file=ECMWFData/monthly/ecmwf2_snd_sep.ensm.ctl;kindname="ECMWF-2";climfield="1Sep snow depth";;
ecmwf2_snd_oct) file=ECMWFData/monthly/ecmwf2_snd_oct.ensm.ctl;kindname="ECMWF-2";climfield="1Oct snow depth";;
ecmwf2_snd_nov) file=ECMWFData/monthly/ecmwf2_snd_nov.ensm.ctl;kindname="ECMWF-2";climfield="1Nov snow depth";;
ecmwf2_snd_dec) file=ECMWFData/monthly/ecmwf2_snd_dec.ensm.ctl;kindname="ECMWF-2";climfield="1Dec snow depth";;

ecmwf2_tsfc_1) file=ECMWFData/monthly/ecmwf2_sst_1.ctl;kindname="ECMWF-2";climfield="+0 Tsfc";LSMASK=ERA-interim/lsmask.ctl;;
ecmwf2_tsfc_2) file=ECMWFData/monthly/ecmwf2_sst_2.ctl;kindname="ECMWF-2";climfield="+1 Tsfc";LSMASK=ERA-interim/lsmask.ctl;;
ecmwf2_tsfc_3) file=ECMWFData/monthly/ecmwf2_sst_3.ctl;kindname="ECMWF-2";climfield="+2 Tsfc";LSMASK=ERA-interim/lsmask.ctl;;
ecmwf2_tsfc_4) file=ECMWFData/monthly/ecmwf2_sst_4.ctl;kindname="ECMWF-2";climfield="+3 Tsfc";LSMASK=ERA-interim/lsmask.ctl;;
ecmwf2_tsfc_5) file=ECMWFData/monthly/ecmwf2_sst_5.ctl;kindname="ECMWF-2";climfield="+4 Tsfc";LSMASK=ERA-interim/lsmask.ctl;;
ecmwf2_tsfc_6) file=ECMWFData/monthly/ecmwf2_sst_6.ctl;kindname="ECMWF-2";climfield="+5 Tsfc";LSMASK=ERA-interim/lsmask.ctl;;
ecmwf2_tsfc_jan) file=ECMWFData/monthly/ecmwf2_sst_jan.ensm.ctl;kindname="ECMWF-2";climfield="1Jan Tsf";LSMASK=ERA-interim/lsmask.ctl;;
ecmwf2_tsfc_feb) file=ECMWFData/monthly/ecmwf2_sst_feb.ensm.ctl;kindname="ECMWF-2";climfield="1Feb Tsf";LSMASK=ERA-interim/lsmask.ctl;;
ecmwf2_tsfc_mar) file=ECMWFData/monthly/ecmwf2_sst_mar.ensm.ctl;kindname="ECMWF-2";climfield="1Mar Tsf";LSMASK=ERA-interim/lsmask.ctl;;
ecmwf2_tsfc_apr) file=ECMWFData/monthly/ecmwf2_sst_apr.ensm.ctl;kindname="ECMWF-2";climfield="1Apr Tsf";LSMASK=ERA-interim/lsmask.ctl;;
ecmwf2_tsfc_may) file=ECMWFData/monthly/ecmwf2_sst_may.ensm.ctl;kindname="ECMWF-2";climfield="1May Tsf";LSMASK=ERA-interim/lsmask.ctl;;
ecmwf2_tsfc_jun) file=ECMWFData/monthly/ecmwf2_sst_jun.ensm.ctl;kindname="ECMWF-2";climfield="1Jun Tsf";LSMASK=ERA-interim/lsmask.ctl;;
ecmwf2_tsfc_jul) file=ECMWFData/monthly/ecmwf2_sst_jul.ensm.ctl;kindname="ECMWF-2";climfield="1Jul Tsf";LSMASK=ERA-interim/lsmask.ctl;;
ecmwf2_tsfc_aug) file=ECMWFData/monthly/ecmwf2_sst_aug.ensm.ctl;kindname="ECMWF-2";climfield="1Aug Tsf";LSMASK=ERA-interim/lsmask.ctl;;
ecmwf2_tsfc_sep) file=ECMWFData/monthly/ecmwf2_sst_sep.ensm.ctl;kindname="ECMWF-2";climfield="1Sep Tsf";LSMASK=ERA-interim/lsmask.ctl;;
ecmwf2_tsfc_oct) file=ECMWFData/monthly/ecmwf2_sst_oct.ensm.ctl;kindname="ECMWF-2";climfield="1Oct Tsf";LSMASK=ERA-interim/lsmask.ctl;;
ecmwf2_tsfc_nov) file=ECMWFData/monthly/ecmwf2_sst_nov.ensm.ctl;kindname="ECMWF-2";climfield="1Nov Tsf";LSMASK=ERA-interim/lsmask.ctl;;
ecmwf2_tsfc_dec) file=ECMWFData/monthly/ecmwf2_sst_dec.ensm.ctl;kindname="ECMWF-2";climfield="1Dec Tsf";LSMASK=ERA-interim/lsmask.ctl;;

ecmwf2_ssh) file=ECMWFData/monthly/ecmwf2_ssh_o.ctl;kindname="ECMWF-2";climfield="SSH";;
ecmwf2_ssh_1) file=ECMWFData/monthly/ecmwf2_ssh_1_o.ctl;kindname="ECMWF-2";climfield="+0 SSH";;
ecmwf2_ssh_2) file=ECMWFData/monthly/ecmwf2_ssh_2_o.ctl;kindname="ECMWF-2";climfield="+1 SSH";;
ecmwf2_ssh_3) file=ECMWFData/monthly/ecmwf2_ssh_3_o.ctl;kindname="ECMWF-2";climfield="+2 SSH";;
ecmwf2_ssh_4) file=ECMWFData/monthly/ecmwf2_ssh_4_o.ctl;kindname="ECMWF-2";climfield="+3 SSH";;
ecmwf2_ssh_5) file=ECMWFData/monthly/ecmwf2_ssh_5_o.ctl;kindname="ECMWF-2";climfield="+4 SSH";;
ecmwf2_ssh_6) file=ECMWFData/monthly/ecmwf2_ssh_6_o.ctl;kindname="ECMWF-2";climfield="+5 SSH";;

ens_ecmwf_t2m) file=ECMWFData/ecmwf_t2m.ctl;kindname="ensemble ECMWF";climfield="T2m";;
ens_ecmwf_t2m_1) file=ECMWFData/ecmwf_t2m_1_%%.ctl;kindname="ensemble ECMWF";climfield="+0 T2m";;
ens_ecmwf_t2m_2) file=ECMWFData/ecmwf_t2m_2_%%.ctl;kindname="ensemble ECMWF";climfield="+1 T2m";;
ens_ecmwf_t2m_3) file=ECMWFData/ecmwf_t2m_3_%%.ctl;kindname="ensemble ECMWF";climfield="+2 T2m";;
ens_ecmwf_t2m_4) file=ECMWFData/ecmwf_t2m_4_%%.ctl;kindname="ensemble ECMWF";climfield="+3 T2m";;
ens_ecmwf_t2m_5) file=ECMWFData/ecmwf_t2m_5_%%.ctl;kindname="ensemble ECMWF";climfield="+4 T2m";;
ens_ecmwf_t2m_6) file=ECMWFData/ecmwf_t2m_6_%%.ctl;kindname="ensemble ECMWF";climfield="+5 T2m";;
ens_ecmwf_t2m_jan) file=ECMWFData/ecmwf_t2m_jan_%%.ctl;kindname="ensemble ECMWF";climfield="1Jan T2m";;
ens_ecmwf_t2m_feb) file=ECMWFData/ecmwf_t2m_feb_%%.ctl;kindname="ensemble ECMWF";climfield="1Feb T2m";;
ens_ecmwf_t2m_mar) file=ECMWFData/ecmwf_t2m_mar_%%.ctl;kindname="ensemble ECMWF";climfield="1Mar T2m";;
ens_ecmwf_t2m_apr) file=ECMWFData/ecmwf_t2m_apr_%%.ctl;kindname="ensemble ECMWF";climfield="1Apr T2m";;
ens_ecmwf_t2m_may) file=ECMWFData/ecmwf_t2m_may_%%.ctl;kindname="ensemble ECMWF";climfield="1May T2m";;
ens_ecmwf_t2m_jun) file=ECMWFData/ecmwf_t2m_jun_%%.ctl;kindname="ensemble ECMWF";climfield="1Jun T2m";;
ens_ecmwf_t2m_jul) file=ECMWFData/ecmwf_t2m_jul_%%.ctl;kindname="ensemble ECMWF";climfield="1Jul T2m";;
ens_ecmwf_t2m_aug) file=ECMWFData/ecmwf_t2m_aug_%%.ctl;kindname="ensemble ECMWF";climfield="1Aug T2m";;
ens_ecmwf_t2m_sep) file=ECMWFData/ecmwf_t2m_sep_%%.ctl;kindname="ensemble ECMWF";climfield="1Sep T2m";;
ens_ecmwf_t2m_oct) file=ECMWFData/ecmwf_t2m_oct_%%.ctl;kindname="ensemble ECMWF";climfield="1Oct T2m";;
ens_ecmwf_t2m_nov) file=ECMWFData/ecmwf_t2m_nov_%%.ctl;kindname="ensemble ECMWF";climfield="1Nov T2m";;
ens_ecmwf_t2m_dec) file=ECMWFData/ecmwf_t2m_dec_%%.ctl;kindname="ensemble ECMWF";climfield="1Dec T2m";;
ens_ecmwf_prcp) file=ECMWFData/ecmwf_tp.ctl;kindname="ensemble ECMWF";climfield="precipitation";;
ens_ecmwf_prcp_1) file=ECMWFData/ecmwf_tp__1_%%.ctl;kindname="ensemble ECMWF";climfield="+0 precipitation";;
ens_ecmwf_prcp_2) file=ECMWFData/ecmwf_tp__2_%%.ctl;kindname="ensemble ECMWF";climfield="+1 precipitation";;
ens_ecmwf_prcp_3) file=ECMWFData/ecmwf_tp__3_%%.ctl;kindname="ensemble ECMWF";climfield="+2 precipitation";;
ens_ecmwf_prcp_4) file=ECMWFData/ecmwf_tp__4_%%.ctl;kindname="ensemble ECMWF";climfield="+3 precipitation";;
ens_ecmwf_prcp_5) file=ECMWFData/ecmwf_tp__5_%%.ctl;kindname="ensemble ECMWF";climfield="+4 precipitation";;
ens_ecmwf_prcp_6) file=ECMWFData/ecmwf_tp__6_%%.ctl;kindname="ensemble ECMWF";climfield="+5 precipitation";;
ens_ecmwf_prcp_jan) file=ECMWFData/ecmwf_tp__jan_%%.ctl;kindname="ensemble ECMWF";climfield="1Jan precipitation";;
ens_ecmwf_prcp_feb) file=ECMWFData/ecmwf_tp__feb_%%.ctl;kindname="ensemble ECMWF";climfield="1Feb precipitation";;
ens_ecmwf_prcp_mar) file=ECMWFData/ecmwf_tp__mar_%%.ctl;kindname="ensemble ECMWF";climfield="1Mar precipitation";;
ens_ecmwf_prcp_apr) file=ECMWFData/ecmwf_tp__apr_%%.ctl;kindname="ensemble ECMWF";climfield="1Apr precipitation";;
ens_ecmwf_prcp_may) file=ECMWFData/ecmwf_tp__may_%%.ctl;kindname="ensemble ECMWF";climfield="1May precipitation";;
ens_ecmwf_prcp_jun) file=ECMWFData/ecmwf_tp__jun_%%.ctl;kindname="ensemble ECMWF";climfield="1Jun precipitation";;
ens_ecmwf_prcp_jul) file=ECMWFData/ecmwf_tp__jul_%%.ctl;kindname="ensemble ECMWF";climfield="1Jul precipitation";;
ens_ecmwf_prcp_aug) file=ECMWFData/ecmwf_tp__aug_%%.ctl;kindname="ensemble ECMWF";climfield="1Aug precipitation";;
ens_ecmwf_prcp_sep) file=ECMWFData/ecmwf_tp__sep_%%.ctl;kindname="ensemble ECMWF";climfield="1Sep precipitation";;
ens_ecmwf_prcp_oct) file=ECMWFData/ecmwf_tp__oct_%%.ctl;kindname="ensemble ECMWF";climfield="1Oct precipitation";;
ens_ecmwf_prcp_nov) file=ECMWFData/ecmwf_tp__nov_%%.ctl;kindname="ensemble ECMWF";climfield="1Nov precipitation";;
ens_ecmwf_prcp_dec) file=ECMWFData/ecmwf_tp__dec_%%.ctl;kindname="ensemble ECMWF";climfield="1Dec precipitation";;
ens_ecmwf_slp) file=ECMWFData/ecmwf_msl.ctl;kindname="ensemble ECMWF";climfield="SLP";;
ens_ecmwf_slp_1) file=ECMWFData/ecmwf_msl_1_%%.ctl;kindname="ensemble ECMWF";climfield="+0 SLP";;
ens_ecmwf_slp_2) file=ECMWFData/ecmwf_msl_2_%%.ctl;kindname="ensemble ECMWF";climfield="+1 SLP";;
ens_ecmwf_slp_3) file=ECMWFData/ecmwf_msl_3_%%.ctl;kindname="ensemble ECMWF";climfield="+2 SLP";;
ens_ecmwf_slp_4) file=ECMWFData/ecmwf_msl_4_%%.ctl;kindname="ensemble ECMWF";climfield="+3 SLP";;
ens_ecmwf_slp_5) file=ECMWFData/ecmwf_msl_5_%%.ctl;kindname="ensemble ECMWF";climfield="+4 SLP";;
ens_ecmwf_slp_6) file=ECMWFData/ecmwf_msl_6_%%.ctl;kindname="ensemble ECMWF";climfield="+5 SLP";;
ens_ecmwf_slp_jan) file=ECMWFData/ecmwf_msl_jan_%%.ctl;kindname="ensemble ECMWF";climfield="1Jan SLP";;
ens_ecmwf_slp_feb) file=ECMWFData/ecmwf_msl_feb_%%.ctl;kindname="ensemble ECMWF";climfield="1Feb SLP";;
ens_ecmwf_slp_mar) file=ECMWFData/ecmwf_msl_mar_%%.ctl;kindname="ensemble ECMWF";climfield="1Mar SLP";;
ens_ecmwf_slp_apr) file=ECMWFData/ecmwf_msl_apr_%%.ctl;kindname="ensemble ECMWF";climfield="1Apr SLP";;
ens_ecmwf_slp_may) file=ECMWFData/ecmwf_msl_may_%%.ctl;kindname="ensemble ECMWF";climfield="1May SLP";;
ens_ecmwf_slp_jun) file=ECMWFData/ecmwf_msl_jun_%%.ctl;kindname="ensemble ECMWF";climfield="1Jun SLP";;
ens_ecmwf_slp_jul) file=ECMWFData/ecmwf_msl_jul_%%.ctl;kindname="ensemble ECMWF";climfield="1Jul SLP";;
ens_ecmwf_slp_aug) file=ECMWFData/ecmwf_msl_aug_%%.ctl;kindname="ensemble ECMWF";climfield="1Aug SLP";;
ens_ecmwf_slp_sep) file=ECMWFData/ecmwf_msl_sep_%%.ctl;kindname="ensemble ECMWF";climfield="1Sep SLP";;
ens_ecmwf_slp_oct) file=ECMWFData/ecmwf_msl_oct_%%.ctl;kindname="ensemble ECMWF";climfield="1Oct SLP";;
ens_ecmwf_slp_nov) file=ECMWFData/ecmwf_msl_nov_%%.ctl;kindname="ensemble ECMWF";climfield="1Nov SLP";;
ens_ecmwf_slp_dec) file=ECMWFData/ecmwf_msl_dec_%%.ctl;kindname="ensemble ECMWF";climfield="1Dec SLP";;
ens_ecmwf_z500) file=ECMWFData/ecmwf_z500.ctl;kindname="ensemble ECMWF";climfield="z500";;
ens_ecmwf_z500_1) file=ECMWFData/ecmwf_z500_1_%%.ctl;kindname="ensemble ECMWF";climfield="+0 z500";;
ens_ecmwf_z500_2) file=ECMWFData/ecmwf_z500_2_%%.ctl;kindname="ensemble ECMWF";climfield="+1 z500";;
ens_ecmwf_z500_3) file=ECMWFData/ecmwf_z500_3_%%.ctl;kindname="ensemble ECMWF";climfield="+2 z500";;
ens_ecmwf_z500_4) file=ECMWFData/ecmwf_z500_4_%%.ctl;kindname="ensemble ECMWF";climfield="+3 z500";;
ens_ecmwf_z500_5) file=ECMWFData/ecmwf_z500_5_%%.ctl;kindname="ensemble ECMWF";climfield="+4 z500";;
ens_ecmwf_z500_6) file=ECMWFData/ecmwf_z500_6_%%.ctl;kindname="ensemble ECMWF";climfield="+5 z500";;
ens_ecmwf_z500_jan) file=ECMWFData/ecmwf_z500_jan_%%.ctl;kindname="ensemble ECMWF";climfield="1Jan z500";;
ens_ecmwf_z500_feb) file=ECMWFData/ecmwf_z500_feb_%%.ctl;kindname="ensemble ECMWF";climfield="1Feb z500";;
ens_ecmwf_z500_mar) file=ECMWFData/ecmwf_z500_mar_%%.ctl;kindname="ensemble ECMWF";climfield="1Mar z500";;
ens_ecmwf_z500_apr) file=ECMWFData/ecmwf_z500_apr_%%.ctl;kindname="ensemble ECMWF";climfield="1Apr z500";;
ens_ecmwf_z500_may) file=ECMWFData/ecmwf_z500_may_%%.ctl;kindname="ensemble ECMWF";climfield="1May z500";;
ens_ecmwf_z500_jun) file=ECMWFData/ecmwf_z500_jun_%%.ctl;kindname="ensemble ECMWF";climfield="1Jun z500";;
ens_ecmwf_z500_jul) file=ECMWFData/ecmwf_z500_jul_%%.ctl;kindname="ensemble ECMWF";climfield="1Jul z500";;
ens_ecmwf_z500_aug) file=ECMWFData/ecmwf_z500_aug_%%.ctl;kindname="ensemble ECMWF";climfield="1Aug z500";;
ens_ecmwf_z500_sep) file=ECMWFData/ecmwf_z500_sep_%%.ctl;kindname="ensemble ECMWF";climfield="1Sep z500";;
ens_ecmwf_z500_oct) file=ECMWFData/ecmwf_z500_oct_%%.ctl;kindname="ensemble ECMWF";climfield="1Oct z500";;
ens_ecmwf_z500_nov) file=ECMWFData/ecmwf_z500_nov_%%.ctl;kindname="ensemble ECMWF";climfield="1Nov z500";;
ens_ecmwf_z500_dec) file=ECMWFData/ecmwf_z500_dec_%%.ctl;kindname="ensemble ECMWF";climfield="1Dec z500";;
ens_ecmwf_u10) file=ECMWFData/ecmwf_u10.ctl;kindname="ensemble ECMWF";climfield="u10";;
ens_ecmwf_u10_1) file=ECMWFData/ecmwf_u10_1_%%.ctl;kindname="ensemble ECMWF";climfield="+0 u10";;
ens_ecmwf_u10_2) file=ECMWFData/ecmwf_u10_2_%%.ctl;kindname="ensemble ECMWF";climfield="+1 u10";;
ens_ecmwf_u10_3) file=ECMWFData/ecmwf_u10_3_%%.ctl;kindname="ensemble ECMWF";climfield="+2 u10";;
ens_ecmwf_u10_4) file=ECMWFData/ecmwf_u10_4_%%.ctl;kindname="ensemble ECMWF";climfield="+3 u10";;
ens_ecmwf_u10_5) file=ECMWFData/ecmwf_u10_5_%%.ctl;kindname="ensemble ECMWF";climfield="+4 u10";;
ens_ecmwf_u10_6) file=ECMWFData/ecmwf_u10_6_%%.ctl;kindname="ensemble ECMWF";climfield="+5 u10";;
ens_ecmwf_u10_jan) file=ECMWFData/ecmwf_u10_jan_%%.ctl;kindname="ensemble ECMWF";climfield="1Jan u10";;
ens_ecmwf_u10_feb) file=ECMWFData/ecmwf_u10_feb_%%.ctl;kindname="ensemble ECMWF";climfield="1Feb u10";;
ens_ecmwf_u10_mar) file=ECMWFData/ecmwf_u10_mar_%%.ctl;kindname="ensemble ECMWF";climfield="1Mar u10";;
ens_ecmwf_u10_apr) file=ECMWFData/ecmwf_u10_apr_%%.ctl;kindname="ensemble ECMWF";climfield="1Apr u10";;
ens_ecmwf_u10_may) file=ECMWFData/ecmwf_u10_may_%%.ctl;kindname="ensemble ECMWF";climfield="1May u10";;
ens_ecmwf_u10_jun) file=ECMWFData/ecmwf_u10_jun_%%.ctl;kindname="ensemble ECMWF";climfield="1Jun u10";;
ens_ecmwf_u10_jul) file=ECMWFData/ecmwf_u10_jul_%%.ctl;kindname="ensemble ECMWF";climfield="1Jul u10";;
ens_ecmwf_u10_aug) file=ECMWFData/ecmwf_u10_aug_%%.ctl;kindname="ensemble ECMWF";climfield="1Aug u10";;
ens_ecmwf_u10_sep) file=ECMWFData/ecmwf_u10_sep_%%.ctl;kindname="ensemble ECMWF";climfield="1Sep u10";;
ens_ecmwf_u10_oct) file=ECMWFData/ecmwf_u10_oct_%%.ctl;kindname="ensemble ECMWF";climfield="1Oct u10";;
ens_ecmwf_u10_nov) file=ECMWFData/ecmwf_u10_nov_%%.ctl;kindname="ensemble ECMWF";climfield="1Nov u10";;
ens_ecmwf_u10_dec) file=ECMWFData/ecmwf_u10_dec_%%.ctl;kindname="ensemble ECMWF";climfield="1Dec u10";;
ens_ecmwf_v10) file=ECMWFData/ecmwf_v10.ctl;kindname="ensemble ECMWF";climfield="v10";;
ens_ecmwf_v10_1) file=ECMWFData/ecmwf_v10_1_%%.ctl;kindname="ensemble ECMWF";climfield="+0 v10";;
ens_ecmwf_v10_2) file=ECMWFData/ecmwf_v10_2_%%.ctl;kindname="ensemble ECMWF";climfield="+1 v10";;
ens_ecmwf_v10_3) file=ECMWFData/ecmwf_v10_3_%%.ctl;kindname="ensemble ECMWF";climfield="+2 v10";;
ens_ecmwf_v10_4) file=ECMWFData/ecmwf_v10_4_%%.ctl;kindname="ensemble ECMWF";climfield="+3 v10";;
ens_ecmwf_v10_5) file=ECMWFData/ecmwf_v10_5_%%.ctl;kindname="ensemble ECMWF";climfield="+4 v10";;
ens_ecmwf_v10_6) file=ECMWFData/ecmwf_v10_6_%%.ctl;kindname="ensemble ECMWF";climfield="+5 v10";;
ens_ecmwf_v10_jan) file=ECMWFData/ecmwf_v10_jan_%%.ctl;kindname="ensemble ECMWF";climfield="1Jan v10";;
ens_ecmwf_v10_feb) file=ECMWFData/ecmwf_v10_feb_%%.ctl;kindname="ensemble ECMWF";climfield="1Feb v10";;
ens_ecmwf_v10_mar) file=ECMWFData/ecmwf_v10_mar_%%.ctl;kindname="ensemble ECMWF";climfield="1Mar v10";;
ens_ecmwf_v10_apr) file=ECMWFData/ecmwf_v10_apr_%%.ctl;kindname="ensemble ECMWF";climfield="1Apr v10";;
ens_ecmwf_v10_may) file=ECMWFData/ecmwf_v10_may_%%.ctl;kindname="ensemble ECMWF";climfield="1May v10";;
ens_ecmwf_v10_jun) file=ECMWFData/ecmwf_v10_jun_%%.ctl;kindname="ensemble ECMWF";climfield="1Jun v10";;
ens_ecmwf_v10_jul) file=ECMWFData/ecmwf_v10_jul_%%.ctl;kindname="ensemble ECMWF";climfield="1Jul v10";;
ens_ecmwf_v10_aug) file=ECMWFData/ecmwf_v10_aug_%%.ctl;kindname="ensemble ECMWF";climfield="1Aug v10";;
ens_ecmwf_v10_sep) file=ECMWFData/ecmwf_v10_sep_%%.ctl;kindname="ensemble ECMWF";climfield="1Sep v10";;
ens_ecmwf_v10_oct) file=ECMWFData/ecmwf_v10_oct_%%.ctl;kindname="ensemble ECMWF";climfield="1Oct v10";;
ens_ecmwf_v10_nov) file=ECMWFData/ecmwf_v10_nov_%%.ctl;kindname="ensemble ECMWF";climfield="1Nov v10";;
ens_ecmwf_v10_dec) file=ECMWFData/ecmwf_v10_dec_%%.ctl;kindname="ensemble ECMWF";climfield="1Dec v10";;
ens_ecmwf_ssr) file=ECMWFData/ecmwf_ssr.ctl;kindname="ensemble ECMWF";climfield="solar radiation";;
ens_ecmwf_ssr_1) file=ECMWFData/ecmwf_ssr_1_%%.ctl;kindname="ensemble ECMWF";climfield="+0 solar radiation";;
ens_ecmwf_ssr_2) file=ECMWFData/ecmwf_ssr_2_%%.ctl;kindname="ensemble ECMWF";climfield="+1 solar radiation";;
ens_ecmwf_ssr_3) file=ECMWFData/ecmwf_ssr_3_%%.ctl;kindname="ensemble ECMWF";climfield="+2 solar radiation";;
ens_ecmwf_ssr_4) file=ECMWFData/ecmwf_ssr_4_%%.ctl;kindname="ensemble ECMWF";climfield="+3 solar radiation";;
ens_ecmwf_ssr_5) file=ECMWFData/ecmwf_ssr_5_%%.ctl;kindname="ensemble ECMWF";climfield="+4 solar radiation";;
ens_ecmwf_ssr_6) file=ECMWFData/ecmwf_ssr_6_%%.ctl;kindname="ensemble ECMWF";climfield="+5 solar radiation";;
ens_ecmwf_ssr_jan) file=ECMWFData/ecmwf_ssr_jan_%%.ctl;kindname="ensemble ECMWF";climfield="1Jan solar radiation";;
ens_ecmwf_ssr_feb) file=ECMWFData/ecmwf_ssr_feb_%%.ctl;kindname="ensemble ECMWF";climfield="1Feb solar radiation";;
ens_ecmwf_ssr_mar) file=ECMWFData/ecmwf_ssr_mar_%%.ctl;kindname="ensemble ECMWF";climfield="1Mar solar radiation";;
ens_ecmwf_ssr_apr) file=ECMWFData/ecmwf_ssr_apr_%%.ctl;kindname="ensemble ECMWF";climfield="1Apr solar radiation";;
ens_ecmwf_ssr_may) file=ECMWFData/ecmwf_ssr_may_%%.ctl;kindname="ensemble ECMWF";climfield="1May solar radiation";;
ens_ecmwf_ssr_jun) file=ECMWFData/ecmwf_ssr_jun_%%.ctl;kindname="ensemble ECMWF";climfield="1Jun solar radiation";;
ens_ecmwf_ssr_jul) file=ECMWFData/ecmwf_ssr_jul_%%.ctl;kindname="ensemble ECMWF";climfield="1Jul solar radiation";;
ens_ecmwf_ssr_aug) file=ECMWFData/ecmwf_ssr_aug_%%.ctl;kindname="ensemble ECMWF";climfield="1Aug solar radiation";;
ens_ecmwf_ssr_sep) file=ECMWFData/ecmwf_ssr_sep_%%.ctl;kindname="ensemble ECMWF";climfield="1Sep solar radiation";;
ens_ecmwf_ssr_oct) file=ECMWFData/ecmwf_ssr_oct_%%.ctl;kindname="ensemble ECMWF";climfield="1Oct solar radiation";;
ens_ecmwf_ssr_nov) file=ECMWFData/ecmwf_ssr_nov_%%.ctl;kindname="ensemble ECMWF";climfield="1Nov solar radiation";;
ens_ecmwf_ssr_dec) file=ECMWFData/ecmwf_ssr_dec_%%.ctl;kindname="ensemble ECMWF";climfield="1Dec solar radiation";;

ens_ecmwf_sst) file=ECMWFData/ecmwf_sst_o.ctl;kindname="ensemble ECMWF";climfield="SST";;
ens_ecmwf_tsf_1) file=ECMWFData/ecmwf_tsf_1_%%.ctl;kindname="ensemble ECMWF";climfield="+0 Tsfc";;
ens_ecmwf_tsf_2) file=ECMWFData/ecmwf_tsf_2_%%.ctl;kindname="ensemble ECMWF";climfield="+1 Tsfc";;
ens_ecmwf_tsf_3) file=ECMWFData/ecmwf_tsf_3_%%.ctl;kindname="ensemble ECMWF";climfield="+2 Tsfc";;
ens_ecmwf_tsf_4) file=ECMWFData/ecmwf_tsf_4_%%.ctl;kindname="ensemble ECMWF";climfield="+3 Tsfc";;
ens_ecmwf_tsf_5) file=ECMWFData/ecmwf_tsf_5_%%.ctl;kindname="ensemble ECMWF";climfield="+4 Tsfc";;
ens_ecmwf_tsf_6) file=ECMWFData/ecmwf_tsf_6_%%.ctl;kindname="ensemble ECMWF";climfield="+5 Tsfc";;
ens_ecmwf_tsf_jan) file=ECMWFData/ecmwf_tsf_jan_%%.ctl;kindname="ensemble ECMWF";climfield="1Jan Tsf";;
ens_ecmwf_tsf_feb) file=ECMWFData/ecmwf_tsf_feb_%%.ctl;kindname="ensemble ECMWF";climfield="1Feb Tsf";;
ens_ecmwf_tsf_mar) file=ECMWFData/ecmwf_tsf_mar_%%.ctl;kindname="ensemble ECMWF";climfield="1Mar Tsf";;
ens_ecmwf_tsf_apr) file=ECMWFData/ecmwf_tsf_apr_%%.ctl;kindname="ensemble ECMWF";climfield="1Apr Tsf";;
ens_ecmwf_tsf_may) file=ECMWFData/ecmwf_tsf_may_%%.ctl;kindname="ensemble ECMWF";climfield="1May Tsf";;
ens_ecmwf_tsf_jun) file=ECMWFData/ecmwf_tsf_jun_%%.ctl;kindname="ensemble ECMWF";climfield="1Jun Tsf";;
ens_ecmwf_tsf_jul) file=ECMWFData/ecmwf_tsf_jul_%%.ctl;kindname="ensemble ECMWF";climfield="1Jul Tsf";;
ens_ecmwf_tsf_aug) file=ECMWFData/ecmwf_tsf_aug_%%.ctl;kindname="ensemble ECMWF";climfield="1Aug Tsf";;
ens_ecmwf_tsf_sep) file=ECMWFData/ecmwf_tsf_sep_%%.ctl;kindname="ensemble ECMWF";climfield="1Sep Tsf";;
ens_ecmwf_tsf_oct) file=ECMWFData/ecmwf_tsf_oct_%%.ctl;kindname="ensemble ECMWF";climfield="1Oct Tsf";;
ens_ecmwf_tsf_nov) file=ECMWFData/ecmwf_tsf_nov_%%.ctl;kindname="ensemble ECMWF";climfield="1Nov Tsf";;
ens_ecmwf_tsf_dec) file=ECMWFData/ecmwf_tsf_dec_%%.ctl;kindname="ensemble ECMWF";climfield="1Dec Tsf";;

ens_ecmwf_ssh) file=ECMWFData/ecmwf_ssh_o.ctl;kindname="ensemble ECMWF";climfield="SSH";;
ens_ecmwf_ssh_1) file=ECMWFData/ecmwf_ssh_1_o_%%.ctl;kindname="ensemble ECMWF";climfield="+0 SSH";;
ens_ecmwf_ssh_2) file=ECMWFData/ecmwf_ssh_2_o_%%.ctl;kindname="ensemble ECMWF";climfield="+1 SSH";;
ens_ecmwf_ssh_3) file=ECMWFData/ecmwf_ssh_3_o_%%.ctl;kindname="ensemble ECMWF";climfield="+2 SSH";;
ens_ecmwf_ssh_4) file=ECMWFData/ecmwf_ssh_4_o_%%.ctl;kindname="ensemble ECMWF";climfield="+3 SSH";;
ens_ecmwf_ssh_5) file=ECMWFData/ecmwf_ssh_5_o_%%.ctl;kindname="ensemble ECMWF";climfield="+4 SSH";;
ens_ecmwf_ssh_6) file=ECMWFData/ecmwf_ssh_6_o_%%.ctl;kindname="ensemble ECMWF";climfield="+5 SSH";;

ens_ecmwf2_t2m_1) file=ECMWFData/monthly/ecmwf2_t2m_1_m%%.ctl;kindname="ensemble ECMWF-2";climfield="+0 T2m";;
ens_ecmwf2_t2m_2) file=ECMWFData/monthly/ecmwf2_t2m_2_m%%.ctl;kindname="ensemble ECMWF-2";climfield="+1 T2m";;
ens_ecmwf2_t2m_3) file=ECMWFData/monthly/ecmwf2_t2m_3_m%%.ctl;kindname="ensemble ECMWF-2";climfield="+2 T2m";;
ens_ecmwf2_t2m_4) file=ECMWFData/monthly/ecmwf2_t2m_4_m%%.ctl;kindname="ensemble ECMWF-2";climfield="+3 T2m";;
ens_ecmwf2_t2m_5) file=ECMWFData/monthly/ecmwf2_t2m_5_m%%.ctl;kindname="ensemble ECMWF-2";climfield="+4 T2m";;
ens_ecmwf2_t2m_6) file=ECMWFData/monthly/ecmwf2_t2m_6_m%%.ctl;kindname="ensemble ECMWF-2";climfield="+5 T2m";;
ens_ecmwf2_t2m_jan) file=ECMWFData/monthly/ecmwf2_t2m_jan_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Jan T2m";;
ens_ecmwf2_t2m_feb) file=ECMWFData/monthly/ecmwf2_t2m_feb_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Feb T2m";;
ens_ecmwf2_t2m_mar) file=ECMWFData/monthly/ecmwf2_t2m_mar_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Mar T2m";;
ens_ecmwf2_t2m_apr) file=ECMWFData/monthly/ecmwf2_t2m_apr_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Apr T2m";;
ens_ecmwf2_t2m_may) file=ECMWFData/monthly/ecmwf2_t2m_may_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1May T2m";;
ens_ecmwf2_t2m_jun) file=ECMWFData/monthly/ecmwf2_t2m_jun_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Jun T2m";;
ens_ecmwf2_t2m_jul) file=ECMWFData/monthly/ecmwf2_t2m_jul_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Jul T2m";;
ens_ecmwf2_t2m_aug) file=ECMWFData/monthly/ecmwf2_t2m_aug_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Aug T2m";;
ens_ecmwf2_t2m_sep) file=ECMWFData/monthly/ecmwf2_t2m_sep_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Sep T2m";;
ens_ecmwf2_t2m_oct) file=ECMWFData/monthly/ecmwf2_t2m_oct_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Oct T2m";;
ens_ecmwf2_t2m_nov) file=ECMWFData/monthly/ecmwf2_t2m_nov_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Nov T2m";;
ens_ecmwf2_t2m_dec) file=ECMWFData/monthly/ecmwf2_t2m_dec_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Dec T2m";;

ens_ecmwf2_t2x_1) file=ECMWFData/monthly/ecmwf2_t2x_1_m%%.ctl;kindname="ensemble ECMWF-2";climfield="+0 T2max";;
ens_ecmwf2_t2x_2) file=ECMWFData/monthly/ecmwf2_t2x_2_m%%.ctl;kindname="ensemble ECMWF-2";climfield="+1 T2max";;
ens_ecmwf2_t2x_3) file=ECMWFData/monthly/ecmwf2_t2x_3_m%%.ctl;kindname="ensemble ECMWF-2";climfield="+2 T2max";;
ens_ecmwf2_t2x_4) file=ECMWFData/monthly/ecmwf2_t2x_4_m%%.ctl;kindname="ensemble ECMWF-2";climfield="+3 T2max";;
ens_ecmwf2_t2x_5) file=ECMWFData/monthly/ecmwf2_t2x_5_m%%.ctl;kindname="ensemble ECMWF-2";climfield="+4 T2max";;
ens_ecmwf2_t2x_6) file=ECMWFData/monthly/ecmwf2_t2x_6_m%%.ctl;kindname="ensemble ECMWF-2";climfield="+5 T2max";;
ens_ecmwf2_t2x_jan) file=ECMWFData/monthly/ecmwf2_t2x_jan_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Jan T2max";;
ens_ecmwf2_t2x_feb) file=ECMWFData/monthly/ecmwf2_t2x_feb_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Feb T2max";;
ens_ecmwf2_t2x_mar) file=ECMWFData/monthly/ecmwf2_t2x_mar_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Mar T2max";;
ens_ecmwf2_t2x_apr) file=ECMWFData/monthly/ecmwf2_t2x_apr_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Apr T2max";;
ens_ecmwf2_t2x_may) file=ECMWFData/monthly/ecmwf2_t2x_may_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1May T2max";;
ens_ecmwf2_t2x_jun) file=ECMWFData/monthly/ecmwf2_t2x_jun_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Jun T2max";;
ens_ecmwf2_t2x_jul) file=ECMWFData/monthly/ecmwf2_t2x_jul_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Jul T2max";;
ens_ecmwf2_t2x_aug) file=ECMWFData/monthly/ecmwf2_t2x_aug_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Aug T2max";;
ens_ecmwf2_t2x_sep) file=ECMWFData/monthly/ecmwf2_t2x_sep_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Sep T2max";;
ens_ecmwf2_t2x_oct) file=ECMWFData/monthly/ecmwf2_t2x_oct_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Oct T2max";;
ens_ecmwf2_t2x_nov) file=ECMWFData/monthly/ecmwf2_t2x_nov_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Nov T2max";;
ens_ecmwf2_t2x_dec) file=ECMWFData/monthly/ecmwf2_t2x_dec_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Dec T2max";;

ens_ecmwf2_t2n_1) file=ECMWFData/monthly/ecmwf2_t2n_1_m%%.ctl;kindname="ensemble ECMWF-2";climfield="+0 T2min";;
ens_ecmwf2_t2n_2) file=ECMWFData/monthly/ecmwf2_t2n_2_m%%.ctl;kindname="ensemble ECMWF-2";climfield="+1 T2min";;
ens_ecmwf2_t2n_3) file=ECMWFData/monthly/ecmwf2_t2n_3_m%%.ctl;kindname="ensemble ECMWF-2";climfield="+2 T2min";;
ens_ecmwf2_t2n_4) file=ECMWFData/monthly/ecmwf2_t2n_4_m%%.ctl;kindname="ensemble ECMWF-2";climfield="+3 T2min";;
ens_ecmwf2_t2n_5) file=ECMWFData/monthly/ecmwf2_t2n_5_m%%.ctl;kindname="ensemble ECMWF-2";climfield="+4 T2min";;
ens_ecmwf2_t2n_6) file=ECMWFData/monthly/ecmwf2_t2n_6_m%%.ctl;kindname="ensemble ECMWF-2";climfield="+5 T2min";;
ens_ecmwf2_t2n_jan) file=ECMWFData/monthly/ecmwf2_t2n_jan_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Jan T2min";;
ens_ecmwf2_t2n_feb) file=ECMWFData/monthly/ecmwf2_t2n_feb_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Feb T2min";;
ens_ecmwf2_t2n_mar) file=ECMWFData/monthly/ecmwf2_t2n_mar_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Mar T2min";;
ens_ecmwf2_t2n_apr) file=ECMWFData/monthly/ecmwf2_t2n_apr_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Apr T2min";;
ens_ecmwf2_t2n_may) file=ECMWFData/monthly/ecmwf2_t2n_may_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1May T2min";;
ens_ecmwf2_t2n_jun) file=ECMWFData/monthly/ecmwf2_t2n_jun_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Jun T2min";;
ens_ecmwf2_t2n_jul) file=ECMWFData/monthly/ecmwf2_t2n_jul_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Jul T2min";;
ens_ecmwf2_t2n_aug) file=ECMWFData/monthly/ecmwf2_t2n_aug_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Aug T2min";;
ens_ecmwf2_t2n_sep) file=ECMWFData/monthly/ecmwf2_t2n_sep_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Sep T2min";;
ens_ecmwf2_t2n_oct) file=ECMWFData/monthly/ecmwf2_t2n_oct_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Oct T2min";;
ens_ecmwf2_t2n_nov) file=ECMWFData/monthly/ecmwf2_t2n_nov_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Nov T2min";;
ens_ecmwf2_t2n_dec) file=ECMWFData/monthly/ecmwf2_t2n_dec_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Dec T2min";;

ens_ecmwf2_t850_1) file=ECMWFData/monthly/ecmwf2_t850_1_m%%.ctl;kindname="ensemble ECMWF-2";climfield="+0 T850";;
ens_ecmwf2_t850_2) file=ECMWFData/monthly/ecmwf2_t850_2_m%%.ctl;kindname="ensemble ECMWF-2";climfield="+1 T850";;
ens_ecmwf2_t850_3) file=ECMWFData/monthly/ecmwf2_t850_3_m%%.ctl;kindname="ensemble ECMWF-2";climfield="+2 T850";;
ens_ecmwf2_t850_4) file=ECMWFData/monthly/ecmwf2_t850_4_m%%.ctl;kindname="ensemble ECMWF-2";climfield="+3 T850";;
ens_ecmwf2_t850_5) file=ECMWFData/monthly/ecmwf2_t850_5_m%%.ctl;kindname="ensemble ECMWF-2";climfield="+4 T850";;
ens_ecmwf2_t850_6) file=ECMWFData/monthly/ecmwf2_t850_6_m%%.ctl;kindname="ensemble ECMWF-2";climfield="+5 T850";;
ens_ecmwf2_t850_jan) file=ECMWFData/monthly/ecmwf2_t850_jan_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Jan T850";;
ens_ecmwf2_t850_feb) file=ECMWFData/monthly/ecmwf2_t850_feb_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Feb T850";;
ens_ecmwf2_t850_mar) file=ECMWFData/monthly/ecmwf2_t850_mar_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Mar T850";;
ens_ecmwf2_t850_apr) file=ECMWFData/monthly/ecmwf2_t850_apr_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Apr T850";;
ens_ecmwf2_t850_may) file=ECMWFData/monthly/ecmwf2_t850_may_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1May T850";;
ens_ecmwf2_t850_jun) file=ECMWFData/monthly/ecmwf2_t850_jun_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Jun T850";;
ens_ecmwf2_t850_jul) file=ECMWFData/monthly/ecmwf2_t850_jul_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Jul T850";;
ens_ecmwf2_t850_aug) file=ECMWFData/monthly/ecmwf2_t850_aug_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Aug T850";;
ens_ecmwf2_t850_sep) file=ECMWFData/monthly/ecmwf2_t850_sep_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Sep T850";;
ens_ecmwf2_t850_oct) file=ECMWFData/monthly/ecmwf2_t850_oct_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Oct T850";;
ens_ecmwf2_t850_nov) file=ECMWFData/monthly/ecmwf2_t850_nov_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Nov T850";;
ens_ecmwf2_t850_dec) file=ECMWFData/monthly/ecmwf2_t850_dec_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Dec T850";;

ens_ecmwf2_prcp_1) file=ECMWFData/monthly/ecmwf2_prcp_1_m%%.ctl;kindname="ensemble ECMWF-2";climfield="+0 precipitation";;
ens_ecmwf2_prcp_2) file=ECMWFData/monthly/ecmwf2_prcp_2_m%%.ctl;kindname="ensemble ECMWF-2";climfield="+1 precipitation";;
ens_ecmwf2_prcp_3) file=ECMWFData/monthly/ecmwf2_prcp_3_m%%.ctl;kindname="ensemble ECMWF-2";climfield="+2 precipitation";;
ens_ecmwf2_prcp_4) file=ECMWFData/monthly/ecmwf2_prcp_4_m%%.ctl;kindname="ensemble ECMWF-2";climfield="+3 precipitation";;
ens_ecmwf2_prcp_5) file=ECMWFData/monthly/ecmwf2_prcp_5_m%%.ctl;kindname="ensemble ECMWF-2";climfield="+4 precipitation";;
ens_ecmwf2_prcp_6) file=ECMWFData/monthly/ecmwf2_prcp_6_m%%.ctl;kindname="ensemble ECMWF-2";climfield="+5 precipitation";;
ens_ecmwf2_prcp_jan) file=ECMWFData/monthly/ecmwf2_prcp_jan_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Jan precipitation";;
ens_ecmwf2_prcp_feb) file=ECMWFData/monthly/ecmwf2_prcp_feb_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Feb precipitation";;
ens_ecmwf2_prcp_mar) file=ECMWFData/monthly/ecmwf2_prcp_mar_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Mar precipitation";;
ens_ecmwf2_prcp_apr) file=ECMWFData/monthly/ecmwf2_prcp_apr_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Apr precipitation";;
ens_ecmwf2_prcp_may) file=ECMWFData/monthly/ecmwf2_prcp_may_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1May precipitation";;
ens_ecmwf2_prcp_jun) file=ECMWFData/monthly/ecmwf2_prcp_jun_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Jun precipitation";;
ens_ecmwf2_prcp_jul) file=ECMWFData/monthly/ecmwf2_prcp_jul_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Jul precipitation";;
ens_ecmwf2_prcp_aug) file=ECMWFData/monthly/ecmwf2_prcp_aug_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Aug precipitation";;
ens_ecmwf2_prcp_sep) file=ECMWFData/monthly/ecmwf2_prcp_sep_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Sep precipitation";;
ens_ecmwf2_prcp_oct) file=ECMWFData/monthly/ecmwf2_prcp_oct_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Oct precipitation";;
ens_ecmwf2_prcp_nov) file=ECMWFData/monthly/ecmwf2_prcp_nov_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Nov precipitation";;
ens_ecmwf2_prcp_dec) file=ECMWFData/monthly/ecmwf2_prcp_dec_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Dec precipitation";;

ens_ecmwf2_msl_1) file=ECMWFData/monthly/ecmwf2_msl_1_m%%.ctl;kindname="ensemble ECMWF-2";climfield="+0 SLP";;
ens_ecmwf2_msl_2) file=ECMWFData/monthly/ecmwf2_msl_2_m%%.ctl;kindname="ensemble ECMWF-2";climfield="+1 SLP";;
ens_ecmwf2_msl_3) file=ECMWFData/monthly/ecmwf2_msl_3_m%%.ctl;kindname="ensemble ECMWF-2";climfield="+2 SLP";;
ens_ecmwf2_msl_4) file=ECMWFData/monthly/ecmwf2_msl_4_m%%.ctl;kindname="ensemble ECMWF-2";climfield="+3 SLP";;
ens_ecmwf2_msl_5) file=ECMWFData/monthly/ecmwf2_msl_5_m%%.ctl;kindname="ensemble ECMWF-2";climfield="+4 SLP";;
ens_ecmwf2_msl_6) file=ECMWFData/monthly/ecmwf2_msl_6_m%%.ctl;kindname="ensemble ECMWF-2";climfield="+5 SLP";;
ens_ecmwf2_msl_jan) file=ECMWFData/monthly/ecmwf2_msl_jan_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Jan SLP";;
ens_ecmwf2_msl_feb) file=ECMWFData/monthly/ecmwf2_msl_feb_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Feb SLP";;
ens_ecmwf2_msl_mar) file=ECMWFData/monthly/ecmwf2_msl_mar_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Mar SLP";;
ens_ecmwf2_msl_apr) file=ECMWFData/monthly/ecmwf2_msl_apr_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Apr SLP";;
ens_ecmwf2_msl_may) file=ECMWFData/monthly/ecmwf2_msl_may_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1May SLP";;
ens_ecmwf2_msl_jun) file=ECMWFData/monthly/ecmwf2_msl_jun_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Jun SLP";;
ens_ecmwf2_msl_jul) file=ECMWFData/monthly/ecmwf2_msl_jul_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Jul SLP";;
ens_ecmwf2_msl_aug) file=ECMWFData/monthly/ecmwf2_msl_aug_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Aug SLP";;
ens_ecmwf2_msl_sep) file=ECMWFData/monthly/ecmwf2_msl_sep_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Sep SLP";;
ens_ecmwf2_msl_oct) file=ECMWFData/monthly/ecmwf2_msl_oct_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Oct SLP";;
ens_ecmwf2_msl_nov) file=ECMWFData/monthly/ecmwf2_msl_nov_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Nov SLP";;
ens_ecmwf2_msl_dec) file=ECMWFData/monthly/ecmwf2_msl_dec_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Dec SLP";;

ens_ecmwf2_z500_1) file=ECMWFData/monthly/ecmwf2_z500_1_m%%.ctl;kindname="ensemble ECMWF-2";climfield="+0 z500";;
ens_ecmwf2_z500_2) file=ECMWFData/monthly/ecmwf2_z500_2_m%%.ctl;kindname="ensemble ECMWF-2";climfield="+1 z500";;
ens_ecmwf2_z500_3) file=ECMWFData/monthly/ecmwf2_z500_3_m%%.ctl;kindname="ensemble ECMWF-2";climfield="+2 z500";;
ens_ecmwf2_z500_4) file=ECMWFData/monthly/ecmwf2_z500_4_m%%.ctl;kindname="ensemble ECMWF-2";climfield="+3 z500";;
ens_ecmwf2_z500_5) file=ECMWFData/monthly/ecmwf2_z500_5_m%%.ctl;kindname="ensemble ECMWF-2";climfield="+4 z500";;
ens_ecmwf2_z500_6) file=ECMWFData/monthly/ecmwf2_z500_6_m%%.ctl;kindname="ensemble ECMWF-2";climfield="+5 z500";;
#ens_ecmwf2_z500_jan) file=ECMWFData/monthly/ecmwf2_z500_jan_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Jan z500";;
#ens_ecmwf2_z500_feb) file=ECMWFData/monthly/ecmwf2_z500_feb_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Feb z500";;
#ens_ecmwf2_z500_mar) file=ECMWFData/monthly/ecmwf2_z500_mar_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Mar z500";;
#ens_ecmwf2_z500_apr) file=ECMWFData/monthly/ecmwf2_z500_apr_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Apr z500";;
#ens_ecmwf2_z500_may) file=ECMWFData/monthly/ecmwf2_z500_may_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1May z500";;
#ens_ecmwf2_z500_jun) file=ECMWFData/monthly/ecmwf2_z500_jun_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Jun z500";;
#ens_ecmwf2_z500_jul) file=ECMWFData/monthly/ecmwf2_z500_jul_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Jul z500";;
#ens_ecmwf2_z500_aug) file=ECMWFData/monthly/ecmwf2_z500_aug_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Aug z500";;
#ens_ecmwf2_z500_sep) file=ECMWFData/monthly/ecmwf2_z500_sep_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Sep z500";;
#ens_ecmwf2_z500_oct) file=ECMWFData/monthly/ecmwf2_z500_oct_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Oct z500";;
#ens_ecmwf2_z500_nov) file=ECMWFData/monthly/ecmwf2_z500_nov_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Nov z500";;
#ens_ecmwf2_z500_dec) file=ECMWFData/monthly/ecmwf2_z500_dec_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Dec z500";;
ens_ecmwf2_z500_jan) file=ECMWFData/monthly/ecmwf2_z500_jan_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Jan z500";;
ens_ecmwf2_z500_feb) file=ECMWFData/monthly/ecmwf2_z500_feb_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Feb z500";;
ens_ecmwf2_z500_mar) file=ECMWFData/monthly/ecmwf2_z500_mar_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Mar z500";;
ens_ecmwf2_z500_apr) file=ECMWFData/monthly/ecmwf2_z500_apr_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Apr z500";;
ens_ecmwf2_z500_may) file=ECMWFData/monthly/ecmwf2_z500_may_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1May z500";;
ens_ecmwf2_z500_jun) file=ECMWFData/monthly/ecmwf2_z500_jun_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Jun z500";;
ens_ecmwf2_z500_jul) file=ECMWFData/monthly/ecmwf2_z500_jul_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Jul z500";;
ens_ecmwf2_z500_aug) file=ECMWFData/monthly/ecmwf2_z500_aug_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Aug z500";;
ens_ecmwf2_z500_sep) file=ECMWFData/monthly/ecmwf2_z500_sep_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Sep z500";;
ens_ecmwf2_z500_oct) file=ECMWFData/monthly/ecmwf2_z500_oct_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Oct z500";;
ens_ecmwf2_z500_nov) file=ECMWFData/monthly/ecmwf2_z500_nov_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Nov z500";;
ens_ecmwf2_z500_dec) file=ECMWFData/monthly/ecmwf2_z500_dec_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Dec z500";;

ens_ecmwf2_u10_1) file=ECMWFData/monthly/ecmwf2_u10_1_m%%.ctl;kindname="ensemble ECMWF-2";climfield="+0 u10";;
ens_ecmwf2_u10_2) file=ECMWFData/monthly/ecmwf2_u10_2_m%%.ctl;kindname="ensemble ECMWF-2";climfield="+1 u10";;
ens_ecmwf2_u10_3) file=ECMWFData/monthly/ecmwf2_u10_3_m%%.ctl;kindname="ensemble ECMWF-2";climfield="+2 u10";;
ens_ecmwf2_u10_4) file=ECMWFData/monthly/ecmwf2_u10_4_m%%.ctl;kindname="ensemble ECMWF-2";climfield="+3 u10";;
ens_ecmwf2_u10_5) file=ECMWFData/monthly/ecmwf2_u10_5_m%%.ctl;kindname="ensemble ECMWF-2";climfield="+4 u10";;
ens_ecmwf2_u10_6) file=ECMWFData/monthly/ecmwf2_u10_6_m%%.ctl;kindname="ensemble ECMWF-2";climfield="+5 u10";;
ens_ecmwf2_u10_jan) file=ECMWFData/monthly/ecmwf2_u10_jan_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Jan u10";;
ens_ecmwf2_u10_feb) file=ECMWFData/monthly/ecmwf2_u10_feb_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Feb u10";;
ens_ecmwf2_u10_mar) file=ECMWFData/monthly/ecmwf2_u10_mar_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Mar u10";;
ens_ecmwf2_u10_apr) file=ECMWFData/monthly/ecmwf2_u10_apr_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Apr u10";;
ens_ecmwf2_u10_may) file=ECMWFData/monthly/ecmwf2_u10_may_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1May u10";;
ens_ecmwf2_u10_jun) file=ECMWFData/monthly/ecmwf2_u10_jun_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Jul u10";;
ens_ecmwf2_u10_jul) file=ECMWFData/monthly/ecmwf2_u10_jul_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Jul u10";;
ens_ecmwf2_u10_aug) file=ECMWFData/monthly/ecmwf2_u10_aug_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Aug u10";;
ens_ecmwf2_u10_sep) file=ECMWFData/monthly/ecmwf2_u10_sep_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Sep u10";;
ens_ecmwf2_u10_oct) file=ECMWFData/monthly/ecmwf2_u10_oct_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Oct u10";;
ens_ecmwf2_u10_nov) file=ECMWFData/monthly/ecmwf2_u10_nov_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Nov u10";;
ens_ecmwf2_u10_dec) file=ECMWFData/monthly/ecmwf2_u10_dec_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Dec u10";;

ens_ecmwf2_v10_1) file=ECMWFData/monthly/ecmwf2_v10_1_m%%.ctl;kindname="ensemble ECMWF-2";climfield="+0 v10";;
ens_ecmwf2_v10_2) file=ECMWFData/monthly/ecmwf2_v10_2_m%%.ctl;kindname="ensemble ECMWF-2";climfield="+1 v10";;
ens_ecmwf2_v10_3) file=ECMWFData/monthly/ecmwf2_v10_3_m%%.ctl;kindname="ensemble ECMWF-2";climfield="+2 v10";;
ens_ecmwf2_v10_4) file=ECMWFData/monthly/ecmwf2_v10_4_m%%.ctl;kindname="ensemble ECMWF-2";climfield="+3 v10";;
ens_ecmwf2_v10_5) file=ECMWFData/monthly/ecmwf2_v10_5_m%%.ctl;kindname="ensemble ECMWF-2";climfield="+4 v10";;
ens_ecmwf2_v10_6) file=ECMWFData/monthly/ecmwf2_v10_6_m%%.ctl;kindname="ensemble ECMWF-2";climfield="+5 v10";;
ens_ecmwf2_v10_jan) file=ECMWFData/monthly/ecmwf2_v10_jan_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Jan v10";;
ens_ecmwf2_v10_feb) file=ECMWFData/monthly/ecmwf2_v10_feb_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Feb v10";;
ens_ecmwf2_v10_mar) file=ECMWFData/monthly/ecmwf2_v10_mar_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Mar v10";;
ens_ecmwf2_v10_apr) file=ECMWFData/monthly/ecmwf2_v10_apr_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Apr v10";;
ens_ecmwf2_v10_may) file=ECMWFData/monthly/ecmwf2_v10_may_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1May v10";;
ens_ecmwf2_v10_jun) file=ECMWFData/monthly/ecmwf2_v10_jun_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Jun v10";;
ens_ecmwf2_v10_jul) file=ECMWFData/monthly/ecmwf2_v10_jul_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Jul v10";;
ens_ecmwf2_v10_aug) file=ECMWFData/monthly/ecmwf2_v10_aug_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Aug v10";;
ens_ecmwf2_v10_sep) file=ECMWFData/monthly/ecmwf2_v10_sep_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Sep v10";;
ens_ecmwf2_v10_oct) file=ECMWFData/monthly/ecmwf2_v10_oct_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Oct v10";;
ens_ecmwf2_v10_nov) file=ECMWFData/monthly/ecmwf2_v10_nov_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Nov v10";;
ens_ecmwf2_v10_dec) file=ECMWFData/monthly/ecmwf2_v10_dec_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Dec v10";;

ens_ecmwf2_ssd_1) file=ECMWFData/monthly/ecmwf2_ssd_1_m%%.ctl;kindname="ensemble ECMWF-2";climfield="+0 solar radiation";;
ens_ecmwf2_ssd_2) file=ECMWFData/monthly/ecmwf2_ssd_2_m%%.ctl;kindname="ensemble ECMWF-2";climfield="+1 solar radiation";;
ens_ecmwf2_ssd_3) file=ECMWFData/monthly/ecmwf2_ssd_3_m%%.ctl;kindname="ensemble ECMWF-2";climfield="+2 solar radiation";;
ens_ecmwf2_ssd_4) file=ECMWFData/monthly/ecmwf2_ssd_4_m%%.ctl;kindname="ensemble ECMWF-2";climfield="+3 solar radiation";;
ens_ecmwf2_ssd_5) file=ECMWFData/monthly/ecmwf2_ssd_5_m%%.ctl;kindname="ensemble ECMWF-2";climfield="+4 solar radiation";;
ens_ecmwf2_ssd_6) file=ECMWFData/monthly/ecmwf2_ssd_6_m%%.ctl;kindname="ensemble ECMWF-2";climfield="+5 solar radiation";;
ens_ecmwf2_ssd_jan) file=ECMWFData/monthly/ecmwf2_ssd_jan_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Jan solar radiation";;
ens_ecmwf2_ssd_feb) file=ECMWFData/monthly/ecmwf2_ssd_feb_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Feb solar radiation";;
ens_ecmwf2_ssd_mar) file=ECMWFData/monthly/ecmwf2_ssd_mar_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Mar solar radiation";;
ens_ecmwf2_ssd_apr) file=ECMWFData/monthly/ecmwf2_ssd_apr_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Apr solar radiation";;
ens_ecmwf2_ssd_may) file=ECMWFData/monthly/ecmwf2_ssd_may_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1May solar radiation";;
ens_ecmwf2_ssd_jun) file=ECMWFData/monthly/ecmwf2_ssd_jun_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Jun solar radiation";;
ens_ecmwf2_ssd_jul) file=ECMWFData/monthly/ecmwf2_ssd_jul_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Jul solar radiation";;
ens_ecmwf2_ssd_aug) file=ECMWFData/monthly/ecmwf2_ssd_aug_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Aug solar radiation";;
ens_ecmwf2_ssd_sep) file=ECMWFData/monthly/ecmwf2_ssd_sep_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Sep solar radiation";;
ens_ecmwf2_ssd_oct) file=ECMWFData/monthly/ecmwf2_ssd_oct_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Oct solar radiation";;
ens_ecmwf2_ssd_nov) file=ECMWFData/monthly/ecmwf2_ssd_nov_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Nov solar radiation";;
ens_ecmwf2_ssd_dec) file=ECMWFData/monthly/ecmwf2_ssd_dec_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Dec solar radiation";;

ens_ecmwf2_snd_1) file=ECMWFData/monthly/ecmwf2_snd_1_m%%.ctl;kindname="ensemble ECMWF-2";climfield="+0 snow depth";;
ens_ecmwf2_snd_2) file=ECMWFData/monthly/ecmwf2_snd_2_m%%.ctl;kindname="ensemble ECMWF-2";climfield="+1 snow depth";;
ens_ecmwf2_snd_3) file=ECMWFData/monthly/ecmwf2_snd_3_m%%.ctl;kindname="ensemble ECMWF-2";climfield="+2 snow depth";;
ens_ecmwf2_snd_4) file=ECMWFData/monthly/ecmwf2_snd_4_m%%.ctl;kindname="ensemble ECMWF-2";climfield="+3 snow depth";;
ens_ecmwf2_snd_5) file=ECMWFData/monthly/ecmwf2_snd_5_m%%.ctl;kindname="ensemble ECMWF-2";climfield="+4 snow depth";;
ens_ecmwf2_snd_6) file=ECMWFData/monthly/ecmwf2_snd_6_m%%.ctl;kindname="ensemble ECMWF-2";climfield="+5 snow depth";;
ens_ecmwf2_snd_jan) file=ECMWFData/monthly/ecmwf2_snd_jan_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Jan snow depth";;
ens_ecmwf2_snd_feb) file=ECMWFData/monthly/ecmwf2_snd_feb_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Feb snow depth";;
ens_ecmwf2_snd_mar) file=ECMWFData/monthly/ecmwf2_snd_mar_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Mar snow depth";;
ens_ecmwf2_snd_apr) file=ECMWFData/monthly/ecmwf2_snd_apr_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Apr snow depth";;
ens_ecmwf2_snd_may) file=ECMWFData/monthly/ecmwf2_snd_may_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1May snow depth";;
ens_ecmwf2_snd_jun) file=ECMWFData/monthly/ecmwf2_snd_jun_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Jun snow depth";;
ens_ecmwf2_snd_jul) file=ECMWFData/monthly/ecmwf2_snd_jul_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Jul snow depth";;
ens_ecmwf2_snd_aug) file=ECMWFData/monthly/ecmwf2_snd_aug_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Aug snow depth";;
ens_ecmwf2_snd_sep) file=ECMWFData/monthly/ecmwf2_snd_sep_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Sep snow depth";;
ens_ecmwf2_snd_oct) file=ECMWFData/monthly/ecmwf2_snd_oct_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Oct snow depth";;
ens_ecmwf2_snd_nov) file=ECMWFData/monthly/ecmwf2_snd_nov_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Nov snow depth";;
ens_ecmwf2_snd_dec) file=ECMWFData/monthly/ecmwf2_snd_dec_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Dec snow depth";;

ens_ecmwf2_wsp_1) file=StormData/ecmwf2_wsp_1_%%.ctl;kindname="ensemble ECMWF-2";climfield="+0 max wind speed";;
ens_ecmwf2_wsp_2) file=StormData/ecmwf2_wsp_2_%%.ctl;kindname="ensemble ECMWF-2";climfield="+1 max wind speed";;
ens_ecmwf2_wsp_3) file=StormData/ecmwf2_wsp_3_%%.ctl;kindname="ensemble ECMWF-2";climfield="+2 max wind speed";;
ens_ecmwf2_wsp_4) file=StormData/ecmwf2_wsp_4_%%.ctl;kindname="ensemble ECMWF-2";climfield="+3 max wind speed";;
ens_ecmwf2_wsp_5) file=StormData/ecmwf2_wsp_5_%%.ctl;kindname="ensemble ECMWF-2";climfield="+4 max wind speed";;
ens_ecmwf2_wsp_6) file=StormData/ecmwf2_wsp_6_%%.ctl;kindname="ensemble ECMWF-2";climfield="+5 max wind speed";;

ens_ecmwf2_prc_1) file=StormData/ecmwf2_prc_1_%%.new.ctl;kindname="ensemble ECMWF-2";climfield="+0 max daily precip";;
ens_ecmwf2_prc_2) file=StormData/ecmwf2_prc_2_%%.new.ctl;kindname="ensemble ECMWF-2";climfield="+1 max daily precip";;
ens_ecmwf2_prc_3) file=StormData/ecmwf2_prc_3_%%.new.ctl;kindname="ensemble ECMWF-2";climfield="+2 max daily precip";;
ens_ecmwf2_prc_4) file=StormData/ecmwf2_prc_4_%%.new.ctl;kindname="ensemble ECMWF-2";climfield="+3 max daily precip";;
ens_ecmwf2_prc_5) file=StormData/ecmwf2_prc_5_%%.new.ctl;kindname="ensemble ECMWF-2";climfield="+4 max daily precip";;
ens_ecmwf2_prc_6) file=StormData/ecmwf2_prc_6_%%.new.ctl;kindname="ensemble ECMWF-2";climfield="+5 max daily precip";;

ens_ecmwf2_tsfc_1) file=ECMWFData/monthly/ecmwf2_sst_1_m%%.ctl;kindname="ensemble ECMWF-2";climfield="+0 Tsfc";;
ens_ecmwf2_tsfc_2) file=ECMWFData/monthly/ecmwf2_sst_2_m%%.ctl;kindname="ensemble ECMWF-2";climfield="+1 Tsfc";;
ens_ecmwf2_tsfc_3) file=ECMWFData/monthly/ecmwf2_sst_3_m%%.ctl;kindname="ensemble ECMWF-2";climfield="+2 Tsfc";;
ens_ecmwf2_tsfc_4) file=ECMWFData/monthly/ecmwf2_sst_4_m%%.ctl;kindname="ensemble ECMWF-2";climfield="+3 Tsfc";;
ens_ecmwf2_tsfc_5) file=ECMWFData/monthly/ecmwf2_sst_5_m%%.ctl;kindname="ensemble ECMWF-2";climfield="+4 Tsfc";;
ens_ecmwf2_tsfc_6) file=ECMWFData/monthly/ecmwf2_sst_6_m%%.ctl;kindname="ensemble ECMWF-2";climfield="+5 Tsfc";;
ens_ecmwf2_tsfc_jan) file=ECMWFData/monthly/ecmwf2_sst_jan_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Jan Tsf";;
ens_ecmwf2_tsfc_feb) file=ECMWFData/monthly/ecmwf2_sst_feb_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Feb Tsf";;
ens_ecmwf2_tsfc_mar) file=ECMWFData/monthly/ecmwf2_sst_mar_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Mar Tsf";;
ens_ecmwf2_tsfc_apr) file=ECMWFData/monthly/ecmwf2_sst_apr_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Apr Tsf";;
ens_ecmwf2_tsfc_may) file=ECMWFData/monthly/ecmwf2_sst_may_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1May Tsf";;
ens_ecmwf2_tsfc_jun) file=ECMWFData/monthly/ecmwf2_sst_jun_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Jun Tsf";;
ens_ecmwf2_tsfc_jul) file=ECMWFData/monthly/ecmwf2_sst_jul_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Jul Tsf";;
ens_ecmwf2_tsfc_aug) file=ECMWFData/monthly/ecmwf2_sst_aug_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Aug Tsf";;
ens_ecmwf2_tsfc_sep) file=ECMWFData/monthly/ecmwf2_sst_sep_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Sep Tsf";;
ens_ecmwf2_tsfc_oct) file=ECMWFData/monthly/ecmwf2_sst_oct_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Oct Tsf";;
ens_ecmwf2_tsfc_nov) file=ECMWFData/monthly/ecmwf2_sst_nov_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Nov Tsf";;
ens_ecmwf2_tsfc_dec) file=ECMWFData/monthly/ecmwf2_sst_dec_m%%.ctl;kindname="ensemble ECMWF-2";climfield="1Dec Tsf";;

ens_ecmwf2_ssh_1) file=ECMWFData/monthly/ecmwf2_ssh_1_o_%%.ctl;kindname="ensemble ECMWF-2";climfield="+0 SSH";;
ens_ecmwf2_ssh_2) file=ECMWFData/monthly/ecmwf2_ssh_2_o_%%.ctl;kindname="ensemble ECMWF-2";climfield="+1 SSH";;
ens_ecmwf2_ssh_3) file=ECMWFData/monthly/ecmwf2_ssh_3_o_%%.ctl;kindname="ensemble ECMWF-2";climfield="+2 SSH";;
ens_ecmwf2_ssh_4) file=ECMWFData/monthly/ecmwf2_ssh_4_o_%%.ctl;kindname="ensemble ECMWF-2";climfield="+3 SSH";;
ens_ecmwf2_ssh_5) file=ECMWFData/monthly/ecmwf2_ssh_5_o_%%.ctl;kindname="ensemble ECMWF-2";climfield="+4 SSH";;
ens_ecmwf2_ssh_6) file=ECMWFData/monthly/ecmwf2_ssh_6_o_%%.ctl;kindname="ensemble ECMWF-2";climfield="+5 SSH";;

ecmwf3_t2m_1) file=ECMWFData/S3/monthly/ecmwf3_t2m_1.ctl;kindname="ECMWF-3";climfield="+0 T2m";;
ecmwf3_t2m_2) file=ECMWFData/S3/monthly/ecmwf3_t2m_2.ctl;kindname="ECMWF-3";climfield="+1 T2m";;
ecmwf3_t2m_3) file=ECMWFData/S3/monthly/ecmwf3_t2m_3.ctl;kindname="ECMWF-3";climfield="+2 T2m";;
ecmwf3_t2m_4) file=ECMWFData/S3/monthly/ecmwf3_t2m_4.ctl;kindname="ECMWF-3";climfield="+3 T2m";;
ecmwf3_t2m_5) file=ECMWFData/S3/monthly/ecmwf3_t2m_5.ctl;kindname="ECMWF-3";climfield="+4 T2m";;
ecmwf3_t2m_6) file=ECMWFData/S3/monthly/ecmwf3_t2m_6.ctl;kindname="ECMWF-3";climfield="+5 T2m";;
ecmwf3_t2m_jan) file=ECMWFData/S3/monthly/ecmwf3_t2m_jan_ensm.ctl;kindname="ECMWF-3";climfield="1Jan T2m";;
ecmwf3_t2m_feb) file=ECMWFData/S3/monthly/ecmwf3_t2m_feb_ensm.ctl;kindname="ECMWF-3";climfield="1Feb T2m";;
ecmwf3_t2m_mar) file=ECMWFData/S3/monthly/ecmwf3_t2m_mar_ensm.ctl;kindname="ECMWF-3";climfield="1Mar T2m";;
ecmwf3_t2m_apr) file=ECMWFData/S3/monthly/ecmwf3_t2m_apr_ensm.ctl;kindname="ECMWF-3";climfield="1Apr T2m";;
ecmwf3_t2m_may) file=ECMWFData/S3/monthly/ecmwf3_t2m_may_ensm.ctl;kindname="ECMWF-3";climfield="1May T2m";;
ecmwf3_t2m_jun) file=ECMWFData/S3/monthly/ecmwf3_t2m_jun_ensm.ctl;kindname="ECMWF-3";climfield="1Jun T2m";;
ecmwf3_t2m_jul) file=ECMWFData/S3/monthly/ecmwf3_t2m_jul_ensm.ctl;kindname="ECMWF-3";climfield="1Jul T2m";;
ecmwf3_t2m_aug) file=ECMWFData/S3/monthly/ecmwf3_t2m_aug_ensm.ctl;kindname="ECMWF-3";climfield="1Aug T2m";;
ecmwf3_t2m_sep) file=ECMWFData/S3/monthly/ecmwf3_t2m_sep_ensm.ctl;kindname="ECMWF-3";climfield="1Sep T2m";;
ecmwf3_t2m_oct) file=ECMWFData/S3/monthly/ecmwf3_t2m_oct_ensm.ctl;kindname="ECMWF-3";climfield="1Oct T2m";;
ecmwf3_t2m_nov) file=ECMWFData/S3/monthly/ecmwf3_t2m_nov_ensm.ctl;kindname="ECMWF-3";climfield="1Nov T2m";;
ecmwf3_t2m_dec) file=ECMWFData/S3/monthly/ecmwf3_t2m_dec_ensm.ctl;kindname="ECMWF-3";climfield="1Dec T2m";;

ecmwf3_t2x_1) file=ECMWFData/S3/monthly/ecmwf3_t2x_1.ctl;kindname="ECMWF-3";climfield="+0 T2max";;
ecmwf3_t2x_2) file=ECMWFData/S3/monthly/ecmwf3_t2x_2.ctl;kindname="ECMWF-3";climfield="+1 T2max";;
ecmwf3_t2x_3) file=ECMWFData/S3/monthly/ecmwf3_t2x_3.ctl;kindname="ECMWF-3";climfield="+2 T2max";;
ecmwf3_t2x_4) file=ECMWFData/S3/monthly/ecmwf3_t2x_4.ctl;kindname="ECMWF-3";climfield="+3 T2max";;
ecmwf3_t2x_5) file=ECMWFData/S3/monthly/ecmwf3_t2x_5.ctl;kindname="ECMWF-3";climfield="+4 T2max";;
ecmwf3_t2x_6) file=ECMWFData/S3/monthly/ecmwf3_t2x_6.ctl;kindname="ECMWF-3";climfield="+5 T2max";;
ecmwf3_t2x_jan) file=ECMWFData/S3/monthly/ecmwf3_t2x_jan_ensm.ctl;kindname="ECMWF-3";climfield="1Jan T2max";;
ecmwf3_t2x_feb) file=ECMWFData/S3/monthly/ecmwf3_t2x_feb_ensm.ctl;kindname="ECMWF-3";climfield="1Feb T2max";;
ecmwf3_t2x_mar) file=ECMWFData/S3/monthly/ecmwf3_t2x_mar_ensm.ctl;kindname="ECMWF-3";climfield="1Mar T2max";;
ecmwf3_t2x_apr) file=ECMWFData/S3/monthly/ecmwf3_t2x_apr_ensm.ctl;kindname="ECMWF-3";climfield="1Apr T2max";;
ecmwf3_t2x_may) file=ECMWFData/S3/monthly/ecmwf3_t2x_may_ensm.ctl;kindname="ECMWF-3";climfield="1May T2max";;
ecmwf3_t2x_jun) file=ECMWFData/S3/monthly/ecmwf3_t2x_jun_ensm.ctl;kindname="ECMWF-3";climfield="1Jun T2max";;
ecmwf3_t2x_jul) file=ECMWFData/S3/monthly/ecmwf3_t2x_jul_ensm.ctl;kindname="ECMWF-3";climfield="1Jul T2max";;
ecmwf3_t2x_aug) file=ECMWFData/S3/monthly/ecmwf3_t2x_aug_ensm.ctl;kindname="ECMWF-3";climfield="1Aug T2max";;
ecmwf3_t2x_sep) file=ECMWFData/S3/monthly/ecmwf3_t2x_sep_ensm.ctl;kindname="ECMWF-3";climfield="1Sep T2max";;
ecmwf3_t2x_oct) file=ECMWFData/S3/monthly/ecmwf3_t2x_oct_ensm.ctl;kindname="ECMWF-3";climfield="1Oct T2max";;
ecmwf3_t2x_nov) file=ECMWFData/S3/monthly/ecmwf3_t2x_nov_ensm.ctl;kindname="ECMWF-3";climfield="1Nov T2max";;
ecmwf3_t2x_dec) file=ECMWFData/S3/monthly/ecmwf3_t2x_dec_ensm.ctl;kindname="ECMWF-3";climfield="1Dec T2max";;

ecmwf3_t2n_1) file=ECMWFData/S3/monthly/ecmwf3_t2n_1.ctl;kindname="ECMWF-3";climfield="+0 T2min";;
ecmwf3_t2n_2) file=ECMWFData/S3/monthly/ecmwf3_t2n_2.ctl;kindname="ECMWF-3";climfield="+1 T2min";;
ecmwf3_t2n_3) file=ECMWFData/S3/monthly/ecmwf3_t2n_3.ctl;kindname="ECMWF-3";climfield="+2 T2min";;
ecmwf3_t2n_4) file=ECMWFData/S3/monthly/ecmwf3_t2n_4.ctl;kindname="ECMWF-3";climfield="+3 T2min";;
ecmwf3_t2n_5) file=ECMWFData/S3/monthly/ecmwf3_t2n_5.ctl;kindname="ECMWF-3";climfield="+4 T2min";;
ecmwf3_t2n_6) file=ECMWFData/S3/monthly/ecmwf3_t2n_6.ctl;kindname="ECMWF-3";climfield="+5 T2min";;
ecmwf3_t2n_jan) file=ECMWFData/S3/monthly/ecmwf3_t2n_jan_ensm.ctl;kindname="ECMWF-3";climfield="1Jan T2min";;
ecmwf3_t2n_feb) file=ECMWFData/S3/monthly/ecmwf3_t2n_feb_ensm.ctl;kindname="ECMWF-3";climfield="1Feb T2min";;
ecmwf3_t2n_mar) file=ECMWFData/S3/monthly/ecmwf3_t2n_mar_ensm.ctl;kindname="ECMWF-3";climfield="1Mar T2min";;
ecmwf3_t2n_apr) file=ECMWFData/S3/monthly/ecmwf3_t2n_apr_ensm.ctl;kindname="ECMWF-3";climfield="1Apr T2min";;
ecmwf3_t2n_may) file=ECMWFData/S3/monthly/ecmwf3_t2n_may_ensm.ctl;kindname="ECMWF-3";climfield="1May T2min";;
ecmwf3_t2n_jun) file=ECMWFData/S3/monthly/ecmwf3_t2n_jun_ensm.ctl;kindname="ECMWF-3";climfield="1Jun T2min";;
ecmwf3_t2n_jul) file=ECMWFData/S3/monthly/ecmwf3_t2n_jul_ensm.ctl;kindname="ECMWF-3";climfield="1Jul T2min";;
ecmwf3_t2n_aug) file=ECMWFData/S3/monthly/ecmwf3_t2n_aug_ensm.ctl;kindname="ECMWF-3";climfield="1Aug T2min";;
ecmwf3_t2n_sep) file=ECMWFData/S3/monthly/ecmwf3_t2n_sep_ensm.ctl;kindname="ECMWF-3";climfield="1Sep T2min";;
ecmwf3_t2n_oct) file=ECMWFData/S3/monthly/ecmwf3_t2n_oct_ensm.ctl;kindname="ECMWF-3";climfield="1Oct T2min";;
ecmwf3_t2n_nov) file=ECMWFData/S3/monthly/ecmwf3_t2n_nov_ensm.ctl;kindname="ECMWF-3";climfield="1Nov T2min";;
ecmwf3_t2n_dec) file=ECMWFData/S3/monthly/ecmwf3_t2n_dec_ensm.ctl;kindname="ECMWF-3";climfield="1Dec T2min";;

ecmwf3_prcp) file=ECMWFData/S3/monthly/ecmwf3_tp.ctl;kindname="ECMWF-3";climfield="precipitation";;
ecmwf3_prcp_1) file=ECMWFData/S3/monthly/ecmwf3_prcp_1_ensm.ctl;kindname="ECMWF-3";climfield="+0 precipitation";;
ecmwf3_prcp_2) file=ECMWFData/S3/monthly/ecmwf3_prcp_2_ensm.ctl;kindname="ECMWF-3";climfield="+1 precipitation";;
ecmwf3_prcp_3) file=ECMWFData/S3/monthly/ecmwf3_prcp_3_ensm.ctl;kindname="ECMWF-3";climfield="+2 precipitation";;
ecmwf3_prcp_4) file=ECMWFData/S3/monthly/ecmwf3_prcp_4_ensm.ctl;kindname="ECMWF-3";climfield="+3 precipitation";;
ecmwf3_prcp_5) file=ECMWFData/S3/monthly/ecmwf3_prcp_5_ensm.ctl;kindname="ECMWF-3";climfield="+4 precipitation";;
ecmwf3_prcp_6) file=ECMWFData/S3/monthly/ecmwf3_prcp_6_ensm.ctl;kindname="ECMWF-3";climfield="+5 precipitation";;
ecmwf3_prcp_jan) file=ECMWFData/S3/monthly/ecmwf3_prcp_jan_ensm.ctl;kindname="ECMWF-3";climfield="1Jan precipitation";;
ecmwf3_prcp_feb) file=ECMWFData/S3/monthly/ecmwf3_prcp_feb_ensm.ctl;kindname="ECMWF-3";climfield="1Feb precipitation";;
ecmwf3_prcp_mar) file=ECMWFData/S3/monthly/ecmwf3_prcp_mar_ensm.ctl;kindname="ECMWF-3";climfield="1Mar precipitation";;
ecmwf3_prcp_apr) file=ECMWFData/S3/monthly/ecmwf3_prcp_apr_ensm.ctl;kindname="ECMWF-3";climfield="1Apr precipitation";;
ecmwf3_prcp_may) file=ECMWFData/S3/monthly/ecmwf3_prcp_may_ensm.ctl;kindname="ECMWF-3";climfield="1May precipitation";;
ecmwf3_prcp_jun) file=ECMWFData/S3/monthly/ecmwf3_prcp_jun_ensm.ctl;kindname="ECMWF-3";climfield="1Jun precipitation";;
ecmwf3_prcp_jul) file=ECMWFData/S3/monthly/ecmwf3_prcp_jul_ensm.ctl;kindname="ECMWF-3";climfield="1Jul precipitation";;
ecmwf3_prcp_aug) file=ECMWFData/S3/monthly/ecmwf3_prcp_aug_ensm.ctl;kindname="ECMWF-3";climfield="1Aug precipitation";;
ecmwf3_prcp_sep) file=ECMWFData/S3/monthly/ecmwf3_prcp_sep_ensm.ctl;kindname="ECMWF-3";climfield="1Sep precipitation";;
ecmwf3_prcp_oct) file=ECMWFData/S3/monthly/ecmwf3_prcp_oct_ensm.ctl;kindname="ECMWF-3";climfield="1Oct precipitation";;
ecmwf3_prcp_nov) file=ECMWFData/S3/monthly/ecmwf3_prcp_nov_ensm.ctl;kindname="ECMWF-3";climfield="1Nov precipitation";;
ecmwf3_prcp_dec) file=ECMWFData/S3/monthly/ecmwf3_prcp_dec_ensm.ctl;kindname="ECMWF-3";climfield="1Dec precipitation";;

ecmwf3_msl) file=ECMWFData/S3/monthly/ecmwf3_msl.ctl;kindname="ECMWF-3";climfield="SLP";;
ecmwf3_msl_1) file=ECMWFData/S3/monthly/ecmwf3_msl_1.ctl;kindname="ECMWF-3";climfield="+0 SLP";;
ecmwf3_msl_2) file=ECMWFData/S3/monthly/ecmwf3_msl_2.ctl;kindname="ECMWF-3";climfield="+1 SLP";;
ecmwf3_msl_3) file=ECMWFData/S3/monthly/ecmwf3_msl_3.ctl;kindname="ECMWF-3";climfield="+2 SLP";;
ecmwf3_msl_4) file=ECMWFData/S3/monthly/ecmwf3_msl_4.ctl;kindname="ECMWF-3";climfield="+3 SLP";;
ecmwf3_msl_5) file=ECMWFData/S3/monthly/ecmwf3_msl_5.ctl;kindname="ECMWF-3";climfield="+4 SLP";;
ecmwf3_msl_6) file=ECMWFData/S3/monthly/ecmwf3_msl_6.ctl;kindname="ECMWF-3";climfield="+5 SLP";;
ecmwf3_msl_jan) file=ECMWFData/S3/monthly/ecmwf3_msl_jan_ensm.ctl;kindname="ECMWF-3";climfield="1Jan SLP";;
ecmwf3_msl_feb) file=ECMWFData/S3/monthly/ecmwf3_msl_feb_ensm.ctl;kindname="ECMWF-3";climfield="1Feb SLP";;
ecmwf3_msl_mar) file=ECMWFData/S3/monthly/ecmwf3_msl_mar_ensm.ctl;kindname="ECMWF-3";climfield="1Mar SLP";;
ecmwf3_msl_apr) file=ECMWFData/S3/monthly/ecmwf3_msl_apr_ensm.ctl;kindname="ECMWF-3";climfield="1Apr SLP";;
ecmwf3_msl_may) file=ECMWFData/S3/monthly/ecmwf3_msl_may_ensm.ctl;kindname="ECMWF-3";climfield="1May SLP";;
ecmwf3_msl_jun) file=ECMWFData/S3/monthly/ecmwf3_msl_jun_ensm.ctl;kindname="ECMWF-3";climfield="1Jun SLP";;
ecmwf3_msl_jul) file=ECMWFData/S3/monthly/ecmwf3_msl_jul_ensm.ctl;kindname="ECMWF-3";climfield="1Jul SLP";;
ecmwf3_msl_aug) file=ECMWFData/S3/monthly/ecmwf3_msl_aug_ensm.ctl;kindname="ECMWF-3";climfield="1Aug SLP";;
ecmwf3_msl_sep) file=ECMWFData/S3/monthly/ecmwf3_msl_sep_ensm.ctl;kindname="ECMWF-3";climfield="1Sep SLP";;
ecmwf3_msl_oct) file=ECMWFData/S3/monthly/ecmwf3_msl_oct_ensm.ctl;kindname="ECMWF-3";climfield="1Oct SLP";;
ecmwf3_msl_nov) file=ECMWFData/S3/monthly/ecmwf3_msl_nov_ensm.ctl;kindname="ECMWF-3";climfield="1Nov SLP";;
ecmwf3_msl_dec) file=ECMWFData/S3/monthly/ecmwf3_msl_dec_ensm.ctl;kindname="ECMWF-3";climfield="1Dec SLP";;

ecmwf3_z500) file=ECMWFData/S3/monthly/ecmwf3_z500.ctl;kindname="ECMWF-3";climfield="z500";;
ecmwf3_z500_1) file=ECMWFData/S3/monthly/ecmwf3_z500_1.ctl;kindname="ECMWF-3";climfield="+0 z500";;
ecmwf3_z500_2) file=ECMWFData/S3/monthly/ecmwf3_z500_2.ctl;kindname="ECMWF-3";climfield="+1 z500";;
ecmwf3_z500_3) file=ECMWFData/S3/monthly/ecmwf3_z500_3.ctl;kindname="ECMWF-3";climfield="+2 z500";;
ecmwf3_z500_4) file=ECMWFData/S3/monthly/ecmwf3_z500_4.ctl;kindname="ECMWF-3";climfield="+3 z500";;
ecmwf3_z500_5) file=ECMWFData/S3/monthly/ecmwf3_z500_5.ctl;kindname="ECMWF-3";climfield="+4 z500";;
ecmwf3_z500_6) file=ECMWFData/S3/monthly/ecmwf3_z500_6.ctl;kindname="ECMWF-3";climfield="+5 z500";;
ecmwf3_z500_jan) file=ECMWFData/S3/monthly/ecmwf3_z500_jan_ensm.ctl;kindname="ECMWF-3";climfield="1Jan z500";;
ecmwf3_z500_feb) file=ECMWFData/S3/monthly/ecmwf3_z500_feb_ensm.ctl;kindname="ECMWF-3";climfield="1Feb z500";;
ecmwf3_z500_mar) file=ECMWFData/S3/monthly/ecmwf3_z500_mar_ensm.ctl;kindname="ECMWF-3";climfield="1Mar z500";;
ecmwf3_z500_apr) file=ECMWFData/S3/monthly/ecmwf3_z500_apr_ensm.ctl;kindname="ECMWF-3";climfield="1Apr z500";;
ecmwf3_z500_may) file=ECMWFData/S3/monthly/ecmwf3_z500_may_ensm.ctl;kindname="ECMWF-3";climfield="1May z500";;
ecmwf3_z500_jun) file=ECMWFData/S3/monthly/ecmwf3_z500_jun_ensm.ctl;kindname="ECMWF-3";climfield="1Jun z500";;
ecmwf3_z500_jul) file=ECMWFData/S3/monthly/ecmwf3_z500_jul_ensm.ctl;kindname="ECMWF-3";climfield="1Jul z500";;
ecmwf3_z500_aug) file=ECMWFData/S3/monthly/ecmwf3_z500_aug_ensm.ctl;kindname="ECMWF-3";climfield="1Aug z500";;
ecmwf3_z500_sep) file=ECMWFData/S3/monthly/ecmwf3_z500_sep_ensm.ctl;kindname="ECMWF-3";climfield="1Sep z500";;
ecmwf3_z500_oct) file=ECMWFData/S3/monthly/ecmwf3_z500_oct_ensm.ctl;kindname="ECMWF-3";climfield="1Oct z500";;
ecmwf3_z500_nov) file=ECMWFData/S3/monthly/ecmwf3_z500_nov_ensm.ctl;kindname="ECMWF-3";climfield="1Nov z500";;
ecmwf3_z500_dec) file=ECMWFData/S3/monthly/ecmwf3_z500_dec_ensm.ctl;kindname="ECMWF-3";climfield="1Dec z500";;

ecmwf3_u10) file=ECMWFData/S3/monthly/ecmwf3_u10.ctl;kindname="ECMWF-3";climfield="u10";;
ecmwf3_u10_1) file=ECMWFData/S3/monthly/ecmwf3_u10_1.ctl;kindname="ECMWF-3";climfield="+0 u10";;
ecmwf3_u10_2) file=ECMWFData/S3/monthly/ecmwf3_u10_2.ctl;kindname="ECMWF-3";climfield="+1 u10";;
ecmwf3_u10_3) file=ECMWFData/S3/monthly/ecmwf3_u10_3.ctl;kindname="ECMWF-3";climfield="+2 u10";;
ecmwf3_u10_4) file=ECMWFData/S3/monthly/ecmwf3_u10_4.ctl;kindname="ECMWF-3";climfield="+3 u10";;
ecmwf3_u10_5) file=ECMWFData/S3/monthly/ecmwf3_u10_5.ctl;kindname="ECMWF-3";climfield="+4 u10";;
ecmwf3_u10_6) file=ECMWFData/S3/monthly/ecmwf3_u10_6.ctl;kindname="ECMWF-3";climfield="+5 u10";;
ecmwf3_u10_jan) file=ECMWFData/S3/monthly/ecmwf3_u10_jan_ensm.ctl;kindname="ECMWF-3";climfield="1Jan u10";;
ecmwf3_u10_feb) file=ECMWFData/S3/monthly/ecmwf3_u10_feb_ensm.ctl;kindname="ECMWF-3";climfield="1Feb u10";;
ecmwf3_u10_mar) file=ECMWFData/S3/monthly/ecmwf3_u10_mar_ensm.ctl;kindname="ECMWF-3";climfield="1Mar u10";;
ecmwf3_u10_apr) file=ECMWFData/S3/monthly/ecmwf3_u10_apr_ensm.ctl;kindname="ECMWF-3";climfield="1Apr u10";;
ecmwf3_u10_may) file=ECMWFData/S3/monthly/ecmwf3_u10_may_ensm.ctl;kindname="ECMWF-3";climfield="1May u10";;
ecmwf3_u10_jun) file=ECMWFData/S3/monthly/ecmwf3_u10_jun_ensm.ctl;kindname="ECMWF-3";climfield="1Jun u10";;
ecmwf3_u10_jul) file=ECMWFData/S3/monthly/ecmwf3_u10_jul_ensm.ctl;kindname="ECMWF-3";climfield="1Jul u10";;
ecmwf3_u10_aug) file=ECMWFData/S3/monthly/ecmwf3_u10_aug_ensm.ctl;kindname="ECMWF-3";climfield="1Aug u10";;
ecmwf3_u10_sep) file=ECMWFData/S3/monthly/ecmwf3_u10_sep_ensm.ctl;kindname="ECMWF-3";climfield="1Sep u10";;
ecmwf3_u10_oct) file=ECMWFData/S3/monthly/ecmwf3_u10_oct_ensm.ctl;kindname="ECMWF-3";climfield="1Oct u10";;
ecmwf3_u10_nov) file=ECMWFData/S3/monthly/ecmwf3_u10_nov_ensm.ctl;kindname="ECMWF-3";climfield="1Nov u10";;
ecmwf3_u10_dec) file=ECMWFData/S3/monthly/ecmwf3_u10_dec_ensm.ctl;kindname="ECMWF-3";climfield="1Dec u10";;

ecmwf3_v10) file=ECMWFData/S3/monthly/ecmwf3_v10.ctl;kindname="ECMWF-3";climfield="v10";;
ecmwf3_v10_1) file=ECMWFData/S3/monthly/ecmwf3_v10_1.ctl;kindname="ECMWF-3";climfield="+0 v10";;
ecmwf3_v10_2) file=ECMWFData/S3/monthly/ecmwf3_v10_2.ctl;kindname="ECMWF-3";climfield="+1 v10";;
ecmwf3_v10_3) file=ECMWFData/S3/monthly/ecmwf3_v10_3.ctl;kindname="ECMWF-3";climfield="+2 v10";;
ecmwf3_v10_4) file=ECMWFData/S3/monthly/ecmwf3_v10_4.ctl;kindname="ECMWF-3";climfield="+3 v10";;
ecmwf3_v10_5) file=ECMWFData/S3/monthly/ecmwf3_v10_5.ctl;kindname="ECMWF-3";climfield="+4 v10";;
ecmwf3_v10_6) file=ECMWFData/S3/monthly/ecmwf3_v10_6.ctl;kindname="ECMWF-3";climfield="+5 v10";;
ecmwf3_v10_jan) file=ECMWFData/S3/monthly/ecmwf3_v10_jan_ensm.ctl;kindname="ECMWF-3";climfield="1Jan v10";;
ecmwf3_v10_feb) file=ECMWFData/S3/monthly/ecmwf3_v10_feb_ensm.ctl;kindname="ECMWF-3";climfield="1Feb v10";;
ecmwf3_v10_mar) file=ECMWFData/S3/monthly/ecmwf3_v10_mar_ensm.ctl;kindname="ECMWF-3";climfield="1Mar v10";;
ecmwf3_v10_apr) file=ECMWFData/S3/monthly/ecmwf3_v10_apr_ensm.ctl;kindname="ECMWF-3";climfield="1Apr v10";;
ecmwf3_v10_may) file=ECMWFData/S3/monthly/ecmwf3_v10_may_ensm.ctl;kindname="ECMWF-3";climfield="1May v10";;
ecmwf3_v10_jun) file=ECMWFData/S3/monthly/ecmwf3_v10_jun_ensm.ctl;kindname="ECMWF-3";climfield="1Jun v10";;
ecmwf3_v10_jul) file=ECMWFData/S3/monthly/ecmwf3_v10_jul_ensm.ctl;kindname="ECMWF-3";climfield="1Jul v10";;
ecmwf3_v10_aug) file=ECMWFData/S3/monthly/ecmwf3_v10_aug_ensm.ctl;kindname="ECMWF-3";climfield="1Aug v10";;
ecmwf3_v10_sep) file=ECMWFData/S3/monthly/ecmwf3_v10_sep_ensm.ctl;kindname="ECMWF-3";climfield="1Sep v10";;
ecmwf3_v10_oct) file=ECMWFData/S3/monthly/ecmwf3_v10_oct_ensm.ctl;kindname="ECMWF-3";climfield="1Oct v10";;
ecmwf3_v10_nov) file=ECMWFData/S3/monthly/ecmwf3_v10_nov_ensm.ctl;kindname="ECMWF-3";climfield="1Nov v10";;
ecmwf3_v10_dec) file=ECMWFData/S3/monthly/ecmwf3_v10_dec_ensm.ctl;kindname="ECMWF-3";climfield="1Dec v10";;

ecmwf3_ssd) file=ECMWFData/S3/monthly/ecmwf3_ssd.ctl;kindname="ECMWF-3";climfield="solar radiation";;
ecmwf3_ssd_1) file=ECMWFData/S3/monthly/ecmwf3_ssd_1.ctl;kindname="ECMWF-3";climfield="+0 solar radiation";;
ecmwf3_ssd_2) file=ECMWFData/S3/monthly/ecmwf3_ssd_2.ctl;kindname="ECMWF-3";climfield="+1 solar radiation";;
ecmwf3_ssd_3) file=ECMWFData/S3/monthly/ecmwf3_ssd_3.ctl;kindname="ECMWF-3";climfield="+2 solar radiation";;
ecmwf3_ssd_4) file=ECMWFData/S3/monthly/ecmwf3_ssd_4.ctl;kindname="ECMWF-3";climfield="+3 solar radiation";;
ecmwf3_ssd_5) file=ECMWFData/S3/monthly/ecmwf3_ssd_5.ctl;kindname="ECMWF-3";climfield="+4 solar radiation";;
ecmwf3_ssd_6) file=ECMWFData/S3/monthly/ecmwf3_ssd_6.ctl;kindname="ECMWF-3";climfield="+5 solar radiation";;
ecmwf3_ssd_jan) file=ECMWFData/S3/monthly/ecmwf3_ssd_jan_ensm.ctl;kindname="ECMWF-3";climfield="1Jan solar radiation";;
ecmwf3_ssd_feb) file=ECMWFData/S3/monthly/ecmwf3_ssd_feb_ensm.ctl;kindname="ECMWF-3";climfield="1Feb solar radiation";;
ecmwf3_ssd_mar) file=ECMWFData/S3/monthly/ecmwf3_ssd_mar_ensm.ctl;kindname="ECMWF-3";climfield="1Mar solar radiation";;
ecmwf3_ssd_apr) file=ECMWFData/S3/monthly/ecmwf3_ssd_apr_ensm.ctl;kindname="ECMWF-3";climfield="1Apr solar radiation";;
ecmwf3_ssd_may) file=ECMWFData/S3/monthly/ecmwf3_ssd_may_ensm.ctl;kindname="ECMWF-3";climfield="1May solar radiation";;
ecmwf3_ssd_jun) file=ECMWFData/S3/monthly/ecmwf3_ssd_jun_ensm.ctl;kindname="ECMWF-3";climfield="1Jun solar radiation";;
ecmwf3_ssd_jul) file=ECMWFData/S3/monthly/ecmwf3_ssd_jul_ensm.ctl;kindname="ECMWF-3";climfield="1Jul solar radiation";;
ecmwf3_ssd_aug) file=ECMWFData/S3/monthly/ecmwf3_ssd_aug_ensm.ctl;kindname="ECMWF-3";climfield="1Aug solar radiation";;
ecmwf3_ssd_sep) file=ECMWFData/S3/monthly/ecmwf3_ssd_sep_ensm.ctl;kindname="ECMWF-3";climfield="1Sep solar radiation";;
ecmwf3_ssd_oct) file=ECMWFData/S3/monthly/ecmwf3_ssd_oct_ensm.ctl;kindname="ECMWF-3";climfield="1Oct solar radiation";;
ecmwf3_ssd_nov) file=ECMWFData/S3/monthly/ecmwf3_ssd_nov_ensm.ctl;kindname="ECMWF-3";climfield="1Nov solar radiation";;
ecmwf3_ssd_dec) file=ECMWFData/S3/monthly/ecmwf3_ssd_dec_ensm.ctl;kindname="ECMWF-3";climfield="1Dec solar radiation";;

ecmwf3_snd_1) file=ECMWFData/S3/monthly/ecmwf3_snd_1.ctl;kindname="ECMWF-3";climfield="+0 snow depth";;
ecmwf3_snd_2) file=ECMWFData/S3/monthly/ecmwf3_snd_2.ctl;kindname="ECMWF-3";climfield="+1 snow depth";;
ecmwf3_snd_3) file=ECMWFData/S3/monthly/ecmwf3_snd_3.ctl;kindname="ECMWF-3";climfield="+2 snow depth";;
ecmwf3_snd_4) file=ECMWFData/S3/monthly/ecmwf3_snd_4.ctl;kindname="ECMWF-3";climfield="+3 snow depth";;
ecmwf3_snd_5) file=ECMWFData/S3/monthly/ecmwf3_snd_5.ctl;kindname="ECMWF-3";climfield="+4 snow depth";;
ecmwf3_snd_6) file=ECMWFData/S3/monthly/ecmwf3_snd_6.ctl;kindname="ECMWF-3";climfield="+5 snow depth";;
ecmwf3_snd_jan) file=ECMWFData/S3/monthly/ecmwf3_snd_jan_ensm.ctl;kindname="ECMWF-3";climfield="1Jan snow depth";;
ecmwf3_snd_feb) file=ECMWFData/S3/monthly/ecmwf3_snd_feb_ensm.ctl;kindname="ECMWF-3";climfield="1Feb snow depth";;
ecmwf3_snd_mar) file=ECMWFData/S3/monthly/ecmwf3_snd_mar_ensm.ctl;kindname="ECMWF-3";climfield="1Mar snow depth";;
ecmwf3_snd_apr) file=ECMWFData/S3/monthly/ecmwf3_snd_apr_ensm.ctl;kindname="ECMWF-3";climfield="1Apr snow depth";;
ecmwf3_snd_may) file=ECMWFData/S3/monthly/ecmwf3_snd_may_ensm.ctl;kindname="ECMWF-3";climfield="1May snow depth";;
ecmwf3_snd_jun) file=ECMWFData/S3/monthly/ecmwf3_snd_jun_ensm.ctl;kindname="ECMWF-3";climfield="1Jun snow depth";;
ecmwf3_snd_jul) file=ECMWFData/S3/monthly/ecmwf3_snd_jul_ensm.ctl;kindname="ECMWF-3";climfield="1Jul snow depth";;
ecmwf3_snd_aug) file=ECMWFData/S3/monthly/ecmwf3_snd_aug_ensm.ctl;kindname="ECMWF-3";climfield="1Aug snow depth";;
ecmwf3_snd_sep) file=ECMWFData/S3/monthly/ecmwf3_snd_sep_ensm.ctl;kindname="ECMWF-3";climfield="1Sep snow depth";;
ecmwf3_snd_oct) file=ECMWFData/S3/monthly/ecmwf3_snd_oct_ensm.ctl;kindname="ECMWF-3";climfield="1Oct snow depth";;
ecmwf3_snd_nov) file=ECMWFData/S3/monthly/ecmwf3_snd_nov_ensm.ctl;kindname="ECMWF-3";climfield="1Nov snow depth";;
ecmwf3_snd_dec) file=ECMWFData/S3/monthly/ecmwf3_snd_dec_ensm.ctl;kindname="ECMWF-3";climfield="1Dec snow depth";;

ecmwf3_tsfc_1) file=ECMWFData/S3/monthly/ecmwf3_tsfc_1.ctl;kindname="ECMWF-3";climfield="+0 Tsfc";;
ecmwf3_tsfc_2) file=ECMWFData/S3/monthly/ecmwf3_tsfc_2.ctl;kindname="ECMWF-3";climfield="+1 Tsfc";;
ecmwf3_tsfc_3) file=ECMWFData/S3/monthly/ecmwf3_tsfc_3.ctl;kindname="ECMWF-3";climfield="+2 Tsfc";;
ecmwf3_tsfc_4) file=ECMWFData/S3/monthly/ecmwf3_tsfc_4.ctl;kindname="ECMWF-3";climfield="+3 Tsfc";;
ecmwf3_tsfc_5) file=ECMWFData/S3/monthly/ecmwf3_tsfc_5.ctl;kindname="ECMWF-3";climfield="+4 Tsfc";;
ecmwf3_tsfc_6) file=ECMWFData/S3/monthly/ecmwf3_tsfc_6.ctl;kindname="ECMWF-3";climfield="+5 Tsfc";;
ecmwf3_tsfc_jan) file=ECMWFData/S3/monthly/ecmwf3_tsfc_jan_ensm.ctl;kindname="ECMWF-3";climfield="1Jan Tsfc";;
ecmwf3_tsfc_feb) file=ECMWFData/S3/monthly/ecmwf3_tsfc_feb_ensm.ctl;kindname="ECMWF-3";climfield="1Feb Tsfc";;
ecmwf3_tsfc_mar) file=ECMWFData/S3/monthly/ecmwf3_tsfc_mar_ensm.ctl;kindname="ECMWF-3";climfield="1Mar Tsfc";;
ecmwf3_tsfc_apr) file=ECMWFData/S3/monthly/ecmwf3_tsfc_apr_ensm.ctl;kindname="ECMWF-3";climfield="1Apr Tsfc";;
ecmwf3_tsfc_may) file=ECMWFData/S3/monthly/ecmwf3_tsfc_may_ensm.ctl;kindname="ECMWF-3";climfield="1May Tsfc";;
ecmwf3_tsfc_jun) file=ECMWFData/S3/monthly/ecmwf3_tsfc_jun_ensm.ctl;kindname="ECMWF-3";climfield="1Jun Tsfc";;
ecmwf3_tsfc_jul) file=ECMWFData/S3/monthly/ecmwf3_tsfc_jul_ensm.ctl;kindname="ECMWF-3";climfield="1Jul Tsfc";;
ecmwf3_tsfc_aug) file=ECMWFData/S3/monthly/ecmwf3_tsfc_aug_ensm.ctl;kindname="ECMWF-3";climfield="1Aug Tsfc";;
ecmwf3_tsfc_sep) file=ECMWFData/S3/monthly/ecmwf3_tsfc_sep_ensm.ctl;kindname="ECMWF-3";climfield="1Sep Tsfc";;
ecmwf3_tsfc_oct) file=ECMWFData/S3/monthly/ecmwf3_tsfc_oct_ensm.ctl;kindname="ECMWF-3";climfield="1Oct Tsfc";;
ecmwf3_tsfc_nov) file=ECMWFData/S3/monthly/ecmwf3_tsfc_nov_ensm.ctl;kindname="ECMWF-3";climfield="1Nov Tsfc";;
ecmwf3_tsfc_dec) file=ECMWFData/S3/monthly/ecmwf3_tsfc_dec_ensm.ctl;kindname="ECMWF-3";climfield="1Dec Tsfc";;

ecmwf3_sst_1) file=ECMWFData/S3/monthly/ecmwf3_sst_1.ctl;kindname="ECMWF-3";climfield="+0 sst";;
ecmwf3_sst_2) file=ECMWFData/S3/monthly/ecmwf3_sst_2.ctl;kindname="ECMWF-3";climfield="+1 sst";;
ecmwf3_sst_3) file=ECMWFData/S3/monthly/ecmwf3_sst_3.ctl;kindname="ECMWF-3";climfield="+2 sst";;
ecmwf3_sst_4) file=ECMWFData/S3/monthly/ecmwf3_sst_4.ctl;kindname="ECMWF-3";climfield="+3 sst";;
ecmwf3_sst_5) file=ECMWFData/S3/monthly/ecmwf3_sst_5.ctl;kindname="ECMWF-3";climfield="+4 sst";;
ecmwf3_sst_6) file=ECMWFData/S3/monthly/ecmwf3_sst_6.ctl;kindname="ECMWF-3";climfield="+5 sst";;
ecmwf3_sst_jan) file=ECMWFData/S3/monthly/ecmwf3_sst_jan_ensm.ctl;kindname="ECMWF-3";climfield="1Jan sst";;
ecmwf3_sst_feb) file=ECMWFData/S3/monthly/ecmwf3_sst_feb_ensm.ctl;kindname="ECMWF-3";climfield="1Feb sst";;
ecmwf3_sst_mar) file=ECMWFData/S3/monthly/ecmwf3_sst_mar_ensm.ctl;kindname="ECMWF-3";climfield="1Mar sst";;
ecmwf3_sst_apr) file=ECMWFData/S3/monthly/ecmwf3_sst_apr_ensm.ctl;kindname="ECMWF-3";climfield="1Apr sst";;
ecmwf3_sst_may) file=ECMWFData/S3/monthly/ecmwf3_sst_may_ensm.ctl;kindname="ECMWF-3";climfield="1May sst";;
ecmwf3_sst_jun) file=ECMWFData/S3/monthly/ecmwf3_sst_jun_ensm.ctl;kindname="ECMWF-3";climfield="1Jun sst";;
ecmwf3_sst_jul) file=ECMWFData/S3/monthly/ecmwf3_sst_jul_ensm.ctl;kindname="ECMWF-3";climfield="1Jul sst";;
ecmwf3_sst_aug) file=ECMWFData/S3/monthly/ecmwf3_sst_aug_ensm.ctl;kindname="ECMWF-3";climfield="1Aug sst";;
ecmwf3_sst_sep) file=ECMWFData/S3/monthly/ecmwf3_sst_sep_ensm.ctl;kindname="ECMWF-3";climfield="1Sep sst";;
ecmwf3_sst_oct) file=ECMWFData/S3/monthly/ecmwf3_sst_oct_ensm.ctl;kindname="ECMWF-3";climfield="1Oct sst";;
ecmwf3_sst_nov) file=ECMWFData/S3/monthly/ecmwf3_sst_nov_ensm.ctl;kindname="ECMWF-3";climfield="1Nov sst";;
ecmwf3_sst_dec) file=ECMWFData/S3/monthly/ecmwf3_sst_dec_ensm.ctl;kindname="ECMWF-3";climfield="1Dec sst";;

ens_ecmwf3_t2m_1) file=ECMWFData/S3/monthly/ecmwf3_t2m_1_m%%.ctl;kindname="ensemble ECMWF-3";climfield="+0 T2m";;
ens_ecmwf3_t2m_2) file=ECMWFData/S3/monthly/ecmwf3_t2m_2_m%%.ctl;kindname="ensemble ECMWF-3";climfield="+1 T2m";;
ens_ecmwf3_t2m_3) file=ECMWFData/S3/monthly/ecmwf3_t2m_3_m%%.ctl;kindname="ensemble ECMWF-3";climfield="+2 T2m";;
ens_ecmwf3_t2m_4) file=ECMWFData/S3/monthly/ecmwf3_t2m_4_m%%.ctl;kindname="ensemble ECMWF-3";climfield="+3 T2m";;
ens_ecmwf3_t2m_5) file=ECMWFData/S3/monthly/ecmwf3_t2m_5_m%%.ctl;kindname="ensemble ECMWF-3";climfield="+4 T2m";;
ens_ecmwf3_t2m_6) file=ECMWFData/S3/monthly/ecmwf3_t2m_6_m%%.ctl;kindname="ensemble ECMWF-3";climfield="+5 T2m";;
ens_ecmwf3_t2m_jan) file=ECMWFData/S3/monthly/ecmwf3_t2m_jan_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Jan T2m";;
ens_ecmwf3_t2m_feb) file=ECMWFData/S3/monthly/ecmwf3_t2m_feb_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Feb T2m";;
ens_ecmwf3_t2m_mar) file=ECMWFData/S3/monthly/ecmwf3_t2m_mar_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Mar T2m";;
ens_ecmwf3_t2m_apr) file=ECMWFData/S3/monthly/ecmwf3_t2m_apr_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Apr T2m";;
ens_ecmwf3_t2m_may) file=ECMWFData/S3/monthly/ecmwf3_t2m_may_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1May T2m";;
ens_ecmwf3_t2m_jun) file=ECMWFData/S3/monthly/ecmwf3_t2m_jun_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Jun T2m";;
ens_ecmwf3_t2m_jul) file=ECMWFData/S3/monthly/ecmwf3_t2m_jul_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Jul T2m";;
ens_ecmwf3_t2m_aug) file=ECMWFData/S3/monthly/ecmwf3_t2m_aug_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Aug T2m";;
ens_ecmwf3_t2m_sep) file=ECMWFData/S3/monthly/ecmwf3_t2m_sep_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Sep T2m";;
ens_ecmwf3_t2m_oct) file=ECMWFData/S3/monthly/ecmwf3_t2m_oct_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Oct T2m";;
ens_ecmwf3_t2m_nov) file=ECMWFData/S3/monthly/ecmwf3_t2m_nov_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Nov T2m";;
ens_ecmwf3_t2m_dec) file=ECMWFData/S3/monthly/ecmwf3_t2m_dec_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Dec T2m";;

ens_ecmwf3_t2x_1) file=ECMWFData/S3/monthly/ecmwf3_t2x_1_m%%.ctl;kindname="ensemble ECMWF-3";climfield="+0 T2max";;
ens_ecmwf3_t2x_2) file=ECMWFData/S3/monthly/ecmwf3_t2x_2_m%%.ctl;kindname="ensemble ECMWF-3";climfield="+1 T2max";;
ens_ecmwf3_t2x_3) file=ECMWFData/S3/monthly/ecmwf3_t2x_3_m%%.ctl;kindname="ensemble ECMWF-3";climfield="+2 T2max";;
ens_ecmwf3_t2x_4) file=ECMWFData/S3/monthly/ecmwf3_t2x_4_m%%.ctl;kindname="ensemble ECMWF-3";climfield="+3 T2max";;
ens_ecmwf3_t2x_5) file=ECMWFData/S3/monthly/ecmwf3_t2x_5_m%%.ctl;kindname="ensemble ECMWF-3";climfield="+4 T2max";;
ens_ecmwf3_t2x_6) file=ECMWFData/S3/monthly/ecmwf3_t2x_6_m%%.ctl;kindname="ensemble ECMWF-3";climfield="+5 T2max";;
ens_ecmwf3_t2x_jan) file=ECMWFData/S3/monthly/ecmwf3_t2x_jan_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Jan T2max";;
ens_ecmwf3_t2x_feb) file=ECMWFData/S3/monthly/ecmwf3_t2x_feb_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Feb T2max";;
ens_ecmwf3_t2x_mar) file=ECMWFData/S3/monthly/ecmwf3_t2x_mar_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Mar T2max";;
ens_ecmwf3_t2x_apr) file=ECMWFData/S3/monthly/ecmwf3_t2x_apr_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Apr T2max";;
ens_ecmwf3_t2x_may) file=ECMWFData/S3/monthly/ecmwf3_t2x_may_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1May T2max";;
ens_ecmwf3_t2x_jun) file=ECMWFData/S3/monthly/ecmwf3_t2x_jun_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Jun T2max";;
ens_ecmwf3_t2x_jul) file=ECMWFData/S3/monthly/ecmwf3_t2x_jul_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Jul T2max";;
ens_ecmwf3_t2x_aug) file=ECMWFData/S3/monthly/ecmwf3_t2x_aug_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Aug T2max";;
ens_ecmwf3_t2x_sep) file=ECMWFData/S3/monthly/ecmwf3_t2x_sep_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Sep T2max";;
ens_ecmwf3_t2x_oct) file=ECMWFData/S3/monthly/ecmwf3_t2x_oct_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Oct T2max";;
ens_ecmwf3_t2x_nov) file=ECMWFData/S3/monthly/ecmwf3_t2x_nov_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Nov T2max";;
ens_ecmwf3_t2x_dec) file=ECMWFData/S3/monthly/ecmwf3_t2x_dec_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Dec T2max";;

ens_ecmwf3_t2n_1) file=ECMWFData/S3/monthly/ecmwf3_t2n_1_m%%.ctl;kindname="ensemble ECMWF-3";climfield="+0 T2min";;
ens_ecmwf3_t2n_2) file=ECMWFData/S3/monthly/ecmwf3_t2n_2_m%%.ctl;kindname="ensemble ECMWF-3";climfield="+1 T2min";;
ens_ecmwf3_t2n_3) file=ECMWFData/S3/monthly/ecmwf3_t2n_3_m%%.ctl;kindname="ensemble ECMWF-3";climfield="+2 T2min";;
ens_ecmwf3_t2n_4) file=ECMWFData/S3/monthly/ecmwf3_t2n_4_m%%.ctl;kindname="ensemble ECMWF-3";climfield="+3 T2min";;
ens_ecmwf3_t2n_5) file=ECMWFData/S3/monthly/ecmwf3_t2n_5_m%%.ctl;kindname="ensemble ECMWF-3";climfield="+4 T2min";;
ens_ecmwf3_t2n_6) file=ECMWFData/S3/monthly/ecmwf3_t2n_6_m%%.ctl;kindname="ensemble ECMWF-3";climfield="+5 T2min";;
ens_ecmwf3_t2n_jan) file=ECMWFData/S3/monthly/ecmwf3_t2n_jan_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Jan T2min";;
ens_ecmwf3_t2n_feb) file=ECMWFData/S3/monthly/ecmwf3_t2n_feb_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Feb T2min";;
ens_ecmwf3_t2n_mar) file=ECMWFData/S3/monthly/ecmwf3_t2n_mar_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Mar T2min";;
ens_ecmwf3_t2n_apr) file=ECMWFData/S3/monthly/ecmwf3_t2n_apr_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Apr T2min";;
ens_ecmwf3_t2n_may) file=ECMWFData/S3/monthly/ecmwf3_t2n_may_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1May T2min";;
ens_ecmwf3_t2n_jun) file=ECMWFData/S3/monthly/ecmwf3_t2n_jun_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Jun T2min";;
ens_ecmwf3_t2n_jul) file=ECMWFData/S3/monthly/ecmwf3_t2n_jul_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Jul T2min";;
ens_ecmwf3_t2n_aug) file=ECMWFData/S3/monthly/ecmwf3_t2n_aug_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Aug T2min";;
ens_ecmwf3_t2n_sep) file=ECMWFData/S3/monthly/ecmwf3_t2n_sep_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Sep T2min";;
ens_ecmwf3_t2n_oct) file=ECMWFData/S3/monthly/ecmwf3_t2n_oct_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Oct T2min";;
ens_ecmwf3_t2n_nov) file=ECMWFData/S3/monthly/ecmwf3_t2n_nov_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Nov T2min";;
ens_ecmwf3_t2n_dec) file=ECMWFData/S3/monthly/ecmwf3_t2n_dec_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Dec T2min";;

ens_ecmwf3_prcp_1) file=ECMWFData/S3/monthly/ecmwf3_prcp_1_m%%.ctl;kindname="ensemble ECMWF-3";climfield="+0 precipitation";;
ens_ecmwf3_prcp_2) file=ECMWFData/S3/monthly/ecmwf3_prcp_2_m%%.ctl;kindname="ensemble ECMWF-3";climfield="+1 precipitation";;
ens_ecmwf3_prcp_3) file=ECMWFData/S3/monthly/ecmwf3_prcp_3_m%%.ctl;kindname="ensemble ECMWF-3";climfield="+2 precipitation";;
ens_ecmwf3_prcp_4) file=ECMWFData/S3/monthly/ecmwf3_prcp_4_m%%.ctl;kindname="ensemble ECMWF-3";climfield="+3 precipitation";;
ens_ecmwf3_prcp_5) file=ECMWFData/S3/monthly/ecmwf3_prcp_5_m%%.ctl;kindname="ensemble ECMWF-3";climfield="+4 precipitation";;
ens_ecmwf3_prcp_6) file=ECMWFData/S3/monthly/ecmwf3_prcp_6_m%%.ctl;kindname="ensemble ECMWF-3";climfield="+5 precipitation";;
ens_ecmwf3_prcp_jan) file=ECMWFData/S3/monthly/ecmwf3_prcp_jan_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Jan precipitation";;
ens_ecmwf3_prcp_feb) file=ECMWFData/S3/monthly/ecmwf3_prcp_feb_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Feb precipitation";;
ens_ecmwf3_prcp_mar) file=ECMWFData/S3/monthly/ecmwf3_prcp_mar_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Mar precipitation";;
ens_ecmwf3_prcp_apr) file=ECMWFData/S3/monthly/ecmwf3_prcp_apr_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Apr precipitation";;
ens_ecmwf3_prcp_may) file=ECMWFData/S3/monthly/ecmwf3_prcp_may_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1May precipitation";;
ens_ecmwf3_prcp_jun) file=ECMWFData/S3/monthly/ecmwf3_prcp_jun_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Jun precipitation";;
ens_ecmwf3_prcp_jul) file=ECMWFData/S3/monthly/ecmwf3_prcp_jul_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Jul precipitation";;
ens_ecmwf3_prcp_aug) file=ECMWFData/S3/monthly/ecmwf3_prcp_aug_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Aug precipitation";;
ens_ecmwf3_prcp_sep) file=ECMWFData/S3/monthly/ecmwf3_prcp_sep_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Sep precipitation";;
ens_ecmwf3_prcp_oct) file=ECMWFData/S3/monthly/ecmwf3_prcp_oct_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Oct precipitation";;
ens_ecmwf3_prcp_nov) file=ECMWFData/S3/monthly/ecmwf3_prcp_nov_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Nov precipitation";;
ens_ecmwf3_prcp_dec) file=ECMWFData/S3/monthly/ecmwf3_prcp_dec_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Dec precipitation";;

ens_ecmwf3_msl_1) file=ECMWFData/S3/monthly/ecmwf3_msl_1_m%%.ctl;kindname="ensemble ECMWF-3";climfield="+0 SLP";;
ens_ecmwf3_msl_2) file=ECMWFData/S3/monthly/ecmwf3_msl_2_m%%.ctl;kindname="ensemble ECMWF-3";climfield="+1 SLP";;
ens_ecmwf3_msl_3) file=ECMWFData/S3/monthly/ecmwf3_msl_3_m%%.ctl;kindname="ensemble ECMWF-3";climfield="+2 SLP";;
ens_ecmwf3_msl_4) file=ECMWFData/S3/monthly/ecmwf3_msl_4_m%%.ctl;kindname="ensemble ECMWF-3";climfield="+3 SLP";;
ens_ecmwf3_msl_5) file=ECMWFData/S3/monthly/ecmwf3_msl_5_m%%.ctl;kindname="ensemble ECMWF-3";climfield="+4 SLP";;
ens_ecmwf3_msl_6) file=ECMWFData/S3/monthly/ecmwf3_msl_6_m%%.ctl;kindname="ensemble ECMWF-3";climfield="+5 SLP";;
ens_ecmwf3_msl_jan) file=ECMWFData/S3/monthly/ecmwf3_msl_jan_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Jan SLP";;
ens_ecmwf3_msl_feb) file=ECMWFData/S3/monthly/ecmwf3_msl_feb_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Feb SLP";;
ens_ecmwf3_msl_mar) file=ECMWFData/S3/monthly/ecmwf3_msl_mar_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Mar SLP";;
ens_ecmwf3_msl_apr) file=ECMWFData/S3/monthly/ecmwf3_msl_apr_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Apr SLP";;
ens_ecmwf3_msl_may) file=ECMWFData/S3/monthly/ecmwf3_msl_may_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1May SLP";;
ens_ecmwf3_msl_jun) file=ECMWFData/S3/monthly/ecmwf3_msl_jun_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Jun SLP";;
ens_ecmwf3_msl_jul) file=ECMWFData/S3/monthly/ecmwf3_msl_jul_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Jul SLP";;
ens_ecmwf3_msl_aug) file=ECMWFData/S3/monthly/ecmwf3_msl_aug_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Aug SLP";;
ens_ecmwf3_msl_sep) file=ECMWFData/S3/monthly/ecmwf3_msl_sep_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Sep SLP";;
ens_ecmwf3_msl_oct) file=ECMWFData/S3/monthly/ecmwf3_msl_oct_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Oct SLP";;
ens_ecmwf3_msl_nov) file=ECMWFData/S3/monthly/ecmwf3_msl_nov_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Nov SLP";;
ens_ecmwf3_msl_dec) file=ECMWFData/S3/monthly/ecmwf3_msl_dec_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Dec SLP";;

ens_ecmwf3_z500_1) file=ECMWFData/S3/monthly/ecmwf3_z500_1_m%%.ctl;kindname="ensemble ECMWF-3";climfield="+0 z500";;
ens_ecmwf3_z500_2) file=ECMWFData/S3/monthly/ecmwf3_z500_2_m%%.ctl;kindname="ensemble ECMWF-3";climfield="+1 z500";;
ens_ecmwf3_z500_3) file=ECMWFData/S3/monthly/ecmwf3_z500_3_m%%.ctl;kindname="ensemble ECMWF-3";climfield="+2 z500";;
ens_ecmwf3_z500_4) file=ECMWFData/S3/monthly/ecmwf3_z500_4_m%%.ctl;kindname="ensemble ECMWF-3";climfield="+3 z500";;
ens_ecmwf3_z500_5) file=ECMWFData/S3/monthly/ecmwf3_z500_5_m%%.ctl;kindname="ensemble ECMWF-3";climfield="+4 z500";;
ens_ecmwf3_z500_6) file=ECMWFData/S3/monthly/ecmwf3_z500_6_m%%.ctl;kindname="ensemble ECMWF-3";climfield="+5 z500";;
ens_ecmwf3_z500_jan) file=ECMWFData/S3/monthly/ecmwf3_z500_jan_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Jan z500";;
ens_ecmwf3_z500_feb) file=ECMWFData/S3/monthly/ecmwf3_z500_feb_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Feb z500";;
ens_ecmwf3_z500_mar) file=ECMWFData/S3/monthly/ecmwf3_z500_mar_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Mar z500";;
ens_ecmwf3_z500_apr) file=ECMWFData/S3/monthly/ecmwf3_z500_apr_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Apr z500";;
ens_ecmwf3_z500_may) file=ECMWFData/S3/monthly/ecmwf3_z500_may_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1May z500";;
ens_ecmwf3_z500_jun) file=ECMWFData/S3/monthly/ecmwf3_z500_jun_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Jun z500";;
ens_ecmwf3_z500_jul) file=ECMWFData/S3/monthly/ecmwf3_z500_jul_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Jul z500";;
ens_ecmwf3_z500_aug) file=ECMWFData/S3/monthly/ecmwf3_z500_aug_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Aug z500";;
ens_ecmwf3_z500_sep) file=ECMWFData/S3/monthly/ecmwf3_z500_sep_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Sep z500";;
ens_ecmwf3_z500_oct) file=ECMWFData/S3/monthly/ecmwf3_z500_oct_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Oct z500";;
ens_ecmwf3_z500_nov) file=ECMWFData/S3/monthly/ecmwf3_z500_nov_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Nov z500";;
ens_ecmwf3_z500_dec) file=ECMWFData/S3/monthly/ecmwf3_z500_dec_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Dec z500";;

ens_ecmwf3_u10_1) file=ECMWFData/S3/monthly/ecmwf3_u10_1_m%%.ctl;kindname="ensemble ECMWF-3";climfield="+0 u10";;
ens_ecmwf3_u10_2) file=ECMWFData/S3/monthly/ecmwf3_u10_2_m%%.ctl;kindname="ensemble ECMWF-3";climfield="+1 u10";;
ens_ecmwf3_u10_3) file=ECMWFData/S3/monthly/ecmwf3_u10_3_m%%.ctl;kindname="ensemble ECMWF-3";climfield="+2 u10";;
ens_ecmwf3_u10_4) file=ECMWFData/S3/monthly/ecmwf3_u10_4_m%%.ctl;kindname="ensemble ECMWF-3";climfield="+3 u10";;
ens_ecmwf3_u10_5) file=ECMWFData/S3/monthly/ecmwf3_u10_5_m%%.ctl;kindname="ensemble ECMWF-3";climfield="+4 u10";;
ens_ecmwf3_u10_6) file=ECMWFData/S3/monthly/ecmwf3_u10_6_m%%.ctl;kindname="ensemble ECMWF-3";climfield="+5 u10";;
ens_ecmwf3_u10_jan) file=ECMWFData/S3/monthly/ecmwf3_u10_jan_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Jan u10";;
ens_ecmwf3_u10_feb) file=ECMWFData/S3/monthly/ecmwf3_u10_feb_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Feb u10";;
ens_ecmwf3_u10_mar) file=ECMWFData/S3/monthly/ecmwf3_u10_mar_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Mar u10";;
ens_ecmwf3_u10_apr) file=ECMWFData/S3/monthly/ecmwf3_u10_apr_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Apr u10";;
ens_ecmwf3_u10_may) file=ECMWFData/S3/monthly/ecmwf3_u10_may_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1May u10";;
ens_ecmwf3_u10_jun) file=ECMWFData/S3/monthly/ecmwf3_u10_jun_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Jul u10";;
ens_ecmwf3_u10_jul) file=ECMWFData/S3/monthly/ecmwf3_u10_jul_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Jul u10";;
ens_ecmwf3_u10_aug) file=ECMWFData/S3/monthly/ecmwf3_u10_aug_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Aug u10";;
ens_ecmwf3_u10_sep) file=ECMWFData/S3/monthly/ecmwf3_u10_sep_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Sep u10";;
ens_ecmwf3_u10_oct) file=ECMWFData/S3/monthly/ecmwf3_u10_oct_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Oct u10";;
ens_ecmwf3_u10_nov) file=ECMWFData/S3/monthly/ecmwf3_u10_nov_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Nov u10";;
ens_ecmwf3_u10_dec) file=ECMWFData/S3/monthly/ecmwf3_u10_dec_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Dec u10";;

ens_ecmwf3_v10_1) file=ECMWFData/S3/monthly/ecmwf3_v10_1_m%%.ctl;kindname="ensemble ECMWF-3";climfield="+0 v10";;
ens_ecmwf3_v10_2) file=ECMWFData/S3/monthly/ecmwf3_v10_2_m%%.ctl;kindname="ensemble ECMWF-3";climfield="+1 v10";;
ens_ecmwf3_v10_3) file=ECMWFData/S3/monthly/ecmwf3_v10_3_m%%.ctl;kindname="ensemble ECMWF-3";climfield="+2 v10";;
ens_ecmwf3_v10_4) file=ECMWFData/S3/monthly/ecmwf3_v10_4_m%%.ctl;kindname="ensemble ECMWF-3";climfield="+3 v10";;
ens_ecmwf3_v10_5) file=ECMWFData/S3/monthly/ecmwf3_v10_5_m%%.ctl;kindname="ensemble ECMWF-3";climfield="+4 v10";;
ens_ecmwf3_v10_6) file=ECMWFData/S3/monthly/ecmwf3_v10_6_m%%.ctl;kindname="ensemble ECMWF-3";climfield="+5 v10";;
ens_ecmwf3_v10_jan) file=ECMWFData/S3/monthly/ecmwf3_v10_jan_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Jan v10";;
ens_ecmwf3_v10_feb) file=ECMWFData/S3/monthly/ecmwf3_v10_feb_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Feb v10";;
ens_ecmwf3_v10_mar) file=ECMWFData/S3/monthly/ecmwf3_v10_mar_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Mar v10";;
ens_ecmwf3_v10_apr) file=ECMWFData/S3/monthly/ecmwf3_v10_apr_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Apr v10";;
ens_ecmwf3_v10_may) file=ECMWFData/S3/monthly/ecmwf3_v10_may_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1May v10";;
ens_ecmwf3_v10_jun) file=ECMWFData/S3/monthly/ecmwf3_v10_jun_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Jun v10";;
ens_ecmwf3_v10_jul) file=ECMWFData/S3/monthly/ecmwf3_v10_jul_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Jul v10";;
ens_ecmwf3_v10_aug) file=ECMWFData/S3/monthly/ecmwf3_v10_aug_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Aug v10";;
ens_ecmwf3_v10_sep) file=ECMWFData/S3/monthly/ecmwf3_v10_sep_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Sep v10";;
ens_ecmwf3_v10_oct) file=ECMWFData/S3/monthly/ecmwf3_v10_oct_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Oct v10";;
ens_ecmwf3_v10_nov) file=ECMWFData/S3/monthly/ecmwf3_v10_nov_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Nov v10";;
ens_ecmwf3_v10_dec) file=ECMWFData/S3/monthly/ecmwf3_v10_dec_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Dec v10";;

ens_ecmwf3_ssd_1) file=ECMWFData/S3/monthly/ecmwf3_ssd_1_m%%.ctl;kindname="ensemble ECMWF-3";climfield="+0 solar radiation";;
ens_ecmwf3_ssd_2) file=ECMWFData/S3/monthly/ecmwf3_ssd_2_m%%.ctl;kindname="ensemble ECMWF-3";climfield="+1 solar radiation";;
ens_ecmwf3_ssd_3) file=ECMWFData/S3/monthly/ecmwf3_ssd_3_m%%.ctl;kindname="ensemble ECMWF-3";climfield="+2 solar radiation";;
ens_ecmwf3_ssd_4) file=ECMWFData/S3/monthly/ecmwf3_ssd_4_m%%.ctl;kindname="ensemble ECMWF-3";climfield="+3 solar radiation";;
ens_ecmwf3_ssd_5) file=ECMWFData/S3/monthly/ecmwf3_ssd_5_m%%.ctl;kindname="ensemble ECMWF-3";climfield="+4 solar radiation";;
ens_ecmwf3_ssd_6) file=ECMWFData/S3/monthly/ecmwf3_ssd_6_m%%.ctl;kindname="ensemble ECMWF-3";climfield="+5 solar radiation";;
ens_ecmwf3_ssd_jan) file=ECMWFData/S3/monthly/ecmwf3_ssd_jan_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Jan solar radiation";;
ens_ecmwf3_ssd_feb) file=ECMWFData/S3/monthly/ecmwf3_ssd_feb_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Feb solar radiation";;
ens_ecmwf3_ssd_mar) file=ECMWFData/S3/monthly/ecmwf3_ssd_mar_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Mar solar radiation";;
ens_ecmwf3_ssd_apr) file=ECMWFData/S3/monthly/ecmwf3_ssd_apr_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Apr solar radiation";;
ens_ecmwf3_ssd_may) file=ECMWFData/S3/monthly/ecmwf3_ssd_may_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1May solar radiation";;
ens_ecmwf3_ssd_jun) file=ECMWFData/S3/monthly/ecmwf3_ssd_jun_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Jun solar radiation";;
ens_ecmwf3_ssd_jul) file=ECMWFData/S3/monthly/ecmwf3_ssd_jul_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Jul solar radiation";;
ens_ecmwf3_ssd_aug) file=ECMWFData/S3/monthly/ecmwf3_ssd_aug_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Aug solar radiation";;
ens_ecmwf3_ssd_sep) file=ECMWFData/S3/monthly/ecmwf3_ssd_sep_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Sep solar radiation";;
ens_ecmwf3_ssd_oct) file=ECMWFData/S3/monthly/ecmwf3_ssd_oct_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Oct solar radiation";;
ens_ecmwf3_ssd_nov) file=ECMWFData/S3/monthly/ecmwf3_ssd_nov_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Nov solar radiation";;
ens_ecmwf3_ssd_dec) file=ECMWFData/S3/monthly/ecmwf3_ssd_dec_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Dec solar radiation";;

ens_ecmwf3_snd_1) file=ECMWFData/S3/monthly/ecmwf3_snd_1_m%%.ctl;kindname="ensemble ECMWF-3";climfield="+0 snow depth";;
ens_ecmwf3_snd_2) file=ECMWFData/S3/monthly/ecmwf3_snd_2_m%%.ctl;kindname="ensemble ECMWF-3";climfield="+1 snow depth";;
ens_ecmwf3_snd_3) file=ECMWFData/S3/monthly/ecmwf3_snd_3_m%%.ctl;kindname="ensemble ECMWF-3";climfield="+2 snow depth";;
ens_ecmwf3_snd_4) file=ECMWFData/S3/monthly/ecmwf3_snd_4_m%%.ctl;kindname="ensemble ECMWF-3";climfield="+3 snow depth";;
ens_ecmwf3_snd_5) file=ECMWFData/S3/monthly/ecmwf3_snd_5_m%%.ctl;kindname="ensemble ECMWF-3";climfield="+4 snow depth";;
ens_ecmwf3_snd_6) file=ECMWFData/S3/monthly/ecmwf3_snd_6_m%%.ctl;kindname="ensemble ECMWF-3";climfield="+5 snow depth";;
ens_ecmwf3_snd_jan) file=ECMWFData/S3/monthly/ecmwf3_snd_jan_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Jan snow depth";;
ens_ecmwf3_snd_feb) file=ECMWFData/S3/monthly/ecmwf3_snd_feb_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Feb snow depth";;
ens_ecmwf3_snd_mar) file=ECMWFData/S3/monthly/ecmwf3_snd_mar_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Mar snow depth";;
ens_ecmwf3_snd_apr) file=ECMWFData/S3/monthly/ecmwf3_snd_apr_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Apr snow depth";;
ens_ecmwf3_snd_may) file=ECMWFData/S3/monthly/ecmwf3_snd_may_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1May snow depth";;
ens_ecmwf3_snd_jun) file=ECMWFData/S3/monthly/ecmwf3_snd_jun_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Jun snow depth";;
ens_ecmwf3_snd_jul) file=ECMWFData/S3/monthly/ecmwf3_snd_jul_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Jul snow depth";;
ens_ecmwf3_snd_aug) file=ECMWFData/S3/monthly/ecmwf3_snd_aug_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Aug snow depth";;
ens_ecmwf3_snd_sep) file=ECMWFData/S3/monthly/ecmwf3_snd_sep_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Sep snow depth";;
ens_ecmwf3_snd_oct) file=ECMWFData/S3/monthly/ecmwf3_snd_oct_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Oct snow depth";;
ens_ecmwf3_snd_nov) file=ECMWFData/S3/monthly/ecmwf3_snd_nov_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Nov snow depth";;
ens_ecmwf3_snd_dec) file=ECMWFData/S3/monthly/ecmwf3_snd_dec_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Dec snow depth";;

ens_ecmwf3_tsfc_1) file=ECMWFData/S3/monthly/ecmwf3_tsfc_1_m%%.ctl;kindname="ECMWF-3";climfield="+0 Tsfc";;
ens_ecmwf3_tsfc_2) file=ECMWFData/S3/monthly/ecmwf3_tsfc_2_m%%.ctl;kindname="ECMWF-3";climfield="+1 Tsfc";;
ens_ecmwf3_tsfc_3) file=ECMWFData/S3/monthly/ecmwf3_tsfc_3_m%%.ctl;kindname="ECMWF-3";climfield="+2 Tsfc";;
ens_ecmwf3_tsfc_4) file=ECMWFData/S3/monthly/ecmwf3_tsfc_4_m%%.ctl;kindname="ECMWF-3";climfield="+3 Tsfc";;
ens_ecmwf3_tsfc_5) file=ECMWFData/S3/monthly/ecmwf3_tsfc_5_m%%.ctl;kindname="ECMWF-3";climfield="+4 Tsfc";;
ens_ecmwf3_tsfc_6) file=ECMWFData/S3/monthly/ecmwf3_tsfc_6_m%%.ctl;kindname="ECMWF-3";climfield="+5 Tsfc";;
ens_ecmwf3_tsfc_jan) file=ECMWFData/S3/monthly/ecmwf3_tsfc_jan_m%%.ctl;kindname="ECMWF-3";climfield="1Jan Tsfc";;
ens_ecmwf3_tsfc_feb) file=ECMWFData/S3/monthly/ecmwf3_tsfc_feb_m%%.ctl;kindname="ECMWF-3";climfield="1Feb Tsfc";;
ens_ecmwf3_tsfc_mar) file=ECMWFData/S3/monthly/ecmwf3_tsfc_mar_m%%.ctl;kindname="ECMWF-3";climfield="1Mar Tsfc";;
ens_ecmwf3_tsfc_apr) file=ECMWFData/S3/monthly/ecmwf3_tsfc_apr_m%%.ctl;kindname="ECMWF-3";climfield="1Apr Tsfc";;
ens_ecmwf3_tsfc_may) file=ECMWFData/S3/monthly/ecmwf3_tsfc_may_m%%.ctl;kindname="ECMWF-3";climfield="1May Tsfc";;
ens_ecmwf3_tsfc_jun) file=ECMWFData/S3/monthly/ecmwf3_tsfc_jun_m%%.ctl;kindname="ECMWF-3";climfield="1Jun Tsfc";;
ens_ecmwf3_tsfc_jul) file=ECMWFData/S3/monthly/ecmwf3_tsfc_jul_m%%.ctl;kindname="ECMWF-3";climfield="1Jul Tsfc";;
ens_ecmwf3_tsfc_aug) file=ECMWFData/S3/monthly/ecmwf3_tsfc_aug_m%%.ctl;kindname="ECMWF-3";climfield="1Aug Tsfc";;
ens_ecmwf3_tsfc_sep) file=ECMWFData/S3/monthly/ecmwf3_tsfc_sep_m%%.ctl;kindname="ECMWF-3";climfield="1Sep Tsfc";;
ens_ecmwf3_tsfc_oct) file=ECMWFData/S3/monthly/ecmwf3_tsfc_oct_m%%.ctl;kindname="ECMWF-3";climfield="1Oct Tsfc";;
ens_ecmwf3_tsfc_nov) file=ECMWFData/S3/monthly/ecmwf3_tsfc_nov_m%%.ctl;kindname="ECMWF-3";climfield="1Nov Tsfc";;
ens_ecmwf3_tsfc_dec) file=ECMWFData/S3/monthly/ecmwf3_tsfc_dec_m%%.ctl;kindname="ECMWF-3";climfield="1Dec Tsfc";;

ens_ecmwf3_sst_1) file=ECMWFData/S3/monthly/ecmwf3_sst_1_m%%.ctl;kindname="ensemble ECMWF-3";climfield="+0 sst";;
ens_ecmwf3_sst_2) file=ECMWFData/S3/monthly/ecmwf3_sst_2_m%%.ctl;kindname="ensemble ECMWF-3";climfield="+1 sst";;
ens_ecmwf3_sst_3) file=ECMWFData/S3/monthly/ecmwf3_sst_3_m%%.ctl;kindname="ensemble ECMWF-3";climfield="+2 sst";;
ens_ecmwf3_sst_4) file=ECMWFData/S3/monthly/ecmwf3_sst_4_m%%.ctl;kindname="ensemble ECMWF-3";climfield="+3 sst";;
ens_ecmwf3_sst_5) file=ECMWFData/S3/monthly/ecmwf3_sst_5_m%%.ctl;kindname="ensemble ECMWF-3";climfield="+4 sst";;
ens_ecmwf3_sst_6) file=ECMWFData/S3/monthly/ecmwf3_sst_6_m%%.ctl;kindname="ensemble ECMWF-3";climfield="+5 sst";;
ens_ecmwf3_sst_jan) file=ECMWFData/S3/monthly/ecmwf3_sst_jan_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Jan sst";;
ens_ecmwf3_sst_feb) file=ECMWFData/S3/monthly/ecmwf3_sst_feb_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Feb sst";;
ens_ecmwf3_sst_mar) file=ECMWFData/S3/monthly/ecmwf3_sst_mar_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Mar sst";;
ens_ecmwf3_sst_apr) file=ECMWFData/S3/monthly/ecmwf3_sst_apr_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Apr sst";;
ens_ecmwf3_sst_may) file=ECMWFData/S3/monthly/ecmwf3_sst_may_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1May sst";;
ens_ecmwf3_sst_jun) file=ECMWFData/S3/monthly/ecmwf3_sst_jun_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Jun sst";;
ens_ecmwf3_sst_jul) file=ECMWFData/S3/monthly/ecmwf3_sst_jul_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Jul sst";;
ens_ecmwf3_sst_aug) file=ECMWFData/S3/monthly/ecmwf3_sst_aug_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Aug sst";;
ens_ecmwf3_sst_sep) file=ECMWFData/S3/monthly/ecmwf3_sst_sep_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Sep sst";;
ens_ecmwf3_sst_oct) file=ECMWFData/S3/monthly/ecmwf3_sst_oct_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Oct sst";;
ens_ecmwf3_sst_nov) file=ECMWFData/S3/monthly/ecmwf3_sst_nov_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Nov sst";;
ens_ecmwf3_sst_dec) file=ECMWFData/S3/monthly/ecmwf3_sst_dec_m%%.ctl;kindname="ensemble ECMWF-3";climfield="1Dec sst";;

cfs_t2m_1) file=CFSData/Monthly/tmp2m.ensm.1.cfs.ctl;kindname="CFS";climfield="+0 tmp2m";;
cfs_t2m_2) file=CFSData/Monthly/tmp2m.ensm.2.cfs.ctl;kindname="CFS";climfield="+1 tmp2m";;
cfs_t2m_3) file=CFSData/Monthly/tmp2m.ensm.3.cfs.ctl;kindname="CFS";climfield="+2 tmp2m";;
cfs_t2m_4) file=CFSData/Monthly/tmp2m.ensm.4.cfs.ctl;kindname="CFS";climfield="+3 tmp2m";;
cfs_t2m_5) file=CFSData/Monthly/tmp2m.ensm.5.cfs.ctl;kindname="CFS";climfield="+4 tmp2m";;
cfs_t2m_6) file=CFSData/Monthly/tmp2m.ensm.6.cfs.ctl;kindname="CFS";climfield="+5 tmp2m";;
cfs_t2m_jan) file="CFSData/Monthly/tmp2m.ensm.jan.cfs.ctl";kindname="CFS";climfield="1Jan tmp2m";;
cfs_t2m_feb) file=CFSData/Monthly/tmp2m.ensm.feb.cfs.ctl;kindname="CFS";climfield="1Feb tmp2m";;
cfs_t2m_mar) file=CFSData/Monthly/tmp2m.ensm.mar.cfs.ctl;kindname="CFS";climfield="1Mar tmp2m";;
cfs_t2m_apr) file=CFSData/Monthly/tmp2m.ensm.apr.cfs.ctl;kindname="CFS";climfield="1Apr tmp2m";;
cfs_t2m_may) file=CFSData/Monthly/tmp2m.ensm.may.cfs.ctl;kindname="CFS";climfield="1May tmp2m";;
cfs_t2m_jun) file=CFSData/Monthly/tmp2m.ensm.jun.cfs.ctl;kindname="CFS";climfield="1Jun tmp2m";;
cfs_t2m_jul) file=CFSData/Monthly/tmp2m.ensm.jul.cfs.ctl;kindname="CFS";climfield="1Jul tmp2m";;
cfs_t2m_aug) file=CFSData/Monthly/tmp2m.ensm.aug.cfs.ctl;kindname="CFS";climfield="1Aug tmp2m";;
cfs_t2m_sep) file=CFSData/Monthly/tmp2m.ensm.sep.cfs.ctl;kindname="CFS";climfield="1Sep tmp2m";;
cfs_t2m_oct) file=CFSData/Monthly/tmp2m.ensm.oct.cfs.ctl;kindname="CFS";climfield="1Oct tmp2m";;
cfs_t2m_nov) file=CFSData/Monthly/tmp2m.ensm.nov.cfs.ctl;kindname="CFS";climfield="1Nov tmp2m";;
cfs_t2m_dec) file=CFSData/Monthly/tmp2m.ensm.dec.cfs.ctl;kindname="CFS";climfield="1Dec tmp2m";;

ens_cfs_t2m_1) file=CFSData/Monthly/tmp2m.m%%.1.cfs.ctl;kindname="ensemble CFS";climfield="+0 tmp2m";;
ens_cfs_t2m_2) file=CFSData/Monthly/tmp2m.m%%.2.cfs.ctl;kindname="ensemble CFS";climfield="+1 tmp2m";;
ens_cfs_t2m_3) file=CFSData/Monthly/tmp2m.m%%.3.cfs.ctl;kindname=ensemble CFS";climfield="+2 tmp2m";;
ens_cfs_t2m_4) file=CFSData/Monthly/tmp2m.m%%.4.cfs.ctl;kindname="ensemble CFS";climfield="+3 tmp2m";;
ens_cfs_t2m_5) file=CFSData/Monthly/tmp2m.m%%.5.cfs.ctl;kindname=ensemble CFS";climfield="+4 tmp2m";;
ens_cfs_t2m_6) file=CFSData/Monthly/tmp2m.m%%.6.cfs.ctl;kindname="ensemble CFS";climfield="+5 tmp2m";;
ens_cfs_t2m_jan) file=CFSData/Monthly/tmp2m.m%%.jan.cfs.ctl;kindname="ensemble CFS";climfield="1Jan tmp2m";;
ens_cfs_t2m_feb) file=CFSData/Monthly/tmp2m.m%%.feb.cfs.ctl;kindname="ensemble CFS";climfield="1Feb tmp2m";;
ens_cfs_t2m_mar) file=CFSData/Monthly/tmp2m.m%%.mar.cfs.ctl;kindname="ensemble CFS";climfield="1Mar tmp2m";;
ens_cfs_t2m_apr) file=CFSData/Monthly/tmp2m.m%%.apr.cfs.ctl;kindname="ensemble CFS";climfield="1Apr tmp2m";;
ens_cfs_t2m_may) file=CFSData/Monthly/tmp2m.m%%.may.cfs.ctl;kindname="ensemble CFS";climfield="1May tmp2m";;
ens_cfs_t2m_jun) file=CFSData/Monthly/tmp2m.m%%.jun.cfs.ctl;kindname="ensemble CFS";climfield="1Jun tmp2m";;
ens_cfs_t2m_jul) file=CFSData/Monthly/tmp2m.m%%.jul.cfs.ctl;kindname="ensemble CFS";climfield="1Jul tmp2m";;
ens_cfs_t2m_aug) file=CFSData/Monthly/tmp2m.m%%.aug.cfs.ctl;kindname="ensemble CFS";climfield="1Aug tmp2m";;
ens_cfs_t2m_sep) file=CFSData/Monthly/tmp2m.m%%.sep.cfs.ctl;kindname="ensemble CFS";climfield="1Sep tmp2m";;
ens_cfs_t2m_oct) file=CFSData/Monthly/tmp2m.m%%.oct.cfs.ctl;kindname="ensemble CFS";climfield="1Oct tmp2m";;
ens_cfs_t2m_nov) file=CFSData/Monthly/tmp2m.m%%.nov.cfs.ctl;kindname="ensemble CFS";climfield="1Nov tmp2m";;
ens_cfs_t2m_dec) file=CFSData/Monthly/tmp2m.m%%.dec.cfs.ctl;kindname="ensemble CFS";climfield="1Dec tmp2m";;

cfs_t2x_1) file=CFSData/Monthly/tmax.ensm.1.cfs.ctl;kindname="CFS";climfield="+0 Tmax";;
cfs_t2x_2) file=CFSData/Monthly/tmax.ensm.2.cfs.ctl;kindname="CFS";climfield="+1 Tmax";;
cfs_t2x_3) file=CFSData/Monthly/tmax.ensm.3.cfs.ctl;kindname="CFS";climfield="+2 Tmax";;
cfs_t2x_4) file=CFSData/Monthly/tmax.ensm.4.cfs.ctl;kindname="CFS";climfield="+3 Tmax";;
cfs_t2x_5) file=CFSData/Monthly/tmax.ensm.5.cfs.ctl;kindname="CFS";climfield="+4 Tmax";;
cfs_t2x_6) file=CFSData/Monthly/tmax.ensm.6.cfs.ctl;kindname="CFS";climfield="+5 Tmax";;
cfs_t2x_jan) file=CFSData/Monthly/tmax.ensm.jan.cfs.ctl;kindname="CFS";climfield="1Jan Tmax";;
cfs_t2x_feb) file=CFSData/Monthly/tmax.ensm.feb.cfs.ctl;kindname="CFS";climfield="1Feb Tmax";;
cfs_t2x_mar) file=CFSData/Monthly/tmax.ensm.mar.cfs.ctl;kindname="CFS";climfield="1Mar Tmax";;
cfs_t2x_apr) file=CFSData/Monthly/tmax.ensm.apr.cfs.ctl;kindname="CFS";climfield="1Apr Tmax";;
cfs_t2x_may) file=CFSData/Monthly/tmax.ensm.may.cfs.ctl;kindname="CFS";climfield="1May Tmax";;
cfs_t2x_jun) file=CFSData/Monthly/tmax.ensm.jun.cfs.ctl;kindname="CFS";climfield="1Jun Tmax";;
cfs_t2x_jul) file=CFSData/Monthly/tmax.ensm.jul.cfs.ctl;kindname="CFS";climfield="1Jul Tmax";;
cfs_t2x_aug) file=CFSData/Monthly/tmax.ensm.aug.cfs.ctl;kindname="CFS";climfield="1Aug Tmax";;
cfs_t2x_sep) file=CFSData/Monthly/tmax.ensm.sep.cfs.ctl;kindname="CFS";climfield="1Sep Tmax";;
cfs_t2x_oct) file=CFSData/Monthly/tmax.ensm.oct.cfs.ctl;kindname="CFS";climfield="1Oct Tmax";;
cfs_t2x_nov) file=CFSData/Monthly/tmax.ensm.nov.cfs.ctl;kindname="CFS";climfield="1Nov Tmax";;
cfs_t2x_dec) file=CFSData/Monthly/tmax.ensm.dec.cfs.ctl;kindname="CFS";climfield="1Dec Tmax";;

ens_cfs_t2x_1) file=CFSData/Monthly/tmax.m%%.1.cfs.ctl;kindname="CFS";climfield="+0 Tmax";;
ens_cfs_t2x_2) file=CFSData/Monthly/tmax.m%%.2.cfs.ctl;kindname="CFS";climfield="+1 Tmax";;
ens_cfs_t2x_3) file=CFSData/Monthly/tmax.m%%.3.cfs.ctl;kindname="CFS";climfield="+2 Tmax";;
ens_cfs_t2x_4) file=CFSData/Monthly/tmax.m%%.4.cfs.ctl;kindname="CFS";climfield="+3 Tmax";;
ens_cfs_t2x_5) file=CFSData/Monthly/tmax.m%%.5.cfs.ctl;kindname="CFS";climfield="+4 Tmax";;
ens_cfs_t2x_6) file=CFSData/Monthly/tmax.m%%.6.cfs.ctl;kindname="CFS";climfield="+5 Tmax";;
ens_cfs_t2x_jan) file=CFSData/Monthly/tmax.m%%.jan.cfs.ctl;kindname="CFS";climfield="1Jan Tmax";;
ens_cfs_t2x_feb) file=CFSData/Monthly/tmax.m%%.feb.cfs.ctl;kindname="CFS";climfield="1Feb Tmax";;
ens_cfs_t2x_mar) file=CFSData/Monthly/tmax.m%%.mar.cfs.ctl;kindname="CFS";climfield="1Mar Tmax";;
ens_cfs_t2x_apr) file=CFSData/Monthly/tmax.m%%.apr.cfs.ctl;kindname="CFS";climfield="1Apr Tmax";;
ens_cfs_t2x_may) file=CFSData/Monthly/tmax.m%%.may.cfs.ctl;kindname="CFS";climfield="1May Tmax";;
ens_cfs_t2x_jun) file=CFSData/Monthly/tmax.m%%.jun.cfs.ctl;kindname="CFS";climfield="1Jun Tmax";;
ens_cfs_t2x_jul) file=CFSData/Monthly/tmax.m%%.jul.cfs.ctl;kindname="CFS";climfield="1Jul Tmax";;
ens_cfs_t2x_aug) file=CFSData/Monthly/tmax.m%%.aug.cfs.ctl;kindname="CFS";climfield="1Aug Tmax";;
ens_cfs_t2x_sep) file=CFSData/Monthly/tmax.m%%.sep.cfs.ctl;kindname="CFS";climfield="1Sep Tmax";;
ens_cfs_t2x_oct) file=CFSData/Monthly/tmax.m%%.oct.cfs.ctl;kindname="CFS";climfield="1Oct Tmax";;
ens_cfs_t2x_nov) file=CFSData/Monthly/tmax.m%%.nov.cfs.ctl;kindname="CFS";climfield="1Nov Tmax";;
ens_cfs_t2x_dec) file=CFSData/Monthly/tmax.m%%.dec.cfs.ctl;kindname="CFS";climfield="1Dec Tmax";;

cfs_t2n_1) file=CFSData/Monthly/tmin.ensm.1.cfs.ctl;kindname="CFS";climfield="+0 T2min";;
cfs_t2n_2) file=CFSData/Monthly/tmin.ensm.2.cfs.ctl;kindname="CFS";climfield="+1 T2min";;
cfs_t2n_3) file=CFSData/Monthly/tmin.ensm.3.cfs.ctl;kindname="CFS";climfield="+2 T2min";;
cfs_t2n_4) file=CFSData/Monthly/tmin.ensm.4.cfs.ctl;kindname="CFS";climfield="+3 T2min";;
cfs_t2n_5) file=CFSData/Monthly/tmin.ensm.5.cfs.ctl;kindname="CFS";climfield="+4 T2min";;
cfs_t2n_6) file=CFSData/Monthly/tmin.ensm.6.cfs.ctl;kindname="CFS";climfield="+5 T2min";;
cfs_t2n_jan) file=CFSData/Monthly/tmin.ensm.jan.cfs.ctl;kindname="CFS";climfield="1Jan T2min";;
cfs_t2n_feb) file=CFSData/Monthly/tmin.ensm.feb.cfs.ctl;kindname="CFS";climfield="1Feb T2min";;
cfs_t2n_mar) file=CFSData/Monthly/tmin.ensm.mar.cfs.ctl;kindname="CFS";climfield="1Mar T2min";;
cfs_t2n_apr) file=CFSData/Monthly/tmin.ensm.apr.cfs.ctl;kindname="CFS";climfield="1Apr T2min";;
cfs_t2n_may) file=CFSData/Monthly/tmin.ensm.may.cfs.ctl;kindname="CFS";climfield="1May T2min";;
cfs_t2n_jun) file=CFSData/Monthly/tmin.ensm.jun.cfs.ctl;kindname="CFS";climfield="1Jun T2min";;
cfs_t2n_jul) file=CFSData/Monthly/tmin.ensm.jul.cfs.ctl;kindname="CFS";climfield="1Jul T2min";;
cfs_t2n_aug) file=CFSData/Monthly/tmin.ensm.aug.cfs.ctl;kindname="CFS";climfield="1Aug T2min";;
cfs_t2n_sep) file=CFSData/Monthly/tmin.ensm.sep.cfs.ctl;kindname="CFS";climfield="1Sep T2min";;
cfs_t2n_oct) file=CFSData/Monthly/tmin.ensm.oct.cfs.ctl;kindname="CFS";climfield="1Oct T2min";;
cfs_t2n_nov) file=CFSData/Monthly/tmin.ensm.nov.cfs.ctl;kindname="CFS";climfield="1Nov T2min";;
cfs_t2n_dec) file=CFSData/Monthly/tmin.ensm.dec.cfs.ctl;kindname="CFS";climfield="1Dec T2min";;

ens_cfs_t2n_1) file=CFSData/Monthly/tmin.m%%.1.cfs.ctl;kindname="CFS";climfield="+0 T2min";;
ens_cfs_t2n_2) file=CFSData/Monthly/tmin.m%%.2.cfs.ctl;kindname="CFS";climfield="+1 T2min";;
ens_cfs_t2n_3) file=CFSData/Monthly/tmin.m%%.3.cfs.ctl;kindname="CFS";climfield="+2 T2min";;
ens_cfs_t2n_4) file=CFSData/Monthly/tmin.m%%.4.cfs.ctl;kindname="CFS";climfield="+3 T2min";;
ens_cfs_t2n_5) file=CFSData/Monthly/tmin.m%%.5.cfs.ctl;kindname="CFS";climfield="+4 T2min";;
ens_cfs_t2n_6) file=CFSData/Monthly/tmin.m%%.6.cfs.ctl;kindname="CFS";climfield="+5 T2min";;
ens_cfs_t2n_jan) file=CFSData/Monthly/tmin.m%%.jan.cfs.ctl;kindname="CFS";climfield="1Jan T2min";;
ens_cfs_t2n_feb) file=CFSData/Monthly/tmin.m%%.feb.cfs.ctl;kindname="CFS";climfield="1Feb T2min";;
ens_cfs_t2n_mar) file=CFSData/Monthly/tmin.m%%.mar.cfs.ctl;kindname="CFS";climfield="1Mar T2min";;
ens_cfs_t2n_apr) file=CFSData/Monthly/tmin.m%%.apr.cfs.ctl;kindname="CFS";climfield="1Apr T2min";;
ens_cfs_t2n_may) file=CFSData/Monthly/tmin.m%%.may.cfs.ctl;kindname="CFS";climfield="1May T2min";;
ens_cfs_t2n_jun) file=CFSData/Monthly/tmin.m%%.jun.cfs.ctl;kindname="CFS";climfield="1Jun T2min";;
ens_cfs_t2n_jul) file=CFSData/Monthly/tmin.m%%.jul.cfs.ctl;kindname="CFS";climfield="1Jul T2min";;
ens_cfs_t2n_aug) file=CFSData/Monthly/tmin.m%%.aug.cfs.ctl;kindname="CFS";climfield="1Aug T2min";;
ens_cfs_t2n_sep) file=CFSData/Monthly/tmin.m%%.sep.cfs.ctl;kindname="CFS";climfield="1Sep T2min";;
ens_cfs_t2n_oct) file=CFSData/Monthly/tmin.m%%.oct.cfs.ctl;kindname="CFS";climfield="1Oct T2min";;
ens_cfs_t2n_nov) file=CFSData/Monthly/tmin.m%%.nov.cfs.ctl;kindname="CFS";climfield="1Nov T2min";;
ens_cfs_t2n_dec) file=CFSData/Monthly/tmin.m%%.dec.cfs.ctl;kindname="CFS";climfield="1Dec T2min";;

cfs_prcp_1) file=CFSData/Monthly/prate.ensm.1.cfs.ctl;kindname="CFS";climfield="+0 precipitation";;
cfs_prcp_2) file=CFSData/Monthly/prate.ensm.2.cfs.ctl;kindname="CFS";climfield="+1 precipitation";;
cfs_prcp_3) file=CFSData/Monthly/prate.ensm.3.cfs.ctl;kindname="CFS";climfield="+2 precipitation";;
cfs_prcp_4) file=CFSData/Monthly/prate.ensm.4.cfs.ctl;kindname="CFS";climfield="+3 precipitation";;
cfs_prcp_5) file=CFSData/Monthly/prate.ensm.5.cfs.ctl;kindname="CFS";climfield="+4 precipitation";;
cfs_prcp_6) file=CFSData/Monthly/prate.ensm.6.cfs.ctl;kindname="CFS";climfield="+5 precipitation";;
cfs_prcp_jan) file=CFSData/Monthly/prate.ensm.jan.cfs.ctl;kindname="CFS";climfield="1Jan precipitation";;
cfs_prcp_feb) file=CFSData/Monthly/prate.ensm.feb.cfs.ctl;kindname="CFS";climfield="1Feb precipitation";;
cfs_prcp_mar) file=CFSData/Monthly/prate.ensm.mar.cfs.ctl;kindname="CFS";climfield="1Mar precipitation";;
cfs_prcp_apr) file=CFSData/Monthly/prate.ensm.apr.cfs.ctl;kindname="CFS";climfield="1Apr precipitation";;
cfs_prcp_may) file=CFSData/Monthly/prate.ensm.may.cfs.ctl;kindname="CFS";climfield="1May precipitation";;
cfs_prcp_jun) file=CFSData/Monthly/prate.ensm.jun.cfs.ctl;kindname="CFS";climfield="1Jun precipitation";;
cfs_prcp_jul) file=CFSData/Monthly/prate.ensm.jul.cfs.ctl;kindname="CFS";climfield="1Jul precipitation";;
cfs_prcp_aug) file=CFSData/Monthly/prate.ensm.aug.cfs.ctl;kindname="CFS";climfield="1Aug precipitation";;
cfs_prcp_sep) file=CFSData/Monthly/prate.ensm.sep.cfs.ctl;kindname="CFS";climfield="1Sep precipitation";;
cfs_prcp_oct) file=CFSData/Monthly/prate.ensm.oct.cfs.ctl;kindname="CFS";climfield="1Oct precipitation";;
cfs_prcp_nov) file=CFSData/Monthly/prate.ensm.nov.cfs.ctl;kindname="CFS";climfield="1Nov precipitation";;
cfs_prcp_dec) file=CFSData/Monthly/prate.ensm.dec.cfs.ctl;kindname="CFS";climfield="1Dec precipitation";;

ens_cfs_prcp_1) file=CFSData/Monthly/prate.m%%.1.cfs.ctl;kindname="CFS";climfield="+0 precipitation";;
ens_cfs_prcp_2) file=CFSData/Monthly/prate.m%%.2.cfs.ctl;kindname="CFS";climfield="+1 precipitation";;
ens_cfs_prcp_3) file=CFSData/Monthly/prate.m%%.3.cfs.ctl;kindname="CFS";climfield="+2 precipitation";;
ens_cfs_prcp_4) file=CFSData/Monthly/prate.m%%.4.cfs.ctl;kindname="CFS";climfield="+3 precipitation";;
ens_cfs_prcp_5) file=CFSData/Monthly/prate.m%%.5.cfs.ctl;kindname="CFS";climfield="+4 precipitation";;
ens_cfs_prcp_6) file=CFSData/Monthly/prate.m%%.6.cfs.ctl;kindname="CFS";climfield="+5 precipitation";;
ens_cfs_prcp_jan) file=CFSData/Monthly/prate.m%%.jan.cfs.ctl;kindname="CFS";climfield="1Jan precipitation";;
ens_cfs_prcp_feb) file=CFSData/Monthly/prate.m%%.feb.cfs.ctl;kindname="CFS";climfield="1Feb precipitation";;
ens_cfs_prcp_mar) file=CFSData/Monthly/prate.m%%.mar.cfs.ctl;kindname="CFS";climfield="1Mar precipitation";;
ens_cfs_prcp_apr) file=CFSData/Monthly/prate.m%%.apr.cfs.ctl;kindname="CFS";climfield="1Apr precipitation";;
ens_cfs_prcp_may) file=CFSData/Monthly/prate.m%%.may.cfs.ctl;kindname="CFS";climfield="1May precipitation";;
ens_cfs_prcp_jun) file=CFSData/Monthly/prate.m%%.jun.cfs.ctl;kindname="CFS";climfield="1Jun precipitation";;
ens_cfs_prcp_jul) file=CFSData/Monthly/prate.m%%.jul.cfs.ctl;kindname="CFS";climfield="1Jul precipitation";;
ens_cfs_prcp_aug) file=CFSData/Monthly/prate.m%%.aug.cfs.ctl;kindname="CFS";climfield="1Aug precipitation";;
ens_cfs_prcp_sep) file=CFSData/Monthly/prate.m%%.sep.cfs.ctl;kindname="CFS";climfield="1Sep precipitation";;
ens_cfs_prcp_oct) file=CFSData/Monthly/prate.m%%.oct.cfs.ctl;kindname="CFS";climfield="1Oct precipitation";;
ens_cfs_prcp_nov) file=CFSData/Monthly/prate.m%%.nov.cfs.ctl;kindname="CFS";climfield="1Nov precipitation";;
ens_cfs_prcp_dec) file=CFSData/Monthly/prate.m%%.dec.cfs.ctl;kindname="CFS";climfield="1Dec precipitation";;

cfs_msl_1) file=CFSData/Monthly/ps.ensm.1.cfs.ctl;kindname="CFS";climfield="+0 SLP";;
cfs_msl_2) file=CFSData/Monthly/ps.ensm.2.cfs.ctl;kindname="CFS";climfield="+1 SLP";;
cfs_msl_3) file=CFSData/Monthly/ps.ensm.3.cfs.ctl;kindname="CFS";climfield="+2 SLP";;
cfs_msl_4) file=CFSData/Monthly/ps.ensm.4.cfs.ctl;kindname="CFS";climfield="+3 SLP";;
cfs_msl_5) file=CFSData/Monthly/ps.ensm.5.cfs.ctl;kindname="CFS";climfield="+4 SLP";;
cfs_msl_6) file=CFSData/Monthly/ps.ensm.6.cfs.ctl;kindname="CFS";climfield="+5 SLP";;
cfs_msl_jan) file=CFSData/Monthly/ps.ensm.jan.cfs.ctl;kindname="CFS";climfield="1Jan SLP";;
cfs_msl_feb) file=CFSData/Monthly/ps.ensm.feb.cfs.ctl;kindname="CFS";climfield="1Feb SLP";;
cfs_msl_mar) file=CFSData/Monthly/ps.ensm.mar.cfs.ctl;kindname="CFS";climfield="1Mar SLP";;
cfs_msl_apr) file=CFSData/Monthly/ps.ensm.apr.cfs.ctl;kindname="CFS";climfield="1Apr SLP";;
cfs_msl_may) file=CFSData/Monthly/ps.ensm.may.cfs.ctl;kindname="CFS";climfield="1May SLP";;
cfs_msl_jun) file=CFSData/Monthly/ps.ensm.jun.cfs.ctl;kindname="CFS";climfield="1Jun SLP";;
cfs_msl_jul) file=CFSData/Monthly/ps.ensm.jul.cfs.ctl;kindname="CFS";climfield="1Jul SLP";;
cfs_msl_aug) file=CFSData/Monthly/ps.ensm.aug.cfs.ctl;kindname="CFS";climfield="1Aug SLP";;
cfs_msl_sep) file=CFSData/Monthly/ps.ensm.sep.cfs.ctl;kindname="CFS";climfield="1Sep SLP";;
cfs_msl_oct) file=CFSData/Monthly/ps.ensm.oct.cfs.ctl;kindname="CFS";climfield="1Oct SLP";;
cfs_msl_nov) file=CFSData/Monthly/ps.ensm.nov.cfs.ctl;kindname="CFS";climfield="1Nov SLP";;
cfs_msl_dec) file=CFSData/Monthly/ps.ensm.dec.cfs.ctl;kindname="CFS";climfield="1Dec SLP";;

ens_cfs_msl_1) file=CFSData/Monthly/ps.m%%.1.cfs.ctl;kindname="CFS";climfield="+0 SLP";;
ens_cfs_msl_2) file=CFSData/Monthly/ps.m%%.2.cfs.ctl;kindname="CFS";climfield="+1 SLP";;
ens_cfs_msl_3) file=CFSData/Monthly/ps.m%%.3.cfs.ctl;kindname="CFS";climfield="+2 SLP";;
ens_cfs_msl_4) file=CFSData/Monthly/ps.m%%.4.cfs.ctl;kindname="CFS";climfield="+3 SLP";;
ens_cfs_msl_5) file=CFSData/Monthly/ps.m%%.5.cfs.ctl;kindname="CFS";climfield="+4 SLP";;
ens_cfs_msl_6) file=CFSData/Monthly/ps.m%%.6.cfs.ctl;kindname="CFS";climfield="+5 SLP";;
ens_cfs_msl_jan) file=CFSData/Monthly/ps.m%%.jan.cfs.ctl;kindname="CFS";climfield="1Jan SLP";;
ens_cfs_msl_feb) file=CFSData/Monthly/ps.m%%.feb.cfs.ctl;kindname="CFS";climfield="1Feb SLP";;
ens_cfs_msl_mar) file=CFSData/Monthly/ps.m%%.mar.cfs.ctl;kindname="CFS";climfield="1Mar SLP";;
ens_cfs_msl_apr) file=CFSData/Monthly/ps.m%%.apr.cfs.ctl;kindname="CFS";climfield="1Apr SLP";;
ens_cfs_msl_may) file=CFSData/Monthly/ps.m%%.may.cfs.ctl;kindname="CFS";climfield="1May SLP";;
ens_cfs_msl_jun) file=CFSData/Monthly/ps.m%%.jun.cfs.ctl;kindname="CFS";climfield="1Jun SLP";;
ens_cfs_msl_jul) file=CFSData/Monthly/ps.m%%.jul.cfs.ctl;kindname="CFS";climfield="1Jul SLP";;
ens_cfs_msl_aug) file=CFSData/Monthly/ps.m%%.aug.cfs.ctl;kindname="CFS";climfield="1Aug SLP";;
ens_cfs_msl_sep) file=CFSData/Monthly/ps.m%%.sep.cfs.ctl;kindname="CFS";climfield="1Sep SLP";;
ens_cfs_msl_oct) file=CFSData/Monthly/ps.m%%.oct.cfs.ctl;kindname="CFS";climfield="1Oct SLP";;
ens_cfs_msl_nov) file=CFSData/Monthly/ps.m%%.nov.cfs.ctl;kindname="CFS";climfield="1Nov SLP";;
ens_cfs_msl_dec) file=CFSData/Monthly/ps.m%%.dec.cfs.ctl;kindname="CFS";climfield="1Dec SLP";;

cfs_z500_1) file=CFSData/Monthly/z500.ensm.1.cfs.ctl;kindname="CFS";climfield="+0 z500";;
cfs_z500_2) file=CFSData/Monthly/z500.ensm.2.cfs.ctl;kindname="CFS";climfield="+1 z500";;
cfs_z500_3) file=CFSData/Monthly/z500.ensm.3.cfs.ctl;kindname="CFS";climfield="+2 z500";;
cfs_z500_4) file=CFSData/Monthly/z500.ensm.4.cfs.ctl;kindname="CFS";climfield="+3 z500";;
cfs_z500_5) file=CFSData/Monthly/z500.ensm.5.cfs.ctl;kindname="CFS";climfield="+4 z500";;
cfs_z500_6) file=CFSData/Monthly/z500.ensm.6.cfs.ctl;kindname="CFS";climfield="+5 z500";;
cfs_z500_jan) file=CFSData/Monthly/z500.ensm.jan.cfs.ctl;kindname="CFS";climfield="1Jan z500";;
cfs_z500_feb) file=CFSData/Monthly/z500.ensm.feb.cfs.ctl;kindname="CFS";climfield="1Feb z500";;
cfs_z500_mar) file=CFSData/Monthly/z500.ensm.mar.cfs.ctl;kindname="CFS";climfield="1Mar z500";;
cfs_z500_apr) file=CFSData/Monthly/z500.ensm.apr.cfs.ctl;kindname="CFS";climfield="1Apr z500";;
cfs_z500_may) file=CFSData/Monthly/z500.ensm.may.cfs.ctl;kindname="CFS";climfield="1May z500";;
cfs_z500_jun) file=CFSData/Monthly/z500.ensm.jun.cfs.ctl;kindname="CFS";climfield="1Jun z500";;
cfs_z500_jul) file=CFSData/Monthly/z500.ensm.jul.cfs.ctl;kindname="CFS";climfield="1Jul z500";;
cfs_z500_aug) file=CFSData/Monthly/z500.ensm.aug.cfs.ctl;kindname="CFS";climfield="1Aug z500";;
cfs_z500_sep) file=CFSData/Monthly/z500.ensm.sep.cfs.ctl;kindname="CFS";climfield="1Sep z500";;
cfs_z500_oct) file=CFSData/Monthly/z500.ensm.oct.cfs.ctl;kindname="CFS";climfield="1Oct z500";;
cfs_z500_nov) file=CFSData/Monthly/z500.ensm.nov.cfs.ctl;kindname="CFS";climfield="1Nov z500";;
cfs_z500_dec) file=CFSData/Monthly/z500.ensm.dec.cfs.ctl;kindname="CFS";climfield="1Dec z500";;

ens_cfs_z500_1) file=CFSData/Monthly/z500.m%%.1.cfs.ctl;kindname="CFS";climfield="+0 z500";;
ens_cfs_z500_2) file=CFSData/Monthly/z500.m%%.2.cfs.ctl;kindname="CFS";climfield="+1 z500";;
ens_cfs_z500_3) file=CFSData/Monthly/z500.m%%.3.cfs.ctl;kindname="CFS";climfield="+2 z500";;
ens_cfs_z500_4) file=CFSData/Monthly/z500.m%%.4.cfs.ctl;kindname="CFS";climfield="+3 z500";;
ens_cfs_z500_5) file=CFSData/Monthly/z500.m%%.5.cfs.ctl;kindname="CFS";climfield="+4 z500";;
ens_cfs_z500_6) file=CFSData/Monthly/z500.m%%.6.cfs.ctl;kindname="CFS";climfield="+5 z500";;
ens_cfs_z500_jan) file=CFSData/Monthly/z500.m%%.jan.cfs.ctl;kindname="CFS";climfield="1Jan z500";;
ens_cfs_z500_feb) file=CFSData/Monthly/z500.m%%.feb.cfs.ctl;kindname="CFS";climfield="1Feb z500";;
ens_cfs_z500_mar) file=CFSData/Monthly/z500.m%%.mar.cfs.ctl;kindname="CFS";climfield="1Mar z500";;
ens_cfs_z500_apr) file=CFSData/Monthly/z500.m%%.apr.cfs.ctl;kindname="CFS";climfield="1Apr z500";;
ens_cfs_z500_may) file=CFSData/Monthly/z500.m%%.may.cfs.ctl;kindname="CFS";climfield="1May z500";;
ens_cfs_z500_jun) file=CFSData/Monthly/z500.m%%.jun.cfs.ctl;kindname="CFS";climfield="1Jun z500";;
ens_cfs_z500_jul) file=CFSData/Monthly/z500.m%%.jul.cfs.ctl;kindname="CFS";climfield="1Jul z500";;
ens_cfs_z500_aug) file=CFSData/Monthly/z500.m%%.aug.cfs.ctl;kindname="CFS";climfield="1Aug z500";;
ens_cfs_z500_sep) file=CFSData/Monthly/z500.m%%.sep.cfs.ctl;kindname="CFS";climfield="1Sep z500";;
ens_cfs_z500_oct) file=CFSData/Monthly/z500.m%%.oct.cfs.ctl;kindname="CFS";climfield="1Oct z500";;
ens_cfs_z500_nov) file=CFSData/Monthly/z500.m%%.nov.cfs.ctl;kindname="CFS";climfield="1Nov z500";;
ens_cfs_z500_dec) file=CFSData/Monthly/z500.m%%.dec.cfs.ctl;kindname="CFS";climfield="1Dec z500";;

cfs_u10_1) file=CFSData/Monthly/ugrd10m.ensm.1.cfs.ctl;kindname="CFS";climfield="+0 u10";;
cfs_u10_2) file=CFSData/Monthly/ugrd10m.ensm.2.cfs.ctl;kindname="CFS";climfield="+1 u10";;
cfs_u10_3) file=CFSData/Monthly/ugrd10m.ensm.3.cfs.ctl;kindname="CFS";climfield="+2 u10";;
cfs_u10_4) file=CFSData/Monthly/ugrd10m.ensm.4.cfs.ctl;kindname="CFS";climfield="+3 u10";;
cfs_u10_5) file=CFSData/Monthly/ugrd10m.ensm.5.cfs.ctl;kindname="CFS";climfield="+4 u10";;
cfs_u10_6) file=CFSData/Monthly/ugrd10m.ensm.6.cfs.ctl;kindname="CFS";climfield="+5 u10";;
cfs_u10_jan) file=CFSData/Monthly/ugrd10m.ensm.jan.cfs.ctl;kindname="CFS";climfield="1Jan u10";;
cfs_u10_feb) file=CFSData/Monthly/ugrd10m.ensm.feb.cfs.ctl;kindname="CFS";climfield="1Feb u10";;
cfs_u10_mar) file=CFSData/Monthly/ugrd10m.ensm.mar.cfs.ctl;kindname="CFS";climfield="1Mar u10";;
cfs_u10_apr) file=CFSData/Monthly/ugrd10m.ensm.apr.cfs.ctl;kindname="CFS";climfield="1Apr u10";;
cfs_u10_may) file=CFSData/Monthly/ugrd10m.ensm.may.cfs.ctl;kindname="CFS";climfield="1May u10";;
cfs_u10_jun) file=CFSData/Monthly/ugrd10m.ensm.jun.cfs.ctl;kindname="CFS";climfield="1Jun u10";;
cfs_u10_jul) file=CFSData/Monthly/ugrd10m.ensm.jul.cfs.ctl;kindname="CFS";climfield="1Jul u10";;
cfs_u10_aug) file=CFSData/Monthly/ugrd10m.ensm.aug.cfs.ctl;kindname="CFS";climfield="1Aug u10";;
cfs_u10_sep) file=CFSData/Monthly/ugrd10m.ensm.sep.cfs.ctl;kindname="CFS";climfield="1Sep u10";;
cfs_u10_oct) file=CFSData/Monthly/ugrd10m.ensm.oct.cfs.ctl;kindname="CFS";climfield="1Oct u10";;
cfs_u10_nov) file=CFSData/Monthly/ugrd10m.ensm.nov.cfs.ctl;kindname="CFS";climfield="1Nov u10";;
cfs_u10_dec) file=CFSData/Monthly/ugrd10m.ensm.dec.cfs.ctl;kindname="CFS";climfield="1Dec u10";;

ens_cfs_u10_1) file=CFSData/Monthly/ugrd10m.m%%.1.cfs.ctl;kindname="CFS";climfield="+0 u10";;
ens_cfs_u10_2) file=CFSData/Monthly/ugrd10m.m%%.2.cfs.ctl;kindname="CFS";climfield="+1 u10";;
ens_cfs_u10_3) file=CFSData/Monthly/ugrd10m.m%%.3.cfs.ctl;kindname="CFS";climfield="+2 u10";;
ens_cfs_u10_4) file=CFSData/Monthly/ugrd10m.m%%.4.cfs.ctl;kindname="CFS";climfield="+3 u10";;
ens_cfs_u10_5) file=CFSData/Monthly/ugrd10m.m%%.5.cfs.ctl;kindname="CFS";climfield="+4 u10";;
ens_cfs_u10_6) file=CFSData/Monthly/ugrd10m.m%%.6.cfs.ctl;kindname="CFS";climfield="+5 u10";;
ens_cfs_u10_jan) file=CFSData/Monthly/ugrd10m.m%%.jan.cfs.ctl;kindname="CFS";climfield="1Jan u10";;
ens_cfs_u10_feb) file=CFSData/Monthly/ugrd10m.m%%.feb.cfs.ctl;kindname="CFS";climfield="1Feb u10";;
ens_cfs_u10_mar) file=CFSData/Monthly/ugrd10m.m%%.mar.cfs.ctl;kindname="CFS";climfield="1Mar u10";;
ens_cfs_u10_apr) file=CFSData/Monthly/ugrd10m.m%%.apr.cfs.ctl;kindname="CFS";climfield="1Apr u10";;
ens_cfs_u10_may) file=CFSData/Monthly/ugrd10m.m%%.may.cfs.ctl;kindname="CFS";climfield="1May u10";;
ens_cfs_u10_jun) file=CFSData/Monthly/ugrd10m.m%%.jun.cfs.ctl;kindname="CFS";climfield="1Jun u10";;
ens_cfs_u10_jul) file=CFSData/Monthly/ugrd10m.m%%.jul.cfs.ctl;kindname="CFS";climfield="1Jul u10";;
ens_cfs_u10_aug) file=CFSData/Monthly/ugrd10m.m%%.aug.cfs.ctl;kindname="CFS";climfield="1Aug u10";;
ens_cfs_u10_sep) file=CFSData/Monthly/ugrd10m.m%%.sep.cfs.ctl;kindname="CFS";climfield="1Sep u10";;
ens_cfs_u10_oct) file=CFSData/Monthly/ugrd10m.m%%.oct.cfs.ctl;kindname="CFS";climfield="1Oct u10";;
ens_cfs_u10_nov) file=CFSData/Monthly/ugrd10m.m%%.nov.cfs.ctl;kindname="CFS";climfield="1Nov u10";;
ens_cfs_u10_dec) file=CFSData/Monthly/ugrd10m.m%%.dec.cfs.ctl;kindname="CFS";climfield="1Dec u10";;

cfs_v10_1) file=CFSData/Monthly/vgrd10m.ensm.1.cfs.ctl;kindname="CFS";climfield="+0 v10";;
cfs_v10_2) file=CFSData/Monthly/vgrd10m.ensm.2.cfs.ctl;kindname="CFS";climfield="+1 v10";;
cfs_v10_3) file=CFSData/Monthly/vgrd10m.ensm.3.cfs.ctl;kindname="CFS";climfield="+2 v10";;
cfs_v10_4) file=CFSData/Monthly/vgrd10m.ensm.4.cfs.ctl;kindname="CFS";climfield="+3 v10";;
cfs_v10_5) file=CFSData/Monthly/vgrd10m.ensm.5.cfs.ctl;kindname="CFS";climfield="+4 v10";;
cfs_v10_6) file=CFSData/Monthly/vgrd10m.ensm.6.cfs.ctl;kindname="CFS";climfield="+5 v10";;
cfs_v10_jan) file=CFSData/Monthly/vgrd10m.ensm.jan.cfs.ctl;kindname="CFS";climfield="1Jan v10";;
cfs_v10_feb) file=CFSData/Monthly/vgrd10m.ensm.feb.cfs.ctl;kindname="CFS";climfield="1Feb v10";;
cfs_v10_mar) file=CFSData/Monthly/vgrd10m.ensm.mar.cfs.ctl;kindname="CFS";climfield="1Mar v10";;
cfs_v10_apr) file=CFSData/Monthly/vgrd10m.ensm.apr.cfs.ctl;kindname="CFS";climfield="1Apr v10";;
cfs_v10_may) file=CFSData/Monthly/vgrd10m.ensm.may.cfs.ctl;kindname="CFS";climfield="1May v10";;
cfs_v10_jun) file=CFSData/Monthly/vgrd10m.ensm.jun.cfs.ctl;kindname="CFS";climfield="1Jun v10";;
cfs_v10_jul) file=CFSData/Monthly/vgrd10m.ensm.jul.cfs.ctl;kindname="CFS";climfield="1Jul v10";;
cfs_v10_aug) file=CFSData/Monthly/vgrd10m.ensm.aug.cfs.ctl;kindname="CFS";climfield="1Aug v10";;
cfs_v10_sep) file=CFSData/Monthly/vgrd10m.ensm.sep.cfs.ctl;kindname="CFS";climfield="1Sep v10";;
cfs_v10_oct) file=CFSData/Monthly/vgrd10m.ensm.oct.cfs.ctl;kindname="CFS";climfield="1Oct v10";;
cfs_v10_nov) file=CFSData/Monthly/vgrd10m.ensm.nov.cfs.ctl;kindname="CFS";climfield="1Nov v10";;
cfs_v10_dec) file=CFSData/Monthly/vgrd10m.ensm.dec.cfs.ctl;kindname="CFS";climfield="1Dec v10";;

ens_cfs_v10_1) file=CFSData/Monthly/vgrd10m.m%%.1.cfs.ctl;kindname="CFS";climfield="+0 v10";;
ens_cfs_v10_2) file=CFSData/Monthly/vgrd10m.m%%.2.cfs.ctl;kindname="CFS";climfield="+1 v10";;
ens_cfs_v10_3) file=CFSData/Monthly/vgrd10m.m%%.3.cfs.ctl;kindname="CFS";climfield="+2 v10";;
ens_cfs_v10_4) file=CFSData/Monthly/vgrd10m.m%%.4.cfs.ctl;kindname="CFS";climfield="+3 v10";;
ens_cfs_v10_5) file=CFSData/Monthly/vgrd10m.m%%.5.cfs.ctl;kindname="CFS";climfield="+4 v10";;
ens_cfs_v10_6) file=CFSData/Monthly/vgrd10m.m%%.6.cfs.ctl;kindname="CFS";climfield="+5 v10";;
ens_cfs_v10_jan) file=CFSData/Monthly/vgrd10m.m%%.jan.cfs.ctl;kindname="CFS";climfield="1Jan v10";;
ens_cfs_v10_feb) file=CFSData/Monthly/vgrd10m.m%%.feb.cfs.ctl;kindname="CFS";climfield="1Feb v10";;
ens_cfs_v10_mar) file=CFSData/Monthly/vgrd10m.m%%.mar.cfs.ctl;kindname="CFS";climfield="1Mar v10";;
ens_cfs_v10_apr) file=CFSData/Monthly/vgrd10m.m%%.apr.cfs.ctl;kindname="CFS";climfield="1Apr v10";;
ens_cfs_v10_may) file=CFSData/Monthly/vgrd10m.m%%.may.cfs.ctl;kindname="CFS";climfield="1May v10";;
ens_cfs_v10_jun) file=CFSData/Monthly/vgrd10m.m%%.jun.cfs.ctl;kindname="CFS";climfield="1Jun v10";;
ens_cfs_v10_jul) file=CFSData/Monthly/vgrd10m.m%%.jul.cfs.ctl;kindname="CFS";climfield="1Jul v10";;
ens_cfs_v10_aug) file=CFSData/Monthly/vgrd10m.m%%.aug.cfs.ctl;kindname="CFS";climfield="1Aug v10";;
ens_cfs_v10_sep) file=CFSData/Monthly/vgrd10m.m%%.sep.cfs.ctl;kindname="CFS";climfield="1Sep v10";;
ens_cfs_v10_oct) file=CFSData/Monthly/vgrd10m.m%%.oct.cfs.ctl;kindname="CFS";climfield="1Oct v10";;
ens_cfs_v10_nov) file=CFSData/Monthly/vgrd10m.m%%.nov.cfs.ctl;kindname="CFS";climfield="1Nov v10";;
ens_cfs_v10_dec) file=CFSData/Monthly/vgrd10m.m%%.dec.cfs.ctl;kindname="CFS";climfield="1Dec v10";;

cfs_ssd_1) file=CFSData/Monthly/dswsfc.ensm.1.cfs.ctl;kindname="CFS";climfield="+0 downward solar radiation";;
cfs_ssd_2) file=CFSData/Monthly/dswsfc.ensm.2.cfs.ctl;kindname="CFS";climfield="+1 downward solar radiation";;
cfs_ssd_3) file=CFSData/Monthly/dswsfc.ensm.3.cfs.ctl;kindname="CFS";climfield="+2 downward solar radiation";;
cfs_ssd_4) file=CFSData/Monthly/dswsfc.ensm.4.cfs.ctl;kindname="CFS";climfield="+3 downward solar radiation";;
cfs_ssd_5) file=CFSData/Monthly/dswsfc.ensm.5.cfs.ctl;kindname="CFS";climfield="+4 downward solar radiation";;
cfs_ssd_6) file=CFSData/Monthly/dswsfc.ensm.6.cfs.ctl;kindname="CFS";climfield="+5 downward solar radiation";;
cfs_ssd_jan) file=CFSData/Monthly/dswsfc.ensm.jan.cfs.ctl;kindname="CFS";climfield="1Jan downward solar radiation";;
cfs_ssd_feb) file=CFSData/Monthly/dswsfc.ensm.feb.cfs.ctl;kindname="CFS";climfield="1Feb downward solar radiation";;
cfs_ssd_mar) file=CFSData/Monthly/dswsfc.ensm.mar.cfs.ctl;kindname="CFS";climfield="1Mar downward solar radiation";;
cfs_ssd_apr) file=CFSData/Monthly/dswsfc.ensm.apr.cfs.ctl;kindname="CFS";climfield="1Apr downward solar radiation";;
cfs_ssd_may) file=CFSData/Monthly/dswsfc.ensm.may.cfs.ctl;kindname="CFS";climfield="1May downward solar radiation";;
cfs_ssd_jun) file=CFSData/Monthly/dswsfc.ensm.jun.cfs.ctl;kindname="CFS";climfield="1Jun downward solar radiation";;
cfs_ssd_jul) file=CFSData/Monthly/dswsfc.ensm.jul.cfs.ctl;kindname="CFS";climfield="1Jul downward solar radiation";;
cfs_ssd_aug) file=CFSData/Monthly/dswsfc.ensm.aug.cfs.ctl;kindname="CFS";climfield="1Aug downward solar radiation";;
cfs_ssd_sep) file=CFSData/Monthly/dswsfc.ensm.sep.cfs.ctl;kindname="CFS";climfield="1Sep downward solar radiation";;
cfs_ssd_oct) file=CFSData/Monthly/dswsfc.ensm.oct.cfs.ctl;kindname="CFS";climfield="1Oct downward solar radiation";;
cfs_ssd_nov) file=CFSData/Monthly/dswsfc.ensm.nov.cfs.ctl;kindname="CFS";climfield="1Nov downward solar radiation";;
cfs_ssd_dec) file=CFSData/Monthly/dswsfc.ensm.dec.cfs.ctl;kindname="CFS";climfield="1Dec downward solar radiation";;

ens_cfs_ssd_1) file=CFSData/Monthly/dswsfc.m%%.1.cfs.ctl;kindname="CFS";climfield="+0 downward solar radiation";;
ens_cfs_ssd_2) file=CFSData/Monthly/dswsfc.m%%.2.cfs.ctl;kindname="CFS";climfield="+1 downward solar radiation";;
ens_cfs_ssd_3) file=CFSData/Monthly/dswsfc.m%%.3.cfs.ctl;kindname="CFS";climfield="+2 downward solar radiation";;
ens_cfs_ssd_4) file=CFSData/Monthly/dswsfc.m%%.4.cfs.ctl;kindname="CFS";climfield="+3 downward solar radiation";;
ens_cfs_ssd_5) file=CFSData/Monthly/dswsfc.m%%.5.cfs.ctl;kindname="CFS";climfield="+4 downward solar radiation";;
ens_cfs_ssd_6) file=CFSData/Monthly/dswsfc.m%%.6.cfs.ctl;kindname="CFS";climfield="+5 downward solar radiation";;
ens_cfs_ssd_jan) file=CFSData/Monthly/dswsfc.m%%.jan.cfs.ctl;kindname="CFS";climfield="1Jan downward solar radiation";;
ens_cfs_ssd_feb) file=CFSData/Monthly/dswsfc.m%%.feb.cfs.ctl;kindname="CFS";climfield="1Feb downward solar radiation";;
ens_cfs_ssd_mar) file=CFSData/Monthly/dswsfc.m%%.mar.cfs.ctl;kindname="CFS";climfield="1Mar downward solar radiation";;
ens_cfs_ssd_apr) file=CFSData/Monthly/dswsfc.m%%.apr.cfs.ctl;kindname="CFS";climfield="1Apr downward solar radiation";;
ens_cfs_ssd_may) file=CFSData/Monthly/dswsfc.m%%.may.cfs.ctl;kindname="CFS";climfield="1May downward solar radiation";;
ens_cfs_ssd_jun) file=CFSData/Monthly/dswsfc.m%%.jun.cfs.ctl;kindname="CFS";climfield="1Jun downward solar radiation";;
ens_cfs_ssd_jul) file=CFSData/Monthly/dswsfc.m%%.jul.cfs.ctl;kindname="CFS";climfield="1Jul downward solar radiation";;
ens_cfs_ssd_aug) file=CFSData/Monthly/dswsfc.m%%.aug.cfs.ctl;kindname="CFS";climfield="1Aug downward solar radiation";;
ens_cfs_ssd_sep) file=CFSData/Monthly/dswsfc.m%%.sep.cfs.ctl;kindname="CFS";climfield="1Sep downward solar radiation";;
ens_cfs_ssd_oct) file=CFSData/Monthly/dswsfc.m%%.oct.cfs.ctl;kindname="CFS";climfield="1Oct downward solar radiation";;
ens_cfs_ssd_nov) file=CFSData/Monthly/dswsfc.m%%.nov.cfs.ctl;kindname="CFS";climfield="1Nov downward solar radiation";;
ens_cfs_ssd_dec) file=CFSData/Monthly/dswsfc.m%%.dec.cfs.ctl;kindname="CFS";climfield="1Dec downward solar radiation";;

cfs_snd_1) file=CFSData/Monthly/weasd.ensm.1.cfs.ctl;kindname="CFS";climfield="+0 snow depth";;
cfs_snd_2) file=CFSData/Monthly/weasd.ensm.2.cfs.ctl;kindname="CFS";climfield="+1 snow depth";;
cfs_snd_3) file=CFSData/Monthly/weasd.ensm.3.cfs.ctl;kindname="CFS";climfield="+2 snow depth";;
cfs_snd_4) file=CFSData/Monthly/weasd.ensm.4.cfs.ctl;kindname="CFS";climfield="+3 snow depth";;
cfs_snd_5) file=CFSData/Monthly/weasd.ensm.5.cfs.ctl;kindname="CFS";climfield="+4 snow depth";;
cfs_snd_6) file=CFSData/Monthly/weasd.ensm.6.cfs.ctl;kindname="CFS";climfield="+5 snow depth";;
cfs_snd_jan) file=CFSData/Monthly/weasd.ensm.jan.cfs.ctl;kindname="CFS";climfield="1Jan snow depth";;
cfs_snd_feb) file=CFSData/Monthly/weasd.ensm.feb.cfs.ctl;kindname="CFS";climfield="1Feb snow depth";;
cfs_snd_mar) file=CFSData/Monthly/weasd.ensm.mar.cfs.ctl;kindname="CFS";climfield="1Mar snow depth";;
cfs_snd_apr) file=CFSData/Monthly/weasd.ensm.apr.cfs.ctl;kindname="CFS";climfield="1Apr snow depth";;
cfs_snd_may) file=CFSData/Monthly/weasd.ensm.may.cfs.ctl;kindname="CFS";climfield="1May snow depth";;
cfs_snd_jun) file=CFSData/Monthly/weasd.ensm.jun.cfs.ctl;kindname="CFS";climfield="1Jun snow depth";;
cfs_snd_jul) file=CFSData/Monthly/weasd.ensm.jul.cfs.ctl;kindname="CFS";climfield="1Jul snow depth";;
cfs_snd_aug) file=CFSData/Monthly/weasd.ensm.aug.cfs.ctl;kindname="CFS";climfield="1Aug snow depth";;
cfs_snd_sep) file=CFSData/Monthly/weasd.ensm.sep.cfs.ctl;kindname="CFS";climfield="1Sep snow depth";;
cfs_snd_oct) file=CFSData/Monthly/weasd.ensm.oct.cfs.ctl;kindname="CFS";climfield="1Oct snow depth";;
cfs_snd_nov) file=CFSData/Monthly/weasd.ensm.nov.cfs.ctl;kindname="CFS";climfield="1Nov snow depth";;
cfs_snd_dec) file=CFSData/Monthly/weasd.ensm.dec.cfs.ctl;kindname="CFS";climfield="1Dec snow depth";;

ens_cfs_snd_1) file=CFSData/Monthly/weasd.m%%.1.cfs.ctl;kindname="CFS";climfield="+0 snow depth";;
ens_cfs_snd_2) file=CFSData/Monthly/weasd.m%%.2.cfs.ctl;kindname="CFS";climfield="+1 snow depth";;
ens_cfs_snd_3) file=CFSData/Monthly/weasd.m%%.3.cfs.ctl;kindname="CFS";climfield="+2 snow depth";;
ens_cfs_snd_4) file=CFSData/Monthly/weasd.m%%.4.cfs.ctl;kindname="CFS";climfield="+3 snow depth";;
ens_cfs_snd_5) file=CFSData/Monthly/weasd.m%%.5.cfs.ctl;kindname="CFS";climfield="+4 snow depth";;
ens_cfs_snd_6) file=CFSData/Monthly/weasd.m%%.6.cfs.ctl;kindname="CFS";climfield="+5 snow depth";;
ens_cfs_snd_jan) file=CFSData/Monthly/weasd.m%%.jan.cfs.ctl;kindname="CFS";climfield="1Jan snow depth";;
ens_cfs_snd_feb) file=CFSData/Monthly/weasd.m%%.feb.cfs.ctl;kindname="CFS";climfield="1Feb snow depth";;
ens_cfs_snd_mar) file=CFSData/Monthly/weasd.m%%.mar.cfs.ctl;kindname="CFS";climfield="1Mar snow depth";;
ens_cfs_snd_apr) file=CFSData/Monthly/weasd.m%%.apr.cfs.ctl;kindname="CFS";climfield="1Apr snow depth";;
ens_cfs_snd_may) file=CFSData/Monthly/weasd.m%%.may.cfs.ctl;kindname="CFS";climfield="1May snow depth";;
ens_cfs_snd_jun) file=CFSData/Monthly/weasd.m%%.jun.cfs.ctl;kindname="CFS";climfield="1Jun snow depth";;
ens_cfs_snd_jul) file=CFSData/Monthly/weasd.m%%.jul.cfs.ctl;kindname="CFS";climfield="1Jul snow depth";;
ens_cfs_snd_aug) file=CFSData/Monthly/weasd.m%%.aug.cfs.ctl;kindname="CFS";climfield="1Aug snow depth";;
ens_cfs_snd_sep) file=CFSData/Monthly/weasd.m%%.sep.cfs.ctl;kindname="CFS";climfield="1Sep snow depth";;
ens_cfs_snd_oct) file=CFSData/Monthly/weasd.m%%.oct.cfs.ctl;kindname="CFS";climfield="1Oct snow depth";;
ens_cfs_snd_nov) file=CFSData/Monthly/weasd.m%%.nov.cfs.ctl;kindname="CFS";climfield="1Nov snow depth";;
ens_cfs_snd_dec) file=CFSData/Monthly/weasd.m%%.dec.cfs.ctl;kindname="CFS";climfield="1Dec snow depth";;

cfs_tsfc_1) file=CFSData/Monthly/tmpsfc.ensm.1.cfs.ctl;kindname="CFS";climfield="+0 Tsfc";;
cfs_tsfc_2) file=CFSData/Monthly/tmpsfc.ensm.2.cfs.ctl;kindname="CFS";climfield="+1 Tsfc";;
cfs_tsfc_3) file=CFSData/Monthly/tmpsfc.ensm.3.cfs.ctl;kindname="CFS";climfield="+2 Tsfc";;
cfs_tsfc_4) file=CFSData/Monthly/tmpsfc.ensm.4.cfs.ctl;kindname="CFS";climfield="+3 Tsfc";;
cfs_tsfc_5) file=CFSData/Monthly/tmpsfc.ensm.5.cfs.ctl;kindname="CFS";climfield="+4 Tsfc";;
cfs_tsfc_6) file=CFSData/Monthly/tmpsfc.ensm.6.cfs.ctl;kindname="CFS";climfield="+5 Tsfc";;
cfs_tsfc_jan) file=CFSData/Monthly/tmpsfc.ensm.jan.cfs.ctl;kindname="CFS";climfield="1Jan Tsfc";;
cfs_tsfc_feb) file=CFSData/Monthly/tmpsfc.ensm.feb.cfs.ctl;kindname="CFS";climfield="1Feb Tsfc";;
cfs_tsfc_mar) file=CFSData/Monthly/tmpsfc.ensm.mar.cfs.ctl;kindname="CFS";climfield="1Mar Tsfc";;
cfs_tsfc_apr) file=CFSData/Monthly/tmpsfc.ensm.apr.cfs.ctl;kindname="CFS";climfield="1Apr Tsfc";;
cfs_tsfc_may) file=CFSData/Monthly/tmpsfc.ensm.may.cfs.ctl;kindname="CFS";climfield="1May Tsfc";;
cfs_tsfc_jun) file=CFSData/Monthly/tmpsfc.ensm.jun.cfs.ctl;kindname="CFS";climfield="1Jun Tsfc";;
cfs_tsfc_jul) file=CFSData/Monthly/tmpsfc.ensm.jul.cfs.ctl;kindname="CFS";climfield="1Jul Tsfc";;
cfs_tsfc_aug) file=CFSData/Monthly/tmpsfc.ensm.aug.cfs.ctl;kindname="CFS";climfield="1Aug Tsfc";;
cfs_tsfc_sep) file=CFSData/Monthly/tmpsfc.ensm.sep.cfs.ctl;kindname="CFS";climfield="1Sep Tsfc";;
cfs_tsfc_oct) file=CFSData/Monthly/tmpsfc.ensm.oct.cfs.ctl;kindname="CFS";climfield="1Oct Tsfc";;
cfs_tsfc_nov) file=CFSData/Monthly/tmpsfc.ensm.nov.cfs.ctl;kindname="CFS";climfield="1Nov Tsfc";;
cfs_tsfc_dec) file=CFSData/Monthly/tmpsfc.ensm.dec.cfs.ctl;kindname="CFS";climfield="1Dec Tsfc";;

ens_cfs_tsfc_1) file=CFSData/Monthly/tmpsfc.m%%.1.cfs.ctl;kindname="CFS";climfield="+0 Tsfc";;
ens_cfs_tsfc_2) file=CFSData/Monthly/tmpsfc.m%%.2.cfs.ctl;kindname="CFS";climfield="+1 Tsfc";;
ens_cfs_tsfc_3) file=CFSData/Monthly/tmpsfc.m%%.3.cfs.ctl;kindname="CFS";climfield="+2 Tsfc";;
ens_cfs_tsfc_4) file=CFSData/Monthly/tmpsfc.m%%.4.cfs.ctl;kindname="CFS";climfield="+3 Tsfc";;
ens_cfs_tsfc_5) file=CFSData/Monthly/tmpsfc.m%%.5.cfs.ctl;kindname="CFS";climfield="+4 Tsfc";;
ens_cfs_tsfc_6) file=CFSData/Monthly/tmpsfc.m%%.6.cfs.ctl;kindname="CFS";climfield="+5 Tsfc";;
ens_cfs_tsfc_jan) file=CFSData/Monthly/tmpsfc.m%%.jan.cfs.ctl;kindname="CFS";climfield="1Jan Tsfc";;
ens_cfs_tsfc_feb) file=CFSData/Monthly/tmpsfc.m%%.feb.cfs.ctl;kindname="CFS";climfield="1Feb Tsfc";;
ens_cfs_tsfc_mar) file=CFSData/Monthly/tmpsfc.m%%.mar.cfs.ctl;kindname="CFS";climfield="1Mar Tsfc";;
ens_cfs_tsfc_apr) file=CFSData/Monthly/tmpsfc.m%%.apr.cfs.ctl;kindname="CFS";climfield="1Apr Tsfc";;
ens_cfs_tsfc_may) file=CFSData/Monthly/tmpsfc.m%%.may.cfs.ctl;kindname="CFS";climfield="1May Tsfc";;
ens_cfs_tsfc_jun) file=CFSData/Monthly/tmpsfc.m%%.jun.cfs.ctl;kindname="CFS";climfield="1Jun Tsfc";;
ens_cfs_tsfc_jul) file=CFSData/Monthly/tmpsfc.m%%.jul.cfs.ctl;kindname="CFS";climfield="1Jul Tsfc";;
ens_cfs_tsfc_aug) file=CFSData/Monthly/tmpsfc.m%%.aug.cfs.ctl;kindname="CFS";climfield="1Aug Tsfc";;
ens_cfs_tsfc_sep) file=CFSData/Monthly/tmpsfc.m%%.sep.cfs.ctl;kindname="CFS";climfield="1Sep Tsfc";;
ens_cfs_tsfc_oct) file=CFSData/Monthly/tmpsfc.m%%.oct.cfs.ctl;kindname="CFS";climfield="1Oct Tsfc";;
ens_cfs_tsfc_nov) file=CFSData/Monthly/tmpsfc.m%%.nov.cfs.ctl;kindname="CFS";climfield="1Nov Tsfc";;
ens_cfs_tsfc_dec) file=CFSData/Monthly/tmpsfc.m%%.dec.cfs.ctl;kindname="CFS";climfield="1Dec Tsfc";;

echam4.5_t2m_1) file=ECHAM/monthly/echam5_tmp2m_1_ensm.ctl;kindname="ECHAM4.5";climfield="+0 T2m";;
echam4.5_t2m_2) file=ECHAM/monthly/echam5_tmp2m_2_ensm.ctl;kindname="ECHAM4.5";climfield="+1 T2m";;
echam4.5_t2m_3) file=ECHAM/monthly/echam5_tmp2m_3_ensm.ctl;kindname="ECHAM4.5";climfield="+2 T2m";;
echam4.5_t2m_4) file=ECHAM/monthly/echam5_tmp2m_4_ensm.ctl;kindname="ECHAM4.5";climfield="+3 T2m";;
echam4.5_t2m_5) file=ECHAM/monthly/echam5_tmp2m_5_ensm.ctl;kindname="ECHAM4.5";climfield="+4 T2m";;
echam4.5_t2m_6) file=ECHAM/monthly/echam5_tmp2m_6_ensm.ctl;kindname="ECHAM4.5";climfield="+5 T2m";;
echam4.5_t2m_jan) file=ECHAM/monthly/echam5_tmp2m_jan_ensm.ctl;kindname="ECHAM4.5";climfield="1Jan T2m";;
echam4.5_t2m_feb) file=ECHAM/monthly/echam5_tmp2m_feb_ensm.ctl;kindname="ECHAM4.5";climfield="1Feb T2m";;
echam4.5_t2m_mar) file=ECHAM/monthly/echam5_tmp2m_mar_ensm.ctl;kindname="ECHAM4.5";climfield="1Mar T2m";;
echam4.5_t2m_apr) file=ECHAM/monthly/echam5_tmp2m_apr_ensm.ctl;kindname="ECHAM4.5";climfield="1Apr T2m";;
echam4.5_t2m_may) file=ECHAM/monthly/echam5_tmp2m_may_ensm.ctl;kindname="ECHAM4.5";climfield="1May T2m";;
echam4.5_t2m_jun) file=ECHAM/monthly/echam5_tmp2m_jun_ensm.ctl;kindname="ECHAM4.5";climfield="1Jun T2m";;
echam4.5_t2m_jul) file=ECHAM/monthly/echam5_tmp2m_jul_ensm.ctl;kindname="ECHAM4.5";climfield="1Jul T2m";;
echam4.5_t2m_aug) file=ECHAM/monthly/echam5_tmp2m_aug_ensm.ctl;kindname="ECHAM4.5";climfield="1Aug T2m";;
echam4.5_t2m_sep) file=ECHAM/monthly/echam5_tmp2m_sep_ensm.ctl;kindname="ECHAM4.5";climfield="1Sep T2m";;
echam4.5_t2m_oct) file=ECHAM/monthly/echam5_tmp2m_oct_ensm.ctl;kindname="ECHAM4.5";climfield="1Oct T2m";;
echam4.5_t2m_nov) file=ECHAM/monthly/echam5_tmp2m_nov_ensm.ctl;kindname="ECHAM4.5";climfield="1Nov T2m";;
echam4.5_t2m_dec) file=ECHAM/monthly/echam5_tmp2m_dec_ensm.ctl;kindname="ECHAM4.5";climfield="1Dec T2m";;

ens_echam4.5_t2m_1) file=ECHAM/monthly/echam5_tmp2m_1_m%%.ctl;kindname="ensemble ECHAM4.5";climfield="+0 T2m";;
ens_echam4.5_t2m_2) file=ECHAM/monthly/echam5_tmp2m_2_m%%.ctl;kindname="ensemble ECHAM4.5";climfield="+1 T2m";;
ens_echam4.5_t2m_3) file=ECHAM/monthly/echam5_tmp2m_3_m%%.ctl;kindname="ensemble ECHAM4.5";climfield="+2 T2m";;
ens_echam4.5_t2m_4) file=ECHAM/monthly/echam5_tmp2m_4_m%%.ctl;kindname="ensemble ECHAM4.5";climfield="+3 T2m";;
ens_echam4.5_t2m_5) file=ECHAM/monthly/echam5_tmp2m_5_m%%.ctl;kindname="ensemble ECHAM4.5";climfield="+4 T2m";;
ens_echam4.5_t2m_6) file=ECHAM/monthly/echam5_tmp2m_6_m%%.ctl;kindname="ensemble ECHAM4.5";climfield="+5 T2m";;
ens_echam4.5_t2m_jan) file=ECHAM/monthly/echam5_tmp2m_jan_m%%.ctl;kindname="ensemble ECHAM4.5";climfield="1Jan T2m";;
ens_echam4.5_t2m_feb) file=ECHAM/monthly/echam5_tmp2m_feb_m%%.ctl;kindname="ensemble ECHAM4.5";climfield="1Feb T2m";;
ens_echam4.5_t2m_mar) file=ECHAM/monthly/echam5_tmp2m_mar_m%%.ctl;kindname="ensemble ECHAM4.5";climfield="1Mar T2m";;
ens_echam4.5_t2m_apr) file=ECHAM/monthly/echam5_tmp2m_apr_m%%.ctl;kindname="ensemble ECHAM4.5";climfield="1Apr T2m";;
ens_echam4.5_t2m_may) file=ECHAM/monthly/echam5_tmp2m_may_m%%.ctl;kindname="ensemble ECHAM4.5";climfield="1May T2m";;
ens_echam4.5_t2m_jun) file=ECHAM/monthly/echam5_tmp2m_jun_m%%.ctl;kindname="ensemble ECHAM4.5";climfield="1Jun T2m";;
ens_echam4.5_t2m_jul) file=ECHAM/monthly/echam5_tmp2m_jul_m%%.ctl;kindname="ensemble ECHAM4.5";climfield="1Jul T2m";;
ens_echam4.5_t2m_aug) file=ECHAM/monthly/echam5_tmp2m_aug_m%%.ctl;kindname="ensemble ECHAM4.5";climfield="1Aug T2m";;
ens_echam4.5_t2m_sep) file=ECHAM/monthly/echam5_tmp2m_sep_m%%.ctl;kindname="ensemble ECHAM4.5";climfield="1Sep T2m";;
ens_echam4.5_t2m_oct) file=ECHAM/monthly/echam5_tmp2m_oct_m%%.ctl;kindname="ensemble ECHAM4.5";climfield="1Oct T2m";;
ens_echam4.5_t2m_nov) file=ECHAM/monthly/echam5_tmp2m_nov_m%%.ctl;kindname="ensemble ECHAM4.5";climfield="1Nov T2m";;
ens_echam4.5_t2m_dec) file=ECHAM/monthly/echam5_tmp2m_dec_m%%.ctl;kindname="ensemble ECHAM4.5";climfield="1Dec T2m";;

echam4.5_tsfc_1) file=ECHAM/monthly/echam5_stemp_1_ensm.ctl;kindname="ECHAM4.5";climfield="+0 Tsfc";;
echam4.5_tsfc_2) file=ECHAM/monthly/echam5_stemp_2_ensm.ctl;kindname="ECHAM4.5";climfield="+1 Tsfc";;
echam4.5_tsfc_3) file=ECHAM/monthly/echam5_stemp_3_ensm.ctl;kindname="ECHAM4.5";climfield="+2 Tsfc";;
echam4.5_tsfc_4) file=ECHAM/monthly/echam5_stemp_4_ensm.ctl;kindname="ECHAM4.5";climfield="+3 Tsfc";;
echam4.5_tsfc_5) file=ECHAM/monthly/echam5_stemp_5_ensm.ctl;kindname="ECHAM4.5";climfield="+4 Tsfc";;
echam4.5_tsfc_6) file=ECHAM/monthly/echam5_stemp_6_ensm.ctl;kindname="ECHAM4.5";climfield="+5 Tsfc";;
echam4.5_tsfc_jan) file=ECHAM/monthly/echam5_stemp_jan_ensm.ctl;kindname="ECHAM4.5";climfield="1Jan Tsfc";;
echam4.5_tsfc_feb) file=ECHAM/monthly/echam5_stemp_feb_ensm.ctl;kindname="ECHAM4.5";climfield="1Feb Tsfc";;
echam4.5_tsfc_mar) file=ECHAM/monthly/echam5_stemp_mar_ensm.ctl;kindname="ECHAM4.5";climfield="1Mar Tsfc";;
echam4.5_tsfc_apr) file=ECHAM/monthly/echam5_stemp_apr_ensm.ctl;kindname="ECHAM4.5";climfield="1Apr Tsfc";;
echam4.5_tsfc_may) file=ECHAM/monthly/echam5_stemp_may_ensm.ctl;kindname="ECHAM4.5";climfield="1May Tsfc";;
echam4.5_tsfc_jun) file=ECHAM/monthly/echam5_stemp_jun_ensm.ctl;kindname="ECHAM4.5";climfield="1Jun Tsfc";;
echam4.5_tsfc_jul) file=ECHAM/monthly/echam5_stemp_jul_ensm.ctl;kindname="ECHAM4.5";climfield="1Jul Tsfc";;
echam4.5_tsfc_aug) file=ECHAM/monthly/echam5_stemp_aug_ensm.ctl;kindname="ECHAM4.5";climfield="1Aug Tsfc";;
echam4.5_tsfc_sep) file=ECHAM/monthly/echam5_stemp_sep_ensm.ctl;kindname="ECHAM4.5";climfield="1Sep Tsfc";;
echam4.5_tsfc_oct) file=ECHAM/monthly/echam5_stemp_oct_ensm.ctl;kindname="ECHAM4.5";climfield="1Oct Tsfc";;
echam4.5_tsfc_nov) file=ECHAM/monthly/echam5_stemp_nov_ensm.ctl;kindname="ECHAM4.5";climfield="1Nov Tsfc";;
echam4.5_tsfc_dec) file=ECHAM/monthly/echam5_stemp_dec_ensm.ctl;kindname="ECHAM4.5";climfield="1Dec Tsfc";;

ens_echam4.5_tsfc_1) file=ECHAM/monthly/echam5_stemp_1_m%%.ctl;kindname="ensemble ECHAM4.5";climfield="+0 Tsfc";;
ens_echam4.5_tsfc_2) file=ECHAM/monthly/echam5_stemp_2_m%%.ctl;kindname="ensemble ECHAM4.5";climfield="+1 Tsfc";;
ens_echam4.5_tsfc_3) file=ECHAM/monthly/echam5_stemp_3_m%%.ctl;kindname="ensemble ECHAM4.5";climfield="+2 Tsfc";;
ens_echam4.5_tsfc_4) file=ECHAM/monthly/echam5_stemp_4_m%%.ctl;kindname="ensemble ECHAM4.5";climfield="+3 Tsfc";;
ens_echam4.5_tsfc_5) file=ECHAM/monthly/echam5_stemp_5_m%%.ctl;kindname="ensemble ECHAM4.5";climfield="+4 Tsfc";;
ens_echam4.5_tsfc_6) file=ECHAM/monthly/echam5_stemp_6_m%%.ctl;kindname="ensemble ECHAM4.5";climfield="+5 Tsfc";;
ens_echam4.5_tsfc_jan) file=ECHAM/monthly/echam5_stemp_jan_m%%.ctl;kindname="ensemble ECHAM4.5";climfield="1Jan Tsfc";;
ens_echam4.5_tsfc_feb) file=ECHAM/monthly/echam5_stemp_feb_m%%.ctl;kindname="ensemble ECHAM4.5";climfield="1Feb Tsfc";;
ens_echam4.5_tsfc_mar) file=ECHAM/monthly/echam5_stemp_mar_m%%.ctl;kindname="ensemble ECHAM4.5";climfield="1Mar Tsfc";;
ens_echam4.5_tsfc_apr) file=ECHAM/monthly/echam5_stemp_apr_m%%.ctl;kindname="ensemble ECHAM4.5";climfield="1Apr Tsfc";;
ens_echam4.5_tsfc_may) file=ECHAM/monthly/echam5_stemp_may_m%%.ctl;kindname="ensemble ECHAM4.5";climfield="1May Tsfc";;
ens_echam4.5_tsfc_jun) file=ECHAM/monthly/echam5_stemp_jun_m%%.ctl;kindname="ensemble ECHAM4.5";climfield="1Jun Tsfc";;
ens_echam4.5_tsfc_jul) file=ECHAM/monthly/echam5_stemp_jul_m%%.ctl;kindname="ensemble ECHAM4.5";climfield="1Jul Tsfc";;
ens_echam4.5_tsfc_aug) file=ECHAM/monthly/echam5_stemp_aug_m%%.ctl;kindname="ensemble ECHAM4.5";climfield="1Aug Tsfc";;
ens_echam4.5_tsfc_sep) file=ECHAM/monthly/echam5_stemp_sep_m%%.ctl;kindname="ensemble ECHAM4.5";climfield="1Sep Tsfc";;
ens_echam4.5_tsfc_oct) file=ECHAM/monthly/echam5_stemp_oct_m%%.ctl;kindname="ensemble ECHAM4.5";climfield="1Oct Tsfc";;
ens_echam4.5_tsfc_nov) file=ECHAM/monthly/echam5_stemp_nov_m%%.ctl;kindname="ensemble ECHAM4.5";climfield="1Nov Tsfc";;
ens_echam4.5_tsfc_dec) file=ECHAM/monthly/echam5_stemp_dec_m%%.ctl;kindname="ensemble ECHAM4.5";climfield="1Dec Tsfc";;

echam4.5_prcp_1) file=ECHAM/monthly/echam5_prcp_1_ensm.ctl;kindname="ECHAM4.5";climfield="+0 Prcp";;
echam4.5_prcp_2) file=ECHAM/monthly/echam5_prcp_2_ensm.ctl;kindname="ECHAM4.5";climfield="+1 Prcp";;
echam4.5_prcp_3) file=ECHAM/monthly/echam5_prcp_3_ensm.ctl;kindname="ECHAM4.5";climfield="+2 Prcp";;
echam4.5_prcp_4) file=ECHAM/monthly/echam5_prcp_4_ensm.ctl;kindname="ECHAM4.5";climfield="+3 Prcp";;
echam4.5_prcp_5) file=ECHAM/monthly/echam5_prcp_5_ensm.ctl;kindname="ECHAM4.5";climfield="+4 Prcp";;
echam4.5_prcp_6) file=ECHAM/monthly/echam5_prcp_6_ensm.ctl;kindname="ECHAM4.5";climfield="+5 Prcp";;
echam4.5_prcp_jan) file=ECHAM/monthly/echam5_prcp_jan_ensm.ctl;kindname="ECHAM4.5";climfield="1Jan Prcp";;
echam4.5_prcp_feb) file=ECHAM/monthly/echam5_prcp_feb_ensm.ctl;kindname="ECHAM4.5";climfield="1Feb Prcp";;
echam4.5_prcp_mar) file=ECHAM/monthly/echam5_prcp_mar_ensm.ctl;kindname="ECHAM4.5";climfield="1Mar Prcp";;
echam4.5_prcp_apr) file=ECHAM/monthly/echam5_prcp_apr_ensm.ctl;kindname="ECHAM4.5";climfield="1Apr Prcp";;
echam4.5_prcp_may) file=ECHAM/monthly/echam5_prcp_may_ensm.ctl;kindname="ECHAM4.5";climfield="1May Prcp";;
echam4.5_prcp_jun) file=ECHAM/monthly/echam5_prcp_jun_ensm.ctl;kindname="ECHAM4.5";climfield="1Jun Prcp";;
echam4.5_prcp_jul) file=ECHAM/monthly/echam5_prcp_jul_ensm.ctl;kindname="ECHAM4.5";climfield="1Jul Prcp";;
echam4.5_prcp_aug) file=ECHAM/monthly/echam5_prcp_aug_ensm.ctl;kindname="ECHAM4.5";climfield="1Aug Prcp";;
echam4.5_prcp_sep) file=ECHAM/monthly/echam5_prcp_sep_ensm.ctl;kindname="ECHAM4.5";climfield="1Sep Prcp";;
echam4.5_prcp_oct) file=ECHAM/monthly/echam5_prcp_oct_ensm.ctl;kindname="ECHAM4.5";climfield="1Oct Prcp";;
echam4.5_prcp_nov) file=ECHAM/monthly/echam5_prcp_nov_ensm.ctl;kindname="ECHAM4.5";climfield="1Nov Prcp";;
echam4.5_prcp_dec) file=ECHAM/monthly/echam5_prcp_dec_ensm.ctl;kindname="ECHAM4.5";climfield="1Dec Prcp";;

ens_echam4.5_prcp_1) file=ECHAM/monthly/echam5_prcp_1_m%%.ctl;kindname="ensemble ECHAM4.5";climfield="+0 Prcp";;
ens_echam4.5_prcp_2) file=ECHAM/monthly/echam5_prcp_2_m%%.ctl;kindname="ensemble ECHAM4.5";climfield="+1 Prcp";;
ens_echam4.5_prcp_3) file=ECHAM/monthly/echam5_prcp_3_m%%.ctl;kindname="ensemble ECHAM4.5";climfield="+2 Prcp";;
ens_echam4.5_prcp_4) file=ECHAM/monthly/echam5_prcp_4_m%%.ctl;kindname="ensemble ECHAM4.5";climfield="+3 Prcp";;
ens_echam4.5_prcp_5) file=ECHAM/monthly/echam5_prcp_5_m%%.ctl;kindname="ensemble ECHAM4.5";climfield="+4 Prcp";;
ens_echam4.5_prcp_6) file=ECHAM/monthly/echam5_prcp_6_m%%.ctl;kindname="ensemble ECHAM4.5";climfield="+5 Prcp";;
ens_echam4.5_prcp_jan) file=ECHAM/monthly/echam5_prcp_jan_m%%.ctl;kindname="ensemble ECHAM4.5";climfield="1Jan Prcp";;
ens_echam4.5_prcp_feb) file=ECHAM/monthly/echam5_prcp_feb_m%%.ctl;kindname="ensemble ECHAM4.5";climfield="1Feb Prcp";;
ens_echam4.5_prcp_mar) file=ECHAM/monthly/echam5_prcp_mar_m%%.ctl;kindname="ensemble ECHAM4.5";climfield="1Mar Prcp";;
ens_echam4.5_prcp_apr) file=ECHAM/monthly/echam5_prcp_apr_m%%.ctl;kindname="ensemble ECHAM4.5";climfield="1Apr Prcp";;
ens_echam4.5_prcp_may) file=ECHAM/monthly/echam5_prcp_may_m%%.ctl;kindname="ensemble ECHAM4.5";climfield="1May Prcp";;
ens_echam4.5_prcp_jun) file=ECHAM/monthly/echam5_prcp_jun_m%%.ctl;kindname="ensemble ECHAM4.5";climfield="1Jun Prcp";;
ens_echam4.5_prcp_jul) file=ECHAM/monthly/echam5_prcp_jul_m%%.ctl;kindname="ensemble ECHAM4.5";climfield="1Jul Prcp";;
ens_echam4.5_prcp_aug) file=ECHAM/monthly/echam5_prcp_aug_m%%.ctl;kindname="ensemble ECHAM4.5";climfield="1Aug Prcp";;
ens_echam4.5_prcp_sep) file=ECHAM/monthly/echam5_prcp_sep_m%%.ctl;kindname="ensemble ECHAM4.5";climfield="1Sep Prcp";;
ens_echam4.5_prcp_oct) file=ECHAM/monthly/echam5_prcp_oct_m%%.ctl;kindname="ensemble ECHAM4.5";climfield="1Oct Prcp";;
ens_echam4.5_prcp_nov) file=ECHAM/monthly/echam5_prcp_nov_m%%.ctl;kindname="ensemble ECHAM4.5";climfield="1Nov Prcp";;
ens_echam4.5_prcp_dec) file=ECHAM/monthly/echam5_prcp_dec_m%%.ctl;kindname="ensemble ECHAM4.5";climfield="1Dec Prcp";;

echam4.5_z500_1) file=ECHAM/monthly/echam5_z500_1_ensm.ctl;kindname="ECHAM4.5";climfield="+0 Z500";;
echam4.5_z500_2) file=ECHAM/monthly/echam5_z500_2_ensm.ctl;kindname="ECHAM4.5";climfield="+1 Z500";;
echam4.5_z500_3) file=ECHAM/monthly/echam5_z500_3_ensm.ctl;kindname="ECHAM4.5";climfield="+2 Z500";;
echam4.5_z500_4) file=ECHAM/monthly/echam5_z500_4_ensm.ctl;kindname="ECHAM4.5";climfield="+3 Z500";;
echam4.5_z500_5) file=ECHAM/monthly/echam5_z500_5_ensm.ctl;kindname="ECHAM4.5";climfield="+4 Z500";;
echam4.5_z500_6) file=ECHAM/monthly/echam5_z500_6_ensm.ctl;kindname="ECHAM4.5";climfield="+5 Z500";;
echam4.5_z500_jan) file=ECHAM/monthly/echam5_z500_jan_ensm.ctl;kindname="ECHAM4.5";climfield="1Jan Z500";;
echam4.5_z500_feb) file=ECHAM/monthly/echam5_z500_feb_ensm.ctl;kindname="ECHAM4.5";climfield="1Feb Z500";;
echam4.5_z500_mar) file=ECHAM/monthly/echam5_z500_mar_ensm.ctl;kindname="ECHAM4.5";climfield="1Mar Z500";;
echam4.5_z500_apr) file=ECHAM/monthly/echam5_z500_apr_ensm.ctl;kindname="ECHAM4.5";climfield="1Apr Z500";;
echam4.5_z500_may) file=ECHAM/monthly/echam5_z500_may_ensm.ctl;kindname="ECHAM4.5";climfield="1May Z500";;
echam4.5_z500_jun) file=ECHAM/monthly/echam5_z500_jun_ensm.ctl;kindname="ECHAM4.5";climfield="1Jun Z500";;
echam4.5_z500_jul) file=ECHAM/monthly/echam5_z500_jul_ensm.ctl;kindname="ECHAM4.5";climfield="1Jul Z500";;
echam4.5_z500_aug) file=ECHAM/monthly/echam5_z500_aug_ensm.ctl;kindname="ECHAM4.5";climfield="1Aug Z500";;
echam4.5_z500_sep) file=ECHAM/monthly/echam5_z500_sep_ensm.ctl;kindname="ECHAM4.5";climfield="1Sep Z500";;
echam4.5_z500_oct) file=ECHAM/monthly/echam5_z500_oct_ensm.ctl;kindname="ECHAM4.5";climfield="1Oct Z500";;
echam4.5_z500_nov) file=ECHAM/monthly/echam5_z500_nov_ensm.ctl;kindname="ECHAM4.5";climfield="1Nov Z500";;
echam4.5_z500_dec) file=ECHAM/monthly/echam5_z500_dec_ensm.ctl;kindname="ECHAM4.5";climfield="1Dec Z500";;

ens_echam4.5_z500_1) file=ECHAM/monthly/echam5_z500_1_m%%.ctl;kindname="ensemble ECHAM4.5";climfield="+0 Z500";;
ens_echam4.5_z500_2) file=ECHAM/monthly/echam5_z500_2_m%%.ctl;kindname="ensemble ECHAM4.5";climfield="+1 Z500";;
ens_echam4.5_z500_3) file=ECHAM/monthly/echam5_z500_3_m%%.ctl;kindname="ensemble ECHAM4.5";climfield="+2 Z500";;
ens_echam4.5_z500_4) file=ECHAM/monthly/echam5_z500_4_m%%.ctl;kindname="ensemble ECHAM4.5";climfield="+3 Z500";;
ens_echam4.5_z500_5) file=ECHAM/monthly/echam5_z500_5_m%%.ctl;kindname="ensemble ECHAM4.5";climfield="+4 Z500";;
ens_echam4.5_z500_6) file=ECHAM/monthly/echam5_z500_6_m%%.ctl;kindname="ensemble ECHAM4.5";climfield="+5 Z500";;
ens_echam4.5_z500_jan) file=ECHAM/monthly/echam5_z500_jan_m%%.ctl;kindname="ensemble ECHAM4.5";climfield="1Jan Z500";;
ens_echam4.5_z500_feb) file=ECHAM/monthly/echam5_z500_feb_m%%.ctl;kindname="ensemble ECHAM4.5";climfield="1Feb Z500";;
ens_echam4.5_z500_mar) file=ECHAM/monthly/echam5_z500_mar_m%%.ctl;kindname="ensemble ECHAM4.5";climfield="1Mar Z500";;
ens_echam4.5_z500_apr) file=ECHAM/monthly/echam5_z500_apr_m%%.ctl;kindname="ensemble ECHAM4.5";climfield="1Apr Z500";;
ens_echam4.5_z500_may) file=ECHAM/monthly/echam5_z500_may_m%%.ctl;kindname="ensemble ECHAM4.5";climfield="1May Z500";;
ens_echam4.5_z500_jun) file=ECHAM/monthly/echam5_z500_jun_m%%.ctl;kindname="ensemble ECHAM4.5";climfield="1Jun Z500";;
ens_echam4.5_z500_jul) file=ECHAM/monthly/echam5_z500_jul_m%%.ctl;kindname="ensemble ECHAM4.5";climfield="1Jul Z500";;
ens_echam4.5_z500_aug) file=ECHAM/monthly/echam5_z500_aug_m%%.ctl;kindname="ensemble ECHAM4.5";climfield="1Aug Z500";;
ens_echam4.5_z500_sep) file=ECHAM/monthly/echam5_z500_sep_m%%.ctl;kindname="ensemble ECHAM4.5";climfield="1Sep Z500";;
ens_echam4.5_z500_oct) file=ECHAM/monthly/echam5_z500_oct_m%%.ctl;kindname="ensemble ECHAM4.5";climfield="1Oct Z500";;
ens_echam4.5_z500_nov) file=ECHAM/monthly/echam5_z500_nov_m%%.ctl;kindname="ensemble ECHAM4.5";climfield="1Nov Z500";;
ens_echam4.5_z500_dec) file=ECHAM/monthly/echam5_z500_dec_m%%.ctl;kindname="ensemble ECHAM4.5";climfield="1Dec Z500";;

ukmo_t2m_1) file=UKMO/monthly/ukmo_t2m_1.ctl;kindname="UKMO";climfield="+0 T1.5m";;
ukmo_t2m_2) file=UKMO/monthly/ukmo_t2m_2.ctl;kindname="UKMO";climfield="+1 T1.5m";;
ukmo_t2m_3) file=UKMO/monthly/ukmo_t2m_3.ctl;kindname="UKMO";climfield="+2 T1.5m";;
ukmo_t2m_4) file=UKMO/monthly/ukmo_t2m_4.ctl;kindname="UKMO";climfield="+3 T1.5m";;
ukmo_t2m_5) file=UKMO/monthly/ukmo_t2m_5.ctl;kindname="UKMO";climfield="+4 T1.5m";;
ukmo_t2m_6) file=UKMO/monthly/ukmo_t2m_6.ctl;kindname="UKMO";climfield="+5 T1.5m";;
ukmo_t2m_jan) file=UKMO/monthly/ukmo_t2m_jan.ensm.ctl;kindname="UKMO";climfield="1Jan T1.5m";;
ukmo_t2m_feb) file=UKMO/monthly/ukmo_t2m_feb.ensm.ctl;kindname="UKMO";climfield="1Feb T1.5m";;
ukmo_t2m_mar) file=UKMO/monthly/ukmo_t2m_mar.ensm.ctl;kindname="UKMO";climfield="1Mar T1.5m";;
ukmo_t2m_apr) file=UKMO/monthly/ukmo_t2m_apr.ensm.ctl;kindname="UKMO";climfield="1Apr T1.5m";;
ukmo_t2m_may) file=UKMO/monthly/ukmo_t2m_may.ensm.ctl;kindname="UKMO";climfield="1May T1.5m";;
ukmo_t2m_jun) file=UKMO/monthly/ukmo_t2m_jun.ensm.ctl;kindname="UKMO";climfield="1Jun T1.5m";;
ukmo_t2m_jul) file=UKMO/monthly/ukmo_t2m_jul.ensm.ctl;kindname="UKMO";climfield="1Jul T1.5m";;
ukmo_t2m_aug) file=UKMO/monthly/ukmo_t2m_aug.ensm.ctl;kindname="UKMO";climfield="1Aug T1.5m";;
ukmo_t2m_sep) file=UKMO/monthly/ukmo_t2m_sep.ensm.ctl;kindname="UKMO";climfield="1Sep T1.5m";;
ukmo_t2m_oct) file=UKMO/monthly/ukmo_t2m_oct.ensm.ctl;kindname="UKMO";climfield="1Oct T1.5m";;
ukmo_t2m_nov) file=UKMO/monthly/ukmo_t2m_nov.ensm.ctl;kindname="UKMO";climfield="1Nov T1.5m";;
ukmo_t2m_dec) file=UKMO/monthly/ukmo_t2m_dec.ensm.ctl;kindname="UKMO";climfield="1Dec T1.5m";;

ens_ukmo_t2m_1) file=UKMO/monthly/ukmo_t2m_1_m%%.ctl;kindname="ensemble UKMO";climfield="+0 T1.5m";;
ens_ukmo_t2m_2) file=UKMO/monthly/ukmo_t2m_2_m%%.ctl;kindname="ensemble UKMO";climfield="+1 T1.5m";;
ens_ukmo_t2m_3) file=UKMO/monthly/ukmo_t2m_3_m%%.ctl;kindname="ensemble UKMO";climfield="+2 T1.5m";;
ens_ukmo_t2m_4) file=UKMO/monthly/ukmo_t2m_4_m%%.ctl;kindname="ensemble UKMO";climfield="+3 T1.5m";;
ens_ukmo_t2m_5) file=UKMO/monthly/ukmo_t2m_5_m%%.ctl;kindname="ensemble UKMO";climfield="+4 T1.5m";;
ens_ukmo_t2m_6) file=UKMO/monthly/ukmo_t2m_6_m%%.ctl;kindname="ensemble UKMO";climfield="+5 T1.5m";;
ens_ukmo_t2m_jan) file=UKMO/monthly/ukmo_t2m_jan_m%%.ctl;kindname="ensemble UKMO";climfield="1Jan T1.5m";;
ens_ukmo_t2m_feb) file=UKMO/monthly/ukmo_t2m_feb_m%%.ctl;kindname="ensemble UKMO";climfield="1Feb T1.5m";;
ens_ukmo_t2m_mar) file=UKMO/monthly/ukmo_t2m_mar_m%%.ctl;kindname="ensemble UKMO";climfield="1Mar T1.5m";;
ens_ukmo_t2m_apr) file=UKMO/monthly/ukmo_t2m_apr_m%%.ctl;kindname="ensemble UKMO";climfield="1Apr T1.5m";;
ens_ukmo_t2m_may) file=UKMO/monthly/ukmo_t2m_may_m%%.ctl;kindname="ensemble UKMO";climfield="1May T1.5m";;
ens_ukmo_t2m_jun) file=UKMO/monthly/ukmo_t2m_jun_m%%.ctl;kindname="ensemble UKMO";climfield="1Jun T1.5m";;
ens_ukmo_t2m_jul) file=UKMO/monthly/ukmo_t2m_jul_m%%.ctl;kindname="ensemble UKMO";climfield="1Jul T1.5m";;
ens_ukmo_t2m_aug) file=UKMO/monthly/ukmo_t2m_aug_m%%.ctl;kindname="ensemble UKMO";climfield="1Aug T1.5m";;
ens_ukmo_t2m_sep) file=UKMO/monthly/ukmo_t2m_sep_m%%.ctl;kindname="ensemble UKMO";climfield="1Sep T1.5m";;
ens_ukmo_t2m_oct) file=UKMO/monthly/ukmo_t2m_oct_m%%.ctl;kindname="ensemble UKMO";climfield="1Oct T1.5m";;
ens_ukmo_t2m_nov) file=UKMO/monthly/ukmo_t2m_nov_m%%.ctl;kindname="ensemble UKMO";climfield="1Nov T1.5m";;
ens_ukmo_t2m_dec) file=UKMO/monthly/ukmo_t2m_dec_m%%.ctl;kindname="ensemble UKMO";climfield="1Dec T1.5m";;

ukmo_t2x_1) file=UKMO/monthly/ukmo_t2x_1.ctl;kindname="UKMO";climfield="+0 T1.5max";;
ukmo_t2x_2) file=UKMO/monthly/ukmo_t2x_2.ctl;kindname="UKMO";climfield="+1 T1.5max";;
ukmo_t2x_3) file=UKMO/monthly/ukmo_t2x_3.ctl;kindname="UKMO";climfield="+2 T1.5max";;
ukmo_t2x_4) file=UKMO/monthly/ukmo_t2x_4.ctl;kindname="UKMO";climfield="+3 T1.5max";;
ukmo_t2x_5) file=UKMO/monthly/ukmo_t2x_5.ctl;kindname="UKMO";climfield="+4 T1.5max";;
ukmo_t2x_6) file=UKMO/monthly/ukmo_t2x_6.ctl;kindname="UKMO";climfield="+5 T1.5max";;
ukmo_t2x_jan) file=UKMO/monthly/ukmo_t2x_jan.ensm.ctl;kindname="UKMO";climfield="1Jan T1.5max";;
ukmo_t2x_feb) file=UKMO/monthly/ukmo_t2x_feb.ensm.ctl;kindname="UKMO";climfield="1Feb T1.5max";;
ukmo_t2x_mar) file=UKMO/monthly/ukmo_t2x_mar.ensm.ctl;kindname="UKMO";climfield="1Mar T1.5max";;
ukmo_t2x_apr) file=UKMO/monthly/ukmo_t2x_apr.ensm.ctl;kindname="UKMO";climfield="1Apr T1.5max";;
ukmo_t2x_may) file=UKMO/monthly/ukmo_t2x_may.ensm.ctl;kindname="UKMO";climfield="1May T1.5max";;
ukmo_t2x_jun) file=UKMO/monthly/ukmo_t2x_jun.ensm.ctl;kindname="UKMO";climfield="1Jun T1.5max";;
ukmo_t2x_jul) file=UKMO/monthly/ukmo_t2x_jul.ensm.ctl;kindname="UKMO";climfield="1Jul T1.5max";;
ukmo_t2x_aug) file=UKMO/monthly/ukmo_t2x_aug.ensm.ctl;kindname="UKMO";climfield="1Aug T1.5max";;
ukmo_t2x_sep) file=UKMO/monthly/ukmo_t2x_sep.ensm.ctl;kindname="UKMO";climfield="1Sep T1.5max";;
ukmo_t2x_oct) file=UKMO/monthly/ukmo_t2x_oct.ensm.ctl;kindname="UKMO";climfield="1Oct T1.5max";;
ukmo_t2x_nov) file=UKMO/monthly/ukmo_t2x_nov.ensm.ctl;kindname="UKMO";climfield="1Nov T1.5max";;
ukmo_t2x_dec) file=UKMO/monthly/ukmo_t2x_dec.ensm.ctl;kindname="UKMO";climfield="1Dec T1.5max";;

ens_ukmo_t2x_1) file=UKMO/monthly/ukmo_t2x_1_m%%.ctl;kindname="ensemble UKMO";climfield="+0 T1.5max";;
ens_ukmo_t2x_2) file=UKMO/monthly/ukmo_t2x_2_m%%.ctl;kindname="ensemble UKMO";climfield="+1 T1.5max";;
ens_ukmo_t2x_3) file=UKMO/monthly/ukmo_t2x_3_m%%.ctl;kindname="ensemble UKMO";climfield="+2 T1.5max";;
ens_ukmo_t2x_4) file=UKMO/monthly/ukmo_t2x_4_m%%.ctl;kindname="ensemble UKMO";climfield="+3 T1.5max";;
ens_ukmo_t2x_5) file=UKMO/monthly/ukmo_t2x_5_m%%.ctl;kindname="ensemble UKMO";climfield="+4 T1.5max";;
ens_ukmo_t2x_6) file=UKMO/monthly/ukmo_t2x_6_m%%.ctl;kindname="ensemble UKMO";climfield="+5 T1.5max";;
ens_ukmo_t2x_jan) file=UKMO/monthly/ukmo_t2x_jan_m%%.ctl;kindname="ensemble UKMO";climfield="1Jan T1.5max";;
ens_ukmo_t2x_feb) file=UKMO/monthly/ukmo_t2x_feb_m%%.ctl;kindname="ensemble UKMO";climfield="1Feb T1.5max";;
ens_ukmo_t2x_mar) file=UKMO/monthly/ukmo_t2x_mar_m%%.ctl;kindname="ensemble UKMO";climfield="1Mar T1.5max";;
ens_ukmo_t2x_apr) file=UKMO/monthly/ukmo_t2x_apr_m%%.ctl;kindname="ensemble UKMO";climfield="1Apr T1.5max";;
ens_ukmo_t2x_may) file=UKMO/monthly/ukmo_t2x_may_m%%.ctl;kindname="ensemble UKMO";climfield="1May T1.5max";;
ens_ukmo_t2x_jun) file=UKMO/monthly/ukmo_t2x_jun_m%%.ctl;kindname="ensemble UKMO";climfield="1Jun T1.5max";;
ens_ukmo_t2x_jul) file=UKMO/monthly/ukmo_t2x_jul_m%%.ctl;kindname="ensemble UKMO";climfield="1Jul T1.5max";;
ens_ukmo_t2x_aug) file=UKMO/monthly/ukmo_t2x_aug_m%%.ctl;kindname="ensemble UKMO";climfield="1Aug T1.5max";;
ens_ukmo_t2x_sep) file=UKMO/monthly/ukmo_t2x_sep_m%%.ctl;kindname="ensemble UKMO";climfield="1Sep T1.5max";;
ens_ukmo_t2x_oct) file=UKMO/monthly/ukmo_t2x_oct_m%%.ctl;kindname="ensemble UKMO";climfield="1Oct T1.5max";;
ens_ukmo_t2x_nov) file=UKMO/monthly/ukmo_t2x_nov_m%%.ctl;kindname="ensemble UKMO";climfield="1Nov T1.5max";;
ens_ukmo_t2x_dec) file=UKMO/monthly/ukmo_t2x_dec_m%%.ctl;kindname="ensemble UKMO";climfield="1Dec T1.5max";;

ukmo_t2n_1) file=UKMO/monthly/ukmo_t2n_1.ctl;kindname="UKMO";climfield="+0 T1.5min";;
ukmo_t2n_2) file=UKMO/monthly/ukmo_t2n_2.ctl;kindname="UKMO";climfield="+1 T1.5min";;
ukmo_t2n_3) file=UKMO/monthly/ukmo_t2n_3.ctl;kindname="UKMO";climfield="+2 T1.5min";;
ukmo_t2n_4) file=UKMO/monthly/ukmo_t2n_4.ctl;kindname="UKMO";climfield="+3 T1.5min";;
ukmo_t2n_5) file=UKMO/monthly/ukmo_t2n_5.ctl;kindname="UKMO";climfield="+4 T1.5min";;
ukmo_t2n_6) file=UKMO/monthly/ukmo_t2n_6.ctl;kindname="UKMO";climfield="+5 T1.5min";;
ukmo_t2n_jan) file=UKMO/monthly/ukmo_t2n_jan.ensm.ctl;kindname="UKMO";climfield="1Jan T1.5min";;
ukmo_t2n_feb) file=UKMO/monthly/ukmo_t2n_feb.ensm.ctl;kindname="UKMO";climfield="1Feb T1.5min";;
ukmo_t2n_mar) file=UKMO/monthly/ukmo_t2n_mar.ensm.ctl;kindname="UKMO";climfield="1Mar T1.5min";;
ukmo_t2n_apr) file=UKMO/monthly/ukmo_t2n_apr.ensm.ctl;kindname="UKMO";climfield="1Apr T1.5min";;
ukmo_t2n_may) file=UKMO/monthly/ukmo_t2n_may.ensm.ctl;kindname="UKMO";climfield="1May T1.5min";;
ukmo_t2n_jun) file=UKMO/monthly/ukmo_t2n_jun.ensm.ctl;kindname="UKMO";climfield="1Jun T1.5min";;
ukmo_t2n_jul) file=UKMO/monthly/ukmo_t2n_jul.ensm.ctl;kindname="UKMO";climfield="1Jul T1.5min";;
ukmo_t2n_aug) file=UKMO/monthly/ukmo_t2n_aug.ensm.ctl;kindname="UKMO";climfield="1Aug T1.5min";;
ukmo_t2n_sep) file=UKMO/monthly/ukmo_t2n_sep.ensm.ctl;kindname="UKMO";climfield="1Sep T1.5min";;
ukmo_t2n_oct) file=UKMO/monthly/ukmo_t2n_oct.ensm.ctl;kindname="UKMO";climfield="1Oct T1.5min";;
ukmo_t2n_nov) file=UKMO/monthly/ukmo_t2n_nov.ensm.ctl;kindname="UKMO";climfield="1Nov T1.5min";;
ukmo_t2n_dec) file=UKMO/monthly/ukmo_t2n_dec.ensm.ctl;kindname="UKMO";climfield="1Dec T1.5min";;

ens_ukmo_t2n_1) file=UKMO/monthly/ukmo_t2n_1_m%%.ctl;kindname="ensemble UKMO";climfield="+0 T1.5min";;
ens_ukmo_t2n_2) file=UKMO/monthly/ukmo_t2n_2_m%%.ctl;kindname="ensemble UKMO";climfield="+1 T1.5min";;
ens_ukmo_t2n_3) file=UKMO/monthly/ukmo_t2n_3_m%%.ctl;kindname="ensemble UKMO";climfield="+2 T1.5min";;
ens_ukmo_t2n_4) file=UKMO/monthly/ukmo_t2n_4_m%%.ctl;kindname="ensemble UKMO";climfield="+3 T1.5min";;
ens_ukmo_t2n_5) file=UKMO/monthly/ukmo_t2n_5_m%%.ctl;kindname="ensemble UKMO";climfield="+4 T1.5min";;
ens_ukmo_t2n_6) file=UKMO/monthly/ukmo_t2n_6_m%%.ctl;kindname="ensemble UKMO";climfield="+5 T1.5min";;
ens_ukmo_t2n_jan) file=UKMO/monthly/ukmo_t2n_jan_m%%.ctl;kindname="ensemble UKMO";climfield="1Jan T1.5min";;
ens_ukmo_t2n_feb) file=UKMO/monthly/ukmo_t2n_feb_m%%.ctl;kindname="ensemble UKMO";climfield="1Feb T1.5min";;
ens_ukmo_t2n_mar) file=UKMO/monthly/ukmo_t2n_mar_m%%.ctl;kindname="ensemble UKMO";climfield="1Mar T1.5min";;
ens_ukmo_t2n_apr) file=UKMO/monthly/ukmo_t2n_apr_m%%.ctl;kindname="ensemble UKMO";climfield="1Apr T1.5min";;
ens_ukmo_t2n_may) file=UKMO/monthly/ukmo_t2n_may_m%%.ctl;kindname="ensemble UKMO";climfield="1May T1.5min";;
ens_ukmo_t2n_jun) file=UKMO/monthly/ukmo_t2n_jun_m%%.ctl;kindname="ensemble UKMO";climfield="1Jun T1.5min";;
ens_ukmo_t2n_jul) file=UKMO/monthly/ukmo_t2n_jul_m%%.ctl;kindname="ensemble UKMO";climfield="1Jul T1.5min";;
ens_ukmo_t2n_aug) file=UKMO/monthly/ukmo_t2n_aug_m%%.ctl;kindname="ensemble UKMO";climfield="1Aug T1.5min";;
ens_ukmo_t2n_sep) file=UKMO/monthly/ukmo_t2n_sep_m%%.ctl;kindname="ensemble UKMO";climfield="1Sep T1.5min";;
ens_ukmo_t2n_oct) file=UKMO/monthly/ukmo_t2n_oct_m%%.ctl;kindname="ensemble UKMO";climfield="1Oct T1.5min";;
ens_ukmo_t2n_nov) file=UKMO/monthly/ukmo_t2n_nov_m%%.ctl;kindname="ensemble UKMO";climfield="1Nov T1.5min";;
ens_ukmo_t2n_dec) file=UKMO/monthly/ukmo_t2n_dec_m%%.ctl;kindname="ensemble UKMO";climfield="1Dec T1.5min";;

ukmo_t850_1) file=UKMO/monthly/ukmo_t850_1.ctl;kindname="UKMO";climfield="+0 T850hPa";;
ukmo_t850_2) file=UKMO/monthly/ukmo_t850_2.ctl;kindname="UKMO";climfield="+1 T850hPa";;
ukmo_t850_3) file=UKMO/monthly/ukmo_t850_3.ctl;kindname="UKMO";climfield="+2 T850hPa";;
ukmo_t850_4) file=UKMO/monthly/ukmo_t850_4.ctl;kindname="UKMO";climfield="+3 T850hPa";;
ukmo_t850_5) file=UKMO/monthly/ukmo_t850_5.ctl;kindname="UKMO";climfield="+4 T850hPa";;
ukmo_t850_6) file=UKMO/monthly/ukmo_t850_6.ctl;kindname="UKMO";climfield="+5 T850hPa";;
ukmo_t850_jan) file=UKMO/monthly/ukmo_t850_jan.ensm.ctl;kindname="UKMO";climfield="1Jan T850hPa";;
ukmo_t850_feb) file=UKMO/monthly/ukmo_t850_feb.ensm.ctl;kindname="UKMO";climfield="1Feb T850hPa";;
ukmo_t850_mar) file=UKMO/monthly/ukmo_t850_mar.ensm.ctl;kindname="UKMO";climfield="1Mar T850hPa";;
ukmo_t850_apr) file=UKMO/monthly/ukmo_t850_apr.ensm.ctl;kindname="UKMO";climfield="1Apr T850hPa";;
ukmo_t850_may) file=UKMO/monthly/ukmo_t850_may.ensm.ctl;kindname="UKMO";climfield="1May T850hPa";;
ukmo_t850_jun) file=UKMO/monthly/ukmo_t850_jun.ensm.ctl;kindname="UKMO";climfield="1Jun T850hPa";;
ukmo_t850_jul) file=UKMO/monthly/ukmo_t850_jul.ensm.ctl;kindname="UKMO";climfield="1Jul T850hPa";;
ukmo_t850_aug) file=UKMO/monthly/ukmo_t850_aug.ensm.ctl;kindname="UKMO";climfield="1Aug T850hPa";;
ukmo_t850_sep) file=UKMO/monthly/ukmo_t850_sep.ensm.ctl;kindname="UKMO";climfield="1Sep T850hPa";;
ukmo_t850_oct) file=UKMO/monthly/ukmo_t850_oct.ensm.ctl;kindname="UKMO";climfield="1Oct T850hPa";;
ukmo_t850_nov) file=UKMO/monthly/ukmo_t850_nov.ensm.ctl;kindname="UKMO";climfield="1Nov T850hPa";;
ukmo_t850_dec) file=UKMO/monthly/ukmo_t850_dec.ensm.ctl;kindname="UKMO";climfield="1Dec T850hPa";;

ens_ukmo_t850_1) file=UKMO/monthly/ukmo_t850_1_m%%.ctl;kindname="ensemble UKMO";climfield="+0 T850hPa";;
ens_ukmo_t850_2) file=UKMO/monthly/ukmo_t850_2_m%%.ctl;kindname="ensemble UKMO";climfield="+1 T850hPa";;
ens_ukmo_t850_3) file=UKMO/monthly/ukmo_t850_3_m%%.ctl;kindname="ensemble UKMO";climfield="+2 T850hPa";;
ens_ukmo_t850_4) file=UKMO/monthly/ukmo_t850_4_m%%.ctl;kindname="ensemble UKMO";climfield="+3 T850hPa";;
ens_ukmo_t850_5) file=UKMO/monthly/ukmo_t850_5_m%%.ctl;kindname="ensemble UKMO";climfield="+4 T850hPa";;
ens_ukmo_t850_6) file=UKMO/monthly/ukmo_t850_6_m%%.ctl;kindname="ensemble UKMO";climfield="+5 T850hPa";;
ens_ukmo_t850_jan) file=UKMO/monthly/ukmo_t850_jan_m%%.ctl;kindname="ensemble UKMO";climfield="1Jan T850hPa";;
ens_ukmo_t850_feb) file=UKMO/monthly/ukmo_t850_feb_m%%.ctl;kindname="ensemble UKMO";climfield="1Feb T850hPa";;
ens_ukmo_t850_mar) file=UKMO/monthly/ukmo_t850_mar_m%%.ctl;kindname="ensemble UKMO";climfield="1Mar T850hPa";;
ens_ukmo_t850_apr) file=UKMO/monthly/ukmo_t850_apr_m%%.ctl;kindname="ensemble UKMO";climfield="1Apr T850hPa";;
ens_ukmo_t850_may) file=UKMO/monthly/ukmo_t850_may_m%%.ctl;kindname="ensemble UKMO";climfield="1May T850hPa";;
ens_ukmo_t850_jun) file=UKMO/monthly/ukmo_t850_jun_m%%.ctl;kindname="ensemble UKMO";climfield="1Jun T850hPa";;
ens_ukmo_t850_jul) file=UKMO/monthly/ukmo_t850_jul_m%%.ctl;kindname="ensemble UKMO";climfield="1Jul T850hPa";;
ens_ukmo_t850_aug) file=UKMO/monthly/ukmo_t850_aug_m%%.ctl;kindname="ensemble UKMO";climfield="1Aug T850hPa";;
ens_ukmo_t850_sep) file=UKMO/monthly/ukmo_t850_sep_m%%.ctl;kindname="ensemble UKMO";climfield="1Sep T850hPa";;
ens_ukmo_t850_oct) file=UKMO/monthly/ukmo_t850_oct_m%%.ctl;kindname="ensemble UKMO";climfield="1Oct T850hPa";;
ens_ukmo_t850_nov) file=UKMO/monthly/ukmo_t850_nov_m%%.ctl;kindname="ensemble UKMO";climfield="1Nov T850hPa";;
ens_ukmo_t850_dec) file=UKMO/monthly/ukmo_t850_dec_m%%.ctl;kindname="ensemble UKMO";climfield="1Dec T850hPa";;

ukmo_prcp_1) file=UKMO/monthly/ukmo_prcp_1.ctl;kindname="UKMO";climfield="+0 Precipitation";;
ukmo_prcp_2) file=UKMO/monthly/ukmo_prcp_2.ctl;kindname="UKMO";climfield="+1 Precipitation";;
ukmo_prcp_3) file=UKMO/monthly/ukmo_prcp_3.ctl;kindname="UKMO";climfield="+2 Precipitation";;
ukmo_prcp_4) file=UKMO/monthly/ukmo_prcp_4.ctl;kindname="UKMO";climfield="+3 Precipitation";;
ukmo_prcp_5) file=UKMO/monthly/ukmo_prcp_5.ctl;kindname="UKMO";climfield="+4 Precipitation";;
ukmo_prcp_6) file=UKMO/monthly/ukmo_prcp_6.ctl;kindname="UKMO";climfield="+5 Precipitation";;
ukmo_prcp_jan) file=UKMO/monthly/ukmo_prcp_jan.ensm.ctl;kindname="UKMO";climfield="1Jan Precipitation";;
ukmo_prcp_feb) file=UKMO/monthly/ukmo_prcp_feb.ensm.ctl;kindname="UKMO";climfield="1Feb Precipitation";;
ukmo_prcp_mar) file=UKMO/monthly/ukmo_prcp_mar.ensm.ctl;kindname="UKMO";climfield="1Mar Precipitation";;
ukmo_prcp_apr) file=UKMO/monthly/ukmo_prcp_apr.ensm.ctl;kindname="UKMO";climfield="1Apr Precipitation";;
ukmo_prcp_may) file=UKMO/monthly/ukmo_prcp_may.ensm.ctl;kindname="UKMO";climfield="1May Precipitation";;
ukmo_prcp_jun) file=UKMO/monthly/ukmo_prcp_jun.ensm.ctl;kindname="UKMO";climfield="1Jun Precipitation";;
ukmo_prcp_jul) file=UKMO/monthly/ukmo_prcp_jul.ensm.ctl;kindname="UKMO";climfield="1Jul Precipitation";;
ukmo_prcp_aug) file=UKMO/monthly/ukmo_prcp_aug.ensm.ctl;kindname="UKMO";climfield="1Aug Precipitation";;
ukmo_prcp_sep) file=UKMO/monthly/ukmo_prcp_sep.ensm.ctl;kindname="UKMO";climfield="1Sep Precipitation";;
ukmo_prcp_oct) file=UKMO/monthly/ukmo_prcp_oct.ensm.ctl;kindname="UKMO";climfield="1Oct Precipitation";;
ukmo_prcp_nov) file=UKMO/monthly/ukmo_prcp_nov.ensm.ctl;kindname="UKMO";climfield="1Nov Precipitation";;
ukmo_prcp_dec) file=UKMO/monthly/ukmo_prcp_dec.ensm.ctl;kindname="UKMO";climfield="1Dec Precipitation";;

ens_ukmo_prcp_1) file=UKMO/monthly/ukmo_prcp_1_m%%.ctl;kindname="ensemble UKMO";climfield="+0 Precipitation";;
ens_ukmo_prcp_2) file=UKMO/monthly/ukmo_prcp_2_m%%.ctl;kindname="ensemble UKMO";climfield="+1 Precipitation";;
ens_ukmo_prcp_3) file=UKMO/monthly/ukmo_prcp_3_m%%.ctl;kindname="ensemble UKMO";climfield="+2 Precipitation";;
ens_ukmo_prcp_4) file=UKMO/monthly/ukmo_prcp_4_m%%.ctl;kindname="ensemble UKMO";climfield="+3 Precipitation";;
ens_ukmo_prcp_5) file=UKMO/monthly/ukmo_prcp_5_m%%.ctl;kindname="ensemble UKMO";climfield="+4 Precipitation";;
ens_ukmo_prcp_6) file=UKMO/monthly/ukmo_prcp_6_m%%.ctl;kindname="ensemble UKMO";climfield="+5 Precipitation";;
ens_ukmo_prcp_jan) file=UKMO/monthly/ukmo_prcp_jan_m%%.ctl;kindname="ensemble UKMO";climfield="1Jan Precipitation";;
ens_ukmo_prcp_feb) file=UKMO/monthly/ukmo_prcp_feb_m%%.ctl;kindname="ensemble UKMO";climfield="1Feb Precipitation";;
ens_ukmo_prcp_mar) file=UKMO/monthly/ukmo_prcp_mar_m%%.ctl;kindname="ensemble UKMO";climfield="1Mar Precipitation";;
ens_ukmo_prcp_apr) file=UKMO/monthly/ukmo_prcp_apr_m%%.ctl;kindname="ensemble UKMO";climfield="1Apr Precipitation";;
ens_ukmo_prcp_may) file=UKMO/monthly/ukmo_prcp_may_m%%.ctl;kindname="ensemble UKMO";climfield="1May Precipitation";;
ens_ukmo_prcp_jun) file=UKMO/monthly/ukmo_prcp_jun_m%%.ctl;kindname="ensemble UKMO";climfield="1Jun Precipitation";;
ens_ukmo_prcp_jul) file=UKMO/monthly/ukmo_prcp_jul_m%%.ctl;kindname="ensemble UKMO";climfield="1Jul Precipitation";;
ens_ukmo_prcp_aug) file=UKMO/monthly/ukmo_prcp_aug_m%%.ctl;kindname="ensemble UKMO";climfield="1Aug Precipitation";;
ens_ukmo_prcp_sep) file=UKMO/monthly/ukmo_prcp_sep_m%%.ctl;kindname="ensemble UKMO";climfield="1Sep Precipitation";;
ens_ukmo_prcp_oct) file=UKMO/monthly/ukmo_prcp_oct_m%%.ctl;kindname="ensemble UKMO";climfield="1Oct Precipitation";;
ens_ukmo_prcp_nov) file=UKMO/monthly/ukmo_prcp_nov_m%%.ctl;kindname="ensemble UKMO";climfield="1Nov Precipitation";;
ens_ukmo_prcp_dec) file=UKMO/monthly/ukmo_prcp_dec_m%%.ctl;kindname="ensemble UKMO";climfield="1Dec Precipitation";;

ukmo_msl_1) file=UKMO/monthly/ukmo_msl_1.ctl;kindname="UKMO";climfield="+0 SLP";;
ukmo_msl_2) file=UKMO/monthly/ukmo_msl_2.ctl;kindname="UKMO";climfield="+1 SLP";;
ukmo_msl_3) file=UKMO/monthly/ukmo_msl_3.ctl;kindname="UKMO";climfield="+2 SLP";;
ukmo_msl_4) file=UKMO/monthly/ukmo_msl_4.ctl;kindname="UKMO";climfield="+3 SLP";;
ukmo_msl_5) file=UKMO/monthly/ukmo_msl_5.ctl;kindname="UKMO";climfield="+4 SLP";;
ukmo_msl_6) file=UKMO/monthly/ukmo_msl_6.ctl;kindname="UKMO";climfield="+5 SLP";;
ukmo_msl_jan) file=UKMO/monthly/ukmo_msl_jan.ensm.ctl;kindname="UKMO";climfield="1Jan SLP";;
ukmo_msl_feb) file=UKMO/monthly/ukmo_msl_feb.ensm.ctl;kindname="UKMO";climfield="1Feb SLP";;
ukmo_msl_mar) file=UKMO/monthly/ukmo_msl_mar.ensm.ctl;kindname="UKMO";climfield="1Mar SLP";;
ukmo_msl_apr) file=UKMO/monthly/ukmo_msl_apr.ensm.ctl;kindname="UKMO";climfield="1Apr SLP";;
ukmo_msl_may) file=UKMO/monthly/ukmo_msl_may.ensm.ctl;kindname="UKMO";climfield="1May SLP";;
ukmo_msl_jun) file=UKMO/monthly/ukmo_msl_jun.ensm.ctl;kindname="UKMO";climfield="1Jun SLP";;
ukmo_msl_jul) file=UKMO/monthly/ukmo_msl_jul.ensm.ctl;kindname="UKMO";climfield="1Jul SLP";;
ukmo_msl_aug) file=UKMO/monthly/ukmo_msl_aug.ensm.ctl;kindname="UKMO";climfield="1Aug SLP";;
ukmo_msl_sep) file=UKMO/monthly/ukmo_msl_sep.ensm.ctl;kindname="UKMO";climfield="1Sep SLP";;
ukmo_msl_oct) file=UKMO/monthly/ukmo_msl_oct.ensm.ctl;kindname="UKMO";climfield="1Oct SLP";;
ukmo_msl_nov) file=UKMO/monthly/ukmo_msl_nov.ensm.ctl;kindname="UKMO";climfield="1Nov SLP";;
ukmo_msl_dec) file=UKMO/monthly/ukmo_msl_dec.ensm.ctl;kindname="UKMO";climfield="1Dec SLP";;

ens_ukmo_msl_1) file=UKMO/monthly/ukmo_msl_1_m%%.ctl;kindname="ensemble UKMO";climfield="+0 SLP";;
ens_ukmo_msl_2) file=UKMO/monthly/ukmo_msl_2_m%%.ctl;kindname="ensemble UKMO";climfield="+1 SLP";;
ens_ukmo_msl_3) file=UKMO/monthly/ukmo_msl_3_m%%.ctl;kindname="ensemble UKMO";climfield="+2 SLP";;
ens_ukmo_msl_4) file=UKMO/monthly/ukmo_msl_4_m%%.ctl;kindname="ensemble UKMO";climfield="+3 SLP";;
ens_ukmo_msl_5) file=UKMO/monthly/ukmo_msl_5_m%%.ctl;kindname="ensemble UKMO";climfield="+4 SLP";;
ens_ukmo_msl_6) file=UKMO/monthly/ukmo_msl_6_m%%.ctl;kindname="ensemble UKMO";climfield="+5 SLP";;
ens_ukmo_msl_jan) file=UKMO/monthly/ukmo_msl_jan_m%%.ctl;kindname="ensemble UKMO";climfield="1Jan SLP";;
ens_ukmo_msl_feb) file=UKMO/monthly/ukmo_msl_feb_m%%.ctl;kindname="ensemble UKMO";climfield="1Feb SLP";;
ens_ukmo_msl_mar) file=UKMO/monthly/ukmo_msl_mar_m%%.ctl;kindname="ensemble UKMO";climfield="1Mar SLP";;
ens_ukmo_msl_apr) file=UKMO/monthly/ukmo_msl_apr_m%%.ctl;kindname="ensemble UKMO";climfield="1Apr SLP";;
ens_ukmo_msl_may) file=UKMO/monthly/ukmo_msl_may_m%%.ctl;kindname="ensemble UKMO";climfield="1May SLP";;
ens_ukmo_msl_jun) file=UKMO/monthly/ukmo_msl_jun_m%%.ctl;kindname="ensemble UKMO";climfield="1Jun SLP";;
ens_ukmo_msl_jul) file=UKMO/monthly/ukmo_msl_jul_m%%.ctl;kindname="ensemble UKMO";climfield="1Jul SLP";;
ens_ukmo_msl_aug) file=UKMO/monthly/ukmo_msl_aug_m%%.ctl;kindname="ensemble UKMO";climfield="1Aug SLP";;
ens_ukmo_msl_sep) file=UKMO/monthly/ukmo_msl_sep_m%%.ctl;kindname="ensemble UKMO";climfield="1Sep SLP";;
ens_ukmo_msl_oct) file=UKMO/monthly/ukmo_msl_oct_m%%.ctl;kindname="ensemble UKMO";climfield="1Oct SLP";;
ens_ukmo_msl_nov) file=UKMO/monthly/ukmo_msl_nov_m%%.ctl;kindname="ensemble UKMO";climfield="1Nov SLP";;
ens_ukmo_msl_dec) file=UKMO/monthly/ukmo_msl_dec_m%%.ctl;kindname="ensemble UKMO";climfield="1Dec SLP";;

ukmo_z500_1) file=UKMO/monthly/ukmo_z500_1.ctl;kindname="UKMO";climfield="+0 500hPa Geopotential";;
ukmo_z500_2) file=UKMO/monthly/ukmo_z500_2.ctl;kindname="UKMO";climfield="+1 500hPa Geopotential";;
ukmo_z500_3) file=UKMO/monthly/ukmo_z500_3.ctl;kindname="UKMO";climfield="+2 500hPa Geopotential";;
ukmo_z500_4) file=UKMO/monthly/ukmo_z500_4.ctl;kindname="UKMO";climfield="+3 500hPa Geopotential";;
ukmo_z500_5) file=UKMO/monthly/ukmo_z500_5.ctl;kindname="UKMO";climfield="+4 500hPa Geopotential";;
ukmo_z500_6) file=UKMO/monthly/ukmo_z500_6.ctl;kindname="UKMO";climfield="+5 500hPa Geopotential";;
ukmo_z500_jan) file=UKMO/monthly/ukmo_z500_jan.ensm.ctl;kindname="UKMO";climfield="1Jan 500hPa Geopotential";;
ukmo_z500_feb) file=UKMO/monthly/ukmo_z500_feb.ensm.ctl;kindname="UKMO";climfield="1Feb 500hPa Geopotential";;
ukmo_z500_mar) file=UKMO/monthly/ukmo_z500_mar.ensm.ctl;kindname="UKMO";climfield="1Mar 500hPa Geopotential";;
ukmo_z500_apr) file=UKMO/monthly/ukmo_z500_apr.ensm.ctl;kindname="UKMO";climfield="1Apr 500hPa Geopotential";;
ukmo_z500_may) file=UKMO/monthly/ukmo_z500_may.ensm.ctl;kindname="UKMO";climfield="1May 500hPa Geopotential";;
ukmo_z500_jun) file=UKMO/monthly/ukmo_z500_jun.ensm.ctl;kindname="UKMO";climfield="1Jun 500hPa Geopotential";;
ukmo_z500_jul) file=UKMO/monthly/ukmo_z500_jul.ensm.ctl;kindname="UKMO";climfield="1Jul 500hPa Geopotential";;
ukmo_z500_aug) file=UKMO/monthly/ukmo_z500_aug.ensm.ctl;kindname="UKMO";climfield="1Aug 500hPa Geopotential";;
ukmo_z500_sep) file=UKMO/monthly/ukmo_z500_sep.ensm.ctl;kindname="UKMO";climfield="1Sep 500hPa Geopotential";;
ukmo_z500_oct) file=UKMO/monthly/ukmo_z500_oct.ensm.ctl;kindname="UKMO";climfield="1Oct 500hPa Geopotential";;
ukmo_z500_nov) file=UKMO/monthly/ukmo_z500_nov.ensm.ctl;kindname="UKMO";climfield="1Nov 500hPa Geopotential";;
ukmo_z500_dec) file=UKMO/monthly/ukmo_z500_dec.ensm.ctl;kindname="UKMO";climfield="1Dec 500hPa Geopotential";;

ens_ukmo_z500_1) file=UKMO/monthly/ukmo_z500_1_m%%.ctl;kindname="ensemble UKMO";climfield="+0 500hPa Geopotential";;
ens_ukmo_z500_2) file=UKMO/monthly/ukmo_z500_2_m%%.ctl;kindname="ensemble UKMO";climfield="+1 500hPa Geopotential";;
ens_ukmo_z500_3) file=UKMO/monthly/ukmo_z500_3_m%%.ctl;kindname="ensemble UKMO";climfield="+2 500hPa Geopotential";;
ens_ukmo_z500_4) file=UKMO/monthly/ukmo_z500_4_m%%.ctl;kindname="ensemble UKMO";climfield="+3 500hPa Geopotential";;
ens_ukmo_z500_5) file=UKMO/monthly/ukmo_z500_5_m%%.ctl;kindname="ensemble UKMO";climfield="+4 500hPa Geopotential";;
ens_ukmo_z500_6) file=UKMO/monthly/ukmo_z500_6_m%%.ctl;kindname="ensemble UKMO";climfield="+5 500hPa Geopotential";;
ens_ukmo_z500_jan) file=UKMO/monthly/ukmo_z500_jan_m%%.ctl;kindname="ensemble UKMO";climfield="1Jan 500hPa Geopotential";;
ens_ukmo_z500_feb) file=UKMO/monthly/ukmo_z500_feb_m%%.ctl;kindname="ensemble UKMO";climfield="1Feb 500hPa Geopotential";;
ens_ukmo_z500_mar) file=UKMO/monthly/ukmo_z500_mar_m%%.ctl;kindname="ensemble UKMO";climfield="1Mar 500hPa Geopotential";;
ens_ukmo_z500_apr) file=UKMO/monthly/ukmo_z500_apr_m%%.ctl;kindname="ensemble UKMO";climfield="1Apr 500hPa Geopotential";;
ens_ukmo_z500_may) file=UKMO/monthly/ukmo_z500_may_m%%.ctl;kindname="ensemble UKMO";climfield="1May 500hPa Geopotential";;
ens_ukmo_z500_jun) file=UKMO/monthly/ukmo_z500_jun_m%%.ctl;kindname="ensemble UKMO";climfield="1Jun 500hPa Geopotential";;
ens_ukmo_z500_jul) file=UKMO/monthly/ukmo_z500_jul_m%%.ctl;kindname="ensemble UKMO";climfield="1Jul 500hPa Geopotential";;
ens_ukmo_z500_aug) file=UKMO/monthly/ukmo_z500_aug_m%%.ctl;kindname="ensemble UKMO";climfield="1Aug 500hPa Geopotential";;
ens_ukmo_z500_sep) file=UKMO/monthly/ukmo_z500_sep_m%%.ctl;kindname="ensemble UKMO";climfield="1Sep 500hPa Geopotential";;
ens_ukmo_z500_oct) file=UKMO/monthly/ukmo_z500_oct_m%%.ctl;kindname="ensemble UKMO";climfield="1Oct 500hPa Geopotential";;
ens_ukmo_z500_nov) file=UKMO/monthly/ukmo_z500_nov_m%%.ctl;kindname="ensemble UKMO";climfield="1Nov 500hPa Geopotential";;
ens_ukmo_z500_dec) file=UKMO/monthly/ukmo_z500_dec_m%%.ctl;kindname="ensemble UKMO";climfield="1Dec 500hPa Geopotential";;

ukmo_ssd_1) file=UKMO/monthly/ukmo_ssd_1.ctl;kindname="UKMO";climfield="+0 downward solar radiation";;
ukmo_ssd_2) file=UKMO/monthly/ukmo_ssd_2.ctl;kindname="UKMO";climfield="+1 downward solar radiation";;
ukmo_ssd_3) file=UKMO/monthly/ukmo_ssd_3.ctl;kindname="UKMO";climfield="+2 downward solar radiation";;
ukmo_ssd_4) file=UKMO/monthly/ukmo_ssd_4.ctl;kindname="UKMO";climfield="+3 downward solar radiation";;
ukmo_ssd_5) file=UKMO/monthly/ukmo_ssd_5.ctl;kindname="UKMO";climfield="+4 downward solar radiation";;
ukmo_ssd_6) file=UKMO/monthly/ukmo_ssd_6.ctl;kindname="UKMO";climfield="+5 downward solar radiation";;
ukmo_ssd_jan) file=UKMO/monthly/ukmo_ssd_jan.ensm.ctl;kindname="UKMO";climfield="1Jan downward solar radiation";;
ukmo_ssd_feb) file=UKMO/monthly/ukmo_ssd_feb.ensm.ctl;kindname="UKMO";climfield="1Feb downward solar radiation";;
ukmo_ssd_mar) file=UKMO/monthly/ukmo_ssd_mar.ensm.ctl;kindname="UKMO";climfield="1Mar downward solar radiation";;
ukmo_ssd_apr) file=UKMO/monthly/ukmo_ssd_apr.ensm.ctl;kindname="UKMO";climfield="1Apr downward solar radiation";;
ukmo_ssd_may) file=UKMO/monthly/ukmo_ssd_may.ensm.ctl;kindname="UKMO";climfield="1May downward solar radiation";;
ukmo_ssd_jun) file=UKMO/monthly/ukmo_ssd_jun.ensm.ctl;kindname="UKMO";climfield="1Jun downward solar radiation";;
ukmo_ssd_jul) file=UKMO/monthly/ukmo_ssd_jul.ensm.ctl;kindname="UKMO";climfield="1Jul downward solar radiation";;
ukmo_ssd_aug) file=UKMO/monthly/ukmo_ssd_aug.ensm.ctl;kindname="UKMO";climfield="1Aug downward solar radiation";;
ukmo_ssd_sep) file=UKMO/monthly/ukmo_ssd_sep.ensm.ctl;kindname="UKMO";climfield="1Sep downward solar radiation";;
ukmo_ssd_oct) file=UKMO/monthly/ukmo_ssd_oct.ensm.ctl;kindname="UKMO";climfield="1Oct downward solar radiation";;
ukmo_ssd_nov) file=UKMO/monthly/ukmo_ssd_nov.ensm.ctl;kindname="UKMO";climfield="1Nov downward solar radiation";;
ukmo_ssd_dec) file=UKMO/monthly/ukmo_ssd_dec.ensm.ctl;kindname="UKMO";climfield="1Dec downward solar radiation";;

ens_ukmo_ssd_1) file=UKMO/monthly/ukmo_ssd_1_m%%.ctl;kindname="ensemble UKMO";climfield="+0 downward solar radiation";;
ens_ukmo_ssd_2) file=UKMO/monthly/ukmo_ssd_2_m%%.ctl;kindname="ensemble UKMO";climfield="+1 downward solar radiation";;
ens_ukmo_ssd_3) file=UKMO/monthly/ukmo_ssd_3_m%%.ctl;kindname="ensemble UKMO";climfield="+2 downward solar radiation";;
ens_ukmo_ssd_4) file=UKMO/monthly/ukmo_ssd_4_m%%.ctl;kindname="ensemble UKMO";climfield="+3 downward solar radiation";;
ens_ukmo_ssd_5) file=UKMO/monthly/ukmo_ssd_5_m%%.ctl;kindname="ensemble UKMO";climfield="+4 downward solar radiation";;
ens_ukmo_ssd_6) file=UKMO/monthly/ukmo_ssd_6_m%%.ctl;kindname="ensemble UKMO";climfield="+5 downward solar radiation";;
ens_ukmo_ssd_jan) file=UKMO/monthly/ukmo_ssd_jan_m%%.ctl;kindname="ensemble UKMO";climfield="1Jan downward solar radiation";;
ens_ukmo_ssd_feb) file=UKMO/monthly/ukmo_ssd_feb_m%%.ctl;kindname="ensemble UKMO";climfield="1Feb downward solar radiation";;
ens_ukmo_ssd_mar) file=UKMO/monthly/ukmo_ssd_mar_m%%.ctl;kindname="ensemble UKMO";climfield="1Mar downward solar radiation";;
ens_ukmo_ssd_apr) file=UKMO/monthly/ukmo_ssd_apr_m%%.ctl;kindname="ensemble UKMO";climfield="1Apr downward solar radiation";;
ens_ukmo_ssd_may) file=UKMO/monthly/ukmo_ssd_may_m%%.ctl;kindname="ensemble UKMO";climfield="1May downward solar radiation";;
ens_ukmo_ssd_jun) file=UKMO/monthly/ukmo_ssd_jun_m%%.ctl;kindname="ensemble UKMO";climfield="1Jun downward solar radiation";;
ens_ukmo_ssd_jul) file=UKMO/monthly/ukmo_ssd_jul_m%%.ctl;kindname="ensemble UKMO";climfield="1Jul downward solar radiation";;
ens_ukmo_ssd_aug) file=UKMO/monthly/ukmo_ssd_aug_m%%.ctl;kindname="ensemble UKMO";climfield="1Aug downward solar radiation";;
ens_ukmo_ssd_sep) file=UKMO/monthly/ukmo_ssd_sep_m%%.ctl;kindname="ensemble UKMO";climfield="1Sep downward solar radiation";;
ens_ukmo_ssd_oct) file=UKMO/monthly/ukmo_ssd_oct_m%%.ctl;kindname="ensemble UKMO";climfield="1Oct downward solar radiation";;
ens_ukmo_ssd_nov) file=UKMO/monthly/ukmo_ssd_nov_m%%.ctl;kindname="ensemble UKMO";climfield="1Nov downward solar radiation";;
ens_ukmo_ssd_dec) file=UKMO/monthly/ukmo_ssd_dec_m%%.ctl;kindname="ensemble UKMO";climfield="1Dec downward solar radiation";;

ukmo_tsfc_1) file=UKMO/monthly/ukmo_sst_1.ctl;kindname="UKMO";climfield="+0 SST";;
ukmo_tsfc_2) file=UKMO/monthly/ukmo_sst_2.ctl;kindname="UKMO";climfield="+1 SST";;
ukmo_tsfc_3) file=UKMO/monthly/ukmo_sst_3.ctl;kindname="UKMO";climfield="+2 SST";;
ukmo_tsfc_4) file=UKMO/monthly/ukmo_sst_4.ctl;kindname="UKMO";climfield="+3 SST";;
ukmo_tsfc_5) file=UKMO/monthly/ukmo_sst_5.ctl;kindname="UKMO";climfield="+4 SST";;
ukmo_tsfc_6) file=UKMO/monthly/ukmo_sst_6.ctl;kindname="UKMO";climfield="+5 SST";;
ukmo_tsfc_jan) file=UKMO/monthly/ukmo_sst_jan.ensm.ctl;kindname="UKMO";climfield="1Jan SST";;
ukmo_tsfc_feb) file=UKMO/monthly/ukmo_sst_feb.ensm.ctl;kindname="UKMO";climfield="1Feb SST";;
ukmo_tsfc_mar) file=UKMO/monthly/ukmo_sst_mar.ensm.ctl;kindname="UKMO";climfield="1Mar SST";;
ukmo_tsfc_apr) file=UKMO/monthly/ukmo_sst_apr.ensm.ctl;kindname="UKMO";climfield="1Apr SST";;
ukmo_tsfc_may) file=UKMO/monthly/ukmo_sst_may.ensm.ctl;kindname="UKMO";climfield="1May SST";;
ukmo_tsfc_jun) file=UKMO/monthly/ukmo_sst_jun.ensm.ctl;kindname="UKMO";climfield="1Jun SST";;
ukmo_tsfc_jul) file=UKMO/monthly/ukmo_sst_jul.ensm.ctl;kindname="UKMO";climfield="1Jul SST";;
ukmo_tsfc_aug) file=UKMO/monthly/ukmo_sst_aug.ensm.ctl;kindname="UKMO";climfield="1Aug SST";;
ukmo_tsfc_sep) file=UKMO/monthly/ukmo_sst_sep.ensm.ctl;kindname="UKMO";climfield="1Sep SST";;
ukmo_tsfc_oct) file=UKMO/monthly/ukmo_sst_oct.ensm.ctl;kindname="UKMO";climfield="1Oct SST";;
ukmo_tsfc_nov) file=UKMO/monthly/ukmo_sst_nov.ensm.ctl;kindname="UKMO";climfield="1Nov SST";;
ukmo_tsfc_dec) file=UKMO/monthly/ukmo_sst_dec.ensm.ctl;kindname="UKMO";climfield="1Dec SST";;

ens_ukmo_tsfc_1) file=UKMO/monthly/ukmo_sst_1_m%%.ctl;kindname="ensemble UKMO";climfield="+0 SST";;
ens_ukmo_tsfc_2) file=UKMO/monthly/ukmo_sst_2_m%%.ctl;kindname="ensemble UKMO";climfield="+1 SST";;
ens_ukmo_tsfc_3) file=UKMO/monthly/ukmo_sst_3_m%%.ctl;kindname="ensemble UKMO";climfield="+2 SST";;
ens_ukmo_tsfc_4) file=UKMO/monthly/ukmo_sst_4_m%%.ctl;kindname="ensemble UKMO";climfield="+3 SST";;
ens_ukmo_tsfc_5) file=UKMO/monthly/ukmo_sst_5_m%%.ctl;kindname="ensemble UKMO";climfield="+4 SST";;
ens_ukmo_tsfc_6) file=UKMO/monthly/ukmo_sst_6_m%%.ctl;kindname="ensemble UKMO";climfield="+5 SST";;
ens_ukmo_tsfc_jan) file=UKMO/monthly/ukmo_sst_jan_m%%.ctl;kindname="ensemble UKMO";climfield="1Jan SST";;
ens_ukmo_tsfc_feb) file=UKMO/monthly/ukmo_sst_feb_m%%.ctl;kindname="ensemble UKMO";climfield="1Feb SST";;
ens_ukmo_tsfc_mar) file=UKMO/monthly/ukmo_sst_mar_m%%.ctl;kindname="ensemble UKMO";climfield="1Mar SST";;
ens_ukmo_tsfc_apr) file=UKMO/monthly/ukmo_sst_apr_m%%.ctl;kindname="ensemble UKMO";climfield="1Apr SST";;
ens_ukmo_tsfc_may) file=UKMO/monthly/ukmo_sst_may_m%%.ctl;kindname="ensemble UKMO";climfield="1May SST";;
ens_ukmo_tsfc_jun) file=UKMO/monthly/ukmo_sst_jun_m%%.ctl;kindname="ensemble UKMO";climfield="1Jun SST";;
ens_ukmo_tsfc_jul) file=UKMO/monthly/ukmo_sst_jul_m%%.ctl;kindname="ensemble UKMO";climfield="1Jul SST";;
ens_ukmo_tsfc_aug) file=UKMO/monthly/ukmo_sst_aug_m%%.ctl;kindname="ensemble UKMO";climfield="1Aug SST";;
ens_ukmo_tsfc_sep) file=UKMO/monthly/ukmo_sst_sep_m%%.ctl;kindname="ensemble UKMO";climfield="1Sep SST";;
ens_ukmo_tsfc_oct) file=UKMO/monthly/ukmo_sst_oct_m%%.ctl;kindname="ensemble UKMO";climfield="1Oct SST";;
ens_ukmo_tsfc_nov) file=UKMO/monthly/ukmo_sst_nov_m%%.ctl;kindname="ensemble UKMO";climfield="1Nov SST";;
ens_ukmo_tsfc_dec) file=UKMO/monthly/ukmo_sst_dec_m%%.ctl;kindname="ensemble UKMO";climfield="1Dec SST";;

ukmo_snd_1) file=UKMO/monthly/ukmo_snd_1.ctl;kindname="UKMO";climfield="+0 snow depth";;
ukmo_snd_2) file=UKMO/monthly/ukmo_snd_2.ctl;kindname="UKMO";climfield="+1 snow depth";;
ukmo_snd_3) file=UKMO/monthly/ukmo_snd_3.ctl;kindname="UKMO";climfield="+2 snow depth";;
ukmo_snd_4) file=UKMO/monthly/ukmo_snd_4.ctl;kindname="UKMO";climfield="+3 snow depth";;
ukmo_snd_5) file=UKMO/monthly/ukmo_snd_5.ctl;kindname="UKMO";climfield="+4 snow depth";;
ukmo_snd_6) file=UKMO/monthly/ukmo_snd_6.ctl;kindname="UKMO";climfield="+5 snow depth";;
ukmo_snd_jan) file=UKMO/monthly/ukmo_snd_jan.ensm.ctl;kindname="UKMO";climfield="1Jan snow depth";;
ukmo_snd_feb) file=UKMO/monthly/ukmo_snd_feb.ensm.ctl;kindname="UKMO";climfield="1Feb snow depth";;
ukmo_snd_mar) file=UKMO/monthly/ukmo_snd_mar.ensm.ctl;kindname="UKMO";climfield="1Mar snow depth";;
ukmo_snd_apr) file=UKMO/monthly/ukmo_snd_apr.ensm.ctl;kindname="UKMO";climfield="1Apr snow depth";;
ukmo_snd_may) file=UKMO/monthly/ukmo_snd_may.ensm.ctl;kindname="UKMO";climfield="1May snow depth";;
ukmo_snd_jun) file=UKMO/monthly/ukmo_snd_jun.ensm.ctl;kindname="UKMO";climfield="1Jun snow depth";;
ukmo_snd_jul) file=UKMO/monthly/ukmo_snd_jul.ensm.ctl;kindname="UKMO";climfield="1Jul snow depth";;
ukmo_snd_aug) file=UKMO/monthly/ukmo_snd_aug.ensm.ctl;kindname="UKMO";climfield="1Aug snow depth";;
ukmo_snd_sep) file=UKMO/monthly/ukmo_snd_sep.ensm.ctl;kindname="UKMO";climfield="1Sep snow depth";;
ukmo_snd_oct) file=UKMO/monthly/ukmo_snd_oct.ensm.ctl;kindname="UKMO";climfield="1Oct snow depth";;
ukmo_snd_nov) file=UKMO/monthly/ukmo_snd_nov.ensm.ctl;kindname="UKMO";climfield="1Nov snow depth";;
ukmo_snd_dec) file=UKMO/monthly/ukmo_snd_dec.ensm.ctl;kindname="UKMO";climfield="1Dec snow depth";;

ens_ukmo_snd_1) file=UKMO/monthly/ukmo_snd_1_m%%.ctl;kindname="ensemble UKMO";climfield="+0 snow depth";;
ens_ukmo_snd_2) file=UKMO/monthly/ukmo_snd_2_m%%.ctl;kindname="ensemble UKMO";climfield="+1 snow depth";;
ens_ukmo_snd_3) file=UKMO/monthly/ukmo_snd_3_m%%.ctl;kindname="ensemble UKMO";climfield="+2 snow depth";;
ens_ukmo_snd_4) file=UKMO/monthly/ukmo_snd_4_m%%.ctl;kindname="ensemble UKMO";climfield="+3 snow depth";;
ens_ukmo_snd_5) file=UKMO/monthly/ukmo_snd_5_m%%.ctl;kindname="ensemble UKMO";climfield="+4 snow depth";;
ens_ukmo_snd_6) file=UKMO/monthly/ukmo_snd_6_m%%.ctl;kindname="ensemble UKMO";climfield="+5 snow depth";;
ens_ukmo_snd_jan) file=UKMO/monthly/ukmo_snd_jan_m%%.ctl;kindname="ensemble UKMO";climfield="1Jan snow depth";;
ens_ukmo_snd_feb) file=UKMO/monthly/ukmo_snd_feb_m%%.ctl;kindname="ensemble UKMO";climfield="1Feb snow depth";;
ens_ukmo_snd_mar) file=UKMO/monthly/ukmo_snd_mar_m%%.ctl;kindname="ensemble UKMO";climfield="1Mar snow depth";;
ens_ukmo_snd_apr) file=UKMO/monthly/ukmo_snd_apr_m%%.ctl;kindname="ensemble UKMO";climfield="1Apr snow depth";;
ens_ukmo_snd_may) file=UKMO/monthly/ukmo_snd_may_m%%.ctl;kindname="ensemble UKMO";climfield="1May snow depth";;
ens_ukmo_snd_jun) file=UKMO/monthly/ukmo_snd_jun_m%%.ctl;kindname="ensemble UKMO";climfield="1Jun snow depth";;
ens_ukmo_snd_jul) file=UKMO/monthly/ukmo_snd_jul_m%%.ctl;kindname="ensemble UKMO";climfield="1Jul snow depth";;
ens_ukmo_snd_aug) file=UKMO/monthly/ukmo_snd_aug_m%%.ctl;kindname="ensemble UKMO";climfield="1Aug snow depth";;
ens_ukmo_snd_sep) file=UKMO/monthly/ukmo_snd_sep_m%%.ctl;kindname="ensemble UKMO";climfield="1Sep snow depth";;
ens_ukmo_snd_oct) file=UKMO/monthly/ukmo_snd_oct_m%%.ctl;kindname="ensemble UKMO";climfield="1Oct snow depth";;
ens_ukmo_snd_nov) file=UKMO/monthly/ukmo_snd_nov_m%%.ctl;kindname="ensemble UKMO";climfield="1Nov snow depth";;
ens_ukmo_snd_dec) file=UKMO/monthly/ukmo_snd_dec_m%%.ctl;kindname="ensemble UKMO";climfield="1Dec snow depth";;

ens_csm_trefht) file=ChallengeData/csmtrefht%%.ctl;kindname="ensemble Challenge";climfield="Tref";;
ens_csm_prec) file=ChallengeData/csmprec%%.ctl;kindname="ensemble Challenge";climfield="prec";;
ens_csm_slp) file=ChallengeData/csmslp%%.ctl;kindname="ensemble Challenge";climfield="SLP";;
ens_csm_z500) file=ChallengeData/csmz500_%%.ctl;kindname="ensemble Challenge";climfield="Z500";;
ens_csm_h2osoil) file=ChallengeData/csmh2osoil%%.ctl;kindname="ensemble Challenge";climfield="soil moisture";;
ens_csm_sst1) file=ChallengeData/csm_sst%%.ctl;kindname="ensemble Challenge";climfield="SST";;
ens_csm_sst) file=ChallengeData/csmsst%%.ctl;kindname="ensemble Challenge";climfield="SST";map='set lat -10 10
set lon 120 290';;
ens_csm_z20) file=ChallengeData/csmz20%%.ctl;kindname="ensemble Challenge";climfield="z20";map='set lat -10 10
set lon 120 290';;
ens_csm_u) file=ChallengeData/csm_u_%%.ctl;kindname="ensemble Challenge";climfield="u";map='set lat -10 10
set lon 120 290';;
ens_csm_h) file=ChallengeData/csm_h_%%.ctl;kindname="ensemble Challenge";climfield="Qtot";map='set lat -10 10
set lon 120 290';;
ens_csm_psl) file=ChallengeData/csmpsl%%.ctl;kindname="ensemble Challenge";climfield="SLP";map='set lat -13 13
set lon 120 290';;
ens_csm_taux) file=ChallengeData/csmtaux%%.ctl;kindname="ensemble Challenge";climfield="taux";map='set lat -13 13
set lon 120 290';;

ens_csm_hicelay) file=ChallengeData/csmhicelay%%.ctl;kindname="ensemble Challenge";climfield="ice thickness";map='set lat 58 90
set mproj nps';;
ens_csm_fice) file=ChallengeData/csmfice%%.ctl;kindname="ensemble Challenge";climfield="ice concentration";map='set lat 58 90
set mproj nps';;
ens_csm_ts) file=ChallengeData/csmts%%.ctl;kindname="ensemble Challenge";climfield="T at ice/snow";map='set lat 58 90
set mproj nps';;
ens_csm_uiceh) file=ChallengeData/csmuiceh%%.ctl;kindname="ensemble Challenge";climfield="zonal ice velocity";map='set lat 58 90
set mproj nps';;
ens_csm_viceh) file=ChallengeData/csmviceh%%.ctl;kindname="ensemble Challenge";climfield="meridional ice velocity";map='set lat 58 90
set mproj nps';;

ens_csm_temp_0) file=ChallengeData/csmtemp0_%%.ctl;kindname="ensemble Challenge";climfield="SST";map='set lat 10 75
set lon 275 380';;
ens_csm_temp_500) file=ChallengeData/csmtemp500_%%.ctl;kindname="ensemble Challenge";climfield="T(500m)";map='set lat 10 75
set lon 275 380';;
ens_csm_temp_1000) file=ChallengeData/csmtemp1000_%%.ctl;kindname="ensemble Challenge";climfield="T(1000m)";map='set lat 10 75
set lon 275 380';;
ens_csm_temp_1500) file=ChallengeData/csmtemp1500_%%.ctl;kindname="ensemble Challenge";climfield="T(1500m)";map='set lat 10 75
set lon 275 380';;
ens_csm_temp_2000) file=ChallengeData/csmtemp2000_%%.ctl;kindname="ensemble Challenge";climfield="T(2000m)";map='set lat 10 75
set lon 275 380';;
ens_csm_temp_3000) file=ChallengeData/csmtemp3000_%%.ctl;kindname="ensemble Challenge";climfield="T(3000m)";map='set lat 10 75
set lon 275 380';;

ens_csm_sal_0) file=ChallengeData/csmsal0_%%.ctl;kindname="ensemble Challenge";climfield="SSS";map='set lat 10 75
set lon 275 380';;
ens_csm_sal_500) file=ChallengeData/csmsal500_%%.ctl;kindname="ensemble Challenge";climfield="S(500m)";map='set lat 10 75
set lon 275 380';;
ens_csm_sal_1000) file=ChallengeData/csmsal1000_%%.ctl;kindname="ensemble Challenge";climfield="S(1000m)";map='set lat 10 75
set lon 275 380';;
ens_csm_sal_1500) file=ChallengeData/csmsal1500_%%.ctl;kindname="ensemble Challenge";climfield="S(1500m)";map='set lat 10 75
set lon 275 380';;
ens_csm_sal_2000) file=ChallengeData/csmsal2000_%%.ctl;kindname="ensemble Challenge";climfield="S(2000m)";map='set lat 10 75
set lon 275 380';;
ens_csm_sal_3000) file=ChallengeData/csmsal3000_%%.ctl;kindname="ensemble Challenge";climfield="S(3000m)";map='set lat 10 75
set lon 275 380';;

ens_csm_dens_0) file=ChallengeData/csmdens0_%%.ctl;kindname="ensemble Challenge";climfield="rho(0m)";map='set lat 10 75
set lon 275 380';;
ens_csm_dens_500) file=ChallengeData/csmdens500_%%.ctl;kindname="ensemble Challenge";climfield="rho(500m)";map='set lat 10 75
set lon 275 380';;
ens_csm_dens_1000) file=ChallengeData/csmdens1000_%%.ctl;kindname="ensemble Challenge";climfield="rho(1000m)";map='set lat 10 75
set lon 275 380';;
ens_csm_dens_1500) file=ChallengeData/csmdens1500_%%.ctl;kindname="ensemble Challenge";climfield="rho(1500m)";map='set lat 10 75
set lon 275 380';;
ens_csm_dens_2000) file=ChallengeData/csmdens2000_%%.ctl;kindname="ensemble Challenge";climfield="rho(2000m)";map='set lat 10 75
set lon 275 380';;
ens_csm_dens_3000) file=ChallengeData/csmdens3000_%%.ctl;kindname="ensemble Challenge";climfield="rho(3000m)";map='set lat 10 75
set lon 275 380';;

ens_csm_ot) file=ChallengeData/csmot%%.ctl;kindname="ensemble Challenge";climfield="overturning";ylint='500';map='set lat -5500 0
set lon -40 80
set mproj off';;

csm_trefht) file=ChallengeData/csmtrefht_ave.nc;kindname="average Challenge";climfield="Tref";;
csm_prec) file=ChallengeData/csmprec_ave.nc;kindname="average Challenge";climfield="prec";;
csm_slp) file=ChallengeData/csmslp_ave.nc;kindname="average Challenge";climfield="SLP";;
csm_z500) file=ChallengeData/csmz500_ave.nc;kindname="average Challenge";climfield="Z500";;
csm_h2osoil) file=ChallengeData/csmh2osoil_ave.nc;kindname="average Challenge";climfield="soil moisture";;
csm_sst) file=ChallengeData/csmsst_ave.nc;kindname="average Challenge";climfield="SST";map='set lat -10 10
set lon 120 290';;
csm_z20) file=ChallengeData/csmz20_ave.nc;kindname="average Challenge";climfield="z20";map='set lat -10 10
set lon 120 290';;
csm_psl) file=ChallengeData/csmpsl_ave.nc;kindname="average Challenge";climfield="SLP";map='set lat -13 13
set lon 120 290';;
csm_taux) file=ChallengeData/csmtaux_ave.nc;kindname="average Challenge";climfield="taux";map='set lat -13 13
set lon 120 290';;

csm_tmin_daily) file=ChallengeData/csm_tmin_%%.ctl;kindname="ensemble Challenge";climfield="Tmin";NPERYEAR=365;;
csm_tmax_daily) file=ChallengeData/csm_tmax_%%.ctl;kindname="ensemble Challenge";climfield="Tmax";NPERYEAR=365;;
csm_prec_daily) file=ChallengeData/csm_prec_%%.ctl;kindname="ensemble Challenge";climfield="Prec";NPERYEAR=365;;
csm_psl_daily) file=ChallengeData/csm_psl_%%.ctl;kindname="ensemble Challenge";climfield="PSL";NPERYEAR=365;;
csm_z500_daily) file=ChallengeData/csm_z501_%%.ctl;kindname="ensemble Challenge";climfield="Z500";NPERYEAR=365;;

demeter_era40_t2m) file=DemeterData/era40_p2m_t.ctl;kindname="ERA40";climfield="T2m";;
demeter_era40_tp) file=DemeterData/era40_tp.ctl;kindname="ERA40";climfield="precip";;
demeter_era40_msl) file=DemeterData/era40_msl.ctl;kindname="ERA40";climfield="SLP";;
demeter_era40_z500) file=ERA40/era40_z500.ctl;kindname="ERA40";climfield="z500";;
demeter_era40_u10) file=DemeterData/era40_p10m_u.ctl;kindname="ERA40";climfield="10m u-wind";;
demeter_era40_v10) file=DemeterData/era40_p10m_v.ctl;kindname="ERA40";climfield="10m v-wind";;
demeter_era40_tsfc) file=DemeterData/era40_st_stl1.ctl;kindname="ERA40";climfield="Tsfc";;

demeter_meteofrance_t2m_feb) file=DemeterData/meteofrance_p2m_t_feb.ctl;kindname="Demeter Meteo France";climfield="1Feb T2m";;
demeter_meteofrance_t2m_may) file=DemeterData/meteofrance_p2m_t_may.ctl;kindname="Demeter Meteo France";climfield="1May T2m";;
demeter_meteofrance_t2m_aug) file=DemeterData/meteofrance_p2m_t_aug.ctl;kindname="Demeter Meteo France";climfield="1Aug T2m";;
demeter_meteofrance_t2m_nov) file=DemeterData/meteofrance_p2m_t_nov.ctl;kindname="Demeter Meteo France";climfield="1Nov T2m";;
demeter_meteofrance_prcp_feb) file=DemeterData/meteofrance_tp_feb.ctl;kindname="Demeter Meteo France";climfield="1Feb precip";;
demeter_meteofrance_prcp_may) file=DemeterData/meteofrance_tp_may.ctl;kindname="Demeter Meteo France";climfield="1May precip";;
demeter_meteofrance_prcp_aug) file=DemeterData/meteofrance_tp_aug.ctl;kindname="Demeter Meteo France";climfield="1Aug precip";;
demeter_meteofrance_prcp_nov) file=DemeterData/meteofrance_tp_nov.ctl;kindname="Demeter Meteo France";climfield="1Nov precip";;
demeter_meteofrance_msl_feb) file=DemeterData/meteofrance_msl_feb.ctl;kindname="Demeter Meteo France";climfield="1Feb SLP";;
demeter_meteofrance_msl_may) file=DemeterData/meteofrance_msl_may.ctl;kindname="Demeter Meteo France";climfield="1May SLP";;
demeter_meteofrance_msl_aug) file=DemeterData/meteofrance_msl_aug.ctl;kindname="Demeter Meteo France";climfield="1Aug SLP";;
demeter_meteofrance_msl_nov) file=DemeterData/meteofrance_msl_nov.ctl;kindname="Demeter Meteo France";climfield="1Nov SLP";;
demeter_meteofrance_z500_feb) file=DemeterData/meteofrance_z500_feb.ctl;kindname="Demeter Meteo France";climfield="1Feb z500";;
demeter_meteofrance_z500_may) file=DemeterData/meteofrance_z500_may.ctl;kindname="Demeter Meteo France";climfield="1May z500";;
demeter_meteofrance_z500_aug) file=DemeterData/meteofrance_z500_aug.ctl;kindname="Demeter Meteo France";climfield="1Aug z500";;
demeter_meteofrance_z500_nov) file=DemeterData/meteofrance_z500_nov.ctl;kindname="Demeter Meteo France";climfield="1Nov z500";;
demeter_meteofrance_u10_feb) file=DemeterData/meteofrance_p10m_u_feb.ctl;kindname="Demeter Meteo France";climfield="1Feb 10m u-wind";;
demeter_meteofrance_u10_may) file=DemeterData/meteofrance_p10m_u_may.ctl;kindname="Demeter Meteo France";climfield="1May 10m u-wind";;
demeter_meteofrance_u10_aug) file=DemeterData/meteofrance_p10m_u_aug.ctl;kindname="Demeter Meteo France";climfield="1Aug 10m u-wind";;
demeter_meteofrance_u10_nov) file=DemeterData/meteofrance_p10m_u_nov.ctl;kindname="Demeter Meteo France";climfield="1Nov 10m u-wind";;
demeter_meteofrance_v10_feb) file=DemeterData/meteofrance_p10m_v_feb.ctl;kindname="Demeter Meteo France";climfield="1Feb 10m v-wind";;
demeter_meteofrance_v10_may) file=DemeterData/meteofrance_p10m_v_may.ctl;kindname="Demeter Meteo France";climfield="1May 10m v-wind";;
demeter_meteofrance_v10_aug) file=DemeterData/meteofrance_p10m_v_aug.ctl;kindname="Demeter Meteo France";climfield="1Aug 10m v-wind";;
demeter_meteofrance_v10_nov) file=DemeterData/meteofrance_p10m_v_nov.ctl;kindname="Demeter Meteo France";climfield="1Nov 10m v-wind";;
demeter_meteofrance_tsfc_feb) file=DemeterData/meteofrance_st_stl1_feb.ctl;kindname="Demeter Meteo France";climfield="1Feb Tsfc";;
demeter_meteofrance_tsfc_may) file=DemeterData/meteofrance_st_stl1_may.ctl;kindname="Demeter Meteo France";climfield="1May Tsfc";;
demeter_meteofrance_tsfc_aug) file=DemeterData/meteofrance_st_stl1_aug.ctl;kindname="Demeter Meteo France";climfield="1Aug Tsfc";;
demeter_meteofrance_tsfc_nov) file=DemeterData/meteofrance_st_stl1_nov.ctl;kindname="Demeter Meteo France";climfield="1Nov Tsfc";;

ens_demeter_meteofrance_t2m_feb) file=DemeterData/meteofrance_p2m_t_feb_%%.ctl;kindname="ens Demeter Meteo France";climfield="1Feb T2m";;
ens_demeter_meteofrance_t2m_may) file=DemeterData/meteofrance_p2m_t_may_%%.ctl;kindname="ens Demeter Meteo France";climfield="1May T2m";;
ens_demeter_meteofrance_t2m_aug) file=DemeterData/meteofrance_p2m_t_aug_%%.ctl;kindname="ens Demeter Meteo France";climfield="1Aug T2m";;
ens_demeter_meteofrance_t2m_nov) file=DemeterData/meteofrance_p2m_t_nov_%%.ctl;kindname="ens Demeter Meteo France";climfield="1Nov T2m";;
ens_demeter_meteofrance_prcp_feb) file=DemeterData/meteofrance_tp_feb_%%.ctl;kindname="ens Demeter Meteo France";climfield="1Feb precip";;
ens_demeter_meteofrance_prcp_may) file=DemeterData/meteofrance_tp_may_%%.ctl;kindname="ens Demeter Meteo France";climfield="1May precip";;
ens_demeter_meteofrance_prcp_aug) file=DemeterData/meteofrance_tp_aug_%%.ctl;kindname="ens Demeter Meteo France";climfield="1Aug precip";;
ens_demeter_meteofrance_prcp_nov) file=DemeterData/meteofrance_tp_nov_%%.ctl;kindname="ens Demeter Meteo France";climfield="1Nov precip";;
ens_demeter_meteofrance_msl_feb) file=DemeterData/meteofrance_msl_feb_%%.ctl;kindname="ens Demeter Meteo France";climfield="1Feb SLP";;
ens_demeter_meteofrance_msl_may) file=DemeterData/meteofrance_msl_may_%%.ctl;kindname="ens Demeter Meteo France";climfield="1May SLP";;
ens_demeter_meteofrance_msl_aug) file=DemeterData/meteofrance_msl_aug_%%.ctl;kindname="ens Demeter Meteo France";climfield="1Aug SLP";;
ens_demeter_meteofrance_msl_nov) file=DemeterData/meteofrance_msl_nov_%%.ctl;kindname="ens Demeter Meteo France";climfield="1Nov SLP";;
ens_demeter_meteofrance_z500_feb) file=DemeterData/meteofrance_z500_feb_%%.ctl;kindname="ens Demeter Meteo France";climfield="1Feb z500";;
ens_demeter_meteofrance_z500_may) file=DemeterData/meteofrance_z500_may_%%.ctl;kindname="ens Demeter Meteo France";climfield="1May z500";;
ens_demeter_meteofrance_z500_aug) file=DemeterData/meteofrance_z500_aug_%%.ctl;kindname="ens Demeter Meteo France";climfield="1Aug z500";;
ens_demeter_meteofrance_z500_nov) file=DemeterData/meteofrance_z500_nov_%%.ctl;kindname="ens Demeter Meteo France";climfield="1Nov z500";;
ens_demeter_meteofrance_u10_feb) file=DemeterData/meteofrance_p10m_u_feb_%%.ctl;kindname="ens Demeter Meteo France";climfield="1Feb 10m u-wind";;
ens_demeter_meteofrance_u10_may) file=DemeterData/meteofrance_p10m_u_may_%%.ctl;kindname="ens Demeter Meteo France";climfield="1May 10m u-wind";;
ens_demeter_meteofrance_u10_aug) file=DemeterData/meteofrance_p10m_u_aug_%%.ctl;kindname="ens Demeter Meteo France";climfield="1Aug 10m u-wind";;
ens_demeter_meteofrance_u10_nov) file=DemeterData/meteofrance_p10m_u_nov_%%.ctl;kindname="ens Demeter Meteo France";climfield="1Nov 10m u-wind";;
ens_demeter_meteofrance_v10_feb) file=DemeterData/meteofrance_p10m_v_feb_%%.ctl;kindname="ens Demeter Meteo France";climfield="1Feb 10m v-wind";;
ens_demeter_meteofrance_v10_may) file=DemeterData/meteofrance_p10m_v_may_%%.ctl;kindname="ens Demeter Meteo France";climfield="1May 10m v-wind";;
ens_demeter_meteofrance_v10_aug) file=DemeterData/meteofrance_p10m_v_aug_%%.ctl;kindname="ens Demeter Meteo France";climfield="1Aug 10m v-wind";;
ens_demeter_meteofrance_v10_nov) file=DemeterData/meteofrance_p10m_v_nov_%%.ctl;kindname="ens Demeter Meteo France";climfield="1Nov 10m v-wind";;
ens_demeter_meteofrance_tsfc_feb) file=DemeterData/meteofrance_st_stl1_feb_%%.ctl;kindname="ens Demeter Meteo France";climfield="1Feb Tsfc";;
ens_demeter_meteofrance_tsfc_may) file=DemeterData/meteofrance_st_stl1_may_%%.ctl;kindname="ens Demeter Meteo France";climfield="1May Tsfc";;
ens_demeter_meteofrance_tsfc_aug) file=DemeterData/meteofrance_st_stl1_aug_%%.ctl;kindname="ens Demeter Meteo France";climfield="1Aug Tsfc";;
ens_demeter_meteofrance_tsfc_nov) file=DemeterData/meteofrance_st_stl1_nov_%%.ctl;kindname="ens Demeter Meteo France";climfield="1Nov Tsfc";;

demeter_cerfacs_t2m_feb) file=DemeterData/cerfacs_p2m_t_feb.ctl;kindname="Demeter CERFACS";climfield="1Feb T2m";;
demeter_cerfacs_t2m_may) file=DemeterData/cerfacs_p2m_t_may.ctl;kindname="Demeter CERFACS";climfield="1May T2m";;
demeter_cerfacs_t2m_aug) file=DemeterData/cerfacs_p2m_t_aug.ctl;kindname="Demeter CERFACS";climfield="1Aug T2m";;
demeter_cerfacs_t2m_nov) file=DemeterData/cerfacs_p2m_t_nov.ctl;kindname="Demeter CERFACS";climfield="1Nov T2m";;
demeter_cerfacs_prcp_feb) file=DemeterData/cerfacs_tp_feb.ctl;kindname="Demeter CERFACS";climfield="1Feb precip";;
demeter_cerfacs_prcp_may) file=DemeterData/cerfacs_tp_may.ctl;kindname="Demeter CERFACS";climfield="1May precip";;
demeter_cerfacs_prcp_aug) file=DemeterData/cerfacs_tp_aug.ctl;kindname="Demeter CERFACS";climfield="1Aug precip";;
demeter_cerfacs_prcp_nov) file=DemeterData/cerfacs_tp_nov.ctl;kindname="Demeter CERFACS";climfield="1Nov precip";;
demeter_cerfacs_msl_feb) file=DemeterData/cerfacs_msl_feb.ctl;kindname="Demeter CERFACS";climfield="1Feb SLP";;
demeter_cerfacs_msl_may) file=DemeterData/cerfacs_msl_may.ctl;kindname="Demeter CERFACS";climfield="1May SLP";;
demeter_cerfacs_msl_aug) file=DemeterData/cerfacs_msl_aug.ctl;kindname="Demeter CERFACS";climfield="1Aug SLP";;
demeter_cerfacs_msl_nov) file=DemeterData/cerfacs_msl_nov.ctl;kindname="Demeter CERFACS";climfield="1Nov SLP";;
demeter_cerfacs_z500_feb) file=DemeterData/cerfacs_z500_feb.ctl;kindname="Demeter CERFACS";climfield="1Feb z500";;
demeter_cerfacs_z500_may) file=DemeterData/cerfacs_z500_may.ctl;kindname="Demeter CERFACS";climfield="1May z500";;
demeter_cerfacs_z500_aug) file=DemeterData/cerfacs_z500_aug.ctl;kindname="Demeter CERFACS";climfield="1Aug z500";;
demeter_cerfacs_z500_nov) file=DemeterData/cerfacs_z500_nov.ctl;kindname="Demeter CERFACS";climfield="1Nov z500";;
demeter_cerfacs_u10_feb) file=DemeterData/cerfacs_p10m_u_feb.ctl;kindname="Demeter CERFACS";climfield="1Feb 10m u-wind";;
demeter_cerfacs_u10_may) file=DemeterData/cerfacs_p10m_u_may.ctl;kindname="Demeter CERFACS";climfield="1May 10m u-wind";;
demeter_cerfacs_u10_aug) file=DemeterData/cerfacs_p10m_u_aug.ctl;kindname="Demeter CERFACS";climfield="1Aug 10m u-wind";;
demeter_cerfacs_u10_nov) file=DemeterData/cerfacs_p10m_u_nov.ctl;kindname="Demeter CERFACS";climfield="1Nov 10m u-wind";;
demeter_cerfacs_v10_feb) file=DemeterData/cerfacs_p10m_v_feb.ctl;kindname="Demeter CERFACS";climfield="1Feb 10m v-wind";;
demeter_cerfacs_v10_may) file=DemeterData/cerfacs_p10m_v_may.ctl;kindname="Demeter CERFACS";climfield="1May 10m v-wind";;
demeter_cerfacs_v10_aug) file=DemeterData/cerfacs_p10m_v_aug.ctl;kindname="Demeter CERFACS";climfield="1Aug 10m v-wind";;
demeter_cerfacs_v10_nov) file=DemeterData/cerfacs_p10m_v_nov.ctl;kindname="Demeter CERFACS";climfield="1Nov 10m v-wind";;
demeter_cerfacs_tsfc_feb) file=DemeterData/cerfacs_st_stl1_feb.ctl;kindname="Demeter CERFACS";climfield="1Feb Tsfc";;
demeter_cerfacs_tsfc_may) file=DemeterData/cerfacs_st_stl1_may.ctl;kindname="Demeter CERFACS";climfield="1May Tsfc";;
demeter_cerfacs_tsfc_aug) file=DemeterData/cerfacs_st_stl1_aug.ctl;kindname="Demeter CERFACS";climfield="1Aug Tsfc";;
demeter_cerfacs_tsfc_nov) file=DemeterData/cerfacs_st_stl1_nov.ctl;kindname="Demeter CERFACS";climfield="1Nov Tsfc";;

ens_demeter_cerfacs_t2m_feb) file=DemeterData/cerfacs_p2m_t_feb_%%.ctl;kindname="ens Demeter CERFACS";climfield="1Feb T2m";;
ens_demeter_cerfacs_t2m_may) file=DemeterData/cerfacs_p2m_t_may_%%.ctl;kindname="ens Demeter CERFACS";climfield="1May T2m";;
ens_demeter_cerfacs_t2m_aug) file=DemeterData/cerfacs_p2m_t_aug_%%.ctl;kindname="ens Demeter CERFACS";climfield="1Aug T2m";;
ens_demeter_cerfacs_t2m_nov) file=DemeterData/cerfacs_p2m_t_nov_%%.ctl;kindname="ens Demeter CERFACS";climfield="1Nov T2m";;
ens_demeter_cerfacs_prcp_feb) file=DemeterData/cerfacs_tp_feb_%%.ctl;kindname="ens Demeter CERFACS";climfield="1Feb precip";;
ens_demeter_cerfacs_prcp_may) file=DemeterData/cerfacs_tp_may_%%.ctl;kindname="ens Demeter CERFACS";climfield="1May precip";;
ens_demeter_cerfacs_prcp_aug) file=DemeterData/cerfacs_tp_aug_%%.ctl;kindname="ens Demeter CERFACS";climfield="1Aug precip";;
ens_demeter_cerfacs_prcp_nov) file=DemeterData/cerfacs_tp_nov_%%.ctl;kindname="ens Demeter CERFACS";climfield="1Nov precip";;
ens_demeter_cerfacs_msl_feb) file=DemeterData/cerfacs_msl_feb_%%.ctl;kindname="ens Demeter CERFACS";climfield="1Feb SLP";;
ens_demeter_cerfacs_msl_may) file=DemeterData/cerfacs_msl_may_%%.ctl;kindname="ens Demeter CERFACS";climfield="1May SLP";;
ens_demeter_cerfacs_msl_aug) file=DemeterData/cerfacs_msl_aug_%%.ctl;kindname="ens Demeter CERFACS";climfield="1Aug SLP";;
ens_demeter_cerfacs_msl_nov) file=DemeterData/cerfacs_msl_nov_%%.ctl;kindname="ens Demeter CERFACS";climfield="1Nov SLP";;
ens_demeter_cerfacs_z500_feb) file=DemeterData/cerfacs_z500_feb_%%.ctl;kindname="ens Demeter CERFACS";climfield="1Feb z500";;
ens_demeter_cerfacs_z500_may) file=DemeterData/cerfacs_z500_may_%%.ctl;kindname="ens Demeter CERFACS";climfield="1May z500";;
ens_demeter_cerfacs_z500_aug) file=DemeterData/cerfacs_z500_aug_%%.ctl;kindname="ens Demeter CERFACS";climfield="1Aug z500";;
ens_demeter_cerfacs_z500_nov) file=DemeterData/cerfacs_z500_nov_%%.ctl;kindname="ens Demeter CERFACS";climfield="1Nov z500";;
ens_demeter_cerfacs_u10_feb) file=DemeterData/cerfacs_p10m_u_feb_%%.ctl;kindname="ens Demeter CERFACS";climfield="1Feb 10m u-wind";;
ens_demeter_cerfacs_u10_may) file=DemeterData/cerfacs_p10m_u_may_%%.ctl;kindname="ens Demeter CERFACS";climfield="1May 10m u-wind";;
ens_demeter_cerfacs_u10_aug) file=DemeterData/cerfacs_p10m_u_aug_%%.ctl;kindname="ens Demeter CERFACS";climfield="1Aug 10m u-wind";;
ens_demeter_cerfacs_u10_nov) file=DemeterData/cerfacs_p10m_u_nov_%%.ctl;kindname="ens Demeter CERFACS";climfield="1Nov 10m u-wind";;
ens_demeter_cerfacs_v10_feb) file=DemeterData/cerfacs_p10m_v_feb_%%.ctl;kindname="ens Demeter CERFACS";climfield="1Feb 10m v-wind";;
ens_demeter_cerfacs_v10_may) file=DemeterData/cerfacs_p10m_v_may_%%.ctl;kindname="ens Demeter CERFACS";climfield="1May 10m v-wind";;
ens_demeter_cerfacs_v10_aug) file=DemeterData/cerfacs_p10m_v_aug_%%.ctl;kindname="ens Demeter CERFACS";climfield="1Aug 10m v-wind";;
ens_demeter_cerfacs_v10_nov) file=DemeterData/cerfacs_p10m_v_nov_%%.ctl;kindname="ens Demeter CERFACS";climfield="1Nov 10m v-wind";;
ens_demeter_cerfacs_tsfc_feb) file=DemeterData/cerfacs_st_stl1_feb_%%.ctl;kindname="ens Demeter CERFACS";climfield="1Feb Tsfc";;
ens_demeter_cerfacs_tsfc_may) file=DemeterData/cerfacs_st_stl1_may_%%.ctl;kindname="ens Demeter CERFACS";climfield="1May Tsfc";;
ens_demeter_cerfacs_tsfc_aug) file=DemeterData/cerfacs_st_stl1_aug_%%.ctl;kindname="ens Demeter CERFACS";climfield="1Aug Tsfc";;
ens_demeter_cerfacs_tsfc_nov) file=DemeterData/cerfacs_st_stl1_nov_%%.ctl;kindname="ens Demeter CERFACS";climfield="1Nov Tsfc";;

demeter_lodyc_t2m_feb) file=DemeterData/lodyc_p2m_t_feb.ctl;kindname="Demeter LODYC";climfield="1Feb T2m";;
demeter_lodyc_t2m_may) file=DemeterData/lodyc_p2m_t_may.ctl;kindname="Demeter LODYC";climfield="1May T2m";;
demeter_lodyc_t2m_aug) file=DemeterData/lodyc_p2m_t_aug.ctl;kindname="Demeter LODYC";climfield="1Aug T2m";;
demeter_lodyc_t2m_nov) file=DemeterData/lodyc_p2m_t_nov.ctl;kindname="Demeter LODYC";climfield="1Nov T2m";;
demeter_lodyc_prcp_feb) file=DemeterData/lodyc_tp_feb.ctl;kindname="Demeter LODYC";climfield="1Feb precip";;
demeter_lodyc_prcp_may) file=DemeterData/lodyc_tp_may.ctl;kindname="Demeter LODYC";climfield="1May precip";;
demeter_lodyc_prcp_aug) file=DemeterData/lodyc_tp_aug.ctl;kindname="Demeter LODYC";climfield="1Aug precip";;
demeter_lodyc_prcp_nov) file=DemeterData/lodyc_tp_nov.ctl;kindname="Demeter LODYC";climfield="1Nov precip";;
demeter_lodyc_msl_feb) file=DemeterData/lodyc_msl_feb.ctl;kindname="Demeter LODYC";climfield="1Feb SLP";;
demeter_lodyc_msl_may) file=DemeterData/lodyc_msl_may.ctl;kindname="Demeter LODYC";climfield="1May SLP";;
demeter_lodyc_msl_aug) file=DemeterData/lodyc_msl_aug.ctl;kindname="Demeter LODYC";climfield="1Aug SLP";;
demeter_lodyc_msl_nov) file=DemeterData/lodyc_msl_nov.ctl;kindname="Demeter LODYC";climfield="1Nov SLP";;
demeter_lodyc_z500_feb) file=DemeterData/lodyc_z500_feb.ctl;kindname="Demeter LODYC";climfield="1Feb z500";;
demeter_lodyc_z500_may) file=DemeterData/lodyc_z500_may.ctl;kindname="Demeter LODYC";climfield="1May z500";;
demeter_lodyc_z500_aug) file=DemeterData/lodyc_z500_aug.ctl;kindname="Demeter LODYC";climfield="1Aug z500";;
demeter_lodyc_z500_nov) file=DemeterData/lodyc_z500_nov.ctl;kindname="Demeter LODYC";climfield="1Nov z500";;
demeter_lodyc_u10_feb) file=DemeterData/lodyc_p10m_u_feb.ctl;kindname="Demeter LODYC";climfield="1Feb 10m u-wind";;
demeter_lodyc_u10_may) file=DemeterData/lodyc_p10m_u_may.ctl;kindname="Demeter LODYC";climfield="1May 10m u-wind";;
demeter_lodyc_u10_aug) file=DemeterData/lodyc_p10m_u_aug.ctl;kindname="Demeter LODYC";climfield="1Aug 10m u-wind";;
demeter_lodyc_u10_nov) file=DemeterData/lodyc_p10m_u_nov.ctl;kindname="Demeter LODYC";climfield="1Nov 10m u-wind";;
demeter_lodyc_v10_feb) file=DemeterData/lodyc_p10m_v_feb.ctl;kindname="Demeter LODYC";climfield="1Feb 10m v-wind";;
demeter_lodyc_v10_may) file=DemeterData/lodyc_p10m_v_may.ctl;kindname="Demeter LODYC";climfield="1May 10m v-wind";;
demeter_lodyc_v10_aug) file=DemeterData/lodyc_p10m_v_aug.ctl;kindname="Demeter LODYC";climfield="1Aug 10m v-wind";;
demeter_lodyc_v10_nov) file=DemeterData/lodyc_p10m_v_nov.ctl;kindname="Demeter LODYC";climfield="1Nov 10m v-wind";;
demeter_lodyc_tsfc_feb) file=DemeterData/lodyc_st_stl1_feb.ctl;kindname="Demeter LODYC";climfield="1Feb Tsfc";;
demeter_lodyc_tsfc_may) file=DemeterData/lodyc_st_stl1_may.ctl;kindname="Demeter LODYC";climfield="1May Tsfc";;
demeter_lodyc_tsfc_aug) file=DemeterData/lodyc_st_stl1_aug.ctl;kindname="Demeter LODYC";climfield="1Aug Tsfc";;
demeter_lodyc_tsfc_nov) file=DemeterData/lodyc_st_stl1_nov.ctl;kindname="Demeter LODYC";climfield="1Nov Tsfc";;

ens_demeter_lodyc_t2m_feb) file=DemeterData/lodyc_p2m_t_feb_%%.ctl;kindname="ens Demeter LODYC";climfield="1Feb T2m";;
ens_demeter_lodyc_t2m_may) file=DemeterData/lodyc_p2m_t_may_%%.ctl;kindname="ens Demeter LODYC";climfield="1May T2m";;
ens_demeter_lodyc_t2m_aug) file=DemeterData/lodyc_p2m_t_aug_%%.ctl;kindname="ens Demeter LODYC";climfield="1Aug T2m";;
ens_demeter_lodyc_t2m_nov) file=DemeterData/lodyc_p2m_t_nov_%%.ctl;kindname="ens Demeter LODYC";climfield="1Nov T2m";;
ens_demeter_lodyc_prcp_feb) file=DemeterData/lodyc_tp_feb_%%.ctl;kindname="ens Demeter LODYC";climfield="1Feb precip";;
ens_demeter_lodyc_prcp_may) file=DemeterData/lodyc_tp_may_%%.ctl;kindname="ens Demeter LODYC";climfield="1May precip";;
ens_demeter_lodyc_prcp_aug) file=DemeterData/lodyc_tp_aug_%%.ctl;kindname="ens Demeter LODYC";climfield="1Aug precip";;
ens_demeter_lodyc_prcp_nov) file=DemeterData/lodyc_tp_nov_%%.ctl;kindname="ens Demeter LODYC";climfield="1Nov precip";;
ens_demeter_lodyc_msl_feb) file=DemeterData/lodyc_msl_feb_%%.ctl;kindname="ens Demeter LODYC";climfield="1Feb SLP";;
ens_demeter_lodyc_msl_may) file=DemeterData/lodyc_msl_may_%%.ctl;kindname="ens Demeter LODYC";climfield="1May SLP";;
ens_demeter_lodyc_msl_aug) file=DemeterData/lodyc_msl_aug_%%.ctl;kindname="ens Demeter LODYC";climfield="1Aug SLP";;
ens_demeter_lodyc_msl_nov) file=DemeterData/lodyc_msl_nov_%%.ctl;kindname="ens Demeter LODYC";climfield="1Nov SLP";;
ens_demeter_lodyc_z500_feb) file=DemeterData/lodyc_z500_feb_%%.ctl;kindname="ens Demeter LODYC";climfield="1Feb z500";;
ens_demeter_lodyc_z500_may) file=DemeterData/lodyc_z500_may_%%.ctl;kindname="ens Demeter LODYC";climfield="1May z500";;
ens_demeter_lodyc_z500_aug) file=DemeterData/lodyc_z500_aug_%%.ctl;kindname="ens Demeter LODYC";climfield="1Aug z500";;
ens_demeter_lodyc_z500_nov) file=DemeterData/lodyc_z500_nov_%%.ctl;kindname="ens Demeter LODYC";climfield="1Nov z500";;
ens_demeter_lodyc_u10_feb) file=DemeterData/lodyc_p10m_u_feb_%%.ctl;kindname="ens Demeter LODYC";climfield="1Feb 10m u-wind";;
ens_demeter_lodyc_u10_may) file=DemeterData/lodyc_p10m_u_may_%%.ctl;kindname="ens Demeter LODYC";climfield="1May 10m u-wind";;
ens_demeter_lodyc_u10_aug) file=DemeterData/lodyc_p10m_u_aug_%%.ctl;kindname="ens Demeter LODYC";climfield="1Aug 10m u-wind";;
ens_demeter_lodyc_u10_nov) file=DemeterData/lodyc_p10m_u_nov_%%.ctl;kindname="ens Demeter LODYC";climfield="1Nov 10m u-wind";;
ens_demeter_lodyc_v10_feb) file=DemeterData/lodyc_p10m_v_feb_%%.ctl;kindname="ens Demeter LODYC";climfield="1Feb 10m v-wind";;
ens_demeter_lodyc_v10_may) file=DemeterData/lodyc_p10m_v_may_%%.ctl;kindname="ens Demeter LODYC";climfield="1May 10m v-wind";;
ens_demeter_lodyc_v10_aug) file=DemeterData/lodyc_p10m_v_aug_%%.ctl;kindname="ens Demeter LODYC";climfield="1Aug 10m v-wind";;
ens_demeter_lodyc_v10_nov) file=DemeterData/lodyc_p10m_v_nov_%%.ctl;kindname="ens Demeter LODYC";climfield="1Nov 10m v-wind";;
ens_demeter_lodyc_tsfc_feb) file=DemeterData/lodyc_st_stl1_feb_%%.ctl;kindname="ens Demeter LODYC";climfield="1Feb Tsfc";;
ens_demeter_lodyc_tsfc_may) file=DemeterData/lodyc_st_stl1_may_%%.ctl;kindname="ens Demeter LODYC";climfield="1May Tsfc";;
ens_demeter_lodyc_tsfc_aug) file=DemeterData/lodyc_st_stl1_aug_%%.ctl;kindname="ens Demeter LODYC";climfield="1Aug Tsfc";;
ens_demeter_lodyc_tsfc_nov) file=DemeterData/lodyc_st_stl1_nov_%%.ctl;kindname="ens Demeter LODYC";climfield="1Nov Tsfc";;

demeter_ingv_t2m_feb) file=DemeterData/ingv_p2m_t_feb.ctl;kindname="Demeter INGV";climfield="1Feb T2m";;
demeter_ingv_t2m_may) file=DemeterData/ingv_p2m_t_may.ctl;kindname="Demeter INGV";climfield="1May T2m";;
demeter_ingv_t2m_aug) file=DemeterData/ingv_p2m_t_aug.ctl;kindname="Demeter INGV";climfield="1Aug T2m";;
demeter_ingv_t2m_nov) file=DemeterData/ingv_p2m_t_nov.ctl;kindname="Demeter INGV";climfield="1Nov T2m";;
demeter_ingv_prcp_feb) file=DemeterData/ingv_tp_feb.ctl;kindname="Demeter INGV";climfield="1Feb precip";;
demeter_ingv_prcp_may) file=DemeterData/ingv_tp_may.ctl;kindname="Demeter INGV";climfield="1May precip";;
demeter_ingv_prcp_aug) file=DemeterData/ingv_tp_aug.ctl;kindname="Demeter INGV";climfield="1Aug precip";;
demeter_ingv_prcp_nov) file=DemeterData/ingv_tp_nov.ctl;kindname="Demeter INGV";climfield="1Nov precip";;
demeter_ingv_z500_feb) file=DemeterData/ingv_z500_feb.ctl;kindname="Demeter INGV";climfield="1Feb z500";;
demeter_ingv_z500_may) file=DemeterData/ingv_z500_may.ctl;kindname="Demeter INGV";climfield="1May z500";;
demeter_ingv_z500_aug) file=DemeterData/ingv_z500_aug.ctl;kindname="Demeter INGV";climfield="1Aug z500";;
demeter_ingv_z500_nov) file=DemeterData/ingv_z500_nov.ctl;kindname="Demeter INGV";climfield="1Nov z500";;
demeter_ingv_u10_feb) file=DemeterData/ingv_p10m_u_feb.ctl;kindname="Demeter INGV";climfield="1Feb 10m u-wind";;
demeter_ingv_u10_may) file=DemeterData/ingv_p10m_u_may.ctl;kindname="Demeter INGV";climfield="1May 10m u-wind";;
demeter_ingv_u10_aug) file=DemeterData/ingv_p10m_u_aug.ctl;kindname="Demeter INGV";climfield="1Aug 10m u-wind";;
demeter_ingv_u10_nov) file=DemeterData/ingv_p10m_u_nov.ctl;kindname="Demeter INGV";climfield="1Nov 10m u-wind";;
demeter_ingv_v10_feb) file=DemeterData/ingv_p10m_v_feb.ctl;kindname="Demeter INGV";climfield="1Feb 10m v-wind";;
demeter_ingv_v10_may) file=DemeterData/ingv_p10m_v_may.ctl;kindname="Demeter INGV";climfield="1May 10m v-wind";;
demeter_ingv_v10_aug) file=DemeterData/ingv_p10m_v_aug.ctl;kindname="Demeter INGV";climfield="1Aug 10m v-wind";;
demeter_ingv_v10_nov) file=DemeterData/ingv_p10m_v_nov.ctl;kindname="Demeter INGV";climfield="1Nov 10m v-wind";;
demeter_ingv_tsfc_feb) file=DemeterData/ingv_st_stl1_feb.ctl;kindname="Demeter INGV";climfield="1Feb Tsfc";;
demeter_ingv_tsfc_may) file=DemeterData/ingv_st_stl1_may.ctl;kindname="Demeter INGV";climfield="1May Tsfc";;
demeter_ingv_tsfc_aug) file=DemeterData/ingv_st_stl1_aug.ctl;kindname="Demeter INGV";climfield="1Aug Tsfc";;
demeter_ingv_tsfc_nov) file=DemeterData/ingv_st_stl1_nov.ctl;kindname="Demeter INGV";climfield="1Nov Tsfc";;

ens_demeter_ingv_t2m_feb) file=DemeterData/ingv_p2m_t_feb_%%.ctl;kindname="ens Demeter INGV";climfield="1Feb T2m";;
ens_demeter_ingv_t2m_may) file=DemeterData/ingv_p2m_t_may_%%.ctl;kindname="ens Demeter INGV";climfield="1May T2m";;
ens_demeter_ingv_t2m_aug) file=DemeterData/ingv_p2m_t_aug_%%.ctl;kindname="ens Demeter INGV";climfield="1Aug T2m";;
ens_demeter_ingv_t2m_nov) file=DemeterData/ingv_p2m_t_nov_%%.ctl;kindname="ens Demeter INGV";climfield="1Nov T2m";;
ens_demeter_ingv_prcp_feb) file=DemeterData/ingv_tp_feb_%%.ctl;kindname="ens Demeter INGV";climfield="1Feb precip";;
ens_demeter_ingv_prcp_may) file=DemeterData/ingv_tp_may_%%.ctl;kindname="ens Demeter INGV";climfield="1May precip";;
ens_demeter_ingv_prcp_aug) file=DemeterData/ingv_tp_aug_%%.ctl;kindname="ens Demeter INGV";climfield="1Aug precip";;
ens_demeter_ingv_prcp_nov) file=DemeterData/ingv_tp_nov_%%.ctl;kindname="ens Demeter INGV";climfield="1Nov precip";;
ens_demeter_ingv_msl_feb) file=DemeterData/ingv_msl_feb_%%.ctl;kindname="ens Demeter INGV";climfield="1Feb SLP";;
ens_demeter_ingv_msl_may) file=DemeterData/ingv_msl_may_%%.ctl;kindname="ens Demeter INGV";climfield="1May SLP";;
ens_demeter_ingv_msl_aug) file=DemeterData/ingv_msl_aug_%%.ctl;kindname="ens Demeter INGV";climfield="1Aug SLP";;
ens_demeter_ingv_msl_nov) file=DemeterData/ingv_msl_nov_%%.ctl;kindname="ens Demeter INGV";climfield="1Nov SLP";;
ens_demeter_ingv_z500_feb) file=DemeterData/ingv_z500_feb_%%.ctl;kindname="ens Demeter INGV";climfield="1Feb z500";;
ens_demeter_ingv_z500_may) file=DemeterData/ingv_z500_may_%%.ctl;kindname="ens Demeter INGV";climfield="1May z500";;
ens_demeter_ingv_z500_aug) file=DemeterData/ingv_z500_aug_%%.ctl;kindname="ens Demeter INGV";climfield="1Aug z500";;
ens_demeter_ingv_z500_nov) file=DemeterData/ingv_z500_nov_%%.ctl;kindname="ens Demeter INGV";climfield="1Nov z500";;
ens_demeter_ingv_u10_feb) file=DemeterData/ingv_p10m_u_feb_%%.ctl;kindname="ens Demeter INGV";climfield="1Feb 10m u-wind";;
ens_demeter_ingv_u10_may) file=DemeterData/ingv_p10m_u_may_%%.ctl;kindname="ens Demeter INGV";climfield="1May 10m u-wind";;
ens_demeter_ingv_u10_aug) file=DemeterData/ingv_p10m_u_aug_%%.ctl;kindname="ens Demeter INGV";climfield="1Aug 10m u-wind";;
ens_demeter_ingv_u10_nov) file=DemeterData/ingv_p10m_u_nov_%%.ctl;kindname="ens Demeter INGV";climfield="1Nov 10m u-wind";;
ens_demeter_ingv_v10_feb) file=DemeterData/ingv_p10m_v_feb_%%.ctl;kindname="ens Demeter INGV";climfield="1Feb 10m v-wind";;
ens_demeter_ingv_v10_may) file=DemeterData/ingv_p10m_v_may_%%.ctl;kindname="ens Demeter INGV";climfield="1May 10m v-wind";;
ens_demeter_ingv_v10_aug) file=DemeterData/ingv_p10m_v_aug_%%.ctl;kindname="ens Demeter INGV";climfield="1Aug 10m v-wind";;
ens_demeter_ingv_v10_nov) file=DemeterData/ingv_p10m_v_nov_%%.ctl;kindname="ens Demeter INGV";climfield="1Nov 10m v-wind";;
ens_demeter_ingv_tsfc_feb) file=DemeterData/ingv_st_stl1_feb_%%.ctl;kindname="ens Demeter INGV";climfield="1Feb Tsfc";;
ens_demeter_ingv_tsfc_may) file=DemeterData/ingv_st_stl1_may_%%.ctl;kindname="ens Demeter INGV";climfield="1May Tsfc";;
ens_demeter_ingv_tsfc_aug) file=DemeterData/ingv_st_stl1_aug_%%.ctl;kindname="ens Demeter INGV";climfield="1Aug Tsfc";;
ens_demeter_ingv_tsfc_nov) file=DemeterData/ingv_st_stl1_nov_%%.ctl;kindname="ens Demeter INGV";climfield="1Nov Tsfc";;

demeter_ecmwf_t2m_feb) file=DemeterData/ecmwf_p2m_t_feb.ctl;kindname="Demeter ECMWF";climfield="1Feb T2m";;
demeter_ecmwf_t2m_may) file=DemeterData/ecmwf_p2m_t_may.ctl;kindname="Demeter ECMWF";climfield="1May T2m";;
demeter_ecmwf_t2m_aug) file=DemeterData/ecmwf_p2m_t_aug.ctl;kindname="Demeter ECMWF";climfield="1Aug T2m";;
demeter_ecmwf_t2m_nov) file=DemeterData/ecmwf_p2m_t_nov.ctl;kindname="Demeter ECMWF";climfield="1Nov T2m";;
demeter_ecmwf_prcp_feb) file=DemeterData/ecmwf_tp_feb.ctl;kindname="Demeter ECMWF";climfield="1Feb precip";;
demeter_ecmwf_prcp_may) file=DemeterData/ecmwf_tp_may.ctl;kindname="Demeter ECMWF";climfield="1May precip";;
demeter_ecmwf_prcp_aug) file=DemeterData/ecmwf_tp_aug.ctl;kindname="Demeter ECMWF";climfield="1Aug precip";;
demeter_ecmwf_prcp_nov) file=DemeterData/ecmwf_tp_nov.ctl;kindname="Demeter ECMWF";climfield="1Nov precip";;
demeter_ecmwf_msl_feb) file=DemeterData/ecmwf_msl_feb.ctl;kindname="Demeter ECMWF";climfield="1Feb SLP";;
demeter_ecmwf_msl_may) file=DemeterData/ecmwf_msl_may.ctl;kindname="Demeter ECMWF";climfield="1May SLP";;
demeter_ecmwf_msl_aug) file=DemeterData/ecmwf_msl_aug.ctl;kindname="Demeter ECMWF";climfield="1Aug SLP";;
demeter_ecmwf_msl_nov) file=DemeterData/ecmwf_msl_nov.ctl;kindname="Demeter ECMWF";climfield="1Nov SLP";;
demeter_ecmwf_z500_feb) file=DemeterData/ecmwf_z500_feb.ctl;kindname="Demeter ECMWF";climfield="1Feb z500";;
demeter_ecmwf_z500_may) file=DemeterData/ecmwf_z500_may.ctl;kindname="Demeter ECMWF";climfield="1May z500";;
demeter_ecmwf_z500_aug) file=DemeterData/ecmwf_z500_aug.ctl;kindname="Demeter ECMWF";climfield="1Aug z500";;
demeter_ecmwf_z500_nov) file=DemeterData/ecmwf_z500_nov.ctl;kindname="Demeter ECMWF";climfield="1Nov z500";;
demeter_ecmwf_u10_feb) file=DemeterData/ecmwf_p10m_u_feb.ctl;kindname="Demeter ECMWF";climfield="1Feb 10m u-wind";;
demeter_ecmwf_u10_may) file=DemeterData/ecmwf_p10m_u_may.ctl;kindname="Demeter ECMWF";climfield="1May 10m u-wind";;
demeter_ecmwf_u10_aug) file=DemeterData/ecmwf_p10m_u_aug.ctl;kindname="Demeter ECMWF";climfield="1Aug 10m u-wind";;
demeter_ecmwf_u10_nov) file=DemeterData/ecmwf_p10m_u_nov.ctl;kindname="Demeter ECMWF";climfield="1Nov 10m u-wind";;
demeter_ecmwf_v10_feb) file=DemeterData/ecmwf_p10m_v_feb.ctl;kindname="Demeter ECMWF";climfield="1Feb 10m v-wind";;
demeter_ecmwf_v10_may) file=DemeterData/ecmwf_p10m_v_may.ctl;kindname="Demeter ECMWF";climfield="1May 10m v-wind";;
demeter_ecmwf_v10_aug) file=DemeterData/ecmwf_p10m_v_aug.ctl;kindname="Demeter ECMWF";climfield="1Aug 10m v-wind";;
demeter_ecmwf_v10_nov) file=DemeterData/ecmwf_p10m_v_nov.ctl;kindname="Demeter ECMWF";climfield="1Nov 10m v-wind";;
demeter_ecmwf_tsfc_feb) file=DemeterData/ecmwf_st_stl1_feb.ctl;kindname="Demeter ECMWF";climfield="1Feb Tsfc";;
demeter_ecmwf_tsfc_may) file=DemeterData/ecmwf_st_stl1_may.ctl;kindname="Demeter ECMWF";climfield="1May Tsfc";;
demeter_ecmwf_tsfc_aug) file=DemeterData/ecmwf_st_stl1_aug.ctl;kindname="Demeter ECMWF";climfield="1Aug Tsfc";;
demeter_ecmwf_tsfc_nov) file=DemeterData/ecmwf_st_stl1_nov.ctl;kindname="Demeter ECMWF";climfield="1Nov Tsfc";;
demeter_ecmwf_ssd_feb) file=DemeterData/ecmwf_dssr_feb.ctl;kindname="Demeter ECMWF";climfield="1Feb dssr";;
demeter_ecmwf_ssd_may) file=DemeterData/ecmwf_dssr_may.ctl;kindname="Demeter ECMWF";climfield="1May dssr";;
demeter_ecmwf_ssd_aug) file=DemeterData/ecmwf_dssr_aug.ctl;kindname="Demeter ECMWF";climfield="1Aug dssr";;
demeter_ecmwf_ssd_nov) file=DemeterData/ecmwf_dssr_nov.ctl;kindname="Demeter ECMWF";climfield="1Nov dssr";;

ens_demeter_ecmwf_t2m_feb) file=DemeterData/ecmwf_p2m_t_feb_%%.ctl;kindname="ens Demeter ECMWF";climfield="1Feb T2m";;
ens_demeter_ecmwf_t2m_may) file=DemeterData/ecmwf_p2m_t_may_%%.ctl;kindname="ens Demeter ECMWF";climfield="1May T2m";;
ens_demeter_ecmwf_t2m_aug) file=DemeterData/ecmwf_p2m_t_aug_%%.ctl;kindname="ens Demeter ECMWF";climfield="1Aug T2m";;
ens_demeter_ecmwf_t2m_nov) file=DemeterData/ecmwf_p2m_t_nov_%%.ctl;kindname="ens Demeter ECMWF";climfield="1Nov T2m";;
ens_demeter_ecmwf_prcp_feb) file=DemeterData/ecmwf_tp_feb_%%.ctl;kindname="ens Demeter ECMWF";climfield="1Feb precip";;
ens_demeter_ecmwf_prcp_may) file=DemeterData/ecmwf_tp_may_%%.ctl;kindname="ens Demeter ECMWF";climfield="1May precip";;
ens_demeter_ecmwf_prcp_aug) file=DemeterData/ecmwf_tp_aug_%%.ctl;kindname="ens Demeter ECMWF";climfield="1Aug precip";;
ens_demeter_ecmwf_prcp_nov) file=DemeterData/ecmwf_tp_nov_%%.ctl;kindname="ens Demeter ECMWF";climfield="1Nov precip";;
ens_demeter_ecmwf_msl_feb) file=DemeterData/ecmwf_msl_feb_%%.ctl;kindname="ens Demeter ECMWF";climfield="1Feb SLP";;
ens_demeter_ecmwf_msl_may) file=DemeterData/ecmwf_msl_may_%%.ctl;kindname="ens Demeter ECMWF";climfield="1May SLP";;
ens_demeter_ecmwf_msl_aug) file=DemeterData/ecmwf_msl_aug_%%.ctl;kindname="ens Demeter ECMWF";climfield="1Aug SLP";;
ens_demeter_ecmwf_msl_nov) file=DemeterData/ecmwf_msl_nov_%%.ctl;kindname="ens Demeter ECMWF";climfield="1Nov SLP";;
ens_demeter_ecmwf_z500_feb) file=DemeterData/ecmwf_z500_feb_%%.ctl;kindname="ens Demeter ECMWF";climfield="1Feb z500";;
ens_demeter_ecmwf_z500_may) file=DemeterData/ecmwf_z500_may_%%.ctl;kindname="ens Demeter ECMWF";climfield="1May z500";;
ens_demeter_ecmwf_z500_aug) file=DemeterData/ecmwf_z500_aug_%%.ctl;kindname="ens Demeter ECMWF";climfield="1Aug z500";;
ens_demeter_ecmwf_z500_nov) file=DemeterData/ecmwf_z500_nov_%%.ctl;kindname="ens Demeter ECMWF";climfield="1Nov z500";;
ens_demeter_ecmwf_u10_feb) file=DemeterData/ecmwf_p10m_u_feb_%%.ctl;kindname="ens Demeter ECMWF";climfield="1Feb 10m u-wind";;
ens_demeter_ecmwf_u10_may) file=DemeterData/ecmwf_p10m_u_may_%%.ctl;kindname="ens Demeter ECMWF";climfield="1May 10m u-wind";;
ens_demeter_ecmwf_u10_aug) file=DemeterData/ecmwf_p10m_u_aug_%%.ctl;kindname="ens Demeter ECMWF";climfield="1Aug 10m u-wind";;
ens_demeter_ecmwf_u10_nov) file=DemeterData/ecmwf_p10m_u_nov_%%.ctl;kindname="ens Demeter ECMWF";climfield="1Nov 10m u-wind";;
ens_demeter_ecmwf_v10_feb) file=DemeterData/ecmwf_p10m_v_feb_%%.ctl;kindname="ens Demeter ECMWF";climfield="1Feb 10m v-wind";;
ens_demeter_ecmwf_v10_may) file=DemeterData/ecmwf_p10m_v_may_%%.ctl;kindname="ens Demeter ECMWF";climfield="1May 10m v-wind";;
ens_demeter_ecmwf_v10_aug) file=DemeterData/ecmwf_v10_aug_%%.ctl;kindname="ens Demeter ECMWF";climfield="1Aug 10m v-wind";;
ens_demeter_ecmwf_p10m_v_nov) file=DemeterData/ecmwf_v10_nov_%%.ctl;kindname="ens Demeter ECMWF";climfield="1Nov 10m v-wind";;
ens_demeter_ecmwf_tsfc_feb) file=DemeterData/ecmwf_st_stl1_feb_%%.ctl;kindname="ens Demeter ECMWF";climfield="1Feb Tsfc";;
ens_demeter_ecmwf_tsfc_may) file=DemeterData/ecmwf_st_stl1_may_%%.ctl;kindname="ens Demeter ECMWF";climfield="1May Tsfc";;
ens_demeter_ecmwf_tsfc_aug) file=DemeterData/ecmwf_st_stl1_aug_%%.ctl;kindname="ens Demeter ECMWF";climfield="1Aug Tsfc";;
ens_demeter_ecmwf_tsfc_nov) file=DemeterData/ecmwf_st_stl1_nov_%%.ctl;kindname="ens Demeter ECMWF";climfield="1Nov Tsfc";;
ens_demeter_ecmwf_ssd_feb) file=DemeterData/ecmwf_dssr_feb_%%.ctl;kindname="ens Demeter ECMWF";climfield="1Feb dssr";;
ens_demeter_ecmwf_ssd_may) file=DemeterData/ecmwf_dssr_may_%%.ctl;kindname="ens Demeter ECMWF";climfield="1May dssr";;
ens_demeter_ecmwf_ssd_aug) file=DemeterData/ecmwf_dssr_aug_%%.ctl;kindname="ens Demeter ECMWF";climfield="1Aug dssr";;
ens_demeter_ecmwf_ssd_nov) file=DemeterData/ecmwf_dssr_nov_%%.ctl;kindname="ens Demeter ECMWF";climfield="1Nov dssr";;

demeter_mpi_t2m_feb) file=DemeterData/mpi_p2m_t_feb.ctl;kindname="Demeter MPI";climfield="1Feb T2m";;
demeter_mpi_t2m_may) file=DemeterData/mpi_p2m_t_may.ctl;kindname="Demeter MPI";climfield="1May T2m";;
demeter_mpi_t2m_aug) file=DemeterData/mpi_p2m_t_aug.ctl;kindname="Demeter MPI";climfield="1Aug T2m";;
demeter_mpi_t2m_nov) file=DemeterData/mpi_p2m_t_nov.ctl;kindname="Demeter MPI";climfield="1Nov T2m";;
demeter_mpi_prcp_feb) file=DemeterData/mpi_tp_feb.ctl;kindname="Demeter MPI";climfield="1Feb precip";;
demeter_mpi_prcp_may) file=DemeterData/mpi_tp_may.ctl;kindname="Demeter MPI";climfield="1May precip";;
demeter_mpi_prcp_aug) file=DemeterData/mpi_tp_aug.ctl;kindname="Demeter MPI";climfield="1Aug precip";;
demeter_mpi_prcp_nov) file=DemeterData/mpi_tp_nov.ctl;kindname="Demeter MPI";climfield="1Nov precip";;
demeter_mpi_msl_feb) file=DemeterData/mpi_msl_feb.ctl;kindname="Demeter MPI";climfield="1Feb SLP";;
demeter_mpi_msl_may) file=DemeterData/mpi_msl_may.ctl;kindname="Demeter MPI";climfield="1May SLP";;
demeter_mpi_msl_aug) file=DemeterData/mpi_msl_aug.ctl;kindname="Demeter MPI";climfield="1Aug SLP";;
demeter_mpi_msl_nov) file=DemeterData/mpi_msl_nov.ctl;kindname="Demeter MPI";climfield="1Nov SLP";;
demeter_mpi_z500_feb) file=DemeterData/mpi_z500_feb.ctl;kindname="Demeter MPI";climfield="1Feb z500";;
demeter_mpi_z500_may) file=DemeterData/mpi_z500_may.ctl;kindname="Demeter MPI";climfield="1May z500";;
demeter_mpi_z500_aug) file=DemeterData/mpi_z500_aug.ctl;kindname="Demeter MPI";climfield="1Aug z500";;
demeter_mpi_z500_nov) file=DemeterData/mpi_z500_nov.ctl;kindname="Demeter MPI";climfield="1Nov z500";;
demeter_mpi_u10_feb) file=DemeterData/mpi_p10m_u_feb.ctl;kindname="Demeter MPI";climfield="1Feb 10m u-wind";;
demeter_mpi_u10_may) file=DemeterData/mpi_p10m_u_may.ctl;kindname="Demeter MPI";climfield="1May 10m u-wind";;
demeter_mpi_u10_aug) file=DemeterData/mpi_p10m_u_aug.ctl;kindname="Demeter MPI";climfield="1Aug 10m u-wind";;
demeter_mpi_u10_nov) file=DemeterData/mpi_p10m_u_nov.ctl;kindname="Demeter MPI";climfield="1Nov 10m u-wind";;
demeter_mpi_v10_feb) file=DemeterData/mpi_p10m_v_feb.ctl;kindname="Demeter MPI";climfield="1Feb 10m v-wind";;
demeter_mpi_v10_may) file=DemeterData/mpi_p10m_v_may.ctl;kindname="Demeter MPI";climfield="1May 10m v-wind";;
demeter_mpi_v10_aug) file=DemeterData/mpi_p10m_v_aug.ctl;kindname="Demeter MPI";climfield="1Aug 10m v-wind";;
demeter_mpi_v10_nov) file=DemeterData/mpi_p10m_v_nov.ctl;kindname="Demeter MPI";climfield="1Nov 10m v-wind";;
demeter_mpi_tsfc_feb) file=DemeterData/mpi_st_stl1_feb.ctl;kindname="Demeter MPI";climfield="1Feb Tsfc";;
demeter_mpi_tsfc_may) file=DemeterData/mpi_st_stl1_may.ctl;kindname="Demeter MPI";climfield="1May Tsfc";;
demeter_mpi_tsfc_aug) file=DemeterData/mpi_st_stl1_aug.ctl;kindname="Demeter MPI";climfield="1Aug Tsfc";;
demeter_mpi_tsfc_nov) file=DemeterData/mpi_st_stl1_nov.ctl;kindname="Demeter MPI";climfield="1Nov Tsfc";;

ens_demeter_mpi_t2m_feb) file=DemeterData/mpi_p2m_t_feb_%%.ctl;kindname="ens Demeter MPI";climfield="1Feb T2m";;
ens_demeter_mpi_t2m_may) file=DemeterData/mpi_p2m_t_may_%%.ctl;kindname="ens Demeter MPI";climfield="1May T2m";;
ens_demeter_mpi_t2m_aug) file=DemeterData/mpi_p2m_t_aug_%%.ctl;kindname="ens Demeter MPI";climfield="1Aug T2m";;
ens_demeter_mpi_t2m_nov) file=DemeterData/mpi_p2m_t_nov_%%.ctl;kindname="ens Demeter MPI";climfield="1Nov T2m";;
ens_demeter_mpi_prcp_feb) file=DemeterData/mpi_tp_feb_%%.ctl;kindname="ens Demeter MPI";climfield="1Feb precip";;
ens_demeter_mpi_prcp_may) file=DemeterData/mpi_tp_may_%%.ctl;kindname="ens Demeter MPI";climfield="1May precip";;
ens_demeter_mpi_prcp_aug) file=DemeterData/mpi_tp_aug_%%.ctl;kindname="ens Demeter MPI";climfield="1Aug precip";;
ens_demeter_mpi_prcp_nov) file=DemeterData/mpi_tp_nov_%%.ctl;kindname="ens Demeter MPI";climfield="1Nov precip";;
ens_demeter_mpi_msl_feb) file=DemeterData/mpi_msl_feb_%%.ctl;kindname="ens Demeter MPI";climfield="1Feb SLP";;
ens_demeter_mpi_msl_may) file=DemeterData/mpi_msl_may_%%.ctl;kindname="ens Demeter MPI";climfield="1May SLP";;
ens_demeter_mpi_msl_aug) file=DemeterData/mpi_msl_aug_%%.ctl;kindname="ens Demeter MPI";climfield="1Aug SLP";;
ens_demeter_mpi_msl_nov) file=DemeterData/mpi_msl_nov_%%.ctl;kindname="ens Demeter MPI";climfield="1Nov SLP";;
ens_demeter_mpi_z500_feb) file=DemeterData/mpi_z500_feb_%%.ctl;kindname="ens Demeter MPI";climfield="1Feb z500";;
ens_demeter_mpi_z500_may) file=DemeterData/mpi_z500_may_%%.ctl;kindname="ens Demeter MPI";climfield="1May z500";;
ens_demeter_mpi_z500_aug) file=DemeterData/mpi_z500_aug_%%.ctl;kindname="ens Demeter MPI";climfield="1Aug z500";;
ens_demeter_mpi_z500_nov) file=DemeterData/mpi_z500_nov_%%.ctl;kindname="ens Demeter MPI";climfield="1Nov z500";;
ens_demeter_mpi_u10_feb) file=DemeterData/mpi_p10m_u_feb_%%.ctl;kindname="ens Demeter MPI";climfield="1Feb 10m u-wind";;
ens_demeter_mpi_u10_may) file=DemeterData/mpi_p10m_u_may_%%.ctl;kindname="ens Demeter MPI";climfield="1May 10m u-wind";;
ens_demeter_mpi_u10_aug) file=DemeterData/mpi_p10m_u_aug_%%.ctl;kindname="ens Demeter MPI";climfield="1Aug 10m u-wind";;
ens_demeter_mpi_u10_nov) file=DemeterData/mpi_p10m_u_nov_%%.ctl;kindname="ens Demeter MPI";climfield="1Nov 10m u-wind";;
ens_demeter_mpi_v10_feb) file=DemeterData/mpi_p10m_v_feb_%%.ctl;kindname="ens Demeter MPI";climfield="1Feb 10m v-wind";;
ens_demeter_mpi_v10_may) file=DemeterData/mpi_p10m_v_may_%%.ctl;kindname="ens Demeter MPI";climfield="1May 10m v-wind";;
ens_demeter_mpi_v10_aug) file=DemeterData/mpi_p10m_v_aug_%%.ctl;kindname="ens Demeter MPI";climfield="1Aug 10m v-wind";;
ens_demeter_mpi_v10_nov) file=DemeterData/mpi_p10m_v_nov_%%.ctl;kindname="ens Demeter MPI";climfield="1Nov 10m v-wind";;
ens_demeter_mpi_tsfc_feb) file=DemeterData/mpi_st_stl1_feb_%%.ctl;kindname="ens Demeter MPI";climfield="1Feb Tsfc";;
ens_demeter_mpi_tsfc_may) file=DemeterData/mpi_st_stl1_may_%%.ctl;kindname="ens Demeter MPI";climfield="1May Tsfc";;
ens_demeter_mpi_tsfc_aug) file=DemeterData/mpi_st_stl1_aug_%%.ctl;kindname="ens Demeter MPI";climfield="1Aug Tsfc";;
ens_demeter_mpi_tsfc_nov) file=DemeterData/mpi_st_stl1_nov_%%.ctl;kindname="ens Demeter MPI";climfield="1Nov Tsfc";;

demeter_ukmo_t2m_feb) file=DemeterData/ukmo_p2m_t_feb.ctl;kindname="Demeter UKMO";climfield="1Feb T2m";;
demeter_ukmo_t2m_may) file=DemeterData/ukmo_p2m_t_may.ctl;kindname="Demeter UKMO";climfield="1May T2m";;
demeter_ukmo_t2m_aug) file=DemeterData/ukmo_p2m_t_aug.ctl;kindname="Demeter UKMO";climfield="1Aug T2m";;
demeter_ukmo_t2m_nov) file=DemeterData/ukmo_p2m_t_nov.ctl;kindname="Demeter UKMO";climfield="1Nov T2m";;
demeter_ukmo_prcp_feb) file=DemeterData/ukmo_tp_feb.ctl;kindname="Demeter UKMO";climfield="1Feb precip";;
demeter_ukmo_prcp_may) file=DemeterData/ukmo_tp_may.ctl;kindname="Demeter UKMO";climfield="1May precip";;
demeter_ukmo_prcp_aug) file=DemeterData/ukmo_tp_aug.ctl;kindname="Demeter UKMO";climfield="1Aug precip";;
demeter_ukmo_prcp_nov) file=DemeterData/ukmo_tp_nov.ctl;kindname="Demeter UKMO";climfield="1Nov precip";;
demeter_ukmo_msl_feb) file=DemeterData/ukmo_msl_feb.ctl;kindname="Demeter UKMO";climfield="1Feb SLP";;
demeter_ukmo_msl_may) file=DemeterData/ukmo_msl_may.ctl;kindname="Demeter UKMO";climfield="1May SLP";;
demeter_ukmo_msl_aug) file=DemeterData/ukmo_msl_aug.ctl;kindname="Demeter UKMO";climfield="1Aug SLP";;
demeter_ukmo_msl_nov) file=DemeterData/ukmo_msl_nov.ctl;kindname="Demeter UKMO";climfield="1Nov SLP";;
demeter_ukmo_z500_feb) file=DemeterData/ukmo_z500_feb.ctl;kindname="Demeter UKMO";climfield="1Feb z500";;
demeter_ukmo_z500_may) file=DemeterData/ukmo_z500_may.ctl;kindname="Demeter UKMO";climfield="1May z500";;
demeter_ukmo_z500_aug) file=DemeterData/ukmo_z500_aug.ctl;kindname="Demeter UKMO";climfield="1Aug z500";;
demeter_ukmo_z500_nov) file=DemeterData/ukmo_z500_nov.ctl;kindname="Demeter UKMO";climfield="1Nov z500";;
demeter_ukmo_u10_feb) file=DemeterData/ukmo_p10m_u_feb.ctl;kindname="Demeter UKMO";climfield="1Feb 10m u-wind";;
demeter_ukmo_u10_may) file=DemeterData/ukmo_p10m_u_may.ctl;kindname="Demeter UKMO";climfield="1May 10m u-wind";;
demeter_ukmo_u10_aug) file=DemeterData/ukmo_p10m_u_aug.ctl;kindname="Demeter UKMO";climfield="1Aug 10m u-wind";;
demeter_ukmo_u10_nov) file=DemeterData/ukmo_p10m_u_nov.ctl;kindname="Demeter UKMO";climfield="1Nov 10m u-wind";;
demeter_ukmo_v10_feb) file=DemeterData/ukmo_p10m_v_feb.ctl;kindname="Demeter UKMO";climfield="1Feb 10m v-wind";;
demeter_ukmo_v10_may) file=DemeterData/ukmo_p10m_v_may.ctl;kindname="Demeter UKMO";climfield="1May 10m v-wind";;
demeter_ukmo_v10_aug) file=DemeterData/ukmo_p10m_v_aug.ctl;kindname="Demeter UKMO";climfield="1Aug 10m v-wind";;
demeter_ukmo_v10_nov) file=DemeterData/ukmo_p10m_v_nov.ctl;kindname="Demeter UKMO";climfield="1Nov 10m v-wind";;
demeter_ukmo_tsfc_feb) file=DemeterData/ukmo_st_stl1_feb.ctl;kindname="Demeter UKMO";climfield="1Feb Tsfc";;
demeter_ukmo_tsfc_may) file=DemeterData/ukmo_st_stl1_may.ctl;kindname="Demeter UKMO";climfield="1May Tsfc";;
demeter_ukmo_tsfc_aug) file=DemeterData/ukmo_st_stl1_aug.ctl;kindname="Demeter UKMO";climfield="1Aug Tsfc";;
demeter_ukmo_tsfc_nov) file=DemeterData/ukmo_st_stl1_nov.ctl;kindname="Demeter UKMO";climfield="1Nov Tsfc";;

ens_demeter_ukmo_t2m_feb) file=DemeterData/ukmo_p2m_t_feb_%%.ctl;kindname="ens Demeter UKMO";climfield="1Feb T2m";;
ens_demeter_ukmo_t2m_may) file=DemeterData/ukmo_p2m_t_may_%%.ctl;kindname="ens Demeter UKMO";climfield="1May T2m";;
ens_demeter_ukmo_t2m_aug) file=DemeterData/ukmo_p2m_t_aug_%%.ctl;kindname="ens Demeter UKMO";climfield="1Aug T2m";;
ens_demeter_ukmo_t2m_nov) file=DemeterData/ukmo_p2m_t_nov_%%.ctl;kindname="ens Demeter UKMO";climfield="1Nov T2m";;
ens_demeter_ukmo_prcp_feb) file=DemeterData/ukmo_tp_feb_%%.ctl;kindname="ens Demeter UKMO";climfield="1Feb precip";;
ens_demeter_ukmo_prcp_may) file=DemeterData/ukmo_tp_may_%%.ctl;kindname="ens Demeter UKMO";climfield="1May precip";;
ens_demeter_ukmo_prcp_aug) file=DemeterData/ukmo_tp_aug_%%.ctl;kindname="ens Demeter UKMO";climfield="1Aug precip";;
ens_demeter_ukmo_prcp_nov) file=DemeterData/ukmo_tp_nov_%%.ctl;kindname="ens Demeter UKMO";climfield="1Nov precip";;
ens_demeter_ukmo_msl_feb) file=DemeterData/ukmo_msl_feb_%%.ctl;kindname="ens Demeter UKMO";climfield="1Feb SLP";;
ens_demeter_ukmo_msl_may) file=DemeterData/ukmo_msl_may_%%.ctl;kindname="ens Demeter UKMO";climfield="1May SLP";;
ens_demeter_ukmo_msl_aug) file=DemeterData/ukmo_msl_aug_%%.ctl;kindname="ens Demeter UKMO";climfield="1Aug SLP";;
ens_demeter_ukmo_msl_nov) file=DemeterData/ukmo_msl_nov_%%.ctl;kindname="ens Demeter UKMO";climfield="1Nov SLP";;
ens_demeter_ukmo_z500_feb) file=DemeterData/ukmo_z500_feb_%%.ctl;kindname="ens Demeter UKMO";climfield="1Feb z500";;
ens_demeter_ukmo_z500_may) file=DemeterData/ukmo_z500_may_%%.ctl;kindname="ens Demeter UKMO";climfield="1May z500";;
ens_demeter_ukmo_z500_aug) file=DemeterData/ukmo_z500_aug_%%.ctl;kindname="ens Demeter UKMO";climfield="1Aug z500";;
ens_demeter_ukmo_z500_nov) file=DemeterData/ukmo_z500_nov_%%.ctl;kindname="ens Demeter UKMO";climfield="1Nov z500";;
ens_demeter_ukmo_u10_feb) file=DemeterData/ukmo_p10m_u_feb_%%.ctl;kindname="ens Demeter UKMO";climfield="1Feb 10m u-wind";;
ens_demeter_ukmo_u10_may) file=DemeterData/ukmo_p10m_u_may_%%.ctl;kindname="ens Demeter UKMO";climfield="1May 10m u-wind";;
ens_demeter_ukmo_u10_aug) file=DemeterData/ukmo_p10m_u_aug_%%.ctl;kindname="ens Demeter UKMO";climfield="1Aug 10m u-wind";;
ens_demeter_ukmo_u10_nov) file=DemeterData/ukmo_p10m_u_nov_%%.ctl;kindname="ens Demeter UKMO";climfield="1Nov 10m u-wind";;
ens_demeter_ukmo_v10_feb) file=DemeterData/ukmo_p10m_v_feb_%%.ctl;kindname="ens Demeter UKMO";climfield="1Feb 10m v-wind";;
ens_demeter_ukmo_v10_may) file=DemeterData/ukmo_p10m_v_may_%%.ctl;kindname="ens Demeter UKMO";climfield="1May 10m v-wind";;
ens_demeter_ukmo_v10_aug) file=DemeterData/ukmo_p10m_v_aug_%%.ctl;kindname="ens Demeter UKMO";climfield="1Aug 10m v-wind";;
ens_demeter_ukmo_v10_nov) file=DemeterData/ukmo_p10m_v_nov_%%.ctl;kindname="ens Demeter UKMO";climfield="1Nov 10m v-wind";;
ens_demeter_ukmo_tsfc_feb) file=DemeterData/ukmo_st_stl1_feb_%%.ctl;kindname="ens Demeter UKMO";climfield="1Feb Tsfc";;
ens_demeter_ukmo_tsfc_may) file=DemeterData/ukmo_st_stl1_may_%%.ctl;kindname="ens Demeter UKMO";climfield="1May Tsfc";;
ens_demeter_ukmo_tsfc_aug) file=DemeterData/ukmo_st_stl1_aug_%%.ctl;kindname="ens Demeter UKMO";climfield="1Aug Tsfc";;
ens_demeter_ukmo_tsfc_nov) file=DemeterData/ukmo_st_stl1_nov_%%.ctl;kindname="ens Demeter UKMO";climfield="1Nov Tsfc";;

demeter_t2m_feb) file=DemeterData/demeter_p2m_t_feb.ctl;kindname="Demeter average";climfield="1Feb T2m";;
demeter_t2m_may) file=DemeterData/demeter_p2m_t_may.ctl;kindname="Demeter average";climfield="1May T2m";;
demeter_t2m_aug) file=DemeterData/demeter_p2m_t_aug.ctl;kindname="Demeter average";climfield="1Aug T2m";;
demeter_t2m_nov) file=DemeterData/demeter_p2m_t_nov.ctl;kindname="Demeter average";climfield="1Nov T2m";;
demeter_prcp_feb) file=DemeterData/demeter_tp_feb.ctl;kindname="Demeter average";climfield="1Feb precip";;
demeter_prcp_may) file=DemeterData/demeter_tp_may.ctl;kindname="Demeter average";climfield="1May precip";;
demeter_prcp_aug) file=DemeterData/demeter_tp_aug.ctl;kindname="Demeter average";climfield="1Aug precip";;
demeter_prcp_nov) file=DemeterData/demeter_tp_nov.ctl;kindname="Demeter average";climfield="1Nov precip";;
demeter_msl_feb) file=DemeterData/demeter_msl_feb.ctl;kindname="Demeter average";climfield="1Feb SLP";;
demeter_msl_may) file=DemeterData/demeter_msl_may.ctl;kindname="Demeter average";climfield="1May SLP";;
demeter_msl_aug) file=DemeterData/demeter_msl_aug.ctl;kindname="Demeter average";climfield="1Aug SLP";;
demeter_msl_nov) file=DemeterData/demeter_msl_nov.ctl;kindname="Demeter average";climfield="1Nov SLP";;
demeter_z500_feb) file=DemeterData/demeter_z500_feb.ctl;kindname="Demeter average";climfield="1Feb z500";;
demeter_z500_may) file=DemeterData/demeter_z500_may.ctl;kindname="Demeter average";climfield="1May z500";;
demeter_z500_aug) file=DemeterData/demeter_z500_aug.ctl;kindname="Demeter average";climfield="1Aug z500";;
demeter_z500_nov) file=DemeterData/demeter_z500_nov.ctl;kindname="Demeter average";climfield="1Nov z500";;
demeter_u10_feb) file=DemeterData/demeter_p10m_u_feb.ctl;kindname="Demeter average";climfield="1Feb 10m u-wind";;
demeter_u10_may) file=DemeterData/demeter_p10m_u_may.ctl;kindname="Demeter average";climfield="1May 10m u-wind";;
demeter_u10_aug) file=DemeterData/demeter_p10m_u_aug.ctl;kindname="Demeter average";climfield="1Aug 10m u-wind";;
demeter_u10_nov) file=DemeterData/demeter_p10m_u_nov.ctl;kindname="Demeter average";climfield="1Nov 10m u-wind";;
demeter_v10_feb) file=DemeterData/demeter_p10m_v_feb.ctl;kindname="Demeter average";climfield="1Feb 10m v-wind";;
demeter_v10_may) file=DemeterData/demeter_p10m_v_may.ctl;kindname="Demeter average";climfield="1May 10m v-wind";;
demeter_v10_aug) file=DemeterData/demeter_p10m_v_aug.ctl;kindname="Demeter average";climfield="1Aug 10m v-wind";;
demeter_v10_nov) file=DemeterData/demeter_p10m_v_nov.ctl;kindname="Demeter average";climfield="1Nov 10m v-wind";;
demeter_tsfc_feb) file=DemeterData/demeter_st_stl1_feb.ctl;kindname="Demeter average";climfield="1Feb Tsfc";;
demeter_tsfc_may) file=DemeterData/demeter_st_stl1_may.ctl;kindname="Demeter average";climfield="1May Tsfc";;
demeter_tsfc_aug) file=DemeterData/demeter_st_stl1_aug.ctl;kindname="Demeter average";climfield="1Aug Tsfc";;
demeter_tsfc_nov) file=DemeterData/demeter_st_stl1_nov.ctl;kindname="Demeter average";climfield="1Nov Tsfc";;

ens_demeter_t2m_feb) file=DemeterData/demeter_p2m_t_feb_%%.ctl;kindname="Demeter ensemble";climfield="1Feb T2m";;
ens_demeter_t2m_may) file=DemeterData/demeter_p2m_t_may_%%.ctl;kindname="Demeter ensemble";climfield="1May T2m";;
ens_demeter_t2m_aug) file=DemeterData/demeter_p2m_t_aug_%%.ctl;kindname="Demeter ensemble";climfield="1Aug T2m";;
ens_demeter_t2m_nov) file=DemeterData/demeter_p2m_t_nov_%%.ctl;kindname="Demeter ensemble";climfield="1Nov T2m";;
ens_demeter_prcp_feb) file=DemeterData/demeter_tp_feb_%%.ctl;kindname="Demeter ensemble";climfield="1Feb precip";;
ens_demeter_prcp_may) file=DemeterData/demeter_tp_may_%%.ctl;kindname="Demeter ensemble";climfield="1May precip";;
ens_demeter_prcp_aug) file=DemeterData/demeter_tp_aug_%%.ctl;kindname="Demeter ensemble";climfield="1Aug precip";;
ens_demeter_prcp_nov) file=DemeterData/demeter_tp_nov_%%.ctl;kindname="Demeter ensemble";climfield="1Nov precip";;
ens_demeter_msl_feb) file=DemeterData/demeter_msl_feb_%%.ctl;kindname="Demeter ensemble";climfield="1Feb SLP";;
ens_demeter_msl_may) file=DemeterData/demeter_msl_may_%%.ctl;kindname="Demeter ensemble";climfield="1May SLP";;
ens_demeter_msl_aug) file=DemeterData/demeter_msl_aug_%%.ctl;kindname="Demeter ensemble";climfield="1Aug SLP";;
ens_demeter_msl_nov) file=DemeterData/demeter_msl_nov_%%.ctl;kindname="Demeter ensemble";climfield="1Nov SLP";;
ens_demeter_z500_feb) file=DemeterData/demeter_z500_feb_%%.ctl;kindname="Demeter ensemble";climfield="1Feb z500";;
ens_demeter_z500_may) file=DemeterData/demeter_z500_may_%%.ctl;kindname="Demeter ensemble";climfield="1May z500";;
ens_demeter_z500_aug) file=DemeterData/demeter_z500_aug_%%.ctl;kindname="Demeter ensemble";climfield="1Aug z500";;
ens_demeter_z500_nov) file=DemeterData/demeter_z500_nov_%%.ctl;kindname="Demeter ensemble";climfield="1Nov z500";;
ens_demeter_u10_feb) file=DemeterData/demeter_p10m_u_feb_%%.ctl;kindname="Demeter ensemble";climfield="1Feb 10m u-wind";;
ens_demeter_u10_may) file=DemeterData/demeter_p10m_u_may_%%.ctl;kindname="Demeter ensemble";climfield="1May 10m u-wind";;
ens_demeter_u10_aug) file=DemeterData/demeter_p10m_u_aug_%%.ctl;kindname="Demeter ensemble";climfield="1Aug 10m u-wind";;
ens_demeter_u10_nov) file=DemeterData/demeter_p10m_u_nov_%%.ctl;kindname="Demeter ensemble";climfield="1Nov 10m u-wind";;
ens_demeter_v10_feb) file=DemeterData/demeter_p10m_v_feb_%%.ctl;kindname="Demeter ensemble";climfield="1Feb 10m v-wind";;
ens_demeter_v10_may) file=DemeterData/demeter_p10m_v_may_%%.ctl;kindname="Demeter ensemble";climfield="1May 10m v-wind";;
ens_demeter_v10_aug) file=DemeterData/demeter_p10m_v_aug_%%.ctl;kindname="Demeter ensemble";climfield="1Aug 10m v-wind";;
ens_demeter_v10_nov) file=DemeterData/demeter_p10m_v_nov_%%.ctl;kindname="Demeter ensemble";climfield="1Nov 10m v-wind";;
ens_demeter_tsfc_feb) file=DemeterData/demeter_st_stl1_feb_%%.ctl;kindname="Demeter ensemble";climfield="1Feb Tsfc";;
ens_demeter_tsfc_may) file=DemeterData/demeter_st_stl1_may_%%.ctl;kindname="Demeter ensemble";climfield="1May Tsfc";;
ens_demeter_tsfc_aug) file=DemeterData/demeter_st_stl1_aug_%%.ctl;kindname="Demeter ensemble";climfield="1Aug Tsfc";;
ens_demeter_tsfc_nov) file=DemeterData/demeter_st_stl1_nov_%%.ctl;kindname="Demeter ensemble";climfield="1Nov Tsfc";;

ens_demeter3_t2m_feb) file=DemeterData/demeter3_p2m_t_feb_%%.ctl;kindname="Demeter3 ensemble";climfield="1Feb T2m";;
ens_demeter3_t2m_may) file=DemeterData/demeter3_p2m_t_may_%%.ctl;kindname="Demeter3 ensemble";climfield="1May T2m";;
ens_demeter3_t2m_aug) file=DemeterData/demeter3_p2m_t_aug_%%.ctl;kindname="Demeter3 ensemble";climfield="1Aug T2m";;
ens_demeter3_t2m_nov) file=DemeterData/demeter3_p2m_t_nov_%%.ctl;kindname="Demeter3 ensemble";climfield="1Nov T2m";;
ens_demeter3_prcp_feb) file=DemeterData/demeter3_tp_feb_%%.ctl;kindname="Demeter3 ensemble";climfield="1Feb precip";;
ens_demeter3_prcp_may) file=DemeterData/demeter3_tp_may_%%.ctl;kindname="Demeter3 ensemble";climfield="1May precip";;
ens_demeter3_prcp_aug) file=DemeterData/demeter3_tp_aug_%%.ctl;kindname="Demeter3 ensemble";climfield="1Aug precip";;
ens_demeter3_prcp_nov) file=DemeterData/demeter3_tp_nov_%%.ctl;kindname="Demeter3 ensemble";climfield="1Nov precip";;
ens_demeter3_msl_feb) file=DemeterData/demeter3_msl_feb_%%.ctl;kindname="Demeter3 ensemble";climfield="1Feb SLP";;
ens_demeter3_msl_may) file=DemeterData/demeter3_msl_may_%%.ctl;kindname="Demeter3 ensemble";climfield="1May SLP";;
ens_demeter3_msl_aug) file=DemeterData/demeter3_msl_aug_%%.ctl;kindname="Demeter3 ensemble";climfield="1Aug SLP";;
ens_demeter3_msl_nov) file=DemeterData/demeter3_msl_nov_%%.ctl;kindname="Demeter3 ensemble";climfield="1Nov SLP";;
ens_demeter3_z500_feb) file=DemeterData/demeter3_z500_feb_%%.ctl;kindname="Demeter3 ensemble";climfield="1Feb z500";;
ens_demeter3_z500_may) file=DemeterData/demeter3_z500_may_%%.ctl;kindname="Demeter3 ensemble";climfield="1May z500";;
ens_demeter3_z500_aug) file=DemeterData/demeter3_z500_aug_%%.ctl;kindname="Demeter3 ensemble";climfield="1Aug z500";;
ens_demeter3_z500_nov) file=DemeterData/demeter3_z500_nov_%%.ctl;kindname="Demeter3 ensemble";climfield="1Nov z500";;
ens_demeter3_u10_feb) file=DemeterData/demeter3_p10m_u_feb_%%.ctl;kindname="Demeter3 ensemble";climfield="1Feb 10m u-wind";;
ens_demeter3_u10_may) file=DemeterData/demeter3_p10m_u_may_%%.ctl;kindname="Demeter3 ensemble";climfield="1May 10m u-wind";;
ens_demeter3_u10_aug) file=DemeterData/demeter3_p10m_u_aug_%%.ctl;kindname="Demeter3 ensemble";climfield="1Aug 10m u-wind";;
ens_demeter3_u10_nov) file=DemeterData/demeter3_p10m_u_nov_%%.ctl;kindname="Demeter3 ensemble";climfield="1Nov 10m u-wind";;
ens_demeter3_v10_feb) file=DemeterData/demeter3_p10m_v_feb_%%.ctl;kindname="Demeter3 ensemble";climfield="1Feb 10m v-wind";;
ens_demeter3_v10_may) file=DemeterData/demeter3_p10m_v_may_%%.ctl;kindname="Demeter3 ensemble";climfield="1May 10m v-wind";;
ens_demeter3_v10_aug) file=DemeterData/demeter3_p10m_v_aug_%%.ctl;kindname="Demeter3 ensemble";climfield="1Aug 10m v-wind";;
ens_demeter3_v10_nov) file=DemeterData/demeter3_p10m_v_nov_%%.ctl;kindname="Demeter3 ensemble";climfield="1Nov 10m v-wind";;
ens_demeter3_tsfc_feb) file=DemeterData/demeter3_st_stl1_feb_%%.ctl;kindname="Demeter3 ensemble";climfield="1Feb Tsfc";;
ens_demeter3_tsfc_may) file=DemeterData/demeter3_st_stl1_may_%%.ctl;kindname="Demeter3 ensemble";climfield="1May Tsfc";;
ens_demeter3_tsfc_aug) file=DemeterData/demeter3_st_stl1_aug_%%.ctl;kindname="Demeter3 ensemble";climfield="1Aug Tsfc";;
ens_demeter3_tsfc_nov) file=DemeterData/demeter3_st_stl1_nov_%%.ctl;kindname="Demeter3 ensemble";climfield="1Nov Tsfc";;

demeter3_t2m_feb) file=DemeterData/demeter3_p2m_t_feb.ctl;kindname="Demeter3 average";climfield="1Feb T2m";;
demeter3_t2m_may) file=DemeterData/demeter3_p2m_t_may.ctl;kindname="Demeter3 average";climfield="1May T2m";;
demeter3_t2m_aug) file=DemeterData/demeter3_p2m_t_aug.ctl;kindname="Demeter3 average";climfield="1Aug T2m";;
demeter3_t2m_nov) file=DemeterData/demeter3_p2m_t_nov.ctl;kindname="Demeter3 average";climfield="1Nov T2m";;
demeter3_prcp_feb) file=DemeterData/demeter3_tp_feb.ctl;kindname="Demeter3 average";climfield="1Feb precip";;
demeter3_prcp_may) file=DemeterData/demeter3_tp_may.ctl;kindname="Demeter3 average";climfield="1May precip";;
demeter3_prcp_aug) file=DemeterData/demeter3_tp_aug.ctl;kindname="Demeter3 average";climfield="1Aug precip";;
demeter3_prcp_nov) file=DemeterData/demeter3_tp_nov.ctl;kindname="Demeter3 average";climfield="1Nov precip";;
demeter3_msl_feb) file=DemeterData/demeter3_msl_feb.ctl;kindname="Demeter3 average";climfield="1Feb SLP";;
demeter3_msl_may) file=DemeterData/demeter3_msl_may.ctl;kindname="Demeter3 average";climfield="1May SLP";;
demeter3_msl_aug) file=DemeterData/demeter3_msl_aug.ctl;kindname="Demeter3 average";climfield="1Aug SLP";;
demeter3_msl_nov) file=DemeterData/demeter3_msl_nov.ctl;kindname="Demeter3 average";climfield="1Nov SLP";;
demeter3_z500_feb) file=DemeterData/demeter3_z500_feb.ctl;kindname="Demeter3 average";climfield="1Feb z500";;
demeter3_z500_may) file=DemeterData/demeter3_z500_may.ctl;kindname="Demeter3 average";climfield="1May z500";;
demeter3_z500_aug) file=DemeterData/demeter3_z500_aug.ctl;kindname="Demeter3 average";climfield="1Aug z500";;
demeter3_z500_nov) file=DemeterData/demeter3_z500_nov.ctl;kindname="Demeter3 average";climfield="1Nov z500";;
demeter3_u10_feb) file=DemeterData/demeter3_p10m_u_feb.ctl;kindname="Demeter3 average";climfield="1Feb 10m u-wind";;
demeter3_u10_may) file=DemeterData/demeter3_p10m_u_may.ctl;kindname="Demeter3 average";climfield="1May 10m u-wind";;
demeter3_u10_aug) file=DemeterData/demeter3_p10m_u_aug.ctl;kindname="Demeter3 average";climfield="1Aug 10m u-wind";;
demeter3_u10_nov) file=DemeterData/demeter3_p10m_u_nov.ctl;kindname="Demeter3 average";climfield="1Nov 10m u-wind";;
demeter3_v10_feb) file=DemeterData/demeter3_p10m_v_feb.ctl;kindname="Demeter3 average";climfield="1Feb 10m v-wind";;
demeter3_v10_may) file=DemeterData/demeter3_p10m_v_may.ctl;kindname="Demeter3 average";climfield="1May 10m v-wind";;
demeter3_v10_aug) file=DemeterData/demeter3_p10m_v_aug.ctl;kindname="Demeter3 average";climfield="1Aug 10m v-wind";;
demeter3_v10_nov) file=DemeterData/demeter3_p10m_v_nov.ctl;kindname="Demeter3 average";climfield="1Nov 10m v-wind";;
demeter3_tsfc_feb) file=DemeterData/demeter3_st_stl1_feb.ctl;kindname="Demeter3 average";climfield="1Feb Tsfc";;
demeter3_tsfc_may) file=DemeterData/demeter3_st_stl1_may.ctl;kindname="Demeter3 average";climfield="1May Tsfc";;
demeter3_tsfc_aug) file=DemeterData/demeter3_st_stl1_aug.ctl;kindname="Demeter3 average";climfield="1Aug Tsfc";;
demeter3_tsfc_nov) file=DemeterData/demeter3_st_stl1_nov.ctl;kindname="Demeter3 average";climfield="1Nov Tsfc";;
demeter3_ssd_feb) file=DemeterData/demeter3_dssr_feb.ctl;kindname="Demeter3 average";climfield="1Feb dssr";;
demeter3_ssd_may) file=DemeterData/demeter3_dssr_may.ctl;kindname="Demeter3 average";climfield="1May dssr";;
demeter3_ssd_aug) file=DemeterData/demeter3_dssr_aug.ctl;kindname="Demeter3 average";climfield="1Aug dssr";;
demeter3_ssd_nov) file=DemeterData/demeter3_dssr_nov.ctl;kindname="Demeter3 average";climfield="1Nov dssr";;

hadcm3_a2_temp) file=IPCCData/HADCM3_A2_temp.ctl;kindname="HADCM3 A2";climfield="T2m";LSMASK="IPCCData/20c3m/sftlf_A1_ukmo_hadcm3.nc";;
hadcm3_a2_tmax) file=IPCCData/HADCM3_A2_tmax.ctl;kindname="HADCM3 A2";climfield="Tmax";LSMASK="IPCCData/20c3m/sftlf_A1_ukmo_hadcm3.nc";;
hadcm3_a2_tmin) file=IPCCData/HADCM3_A2_tmin.ctl;kindname="HADCM3 A2";climfield="Tmin";LSMASK="IPCCData/20c3m/sftlf_A1_ukmo_hadcm3.nc";;
hadcm3_a2_prcp) file=IPCCData/HADCM3_A2_prec.new.ctl;kindname="HADCM3 A2";climfield="prcp";LSMASK="IPCCData/20c3m/sftlf_A1_ukmo_hadcm3.nc";;
hadcm3_a2_wind) file=IPCCData/HADCM3_A2_wind.ctl;kindname="HADCM3 A2";climfield="10m wind";LSMASK="IPCCData/20c3m/sftlf_A1_ukmo_hadcm3.nc";;
hadcm3_a2_mslp) file=IPCCData/HADCM3_A2_mslp.ctl;kindname="HADCM3 A2";climfield="SLP";LSMASK="IPCCData/20c3m/sftlf_A1_ukmo_hadcm3.nc";;
hadcm3_a2_z500) file=IPCCData/HADCM3_A2_p500.ctl;kindname="HADCM3 A2";climfield="Z500";LSMASK="IPCCData/20c3m/sftlf_A1_ukmo_hadcm3.nc";;

hadcm3_b2_temp) file=IPCCData/HADCM3_B2_temp.ctl;kindname="HADCM3 B2";climfield="T2m";LSMASK="IPCCData/20c3m/sftlf_A1_ukmo_hadcm3.nc";;
hadcm3_b2_tmax) file=IPCCData/HADCM3_B2_tmax.ctl;kindname="HADCM3 B2";climfield="Tmax";LSMASK="IPCCData/20c3m/sftlf_A1_ukmo_hadcm3.nc";;
hadcm3_b2_tmin) file=IPCCData/HADCM3_B2_tmin.ctl;kindname="HADCM3 B2";climfield="Tmin";LSMASK="IPCCData/20c3m/sftlf_A1_ukmo_hadcm3.nc";;
hadcm3_b2_prcp) file=IPCCData/HADCM3_B2_prec.new.ctl;kindname="HADCM3 B2";climfield="prcp";LSMASK="IPCCData/20c3m/sftlf_A1_ukmo_hadcm3.nc";;
hadcm3_b2_wind) file=IPCCData/HADCM3_B2_wind.ctl;kindname="HADCM3 B2";climfield="10m wind";LSMASK="IPCCData/20c3m/sftlf_A1_ukmo_hadcm3.nc";;
hadcm3_b2_mslp) file=IPCCData/HADCM3_B2_mslp.ctl;kindname="HADCM3 B2";climfield="SLP";LSMASK="IPCCData/20c3m/sftlf_A1_ukmo_hadcm3.nc";;
hadcm3_b2_z500) file=IPCCData/HADCM3_B2_p500.ctl;kindname="HADCM3 B2";climfield="Z500";LSMASK="IPCCData/20c3m/sftlf_A1_ukmo_hadcm3.nc";;

eh4opyc_a2_temp) file=IPCCData/EH4OPYC_SRES_A2_TMP.ctl;kindname="EH4OPYC A2";climfield="Tsfc";;
eh4opyc_a2_tmax) file=IPCCData/EH4OPYC_SRES_A2_tmax.ctl;kindname="EH4OPYC A2";climfield="Tmax";;
eh4opyc_a2_tmin) file=IPCCData/EH4OPYC_SRES_A2_tmin.ctl;kindname="EH4OPYC A2";climfield="Tmin";;
eh4opyc_a2_prcp) file=IPCCData/EH4OPYC_SRES_A2_PREC.new.ctl;kindname="EH4OPYC A2";climfield="prcp";;
eh4opyc_a2_wind) file=IPCCData/EH4OPYC_SRES_A2_WIND.ctl;kindname="EH4OPYC A2";climfield="surface wind";;
eh4opyc_a2_mslp) file=IPCCData/EH4OPYC_SRES_A2_MSLP.ctl;kindname="EH4OPYC A2";climfield="SLP";;
eh4opyc_a2_z500) file=IPCCData/EH4OPYC_SRES_A2_HGT500.ctl;kindname="EH4OPYC A2";climfield="Z500";;

eh4opyc_b2_temp) file=IPCCData/EH4OPYC_SRES_B2_TMP.ctl;kindname="EH4OPYC B2";climfield="Tsfc";;
eh4opyc_b2_tmax) file=IPCCData/EH4OPYC_SRES_B2_tmax.ctl;kindname="EH4OPYC B2";climfield="Tmax";;
eh4opyc_b2_tmin) file=IPCCData/EH4OPYC_SRES_B2_tmin.ctl;kindname="EH4OPYC B2";climfield="Tmin";;
eh4opyc_b2_prcp) file=IPCCData/EH4OPYC_SRES_B2_PREC.new.ctl;kindname="EH4OPYC B2";climfield="prcp";;
eh4opyc_b2_wind) file=IPCCData/EH4OPYC_SRES_B2_WIND.ctl;kindname="EH4OPYC B2";climfield="surface wind";;
eh4opyc_b2_mslp) file=IPCCData/EH4OPYC_SRES_B2_MSLP.ctl;kindname="EH4OPYC B2";climfield="SLP";;
eh4opyc_b2_z500) file=IPCCData/EH4OPYC_SRES_B2_HGT500.ctl;kindname="EH4OPYC B2";climfield="Z500";;

ncarcsm_a2_temp) file=IPCCData/NCARCSM_SRES_A2_TMP.ctl;kindname="NCARCSM A2";climfield="Tsfc";;
ncarcsm_a2_tmax) file=IPCCData/NCARCSM_SRES_A2_TMAX.ctl;kindname="NCARCSM A2";climfield="Tmax";;
ncarcsm_a2_tmin) file=IPCCData/NCARCSM_SRES_A2_TMIN.ctl;kindname="NCARCSM A2";climfield="Tmin";;
ncarcsm_a2_prcp) file=IPCCData/NCARCSM_SRES_A2_PREC.new.ctl;kindname="NCARCSM A2";climfield="prcp";;
ncarcsm_a2_wind) file=IPCCData/NCARCSM_SRES_A2_wind.ctl;kindname="NCARCSM A2";climfield="10m wind";;
ncarcsm_a2_mslp) file=IPCCData/NCARCSM_SRES_A2_MSLP.ctl;kindname="NCARCSM A2";climfield="SLP";;
ncarcsm_a2_z500) file=IPCCData/NCARCSM_SRES_A2_HGT500.ctl;kindname="NCARCSM A2";climfield="Z500";;

gfdl_a2_temp) file=IPCCData/GFDL_SRES_A2_TMP.ctl;kindname="GFDL A2";climfield="Tsfc";;
gfdl_a2_prcp) file=IPCCData/GFDL_SRES_A2_PREC.new.ctl;kindname="GFDL A2";climfield="prcp";;
gfdl_a2_prssfc) file=IPCCData/GFDL_SRES_A2_PRES.ctl;kindname="GFDL A2";climfield="prssfc";;

gfdl_b2_temp) file=IPCCData/GFDL_SRES_B2_TMP.ctl;kindname="GFDL A2";climfield="Tsfc";;
gfdl_b2_prcp) file=IPCCData/GFDL_SRES_B2_PREC.new.ctl;kindname="GFDL A2";climfield="prcp";;
gfdl_b2_prssfc) file=IPCCData/GFDL_SRES_B2_PRES.ctl;kindname="GFDL A2";climfield="prssfc";;

t2m_racmo_era40) file=ENSEMBLES/n_KNMI-RACMO2_CTL_ERA40_MM_25km_tas.nc;kindname="RACMO ERA40";climfield="t2m";map='set lat 30 72
set lon -30 50';;
slp_racmo_era40) file=ENSEMBLES/n_KNMI-RACMO2_CTL_ERA40_MM_25km_tas.nc;kindname="RACMO ERA40";climfield="t2m";map='set lat 30 72
set lon -30 50';;
prcp_racmo_era40) file=ENSEMBLES/n_KNMI-RACMO2_CTL_ERA40_MM_25km_tas.nc;kindname="RACMO ERA40";climfield="t2m";map='set lat 30 72
set lon -30 50';;

t2m_hadam3_6090) file="PrudenceData/t2m.HC.acdhd.1960-1990.nc";kindname="HadAM3H 60-90";climfield="t2m";map='set lon -60 90';;
precip_hadam3_6090) file="PrudenceData/precip.HC.acdhd.1960-1990.nc";kindname="HadAM3H 60-90";climfield="precip";map='set lon -60 90';;
mslp_hadam3_6090) file="PrudenceData/MSLP.HC.acdhd.1960-1990.nc";kindname="HadAM3H 60-90";climfield="MSLP";map='set lon -60 90';;
t2m_hadam3_a2_7000) file="PrudenceData/t2m.HC.acftc.2070-2100.nc";kindname="HadAM3H A2 2070-2100";climfield="t2m";map='set lon -60 90';;
precip_hadam3_a2_7000) file="PrudenceData/precip.HC.acftc.2070-2100.nc";kindname="HadAM3H A2 2070-2100";climfield="precip";map='set lon -60 90';;
mslp_hadam3_a2_7000) file="PrudenceData/MSLP.HC.acftc.2070-2100.nc";kindname="HadAM3H A2 2070-2100";climfield="MSLP";map='set lon -60 90';;

tas_cmip3_all_sresa1b) file="IPCCData/sresa1b/tas_cmip3_%%_144.nc";kindname="CMIP3 20c3m/sresa1b all members";climfield="tas";LSMASK=IPCCData/sresa1b/lsmask_cmip3_144.nc;;
tas_cmip3_ave_sresa1b) file="IPCCData/sresa1b/tas_cmip3_ave_%%_144.nc";kindname="CMIP3 20c3m/sresa1b all models";climfield="tas";LSMASK=IPCCData/sresa1b/lsmask_cmip3_144.nc;;
tas_cmip3_ave_mean_sresa1b) file="IPCCData/sresa1b/tas_cmip3_ave_mean_144.nc";kindname="CMIP3 20c3m/sresa1b multi-model mean";climfield="tas";LSMASK=IPCCData/sresa1b/lsmask_cmip3_144.nc;;
tas_cmip3_volcano_all_sresa1b) file="IPCCData/sresa1b/tas_cmip3_volcano_%%_144.nc";kindname="CMIP3 20c3m/sresa1b volcano members";climfield="tas";LSMASK=IPCCData/sresa1b/lsmask_cmip3_144.nc;;
tas_cmip3_volcano_ave_sresa1b) file="IPCCData/sresa1b/tas_cmip3_volcano_ave_%%_144.nc";kindname="CMIP3 20c3m/sresa1b volcano models";climfield="tas";LSMASK=IPCCData/sresa1b/lsmask_cmip3_144.nc;;
tas_cmip3_volcano_ave_mean_sresa1b) file="IPCCData/sresa1b/tas_cmip3_volcano_ave_mean_144.nc";kindname="CMIP3 20c3m/sresa1b volcano mean";climfield="tas";LSMASK=IPCCData/sresa1b/lsmask_cmip3_144.nc;;
tas_cmip3_novolcano_all_sresa1b) file="IPCCData/sresa1b/tas_cmip3_novolcano_%%_144.nc";kindname="CMIP3 20c3m/sresa1b novolcano members";climfield="tas";LSMASK=IPCCData/sresa1b/lsmask_cmip3_144.nc;;
tas_cmip3_novolcano_ave_sresa1b) file="IPCCData/sresa1b/tas_cmip3_novolcano_ave_%%_144.nc";kindname="CMIP3 20c3m/sresa1b novolcano models";climfield="tas";LSMASK=IPCCData/sresa1b/lsmask_cmip3_144.nc;;
tas_cmip3_novolcano_ave_mean_sresa1b) file="IPCCData/sresa1b/tas_cmip3_novolcano_ave_mean_144.nc";kindname="CMIP3 20c3m/sresa1b novolcano mean";climfield="tas";LSMASK=IPCCData/sresa1b/lsmask_cmip3_144.nc;;
tas_bcc_cm1_20c3m) file="IPCCData/20c3m/tas_A1_bcc_cm1_%%_1871_2003.nc";kindname="bcc cm1 20c3m";climfield="tas";;
tas_bcc_cm1_sresa2) file="IPCCData/sresa2/tas_A1_bcc_cm1_%%.nc";kindname="bcc cm1 sresa2";climfield="tas";;
tas_bccr_bcm2_0_20c3m) file="IPCCData/20c3m/tas_A1_bccr_bcm2_0.nc";kindname="bccr bcm2.0 20c3m";climfield="tas";LSMASK=IPCCData/20c3m/sftlf_A1_bccr_bcm2_0.ctl;;
tas_bccr_bcm2_0_sresa1b) file="IPCCData/sresa1b/tas_A1_bccr_bcm2_0.nc";kindname="bccr bcm2.0 sresa1b";climfield="tas";LSMASK=IPCCData/20c3m/sftlf_A1_bccr_bcm2_0.ctl;;
tas_bccr_bcm2_0_sresa2) file="IPCCData/sresa2/tas_A1_bccr_bcm2_0.nc";kindname="bccr bcm2.0 sresa2";climfield="tas";LSMASK=IPCCData/20c3m/sftlf_A1_bccr_bcm2_0.ctl;;
tas_bccr_bcm2_0_sresb1) file="IPCCData/sresb1/tas_A1_bccr_bcm2_0.nc";kindname="bccr bcm2.0 sresb1";climfield="tas";LSMASK=IPCCData/20c3m/sftlf_A1_bccr_bcm2_0.ctl;;
tas_cccma_cgcm3_1_20c3m) file="IPCCData/20c3m/tas_a1_20c3m_%%_cgcm3.1_t47_1850-2000.nc";kindname="cccma cgcm3.1 20c3m";climfield="tas";LSMASK=IPCCData/20c3m/sftlf_a1_20c3m_cgcm3.1_t47.nc;;
tas_A2_cccma_cgcm3_1_20c3m) file="IPCCData/20c3m_daily/tas_a2_20c3m_%%_cgcm3.1_t47_1961_2000.nc";kindname="cccma cgcm3.1 20c3m";climfield="tas";LSMASK=IPCCData/20c3m/sftlf_a1_20c3m_cgcm3.1_t47.nc;NPERYEAR=365;;
tas_cccma_cgcm3_1_sresa1b) file="IPCCData/sresa1b/tas_a1_sresa1b_%%_cgcm3.1_t47.nc";kindname="cccma cgcm3.1 sresa1b";climfield="tas";LSMASK=IPCCData/20c3m/sftlf_a1_20c3m_cgcm3.1_t47.nc;;
tas_A2_cccma_cgcm3_1_sresa1b_21) file="IPCCData/sresa1b_daily/tas_a2_sresa1b_%%_cgcm3.1_t47_2081_2100.nc";kindname="cccma cgcm3.1 sresa1b";climfield="tas";LSMASK=IPCCData/20c3m/sftlf_a1_20c3m_cgcm3.1_t47.nc;NPERYEAR=365;;
tas_cccma_cgcm3_1_sresa2) file="IPCCData/sresa2/tas_a1_sresa2_1_cgcm3.1_t47_2001_2100.nc";kindname="cccma cgcm3.1 sresa2";climfield="tas";LSMASK=IPCCData/20c3m/sftlf_a1_20c3m_cgcm3.1_t47.nc;;
tas_cccma_cgcm3_1_sresb1) file="IPCCData/sresb1/tas_a1_sresb1_%%_cgcm3.1_t47.nc";kindname="cccma cgcm3.1 sresb1";climfield="tas";LSMASK=IPCCData/20c3m/sftlf_a1_20c3m_cgcm3.1_t47.nc;;
tas_cccma_cgcm3_1_1pctto2x) file="IPCCData/1pctto2x/tas_a1_1pctto2x_1_cgcm3.1_t47_1850_2069.nc";kindname="cccma cgcm3.1 1pctto2x";climfield="tas";LSMASK=IPCCData/20c3m/sftlf_a1_20c3m_cgcm3.1_t47.nc;;
tas_cccma_cgcm3_1_1pctto4x) file="IPCCData/1pctto4x/tas_a1_1pctto4x_1_cgcm3.1_t47_1850_2139.nc";kindname="cccma cgcm3.1 1pctto4x";climfield="tas";LSMASK=IPCCData/20c3m/sftlf_a1_20c3m_cgcm3.1_t47.nc;;
tas_cccma_cgcm3_1_t63_20c3m) file="IPCCData/20c3m/tas_a1_20c3m_1_cgcm3.1_t63_1850_2000.nc";kindname="cccma cgcm3.1 t63 20c3m";climfield="tas";LSMASK=IPCCData/20c3m/sftlf_a1_20c3m_cgcm3.1_t63.nc;;
tas_A2_cccma_cgcm3_1_t63_20c3m) file="IPCCData/20c3m_daily/tas_a2_20c3m_1_cgcm3.1_t63_1961_2000.nc";kindname="cccma cgcm3.1 t63 20c3m";climfield="tas";LSMASK=IPCCData/20c3m/sftlf_a1_20c3m_cgcm3.1_t63.nc;NPERYEAR=365;;
tas_cccma_cgcm3_1_t63_sresa1b) file="IPCCData/sresa1b/tas_a1_sresa1b_1_cgcm3.1_t63_1850_2300.nc";kindname="cccma cgcm3.1 t63 sresa1b";climfield="tas";LSMASK=IPCCData/20c3m/sftlf_a1_20c3m_cgcm3.1_t63.nc;;
tas_A2_cccma_cgcm3_1_t63_sresa1b_21) file="IPCCData/sresa1b_daily/tas_a2_sresa1b_1_cgcm3.1_t63_2081_2100.nc";kindname="cccma cgcm3.1 t63 sresa1b";climfield="tas";LSMASK=IPCCData/20c3m/sftlf_a1_20c3m_cgcm3.1_t63.nc;NPERYEAR=365;;
tas_A2_cccma_cgcm3_1_t63_sresa1b_22) file="IPCCData/sresa1b_daily/tas_a2_sresa1b_1_cgcm3.1_t63_2181_2200.nc";kindname="cccma cgcm3.1 t63 sresa1b";climfield="tas";LSMASK=IPCCData/20c3m/sftlf_a1_20c3m_cgcm3.1_t63.nc;NPERYEAR=365;;
tas_cccma_cgcm3_1_t63_sresb1) file="IPCCData/sresb1/tas_a1_sresb1_1_cgcm3.1_t63_2001_2260.nc";kindname="cccma cgcm3.1 t63 sresb1";climfield="tas";LSMASK=IPCCData/20c3m/sftlf_a1_20c3m_cgcm3.1_t63.nc;;
tas_cnrm_cm3_20c3m) file="IPCCData/20c3m/tas_A1_cnrm_cm3.nc";kindname="cnrm cm3 20c3m";climfield="tas";LSMASK=IPCCData/20c3m/sftlf_A1_cnrm_cm3.nc;;
tas_A2_cnrm_cm3_20c3m) file="IPCCData/20c3m_daily/tas_A2_cnrm_cm3_1961_2000.nc";kindname="cnrm cm3 20c3m";climfield="tas";LSMASK=IPCCData/20c3m/sftlf_A1_cnrm_cm3.nc;NPERYEAR=366;;
tas_cnrm_cm3_sresa1b) file="IPCCData/sresa1b/tas_A1_cnrm_cm3.nc";kindname="cnrm cm3 sresa1b";climfield="tas";LSMASK=IPCCData/20c3m/sftlf_A1_cnrm_cm3.nc;;
tas_A2_cnrm_cm3_sresa1b_21) file="IPCCData/sresa1b_daily/tas_A2_cnrm_cm3_2081_2100.nc";kindname="cnrm cm3 sresa1b";climfield="tas";LSMASK=IPCCData/20c3m/sftlf_A1_cnrm_cm3.nc;NPERYEAR=366;;
tas_cnrm_cm3_sresa2) file="IPCCData/sresa2/tas_A1_cnrm_cm3.nc";kindname="cnrm cm3 sresa2";climfield="tas";LSMASK=IPCCData/20c3m/sftlf_A1_cnrm_cm3.nc;;
tas_cnrm_cm3_sresb1) file="IPCCData/sresb1/tas_A1_cnrm_cm3.nc";kindname="cnrm cm3 sresb1";climfield="tas";LSMASK=IPCCData/20c3m/sftlf_A1_cnrm_cm3.nc;;
tas_csiro_mk3_0_20c3m) file="IPCCData/20c3m/tas_A1_csiro_mk3_0_%%.nc";kindname="csiro_mk3_0 20c3m";climfield="tas";LSMASK=IPCCData/20c3m/sftlf_A1_csiro_mk3_0.nc;;
tas_A2_csiro_mk3_0_20c3m) file="IPCCData/20c3m_daily/tas_A2_csiro_mk3_0_%%_1961-2000.nc";kindname="csiro_mk3_0 20c3m";climfield="tas";LSMASK=IPCCData/20c3m/sftlf_A1_csiro_mk3_0.nc;NPERYEAR=365;;
tas_csiro_mk3_0_sresa1b) file="IPCCData/sresa1b/tas_A1_csiro_mk3_0.nc";kindname="csiro_mk3_0 sresa1b";climfield="tas";LSMASK=IPCCData/20c3m/sftlf_A1_csiro_mk3_0.nc;;
tas_A2_csiro_mk3_0_sresa1b_21) file="IPCCData/sresa1b_daily/tas_A2_csiro_mk3_0_2081_2100.nc";kindname="csiro_mk3_0 sresa1b";climfield="tas";LSMASK=IPCCData/20c3m/sftlf_A1_csiro_mk3_0.nc;NPERYEAR=365;;
tas_csiro_mk3_0_sresa2) file="IPCCData/sresa2/tas_A1_csiro_mk3_0.nc";kindname="csiro_mk3_0 sresa2";climfield="tas";LSMASK=IPCCData/20c3m/sftlf_A1_csiro_mk3_0.nc;;
tas_csiro_mk3_0_sresb1) file="IPCCData/sresb1/tas_A1_csiro_mk3_0.nc";kindname="csiro_mk3_0 sresb1";climfield="tas";LSMASK=IPCCData/20c3m/sftlf_A1_csiro_mk3_0.nc;;
tas_csiro_mk3_5_20c3m) file="IPCCData/20c3m/tas_A1_csiro_mk3_5_%%.nc";kindname="csiro_mk3_5 20c3m";climfield="tas";LSMASK=IPCCData/20c3m/sftlf_A1_csiro_mk3_5.nc;;
tas_csiro_mk3_5_sresa1b) file="IPCCData/sresa1b/tas_A1_csiro_mk3_5.nc";kindname="csiro_mk3_5 sresa1b";climfield="tas";LSMASK=IPCCData/20c3m/sftlf_A1_csiro_mk3_5.nc;;
tas_gfdl_cm2_0_20c3m) file="IPCCData/20c3m/tas_A1_gfdl_cm2_0_%%.186101-200012.nc";kindname="gfdl 2.0 20c3m";climfield="tas";LSMASK="IPCCData/20c3m/sftlf_A1_gfdl_cm2_0.nc";;
tas_A2_gfdl_cm2_0_20c3m) file="IPCCData/20c3m_daily/tas_A2_gfdl_cm2_0_1961-2000.nc";kindname="gfdl 2.0 20c3m";climfield="tas";LSMASK="IPCCData/20c3m/sftlf_A1_gfdl_cm2_0.nc";;
tas_gfdl_cm2_0_sresa1b) file="IPCCData/sresa1b/tas_A1_gfdl_cm2_0.nc";kindname="gfdl 2.0 sresa1b";climfield="tas";LSMASK="IPCCData/20c3m/sftlf_A1_gfdl_cm2_0.nc";;
tas_A2_gfdl_cm2_0_sresa1b_21) file="IPCCData/sresa1b_daily/tas_A2_gfdl_cm2_0_2081-2100.nc";kindname="gfdl 2.0 sresa1b";climfield="tas";LSMASK="IPCCData/20c3m/sftlf_A1_gfdl_cm2_0.nc";NPERYEAR=365;;
tas_gfdl_cm2_0_sresa2) file="IPCCData/sresa2/tas_A1_gfdl_cm2_0.200101-210012.nc";kindname="gfdl 2.0 sresa2";climfield="tas";LSMASK="IPCCData/20c3m/sftlf_A1_gfdl_cm2_0.nc";;
tas_gfdl_cm2_0_sresb1) file="IPCCData/sresb1/tas_A1_gfdl_cm2_0.200101-230012.nc";kindname="gfdl 2.0 sresb1";climfield="tas";LSMASK="IPCCData/20c3m/sftlf_A1_gfdl_cm2_0.nc";;
tas_gfdl_cm2_1_20c3m) file="IPCCData/20c3m/tas_A1_gfdl_cm2_1_%%.186101-200012.nc";kindname="gfdl 2.1 20c3m";climfield="tas";LSMASK="IPCCData/20c3m/sftlf_A1_gfdl_cm2_1.nc";;
tas_A2_gfdl_cm2_1_20c3m) file="IPCCData/20c3m_daily/tas_A2_gfdl_cm2_1.nc";kindname="gfdl 2.1 20c3m";climfield="tas";LSMASK="IPCCData/20c3m/sftlf_A1_gfdl_cm2_1.nc";NPERYEAR=365;;
tas_gfdl_cm2_1_sresa1b) file="IPCCData/sresa1b/tas_A1_gfdl_cm2_1.nc";kindname="gfdl 2.1 sresa1b";climfield="tas";LSMASK="IPCCData/20c3m/sftlf_A1_gfdl_cm2_1.nc";;
tas_gfdl_cm2_1_sresa1b_daily) file="IPCCData/sresa1b_daily/tas_A2.20010101-21001231.nc";kindname="gfdl 2.1 sresa1b";climfield="tas";LSMASK="IPCCData/20c3m/sftlf_A1_gfdl_cm2_1.nc";NPERYEAR=365;;
tas_A2_gfdl_cm2_1_sresa1b_21) file="IPCCData/sresa1b_daily/tas_A2_gfdl_cm2_1_2081-2100.nc";kindname="gfdl 2.1 sresa1b";climfield="tas";LSMASK="IPCCData/20c3m/sftlf_A1_gfdl_cm2_1.nc";NPERYEAR=365;;
tas_A2_gfdl_cm2_1_sresa1b_22) file="IPCCData/sresa1b_daily/tas_A2_gfdl_cm2_1_2181-2200.nc";kindname="gfdl 2.1 sresa1b";climfield="tas";LSMASK="IPCCData/20c3m/sftlf_A1_gfdl_cm2_1.nc";NPERYEAR=365;;
tas_A2_gfdl_cm2_1_sresa1b_23) file="IPCCData/sresa1b_daily/tas_A2_gfdl_cm2_1_2281-2300.nc";kindname="gfdl 2.1 sresa1b";climfield="tas";LSMASK="IPCCData/20c3m/sftlf_A1_gfdl_cm2_1.nc";NPERYEAR=365;;
tas_gfdl_cm2_1_sresa2) file="IPCCData/sresa2/tas_A1_gfdl_cm2_1.200101-210012.nc";kindname="gfdl 2.1 sresa2";climfield="tas";LSMASK="IPCCData/20c3m/sftlf_A1_gfdl_cm2_1.nc";;
tas_gfdl_cm2_1_sresb1) file="IPCCData/sresb1/tas_A1_gfdl_cm2_1.nc";kindname="gfdl 2.1 sresb1";climfield="tas";LSMASK="IPCCData/20c3m/sftlf_A1_gfdl_cm2_1.nc";;
tas_gfdl_cm2_1_1pctto4x) file="IPCCData/1pctto4x/tas_A1_gfdl_cm2_1.nc";kindname="gfdl 2.1 1pctto4x";climfield="tas";LSMASK="IPCCData/20c3m/sftlf_A1_gfdl_cm2_1.nc";;
tas_giss_aom_20c3m) file="IPCCData/20c3m/tas_A1_giss_aom_%%.nc";kindname="giss aom 20c3m";climfield="tas";LSMASK=IPCCData/20c3m/lsmask_giss_aom.nc;;
tas_giss_aom_sresa1b) file="IPCCData/sresa1b/tas_A1_giss_aom_%%.nc";kindname="giss aom sresa1b";climfield="tas";LSMASK=IPCCData/20c3m/lsmask_giss_aom.nc;;
tas_giss_aom_sresb1) file="IPCCData/sresb1/tas_A1_giss_aom_%%.nc";kindname="giss aom sresb1";climfield="tas";LSMASK=IPCCData/20c3m/lsmask_giss_aom.nc;;
tas_giss_aom_sresb1) file="IPCCData/sresb1/tas_A1_giss_aom_%%.nc";kindname="giss aom sresb1";climfield="tas";LSMASK=IPCCData/20c3m/lsmask_giss_aom.nc;;
tas_giss_model_e_h_20c3m) file="IPCCData/20c3m/tas_A1.GISS3.20C3M.%%.nc";kindname="giss eh 20c3m";climfield="tas";LSMASK=IPCCData/20c3m/lsmask_giss_model_e_h.nc;;
tas_giss_model_e_h_sresa1b) file="IPCCData/sresa1b/tas_A1.GISS3.SRESA1B.%%.nc";kindname="giss eh sresa1b";climfield="tas";LSMASK=IPCCData/20c3m/lsmask_giss_model_e_h.nc;;
tas_giss_model_e_h_1pctto2x) file="IPCCData/1pctto2x/tas_A1.GISS3.1pctto2.nc";kindname="giss eh 1pctto2x";climfield="tas";LSMASK=IPCCData/20c3m/lsmask_giss_model_e_h.nc;;
tas_giss_model_e_r_20c3m) file="IPCCData/20c3m/tas_A1.GISS1.20C3M.%%.nc";kindname="giss er 20c3m";climfield="tas";LSMASK=IPCCData/20c3m/lsmask_giss_model_e_r.nc;;
tas_giss_model_e_r_sresa1b) file="IPCCData/sresa1b/tas_A1.GISS1.SRESA1B.%%.nc";kindname="giss er sresa1b";climfield="tas";LSMASK=IPCCData/20c3m/lsmask_giss_model_e_r.nc;;
tas_giss_model_e_r_sresa2) file="IPCCData/sresa2/tas_A1.GISS1.SRESA2.nc";kindname="giss er sresa2";climfield="tas";LSMASK=IPCCData/20c3m/lsmask_giss_model_e_r.nc;;
tas_iap_fgoals1_0_g_20c3m) file="IPCCData/20c3m/tas_A1_iap_fgoals1_0_g_%%.nc";kindname="iap fgoals10g 20c3m";climfield="tas";;
tas_iap_fgoals1_0_g_sresa1b) file="IPCCData/sresa1b/tas_A1_iap_fgoals1_0_g_%%.nc";kindname="iap fgoals10g sresa1b";climfield="tas";;
tas_ingv_echam4_20c3m) file="IPCCData/20c3m/tas_A1_ingv_echam4.nc";kindname="ingv_echam4 20c3m";climfield="tas";LSMASK=IPCCData/20c3m/sftlf_A1_ingv_echam4.nc;;
tas_ingv_echam4_sresa1b) file="IPCCData/sresa1b/tas_A1_ingv_echam4.nc";kindname="ingv_echam4 sresa1b";climfield="tas";LSMASK=IPCCData/20c3m/sftlf_A1_ingv_echam4.nc;;
tas_inmcm3_0_20c3m) file="IPCCData/20c3m/tas_A1_inmcm3_0.nc";kindname="inmcm3.0 20c3m";climfield="tas";LSMASK=IPCCData/20c3m/sftlf_A1_inmcm3_0.nc;;
tas_inmcm3_0_sresa1b) file="IPCCData/sresa1b/tas_A1_inmcm3_0.nc";kindname="inmcm3.0 sresa1b";climfield="tas";LSMASK=IPCCData/20c3m/sftlf_A1_inmcm3_0.nc;;
tas_inmcm3_0_sresa2) file="IPCCData/sresa2/tas_A1_inmcm3_0.nc";kindname="inmcm3.0 sresa2";climfield="tas";LSMASK=IPCCData/20c3m/sftlf_A1_inmcm3_0.nc;;
tas_inmcm3_0_sresb1) file="IPCCData/sresb1/tas_A1_inmcm3_0.nc";kindname="inmcm3.0 sresb1";climfield="tas";LSMASK=IPCCData/20c3m/sftlf_A1_inmcm3_0.nc;;
tas_ipsl_cm4_20c3m) file="IPCCData/20c3m/tas_A1_ipsl_cm4_1860-2000.nc";kindname="ipsl cm4 20c3m";climfield="tas";LSMASK=IPCCData/20c3m/sftlf_A1_ipsl_cm4.nc;;
tas_A2_ipsl_cm4_20c3m) file="IPCCData/20c3m_daily/tas_A2_ipsl_cm4_%%_1961_2000.nc";kindname="ipsl cm4 20c3m";climfield="tas";LSMASK=IPCCData/20c3m/sftlf_A1_ipsl_cm4.nc;NPERYEAR=360;;
tas_ipsl_cm4_sresa1b) file="IPCCData/sresa1b/tas_A1_ipsl_cm4.nc";kindname="ipsl cm4 sresa1b";climfield="tas";LSMASK=IPCCData/20c3m/sftlf_A1_ipsl_cm4.nc;;
tas_A2_ipsl_cm4_sresa1b_21) file="IPCCData/sresa1b_daily/tas_A2_ipsl_cm4_2081-2100.nc";kindname="ipsl cm4 sresa1b";climfield="tas";LSMASK=IPCCData/20c3m/sftlf_A1_ipsl_cm4.nc;NPERYEAR=360;;
tas_A2_ipsl_cm4_sresa1b_22) file="IPCCData/sresa1b_daily/tas_A2_ipsl_cm4_2181-2200.nc";kindname="ipsl cm4 sresa1b";climfield="tas";LSMASK=IPCCData/20c3m/sftlf_A1_ipsl_cm4.nc;NPERYEAR=360;;
tas_ipsl_cm4_sresa2) file="IPCCData/sresa2/tas_A1_ipsl_cm4_2000-2100.nc";kindname="ipsl cm4 sresa2";climfield="tas";LSMASK=IPCCData/20c3m/sftlf_A1_ipsl_cm4.nc;;
tas_ipsl_cm4_sresb1) file="IPCCData/sresb1/tas_A1_ipsl_cm4.nc";kindname="ipsl cm4 sresb1";climfield="tas";LSMASK=IPCCData/20c3m/sftlf_A1_ipsl_cm4.nc;;
tas_miroc3_2_hires_20c3m) file="IPCCData/20c3m/tas_A1_miroc3_2_hires.nc";kindname="miroc 3.2 hi 20c3m";climfield="tas";LSMASK="IPCCData/20c3m/sftlf_A1_miroc3_2_hires.nc";;
tas_A2_miroc3_2_hires_20c3m) file="IPCCData/20c3m_daily/tas_A2_miroc3_2_hires.nc";kindname="miroc 3.2 hi 20c3m";climfield="tas";LSMASK="IPCCData/20c3m/sftlf_A1_miroc3_2_hires.nc";NPERYEAR=366;;
tas_miroc3_2_hires_sresa1b) file="IPCCData/sresa1b/tas_A1_miroc3_2_hires.nc";kindname="miroc 3.2 hi sresa1b";climfield="tas";LSMASK="IPCCData/20c3m/sftlf_A1_miroc3_2_hires.nc";;
tas_A2_miroc3_2_hires_sresa1b) file="IPCCData/sresa1b_daily/tas_A2_miroc3_2_hires_2081_2100.nc";kindname="miroc 3.2 hi sresa1b";climfield="tas";LSMASK="IPCCData/20c3m/sftlf_A1_miroc3_2_hires.nc";NPERYEAR=366;;
tas_miroc3_2_hires_sresb1) file="IPCCData/sresb1/tas_A1_miroc3_2_hires.nc";kindname="miroc 3.2 hi sresb1";climfield="tas";LSMASK="IPCCData/20c3m/sftlf_A1_miroc3_2_hires.nc";;
tas_miroc3_2_hires_1pctto2x) file="IPCCData/1pctto2x/tas_A1_miroc3_2_hires.nc";kindname="miroc 3.2 hi 1pctto2x";climfield="tas";LSMASK="IPCCData/20c3m/sftlf_A1_miroc3_2_hires.nc";;
tas_miroc3_2_medres_20c3m) file="IPCCData/20c3m/tas_A1_miroc3_2_medres_%%.nc";kindname="miroc 3.2 med 20c3m";climfield="tas";LSMASK="IPCCData/20c3m/sftlf_A1_miroc3_2_medres.nc";;
tas_A2_miroc3_2_medres_20c3m) file="IPCCData/20c3m_daily/tas_A2_miroc3_2_medres_%%_1961_2000.nc";kindname="miroc 3.2 med 20c3m";climfield="tas";LSMASK="IPCCData/20c3m/sftlf_A1_miroc3_2_medres.nc";NPERYEAR=366;;
tas_miroc3_2_medres_sresa1b) file="IPCCData/sresa1b/tas_A1_miroc3_2_medres_%%.nc";kindname="miroc 3.2 med sresa1b";climfield="tas";LSMASK="IPCCData/20c3m/sftlf_A1_miroc3_2_medres.nc";;
tas_A2_miroc3_2_medres_sresa1b_21) file="IPCCData/sresa1b_daily/tas_A2_miroc3_2_medres_%%_2081_2100.nc";kindname="miroc 3.2 med sresa1b";climfield="tas";LSMASK="IPCCData/20c3m/sftlf_A1_miroc3_2_medres.nc";NPERYEAR=366;;
tas_miroc3_2_medres_sresa2) file="IPCCData/sresa2/tas_A1_miroc3_2_medres_%%.nc";kindname="miroc 3.2 med sresa2";climfield="tas";LSMASK="IPCCData/20c3m/sftlf_A1_miroc3_2_medres.nc";;
tas_miroc3_2_medres_sresb1) file="IPCCData/sresb1/tas_A1_miroc3_2_medres_%%.nc";kindname="miroc 3.2 med sresb1";climfield="tas";LSMASK="IPCCData/20c3m/sftlf_A1_miroc3_2_medres.nc";;
tas_miroc3_2_medres_1pctto4x) file="IPCCData/1pctto4x/tas_A1_miroc3_2_medres_%%.nc";kindname="miroc 3.2 med 1pctto4x";climfield="tas";LSMASK="IPCCData/20c3m/sftlf_A1_miroc3_2_medres.nc";;
tas_miub_echo_g_20c3m) file="IPCCData/20c3m/tas_A1_miub_echo_g_%%_0007-0147.nc";kindname="miub echo g 20c3m";climfield="tas";LSMASK="IPCCData/20c3m/sftlf_A1_miub_echo_g.nc";;
tas_A2_miub_echo_g_20c3m) file="IPCCData/20c3m_daily/tas_A2_miub_echo_g_%%_1961_2000.nc";kindname="miub echo g 20c3m";climfield="tas";LSMASK="IPCCData/20c3m/sftlf_A1_miub_echo_g.nc";NPERYEAR=360;;
tas_miub_echo_g_sresa1b) file="IPCCData/sresa1b/tas_A1_miub_echo_g_%%.nc";kindname="miub echo g sresa1b";climfield="tas";LSMASK="IPCCData/20c3m/sftlf_A1_miub_echo_g.nc";;
tas_A2_miub_echo_g_sresa1b_21) file="IPCCData/sresa1b_daily/tas_A2_miub_echo_g_%%_2081_2100.nc";kindname="miub echo g sresa1b";climfield="tas";LSMASK="IPCCData/20c3m/sftlf_A1_miub_echo_g.nc";NPERYEAR=360;;
tas_miub_echo_g_sresa2) file="IPCCData/sresa2/tas_A1_miub_echo_g_%%_0148-0247.nc";kindname="miub echo g sresa2";climfield="tas";LSMASK="IPCCData/20c3m/sftlf_A1_miub_echo_g.nc";;
tas_miub_echo_g_sresb1) file="IPCCData/sresb1/tas_A1_miub_echo_g_%%.nc";kindname="miub echo g sresb1";climfield="tas";LSMASK="IPCCData/20c3m/sftlf_A1_miub_echo_g.nc";;
tas_mpi_echam5_20c3m) file="IPCCData/20c3m/tas_A1_mpi_echam5_%%.nc";kindname="mpi echam5 20c3m";climfield="tas";LSMASK="IPCCData/20c3m/lsmask_mpi_echam5.nc";;
tas_A2_mpi_echam5_20c3m) file="IPCCData/20c3m_daily/tas_A2_mpi_echam5_%%_1961_2000.nc";kindname="mpi echam5 20c3m";climfield="tas";LSMASK="IPCCData/20c3m/lsmask_mpi_echam5.nc";NPERYEAR=366;;
tas_mpi_echam5_sresa1b) file="IPCCData/sresa1b/tas_A1_mpi_echam5_%%.nc";kindname="mpi echam5 sresa1b";climfield="tas";LSMASK="IPCCData/20c3m/lsmask_mpi_echam5.nc";;
tas_mpi_echam5_picntrl) file="IPCCData/picntrl/tas_mpi_echam5.nc";kindname="mpi echam5 picntrl";climfield="tas";LSMASK="IPCCData/20c3m/lsmask_mpi_echam5.nc";;
tas_A2_mpi_echam5_sresa1b_21) file="IPCCData/sresa1b_daily/tas_A2_mpi_echam5_%%_2081-2100.nc";kindname="mpi echam5 sresa1b";climfield="tas";LSMASK="IPCCData/20c3m/lsmask_mpi_echam5.nc";NPERYEAR=366;;
tas_A2_mpi_echam5_sresa1b_22) file="IPCCData/sresa1b_daily/tas_A2_mpi_echam5_2181-2200.nc";kindname="mpi echam5 sresa1b";climfield="tas";LSMASK="IPCCData/20c3m/lsmask_mpi_echam5.nc";NPERYEAR=366;;
tas_A2_mpi_echam5_sresa1b_23) file="IPCCData/sresa1b_daily/tas_A2_mpi_echam5_2281-2300.nc";kindname="mpi echam5 sresa1b";climfield="tas";LSMASK="IPCCData/20c3m/lsmask_mpi_echam5.nc";NPERYEAR=366;;
tas_mpi_echam5_sresa2) file="IPCCData/sresa2/tas_A1_mpi_echam5_%%.nc";kindname="mpi echam5 sresa2";climfield="tas";LSMASK="IPCCData/20c3m/lsmask_mpi_echam5.nc";;
tas_mpi_echam5_sresb1) file="IPCCData/sresb1/tas_A1_mpi_echam5_%%.nc";kindname="mpi echam5 sresb1";climfield="tas";LSMASK="IPCCData/20c3m/lsmask_mpi_echam5.nc";;
tas_mpi_echam5_picntrl) file="IPCCData/picntrl/tas_A1_mpi_echam5_%%.nc";kindname="mpi echam5 picntrl";climfield="tas";LSMASK="IPCCData/20c3m/lsmask_mpi_echam5.nc";;
tas_mpi_echam5_1pctto2x) file="IPCCData/1pctto2x/tas_A1_mpi_echam5_%%.nc";kindname="mpi echam5 1pctto2x";climfield="tas";LSMASK="IPCCData/20c3m/lsmask_mpi_echam5.nc";;
tas_mpi_echam5_1pctto4x) file="IPCCData/1pctto4x/tas_A1_mpi_echam5.nc";kindname="mpi echam5 1pctto4x";climfield="tas";LSMASK="IPCCData/20c3m/lsmask_mpi_echam5.nc";;
tas_mri_cgcm2_3_2a_20c3m) file="IPCCData/20c3m/tas_A1_mri_cgcm2_3_2a_%%.nc";kindname="mri cgcm232a 20c3m";climfield="tas";LSMASK="IPCCData/20c3m/sftlf_A1_mri_cgcm2_3_2a.nc";;
tas_A2_mri_cgcm2_3_2a_20c3m) file="IPCCData/20c3m_daily/tas_A2_mri_cgcm2_3_2a_%%_1961_2000.nc";kindname="mri cgcm232a 20c3m";climfield="tas";LSMASK="IPCCData/20c3m/sftlf_A1_mri_cgcm2_3_2a.nc";NPERYEAR=365;;
tas_mri_cgcm2_3_2a_sresa1b) file="IPCCData/sresa1b/tas_A1_mri_cgcm2_3_2a_%%.nc";kindname="mri cgcm232a sresa1b";climfield="tas";LSMASK="IPCCData/20c3m/sftlf_A1_mri_cgcm2_3_2a.nc";;
tas_A2_mri_cgcm2_3_2a_sresa1b_21) file="IPCCData/sresa1b_daily/tas_A2_mri_cgcm2_3_2a_%%.nc";kindname="mri cgcm232a sresa1b";climfield="tas";LSMASK="IPCCData/20c3m/sftlf_A1_mri_cgcm2_3_2a.nc";NPERYEAR=365;;
tas_mri_cgcm2_3_2a_sresa2) file="IPCCData/sresa2/tas_A1_mri_cgcm2_3_2a_%%.nc";kindname="mri cgcm232a sresa2";climfield="tas";LSMASK="IPCCData/20c3m/sftlf_A1_mri_cgcm2_3_2a.nc";;
tas_mri_cgcm2_3_2a_sresb1) file="IPCCData/sresb1/tas_A1_mri_cgcm2_3_2a_%%.nc";kindname="mri cgcm232a sresb1";climfield="tas";LSMASK="IPCCData/20c3m/sftlf_A1_mri_cgcm2_3_2a.nc";;
tas_ncar_ccsm3_0_20c3m) file="IPCCData/20c3m/tas_A1.20C3M_%%.CCSM.atmm.1870-01_cat_1999-12.nc";kindname="ccsm 3.0 20c3m";climfield="tas";LSMASK="IPCCData/20c3m/sftlf_A1.20C3M.CCSM.atmm.nc";;
tas_ncar_ccsm3_0_sresa1b) file="IPCCData/sresa1b/tas_A1.SRESA1B_%%.CCSM.atmm.2000-01_cat_2099-12.nc";kindname="ccsm 3.0 sresa1b";climfield="tas";LSMASK="IPCCData/20c3m/sftlf_A1.20C3M.CCSM.atmm.nc";;
tas_ncar_ccsm3_0_sresa2) file="IPCCData/sresa2/tas_A1_ncar_ccsm3_0_%%.nc";kindname="ccsm 3.0 sresa2";climfield="tas";LSMASK="IPCCData/20c3m/sftlf_A1.20C3M.CCSM.atmm.nc";;
tas_ncar_ccsm3_0_sresb1) file="IPCCData/sresb1/tas_A1.SRESB1_%%.CCSM.atmm.nc";kindname="ccsm 3.0 sresb1";climfield="tas";LSMASK="IPCCData/20c3m/sftlf_A1.20C3M.CCSM.atmm.nc";;
tas_ncar_pcm1_20c3m) file="IPCCData/20c3m/tas_A1.20C3M_%%.PCM1.atmm.1890-01_cat_1999-12.nc";kindname="pcm1 20c3m";climfield="tas";LSMASK="IPCCData/20c3m/sftlf_A1.20C3M.PCM1.atmm.nc";;
tas_ncar_pcm1_sresa1b) file="IPCCData/sresa1b/tas_A1.SRESA1B_%%.PCM1.nc";kindname="pcm1 sresa1b";climfield="tas";LSMASK="IPCCData/20c3m/sftlf_A1.20C3M.PCM1.atmm.nc";;
tas_ncar_pcm1_sresa2) file="IPCCData/sresa2/tas_A1.SRESA2_1.PCM1.atmm.2000-01_cat_2099-12.nc";kindname="pcm1 sresa2";climfield="tas";LSMASK="IPCCData/20c3m/sftlf_A1.20C3M.PCM1.atmm.nc";;
tas_ncar_pcm1_sresb1) file="IPCCData/sresb1/tas_A1_ncar_pcm1_%%.nc";kindname="pcm1 sresb1";climfield="tas";LSMASK="IPCCData/20c3m/sftlf_A1.20C3M.PCM1.atmm.nc";;
tas_ukmo_hadcm3_20c3m) file="IPCCData/20c3m/tas_A1_ukmo_hadcm3_%%.nc";kindname="hadcm3 20c3m";climfield="tas";LSMASK="IPCCData/20c3m/sftlf_A1_ukmo_hadcm3.nc";;
tas_ukmo_hadcm3_sresa1b) file="IPCCData/sresa1b/tas_A1_ukmo_hadcm3.nc";kindname="hadcm3 sresa1b";climfield="tas";LSMASK="IPCCData/20c3m/sftlf_A1_ukmo_hadcm3.nc";;
tas_ukmo_hadcm3_sresa2) file="IPCCData/sresa2/tas_A1_ukmo_hadcm3.nc";kindname="hadcm3 sresa2";climfield="tas";LSMASK="IPCCData/20c3m/sftlf_A1_ukmo_hadcm3.nc";;
tas_ukmo_hadcm3_sresb1) file="IPCCData/sresb1/tas_A1_ukmo_hadcm3.nc";kindname="hadcm3 sresb1";climfield="tas";LSMASK="IPCCData/20c3m/sftlf_A1_ukmo_hadcm3.nc";;
tas_ukmo_hadgem1_picntrl) file="IPCCData/picntrl/tas_A1_ukmo_hadgem1.nc";kindname="hadgem1";climfield="tas";LSMASK="IPCCData/picntrl/sftlf_A1_ukmo_hadgem1.nc";;
tas_ukmo_hadgem1_20c3m) file="IPCCData/20c3m/tas_A1_ukmo_hadgem1_%%.nc";kindname="hadgem1";climfield="tas";LSMASK="IPCCData/picntrl/sftlf_A1_ukmo_hadgem1.nc";;
tas_ukmo_hadgem1_1pctto2x) file="IPCCData/1pctto2x/tas_A1_ukmo_hadgem1.nc";kindname="hadgem1";climfield="tas";LSMASK="IPCCData/picntrl/sftlf_A1_ukmo_hadgem1.nc";;
tas_ukmo_hadgem1_sresa1b) file="IPCCData/sresa1b/tas_A1_ukmo_hadgem1.nc";kindname="hadgem1";climfield="tas";LSMASK="IPCCData/picntrl/sftlf_A1_ukmo_hadgem1.nc";;
tas_ukmo_hadgem1_sresa2) file="IPCCData/sresa2/tas_A1_ukmo_hadgem1_2000_Jan_to_2099_Nov.nc";kindname="hadgem1";climfield="tas";LSMASK="IPCCData/picntrl/sftlf_A1_ukmo_hadgem1.nc";;

tmin_A2_cccma_cgcm3_1_20c3m) file="IPCCData/20c3m_daily/tasmin_a2_cccma_cgcm3_1_%%.nc";kindname="cccma cgcm3.1  20c3m";climfield="tmin";LSMASK=IPCCData/20c3m/sftlf_a1_20c3m_cgcm3.1_t47.nc;NPERYEAR=365;;
tmin_A2_cccma_cgcm3_1_sresa1b_20) file="IPCCData/sresa1b_daily/tasmin_a2_sresa1b_%%_cgcm3.1_t47_2046_2065.nc";kindname="cccma cgcm3.1 sresa1b";climfield="tmin";LSMASK=IPCCData/20c3m/sftlf_a1_20c3m_cgcm3.1_t47.nc;;
tmin_A2_cccma_cgcm3_1_sresa1b_21) file="IPCCData/sresa1b_daily/tasmin_a2_sresa1b_%%_cgcm3.1_t47_2081_2100.nc";kindname="cccma cgcm3.1 sresa1b";climfield="tmin";LSMASK=IPCCData/20c3m/sftlf_a1_20c3m_cgcm3.1_t47.nc;;
tmin_A2_cnrm_cm3_20c3m) file="IPCCData/20c3m_daily/tasmin_A2_cnrm_cm3.nc";kindname="cnrm cm3 20c3m";climfield="tmin";LSMASK=IPCCData/20c3m/sftlf_A1_cnrm_cm3.nc;NPERYEAR=366;;
tmin_A2_cnrm_cm3_sresa1b_20) file="IPCCData/sresa1b_daily/tasmin_A2_cnrm_cm3_2046_2065.nc";kindname="cnrm cm3 sresa1b";climfield="tmin";LSMASK=IPCCData/20c3m/sftlf_A1_cnrm_cm3.nc;;
tmin_A2_cnrm_cm3_sresa1b_21) file="IPCCData/sresa1b_daily/tasmin_A2_cnrm_cm3_2081_2100.nc";kindname="cnrm cm3 sresa1b";climfield="tmin";LSMASK=IPCCData/20c3m/sftlf_A1_cnrm_cm3.nc;;
tmin_A2_csiro_mk3_0_20c3m) file="IPCCData/20c3m_daily/tasmin_A2_csiro_mk3_0_%%.nc";kindname="csiro_mk3_0 20c3m";climfield="tmin";LSMASK=IPCCData/20c3m/sftlf_A1_csiro_mk3_0.nc;NPERYEAR=365;;
tmin_A2_csiro_mk3_0_sresa1b_20) file="IPCCData/sresa1b_daily/tasmin_A2_csiro_mk3_0_2046_2065.nc";kindname="csiro mk3.0 sresa1b";climfield="tmin";LSMASK=IPCCData/20c3m/sftlf_A1_csiro_mk3_0.nc;;
tmin_A2_csiro_mk3_0_sresa1b_21) file="IPCCData/sresa1b_daily/tasmin_A2_csiro_mk3_0_2081_2100.nc";kindname="csiro mk3.0 sresa1b";climfield="tmin";LSMASK=IPCCData/20c3m/sftlf_A1_csiro_mk3_0.nc;;
tmin_A2_gfdl_cm2_0_20c3m) file="IPCCData/20c3m_daily/tasmin_A2_gfdl_cm2_0.nc";kindname="gfdl 2.0 20c3m";climfield="tmin";LSMASK="IPCCData/20c3m/sftlf_A1_gfdl_cm2_0.nc";NPERYEAR=365;;
tmin_A2_gfdl_cm2_0_sresa1b_20) file="IPCCData/sresa1b_daily/tasmin_A2_gfdl_cm2_0_2046-2065.nc";kindname="gfdl 2.0 sresa1b";climfield="tmin";LSMASK="IPCCData/20c3m/sftlf_A1_gfdl_cm2_0.nc";NPERYEAR=365;;
tmin_A2_gfdl_cm2_0_sresa1b_21) file="IPCCData/sresa1b_daily/tasmin_A2_gfdl_cm2_0_2081-2100.nc";kindname="gfdl 2.0 sresa1b";climfield="tmin";LSMASK="IPCCData/20c3m/sftlf_A1_gfdl_cm2_0.nc";NPERYEAR=365;;
tmin_A2_gfdl_cm2_1_20c3m) file="IPCCData/20c3m_daily/tasmin_A2_gfdl_cm2_1.nc";kindname="gfdl 2.1 20c3m";climfield="tmin";LSMASK="IPCCData/20c3m/sftlf_A1_gfdl_cm2_1.nc";NPERYEAR=365;;
tmin_A2_gfdl_cm2_1_sresa1b_20) file="IPCCData/sresa1b_daily/tasmin_A2_gfdl_cm2_1_2046-2065.nc";kindname="gfdl 2.1 sresa1b";climfield="tmin";LSMASK="IPCCData/20c3m/sftlf_A1_gfdl_cm2_1.nc";NPERYEAR=365;;
tmin_A2_gfdl_cm2_1_sresa1b_21) file="IPCCData/sresa1b_daily/tasmin_A2_gfdl_cm2_1_2081-2100.nc";kindname="gfdl 2.1 sresa1b";climfield="tmin";LSMASK="IPCCData/20c3m/sftlf_A1_gfdl_cm2_1.nc";NPERYEAR=365;;
tmin_A2_ipsl_cm4_20c3m) file="IPCCData/20c3m_daily/tasmin_A2_ipsl_%%.nc";kindname="ipsl cm4 20c3m";climfield="tmin";LSMASK=IPCCData/20c3m/sftlf_A1_ipsl_cm4.nc;NPERYEAR=360;;
tmin_A2_ipsl_cm4_sresa1b_20) file="IPCCData/sresa1b_daily/tasmin_A2_ipsl_cm4_2046-2065.nc";kindname="ipsl cm4 sresa1b";climfield="tmin";LSMASK=IPCCData/20c3m/sftlf_A1_ipsl_cm4.nc;NPERYEAR=360;;
tmin_A2_ipsl_cm4_sresa1b_21) file="IPCCData/sresa1b_daily/tasmin_A2_ipsl_cm4_2081-2100.nc";kindname="ipsl cm4 sresa1b";climfield="tmin";LSMASK=IPCCData/20c3m/sftlf_A1_ipsl_cm4.nc;NPERYEAR=360;;
tmin_A2_miroc3_2_medres_20c3m) file="IPCCData/20c3m_daily/tasmin_A2_miroc3_2_medres_%%.nc";kindname="miroc 3.2 med 20c3m";climfield="tmin";LSMASK="IPCCData/20c3m/sftlf_A1_miroc3_2_medres.nc";NPERYEAR=366;;
tmin_A2_miroc3_2_medres_sresa1b_20) file="IPCCData/sresa1b_daily/tasmin_A2_miroc3_2_medres_%%_2046_2065.nc";kindname="miroc 3.2 med sresa1b";climfield="tmin";LSMASK="IPCCData/20c3m/sftlf_A1_miroc3_2_medres.nc";NPERYEAR=366;;
tmin_A2_miroc3_2_medres_sresa1b_21) file="IPCCData/sresa1b_daily/tasmin_A2_miroc3_2_medres_%%_2081_2100.nc";kindname="miroc 3.2 med sresa1b";climfield="tmin";LSMASK="IPCCData/20c3m/sftlf_A1_miroc3_2_medres.nc";NPERYEAR=366;;
tmin_A2_miub_echo_g_20c3m) file="IPCCData/20c3m_daily/tasmin_A2_miub_echo_g_%%.nc";kindname="miub echo g 20c3m";climfield="tmin";LSMASK="IPCCData/20c3m/sftlf_A1_miub_echo_g.nc";NPERYEAR=360;;
tmin_A2_miub_echo_g_sresa1b_20) file="IPCCData/sresa1b_daily/tasmin_A2_miub_echo_g_%%_2046_2065.nc";kindname="miub echo g sresa1b";climfield="tmin";LSMASK="IPCCData/20c3m/sftlf_A1_miub_echo_g.nc";NPERYEAR=360;;
tmin_A2_miub_echo_g_sresa1b_21) file="IPCCData/sresa1b_daily/tasmin_A2_miub_echo_g_%%_2081_2100.nc";kindname="miub echo g sresa1b";climfield="tmin";LSMASK="IPCCData/20c3m/sftlf_A1_miub_echo_g.nc";NPERYEAR=360;;
tmin_A2_mpi_echam5_20c3m) file="IPCCData/20c3m_daily/tasmin_A2_mpi_echam5_00.nc";kindname="mpi echam5 20c3m";climfield="tmin";LSMASK="IPCCData/20c3m/lsmask_mpi_echam5.nc";NPERYEAR=366;;
tmin_A2_mpi_echam5_sresa1b_20) file="IPCCData/sresa1b_daily/tasmin_A2_mpi_echam5_2046-2065.nc";kindname="mpi echam5 sresa1b";climfield="tmin";LSMASK="IPCCData/20c3m/lsmask_mpi_echam5.nc";NPERYEAR=366;;
tmin_A2_mpi_echam5_sresa1b_21) file="IPCCData/sresa1b_daily/tasmin_A2_mpi_echam5_2081-2100.nc";kindname="mpi echam5 sresa1b";climfield="tmin";LSMASK="IPCCData/20c3m/lsmask_mpi_echam5.nc";NPERYEAR=366;;
tmin_A2_mri_cgcm2_3_2a_20c3m) file="IPCCData/20c3m_daily/tasmin_A2_mri_cgcm2_3_2a_%%.nc";kindname="mri cgcm232a 20c3m";climfield="tmin";LSMASK="IPCCData/20c3m/sftlf_A1_mri_cgcm2_3_2a.nc";NPERYEAR=365;;
tmin_A2_mri_cgcm2_3_2a_sresa1b_20) file="IPCCData/sresa1b_daily/tasmin_A2_mri_cgcm2_3_2a_%%_2046-2065.nc";kindname="mri cgcm232a sresa1b";climfield="tmin";LSMASK="IPCCData/20c3m/sftlf_A1_mri_cgcm2_3_2a.nc";NPERYEAR=365;;
tmin_A2_mri_cgcm2_3_2a_sresa1b_21) file="IPCCData/sresa1b_daily/tasmin_A2_mri_cgcm2_3_2a_%%_2081-2100.nc";kindname="mri cgcm232a sresa1b";climfield="tmin";LSMASK="IPCCData/20c3m/sftlf_A1_mri_cgcm2_3_2a.nc";NPERYEAR=365;;
tmin_A2_ukmo_hadcm3_20c3m) file="IPCCData/20c3m_daily/tasmin_A2_ukmo_hadcm3.nc";kindname="hadcm3 20c3m";climfield="tmin";LSMASK="IPCCData/20c3m/sftlf_A1_ukmo_hadcm3.nc";NPERYEAR=360;;
tmin_A2_ukmo_hadgem1_20c3m) file="IPCCData/20c3m_daily/tasmin_A2_ukmo_hadgem1.nc";kindname="hadgem1 20c3m";climfield="tmin";LSMASK="IPCCData/picntrl/sftlf_A1_ukmo_hadgem1.nc";NPERYEAR=360;;


tmax_A2_cccma_cgcm3_1_20c3m) file="IPCCData/20c3m_daily/tasmax_a2_cccma_cgcm3_1_%%.nc";kindname="cccma cgcm3.1  20c3m";climfield="tmax";LSMASK=IPCCData/20c3m/sftlf_a1_20c3m_cgcm3.1_t47.nc;NPERYEAR=365;;
tmax_A2_cccma_cgcm3_1_sresa1b_20) file="IPCCData/sresa1b_daily/tasmax_a2_sresa1b_%%_cgcm3.1_t47_2046_2065.nc";kindname="cccma cgcm3.1 sresa1b";climfield="tmax";LSMASK=IPCCData/20c3m/sftlf_a1_20c3m_cgcm3.1_t47.nc;;
tmax_A2_cccma_cgcm3_1_sresa1b_21) file="IPCCData/sresa1b_daily/tasmax_a2_sresa1b_%%_cgcm3.1_t47_2081_2100.nc";kindname="cccma cgcm3.1 sresa1b";climfield="tmax";LSMASK=IPCCData/20c3m/sftlf_a1_20c3m_cgcm3.1_t47.nc;;
tmax_A2_cnrm_cm3_20c3m) file="IPCCData/20c3m_daily/tasmax_A2_cnrm_cm3.nc";kindname="cnrm cm3 20c3m";climfield="tmax";LSMASK=IPCCData/20c3m/sftlf_A1_cnrm_cm3.nc;NPERYEAR=366;;
tmax_A2_cnrm_cm3_sresa1b_20) file="IPCCData/sresa1b_daily/tasmax_A2_cnrm_cm3_2046_2065.nc";kindname="cnrm cm3 sresa1b";climfield="tmax";LSMASK=IPCCData/20c3m/sftlf_A1_cnrm_cm3.nc;;
tmax_A2_cnrm_cm3_sresa1b_21) file="IPCCData/sresa1b_daily/tasmax_A2_cnrm_cm3_2081_2100.nc";kindname="cnrm cm3 sresa1b";climfield="tmax";LSMASK=IPCCData/20c3m/sftlf_A1_cnrm_cm3.nc;;
tmax_A2_csiro_mk3_0_20c3m) file="IPCCData/20c3m_daily/tasmax_A2_csiro_mk3_0_%%.nc";kindname="csiro_mk3_0 20c3m";climfield="tmax";LSMASK=IPCCData/20c3m/sftlf_A1_csiro_mk3_0.nc;NPERYEAR=365;;
tmax_A2_csiro_mk3_0_sresa1b_20) file="IPCCData/sresa1b_daily/tasmax_A2_csiro_mk3_0_2046_2065.nc";kindname="csiro mk3.0 sresa1b";climfield="tmax";LSMASK=IPCCData/20c3m/sftlf_A1_csiro_mk3_0.nc;;
tmax_A2_csiro_mk3_0_sresa1b_21) file="IPCCData/sresa1b_daily/tasmax_A2_csiro_mk3_0_2081_2100.nc";kindname="csiro mk3.0 sresa1b";climfield="tmax";LSMASK=IPCCData/20c3m/sftlf_A1_csiro_mk3_0.nc;;
tmax_A2_gfdl_cm2_0_20c3m) file="IPCCData/20c3m_daily/tasmax_A2_gfdl_cm2_0.nc";kindname="gfdl 2.0 20c3m";climfield="tmax";LSMASK="IPCCData/20c3m/sftlf_A1_gfdl_cm2_0.nc";NPERYEAR=365;;
tmax_A2_gfdl_cm2_0_sresa1b_20) file="IPCCData/sresa1b_daily/tasmax_A2_gfdl_cm2_0_2046-2065.nc";kindname="gfdl 2.0 sresa1b";climfield="tmax";LSMASK="IPCCData/20c3m/sftlf_A1_gfdl_cm2_0.nc";NPERYEAR=365;;
tmax_A2_gfdl_cm2_0_sresa1b_21) file="IPCCData/sresa1b_daily/tasmax_A2_gfdl_cm2_0_2081-2100.nc";kindname="gfdl 2.0 sresa1b";climfield="tmax";LSMASK="IPCCData/20c3m/sftlf_A1_gfdl_cm2_0.nc";NPERYEAR=365;;
tmax_A2_gfdl_cm2_1_20c3m) file="IPCCData/20c3m_daily/tasmax_A2_gfdl_cm2_1.nc";kindname="gfdl 2.1 20c3m";climfield="tmax";LSMASK="IPCCData/20c3m/sftlf_A1_gfdl_cm2_1.nc";NPERYEAR=365;;
tmax_A2_gfdl_cm2_1_sresa1b_20) file="IPCCData/sresa1b_daily/tasmax_A2_gfdl_cm2_1_2046-2065.nc";kindname="gfdl 2.1 sresa1b";climfield="tmax";LSMASK="IPCCData/20c3m/sftlf_A1_gfdl_cm2_1.nc";NPERYEAR=365;;
tmax_A2_gfdl_cm2_1_sresa1b_21) file="IPCCData/sresa1b_daily/tasmax_A2_gfdl_cm2_1_2081-2100.nc";kindname="gfdl 2.1 sresa1b";climfield="tmax";LSMASK="IPCCData/20c3m/sftlf_A1_gfdl_cm2_1.nc";NPERYEAR=365;;
tmax_A2_ipsl_cm4_20c3m) file="IPCCData/20c3m_daily/tasmax_A2_ipsl_%%.nc";kindname="ipsl cm4 20c3m";climfield="tmax";LSMASK=IPCCData/20c3m/sftlf_A1_ipsl_cm4.nc;NPERYEAR=360;;
tmax_A2_ipsl_cm4_sresa1b_20) file="IPCCData/sresa1b_daily/tasmax_A2_ipsl_cm4_2046-2065.nc";kindname="ipsl cm4 sresa1b";climfield="tmax";LSMASK=IPCCData/20c3m/sftlf_A1_ipsl_cm4.nc;NPERYEAR=360;;
tmax_A2_ipsl_cm4_sresa1b_21) file="IPCCData/sresa1b_daily/tasmax_A2_ipsl_cm4_2081-2100.nc";kindname="ipsl cm4 sresa1b";climfield="tmax";LSMASK=IPCCData/20c3m/sftlf_A1_ipsl_cm4.nc;NPERYEAR=360;;
tmax_A2_miroc3_2_medres_20c3m) file="IPCCData/20c3m_daily/tasmax_A2_miroc3_2_medres_%%.nc";kindname="miroc 3.2 med 20c3m";climfield="tmax";LSMASK="IPCCData/20c3m/sftlf_A1_miroc3_2_medres.nc";NPERYEAR=366;;
tmax_A2_miroc3_2_medres_sresa1b_20) file="IPCCData/sresa1b_daily/tasmax_A2_miroc3_2_medres_%%_2046_2065.nc";kindname="miroc 3.2 med sresa1b";climfield="tmax";LSMASK="IPCCData/20c3m/sftlf_A1_miroc3_2_medres.nc";NPERYEAR=366;;
tmax_A2_miroc3_2_medres_sresa1b_21) file="IPCCData/sresa1b_daily/tasmax_A2_miroc3_2_medres_%%_2081_2100.nc";kindname="miroc 3.2 med sresa1b";climfield="tmax";LSMASK="IPCCData/20c3m/sftlf_A1_miroc3_2_medres.nc";NPERYEAR=366;;
tmax_A2_miub_echo_g_20c3m) file="IPCCData/20c3m_daily/tasmax_A2_miub_echo_g_%%.nc";kindname="miub echo g 20c3m";climfield="tmax";LSMASK="IPCCData/20c3m/sftlf_A1_miub_echo_g.nc";NPERYEAR=360;;
tmax_A2_miub_echo_g_sresa1b_20) file="IPCCData/sresa1b_daily/tasmax_A2_miub_echo_g_%%_2046_2065.nc";kindname="miub echo g sresa1b";climfield="tmax";LSMASK="IPCCData/20c3m/sftlf_A1_miub_echo_g.nc";NPERYEAR=360;;
tmax_A2_miub_echo_g_sresa1b_21) file="IPCCData/sresa1b_daily/tasmax_A2_miub_echo_g_%%_2081_2100.nc";kindname="miub echo g sresa1b";climfield="tmax";LSMASK="IPCCData/20c3m/sftlf_A1_miub_echo_g.nc";NPERYEAR=360;;
tmax_A2_mpi_echam5_20c3m) file="IPCCData/20c3m_daily/tasmax_A2_mpi_echam5_00.nc";kindname="mpi echam5 20c3m";climfield="tmax";LSMASK="IPCCData/20c3m/lsmask_mpi_echam5.nc";NPERYEAR=366;;
tmax_A2_mpi_echam5_sresa1b_20) file="IPCCData/sresa1b_daily/tasmax_A2_mpi_echam5_2046-2065.nc";kindname="mpi echam5 sresa1b";climfield="tmax";LSMASK="IPCCData/20c3m/lsmask_mpi_echam5.nc";NPERYEAR=366;;
tmax_A2_mpi_echam5_sresa1b_21) file="IPCCData/sresa1b_daily/tasmax_A2_mpi_echam5_2081-2100.nc";kindname="mpi echam5 sresa1b";climfield="tmax";LSMASK="IPCCData/20c3m/lsmask_mpi_echam5.nc";NPERYEAR=366;;
tmax_A2_mri_cgcm2_3_2a_20c3m) file="IPCCData/20c3m_daily/tasmax_A2_mri_cgcm2_3_2a_%%.nc";kindname="mri cgcm232a 20c3m";climfield="tmax";LSMASK="IPCCData/20c3m/sftlf_A1_mri_cgcm2_3_2a.nc";NPERYEAR=365;;
tmax_A2_mri_cgcm2_3_2a_sresa1b_20) file="IPCCData/sresa1b_daily/tasmax_A2_mri_cgcm2_3_2a_%%_2046-2065.nc";kindname="mri cgcm232a sresa1b";climfield="tmax";LSMASK="IPCCData/20c3m/sftlf_A1_mri_cgcm2_3_2a.nc";NPERYEAR=365;;
tmax_A2_mri_cgcm2_3_2a_sresa1b_21) file="IPCCData/sresa1b_daily/tasmax_A2_mri_cgcm2_3_2a_%%_2081-2100.nc";kindname="mri cgcm232a sresa1b";climfield="tmax";LSMASK="IPCCData/20c3m/sftlf_A1_mri_cgcm2_3_2a.nc";NPERYEAR=365;;
tmax_A2_ukmo_hadcm3_20c3m) file="IPCCData/20c3m_daily/tasmax_A2_ukmo_hadcm3.nc";kindname="hadcm3 20c3m";climfield="tmax";LSMASK="IPCCData/20c3m/sftlf_A1_ukmo_hadcm3.nc";NPERYEAR=360;;
tmax_A2_ukmo_hadgem1_20c3m) file="IPCCData/20c3m_daily/tasmax_A2_ukmo_hadgem1.nc";kindname="hadgem1 20c3m";climfield="tmax";LSMASK="IPCCData/picntrl/sftlf_A1_ukmo_hadgem1.nc";NPERYEAR=360;;


rsds_A2_cccma_cgcm3_1_20c3m) file="IPCCData/20c3m_daily/rsds_a2_cccma_cgcm3_1_%%.nc";kindname="cccma cgcm3.1  20c3m";climfield="rsds";LSMASK=IPCCData/20c3m/sftlf_a1_20c3m_cgcm3.1_t47.nc;NPERYEAR=365;;
rsds_A2_cccma_cgcm3_1_sresa1b_20) file="IPCCData/sresa1b_daily/rsds_a2_sresa1b_%%_cgcm3.1_t47_2046_2065.nc";kindname="cccma cgcm3.1 sresa1b";climfield="rsds";LSMASK=IPCCData/20c3m/sftlf_a1_20c3m_cgcm3.1_t47.nc;;
rsds_A2_cccma_cgcm3_1_sresa1b_21) file="IPCCData/sresa1b_daily/rsds_a2_sresa1b_%%_cgcm3.1_t47_2081_2100.nc";kindname="cccma cgcm3.1 sresa1b";climfield="rsds";LSMASK=IPCCData/20c3m/sftlf_a1_20c3m_cgcm3.1_t47.nc;;
rsds_A2_cnrm_cm3_20c3m) file="IPCCData/20c3m_daily/rsds_A2_cnrm_cm3.nc";kindname="cnrm cm3 20c3m";climfield="rsds";LSMASK=IPCCData/20c3m/sftlf_A1_cnrm_cm3.nc;NPERYEAR=366;;
rsds_A2_cnrm_cm3_sresa1b_20) file="IPCCData/sresa1b_daily/rsds_A2_cnrm_cm3_2046_2065.nc";kindname="cnrm cm3 sresa1b";climfield="rsds";LSMASK=IPCCData/20c3m/sftlf_A1_cnrm_cm3.nc;;
rsds_A2_cnrm_cm3_sresa1b_21) file="IPCCData/sresa1b_daily/rsds_A2_cnrm_cm3_2081_2100.nc";kindname="cnrm cm3 sresa1b";climfield="rsds";LSMASK=IPCCData/20c3m/sftlf_A1_cnrm_cm3.nc;;
rsds_A2_csiro_mk3_0_20c3m) file="IPCCData/20c3m_daily/rsds_A2_csiro_mk3_0_%%.nc";kindname="csiro mk3.0 20c3m";climfield="rsds";LSMASK=IPCCData/20c3m/sftlf_A1_csiro_mk3_0.nc;NPERYEAR=365;;
rsds_A2_csiro_mk3_0_sresa1b_20) file="IPCCData/sresa1b_daily/rsds_A2_csiro_mk3_0_2046_2065.nc";kindname="csiro mk3.0 sresa1b";climfield="rsds";LSMASK=IPCCData/20c3m/sftlf_A1_csiro_mk3_0.nc;;
rsds_A2_csiro_mk3_0_sresa1b_21) file="IPCCData/sresa1b_daily/rsds_A2_csiro_mk3_0_2081_2100.nc";kindname="csiro mk3.0 sresa1b";climfield="rsds";LSMASK=IPCCData/20c3m/sftlf_A1_csiro_mk3_0.nc;;
rsds_A2_gfdl_cm2_0_20c3m) file="IPCCData/20c3m_daily/rsds_A2_gfdl_cm2_0.nc";kindname="gfdl 2.0 20c3m";climfield="rsds";LSMASK="IPCCData/20c3m/sftlf_A1_gfdl_cm2_0.nc";NPERYEAR=365;;
rsds_A2_gfdl_cm2_0_sresa1b_20) file="IPCCData/sresa1b_daily/rsds_A2_gfdl_cm2_0_2046-2065.nc";kindname="gfdl 2.0 sresa1b";climfield="rsds";LSMASK="IPCCData/20c3m/sftlf_A1_gfdl_cm2_0.nc";NPERYEAR=365;;
rsds_A2_gfdl_cm2_0_sresa1b_21) file="IPCCData/sresa1b_daily/rsds_A2_gfdl_cm2_0_2081-2100.nc";kindname="gfdl 2.0 sresa1b";climfield="rsds";LSMASK="IPCCData/20c3m/sftlf_A1_gfdl_cm2_0.nc";NPERYEAR=365;;
rsds_A2_gfdl_cm2_1_20c3m) file="IPCCData/20c3m_daily/rsds_A2_gfdl_cm2_1.nc";kindname="gfdl 2.1 20c3m";climfield="rsds";LSMASK="IPCCData/20c3m/sftlf_A1_gfdl_cm2_1.nc";NPERYEAR=365;;
rsds_A2_gfdl_cm2_1_sresa1b_20) file="IPCCData/sresa1b_daily/rsds_A2_gfdl_cm2_1_2046-2065.nc";kindname="gfdl 2.1 sresa1b";climfield="rsds";LSMASK="IPCCData/20c3m/sftlf_A1_gfdl_cm2_1.nc";NPERYEAR=365;;
rsds_A2_gfdl_cm2_1_sresa1b_21) file="IPCCData/sresa1b_daily/rsds_A2_gfdl_cm2_1_2081-2100.nc";kindname="gfdl 2.1 sresa1b";climfield="rsds";LSMASK="IPCCData/20c3m/sftlf_A1_gfdl_cm2_1.nc";NPERYEAR=365;;
rsds_A2_miroc3_2_medres_20c3m) file="IPCCData/20c3m_daily/rsds_A2_miroc3_2_medres_%%.nc";kindname="miroc 3.2 med 20c3m";climfield="rsds";LSMASK="IPCCData/20c3m/sftlf_A1_miroc3_2_medres.nc";NPERYEAR=366;;
rsds_A2_miroc3_2_medres_sresa1b_20) file="IPCCData/sresa1b_daily/rsds_A2_miroc3_2_medres_%%_2046_2065.nc";kindname="miroc 3.2 med sresa1b";climfield="rsds";LSMASK="IPCCData/20c3m/sftlf_A1_miroc3_2_medres.nc";NPERYEAR=366;;
rsds_A2_miroc3_2_medres_sresa1b_21) file="IPCCData/sresa1b_daily/rsds_A2_miroc3_2_medres_%%_2081_2100.nc";kindname="miroc 3.2 med sresa1b";climfield="rsds";LSMASK="IPCCData/20c3m/sftlf_A1_miroc3_2_medres.nc";NPERYEAR=366;;
rsds_A2_miub_echo_g_20c3m) file="IPCCData/20c3m_daily/rsds_A2_miub_echo_g_%%.nc";kindname="miub echo g 20c3m";climfield="rsds";LSMASK="IPCCData/20c3m/sftlf_A1_miub_echo_g.nc";NPERYEAR=360;;
rsds_A2_miub_echo_g_sresa1b_20) file="IPCCData/sresa1b_daily/rsds_A2_miub_echo_g_%%_2046_2065.nc";kindname="miub echo g sresa1b";climfield="rsds";LSMASK="IPCCData/20c3m/sftlf_A1_miub_echo_g.nc";NPERYEAR=360;;
rsds_A2_miub_echo_g_sresa1b_21) file="IPCCData/sresa1b_daily/rsds_A2_miub_echo_g_%%_2081_2100.nc";kindname="miub echo g sresa1b";climfield="rsds";LSMASK="IPCCData/20c3m/sftlf_A1_miub_echo_g.nc";NPERYEAR=360;;
rsds_A2_mpi_echam5_20c3m) file="IPCCData/20c3m_daily/rsds_A2_mpi_echam5_00.nc";kindname="mpi echam5 20c3m";climfield="rsds";LSMASK="IPCCData/20c3m/lsmask_mpi_echam5.nc";NPERYEAR=366;;
rsds_A2_mpi_echam5_sresa1b_20) file="IPCCData/sresa1b_daily/rsds_A2_mpi_echam5_2046-2065.nc";kindname="mpi echam5 sresa1b";climfield="rsds";LSMASK="IPCCData/20c3m/lsmask_mpi_echam5.nc";NPERYEAR=366;;
rsds_A2_mpi_echam5_sresa1b_21) file="IPCCData/sresa1b_daily/rsds_A2_mpi_echam5_2081-2100.nc";kindname="mpi echam5 sresa1b";climfield="rsds";LSMASK="IPCCData/20c3m/lsmask_mpi_echam5.nc";NPERYEAR=366;;
rsds_A2_mri_cgcm2_3_2a_20c3m) file="IPCCData/20c3m_daily/rsds_A2_mri_cgcm2_3_2a_%%.nc";kindname="mri cgcm232a 20c3m";climfield="rsds";LSMASK="IPCCData/20c3m/sftlf_A1_mri_cgcm2_3_2a.nc";NPERYEAR=365;;
rsds_A2_mri_cgcm2_3_2a_sresa1b_20) file="IPCCData/sresa1b_daily/rsds_A2_mri_cgcm2_3_2a_%%_2046-2065.nc";kindname="mri cgcm232a sresa1b";climfield="rsds";LSMASK="IPCCData/20c3m/sftlf_A1_mri_cgcm2_3_2a.nc";NPERYEAR=365;;
rsds_A2_mri_cgcm2_3_2a_sresa1b_21) file="IPCCData/sresa1b_daily/rsds_A2_mri_cgcm2_3_2a_%%_2081-2100.nc";kindname="mri cgcm232a sresa1b";climfield="rsds";LSMASK="IPCCData/20c3m/sftlf_A1_mri_cgcm2_3_2a.nc";NPERYEAR=365;;

rlds_A2_cccma_cgcm3_1_20c3m) file="IPCCData/20c3m_daily/rlds_a2_cccma_cgcm3_1_%%.nc";kindname="cccma cgcm3.1  20c3m";climfield="rlds";LSMASK=IPCCData/20c3m/sftlf_a1_20c3m_cgcm3.1_t47.nc;NPERYEAR=365;;
rlds_A2_cccma_cgcm3_1_sresa1b_20) file="IPCCData/sresa1b_daily/rlds_a2_sresa1b_%%_cgcm3.1_t47_2046_2065.nc";kindname="cccma cgcm3.1 sresa1b";climfield="rlds";LSMASK=IPCCData/20c3m/sftlf_a1_20c3m_cgcm3.1_t47.nc;;
rlds_A2_cccma_cgcm3_1_sresa1b_21) file="IPCCData/sresa1b_daily/rlds_a2_sresa1b_%%_cgcm3.1_t47_2081_2100.nc";kindname="cccma cgcm3.1 sresa1b";climfield="rlds";LSMASK=IPCCData/20c3m/sftlf_a1_20c3m_cgcm3.1_t47.nc;;
rlds_A2_cnrm_cm3_20c3m) file="IPCCData/20c3m_daily/rlds_A2_cnrm_cm3.nc";kindname="cnrm cm3 20c3m";climfield="rlds";LSMASK=IPCCData/20c3m/sftlf_A1_cnrm_cm3.nc;NPERYEAR=366;;
rlds_A2_cnrm_cm3_sresa1b_20) file="IPCCData/sresa1b_daily/rlds_A2_cnrm_cm3_2046_2065.nc";kindname="cnrm cm3 sresa1b";climfield="rlds";LSMASK=IPCCData/20c3m/sftlf_A1_cnrm_cm3.nc;;
rlds_A2_cnrm_cm3_sresa1b_21) file="IPCCData/sresa1b_daily/rlds_A2_cnrm_cm3_2081_2100.nc";kindname="cnrm cm3 sresa1b";climfield="rlds";LSMASK=IPCCData/20c3m/sftlf_A1_cnrm_cm3.nc;;
rlds_A2_csiro_mk3_0_20c3m) file="IPCCData/20c3m_daily/rlds_A2_csiro_mk3_0_%%.nc";kindname="csiro mk3.0 20c3m";climfield="rlds";LSMASK=IPCCData/20c3m/sftlf_A1_csiro_mk3_0.nc;NPERYEAR=365;;
rlds_A2_csiro_mk3_0_sresa1b_20) file="IPCCData/sresa1b_daily/rlds_A2_csiro_mk3_0_2046_2065.nc";kindname="csiro mk3.0 sresa1b";climfield="rlds";LSMASK=IPCCData/20c3m/sftlf_A1_csiro_mk3_0.nc;;
rlds_A2_csiro_mk3_0_sresa1b_21) file="IPCCData/sresa1b_daily/rlds_A2_csiro_mk3_0_2081_2100.nc";kindname="csiro mk3.0 sresa1b";climfield="rlds";LSMASK=IPCCData/20c3m/sftlf_A1_csiro_mk3_0.nc;;
rlds_A2_gfdl_cm2_0_20c3m) file="IPCCData/20c3m_daily/rlds_A2_gfdl_cm2_0.nc";kindname="gfdl 2.0 20c3m";climfield="rlds";LSMASK="IPCCData/20c3m/sftlf_A1_gfdl_cm2_0.nc";NPERYEAR=365;;
rlds_A2_gfdl_cm2_0_sresa1b_20) file="IPCCData/sresa1b_daily/rlds_A2_gfdl_cm2_0_2046-2065.nc";kindname="gfdl 2.0 sresa1b";climfield="rlds";LSMASK="IPCCData/20c3m/sftlf_A1_gfdl_cm2_0.nc";NPERYEAR=365;;
rlds_A2_gfdl_cm2_0_sresa1b_21) file="IPCCData/sresa1b_daily/rlds_A2_gfdl_cm2_0_2081-2100.nc";kindname="gfdl 2.0 sresa1b";climfield="rlds";LSMASK="IPCCData/20c3m/sftlf_A1_gfdl_cm2_0.nc";NPERYEAR=365;;
rlds_A2_gfdl_cm2_1_20c3m) file="IPCCData/20c3m_daily/rlds_A2_gfdl_cm2_1.nc";kindname="gfdl 2.1 20c3m";climfield="rlds";LSMASK="IPCCData/20c3m/sftlf_A1_gfdl_cm2_1.nc";NPERYEAR=365;;
rlds_A2_gfdl_cm2_1_sresa1b_20) file="IPCCData/sresa1b_daily/rlds_A2_gfdl_cm2_1_2046-2065.nc";kindname="gfdl 2.1 sresa1b";climfield="rlds";LSMASK="IPCCData/20c3m/sftlf_A1_gfdl_cm2_1.nc";NPERYEAR=365;;
rlds_A2_gfdl_cm2_1_sresa1b_21) file="IPCCData/sresa1b_daily/rlds_A2_gfdl_cm2_1_2081-2100.nc";kindname="gfdl 2.1 sresa1b";climfield="rlds";LSMASK="IPCCData/20c3m/sftlf_A1_gfdl_cm2_1.nc";NPERYEAR=365;;
rlds_A2_miroc3_2_medres_20c3m) file="IPCCData/20c3m_daily/rlds_A2_miroc3_2_medres_%%.nc";kindname="miroc 3.2 med 20c3m";climfield="rlds";LSMASK="IPCCData/20c3m/sftlf_A1_miroc3_2_medres.nc";NPERYEAR=366;;
rlds_A2_miroc3_2_medres_sresa1b_20) file="IPCCData/sresa1b_daily/rlds_A2_miroc3_2_medres_%%_2046_2065.nc";kindname="miroc 3.2 med sresa1b";climfield="rlds";LSMASK="IPCCData/20c3m/sftlf_A1_miroc3_2_medres.nc";NPERYEAR=366;;
rlds_A2_miroc3_2_medres_sresa1b_21) file="IPCCData/sresa1b_daily/rlds_A2_miroc3_2_medres_%%_2081_2100.nc";kindname="miroc 3.2 med sresa1b";climfield="rlds";LSMASK="IPCCData/20c3m/sftlf_A1_miroc3_2_medres.nc";NPERYEAR=366;;
rlds_A2_miub_echo_g_20c3m) file="IPCCData/20c3m_daily/rlds_A2_miub_echo_g_%%.nc";kindname="miub echo g 20c3m";climfield="rlds";LSMASK="IPCCData/20c3m/sftlf_A1_miub_echo_g.nc";NPERYEAR=360;;
rlds_A2_miub_echo_g_sresa1b_20) file="IPCCData/sresa1b_daily/rlds_A2_miub_echo_g_%%_2046_2065.nc";kindname="miub echo g sresa1b";climfield="rlds";LSMASK="IPCCData/20c3m/sftlf_A1_miub_echo_g.nc";NPERYEAR=360;;
rlds_A2_miub_echo_g_sresa1b_21) file="IPCCData/sresa1b_daily/rlds_A2_miub_echo_g_%%_2081_2100.nc";kindname="miub echo g sresa1b";climfield="rlds";LSMASK="IPCCData/20c3m/sftlf_A1_miub_echo_g.nc";NPERYEAR=360;;
rlds_A2_mpi_echam5_20c3m) file="IPCCData/20c3m_daily/rlds_A2_mpi_echam5_00.nc";kindname="mpi echam5 20c3m";climfield="rlds";LSMASK="IPCCData/20c3m/lsmask_mpi_echam5.nc";NPERYEAR=366;;
rlds_A2_mpi_echam5_sresa1b_20) file="IPCCData/sresa1b_daily/rlds_A2_mpi_echam5_2046-2065.nc";kindname="mpi echam5 sresa1b";climfield="rlds";LSMASK="IPCCData/20c3m/lsmask_mpi_echam5.nc";NPERYEAR=366;;
rlds_A2_mpi_echam5_sresa1b_21) file="IPCCData/sresa1b_daily/rlds_A2_mpi_echam5_2081-2100.nc";kindname="mpi echam5 sresa1b";climfield="rlds";LSMASK="IPCCData/20c3m/lsmask_mpi_echam5.nc";NPERYEAR=366;;
rlds_A2_mri_cgcm2_3_2a_20c3m) file="IPCCData/20c3m_daily/rlds_A2_mri_cgcm2_3_2a_%%.nc";kindname="mri cgcm232a 20c3m";climfield="rlds";LSMASK="IPCCData/20c3m/sftlf_A1_mri_cgcm2_3_2a.nc";NPERYEAR=365;;
rlds_A2_mri_cgcm2_3_2a_sresa1b_20) file="IPCCData/sresa1b_daily/rlds_A2_mri_cgcm2_3_2a_%%_2046-2065.nc";kindname="mri cgcm232a sresa1b";climfield="rlds";LSMASK="IPCCData/20c3m/sftlf_A1_mri_cgcm2_3_2a.nc";NPERYEAR=365;;
rlds_A2_mri_cgcm2_3_2a_sresa1b_21) file="IPCCData/sresa1b_daily/rlds_A2_mri_cgcm2_3_2a_%%_2081-2100.nc";kindname="mri cgcm232a sresa1b";climfield="rlds";LSMASK="IPCCData/20c3m/sftlf_A1_mri_cgcm2_3_2a.nc";NPERYEAR=365;;


ts_cnrm_cm3_20c3m) file="IPCCData/20c3m/ts_A1_cnrm_cm3.nc";kindname="cnrm cm3 20c3m";climfield="ts";LSMASK=IPCCData/20c3m/sftlf_A1_cnrm_cm3.nc;;
ts_cnrm_cm3_sresa2) file="IPCCData/sresa2/ts_A1_cnrm_cm3.nc";kindname="cnrm cm3 sresa2";climfield="ts";LSMASK=IPCCData/20c3m/sftlf_A1_cnrm_cm3.nc;;
ts_gfdl_cm2_0_20c3m) file="IPCCData/20c3m/ts_A1_gfdl_cm2_0_%%.186101-200012.nc";kindname="gfdl 2.0 20c3m";climfield="ts";LSMASK="IPCCData/20c3m/sftlf_A1_gfdl_cm2_0.nc";;
ts_gfdl_cm2_0_sresa2) file="IPCCData/sresa2/ts_A1_gfdl_cm2_0.200101-210012.nc";kindname="gfdl 2.0 sresa2";climfield="ts";LSMASK="IPCCData/20c3m/sftlf_A1_gfdl_cm2_0.nc";;
ts_gfdl_cm2_1_20c3m) file="IPCCData/20c3m/ts_A1_gfdl_cm2_1_%%.186101-200012.nc";kindname="gfdl 2.1 20c3m";climfield="ts";LSMASK="IPCCData/20c3m/sftlf_A1_gfdl_cm2_1.nc";;
ts_gfdl_cm2_1_sresa2) file="IPCCData/sresa2/ts_A1_gfdl_cm2_1_%%.186101-200012.nc";kindname="gfdl 2.1 sresa2";climfield="ts";LSMASK="IPCCData/20c3m/sftlf_A1_gfdl_cm2_1.nc";;
ts_giss_aom_20c3m) file="IPCCData/20c3m/ts_A1_giss_aom_%%.nc";kindname="giss aom 20c3m";climfield="ts";LSMASK=IPCCData/20c3m/lsmask_giss_aom.nc;;
ts_giss_model_e_h_20c3m) file="IPCCData/20c3m/ts_A1.GISS3.20C3M.%%.nc";kindname="giss eh 20c3m";climfield="ts";LSMASK=IPCCData/20c3m/lsmask_giss_model_e_h.nc;;
ts_giss_model_e_r_20c3m) file="IPCCData/20c3m/ts_A1.GISS1.20C3M.%%.nc";kindname="giss er 20c3m";climfield="ts";LSMASK=IPCCData/20c3m/lsmask_giss_model_e_r.nc;;
ts_giss_model_e_r_sresa2) file="IPCCData/sresa2/ts_A1.GISS1.SRESA2.nc";kindname="giss er sresa2";climfield="ts";LSMASK=IPCCData/20c3m/lsmask_giss_model_e_r.nc;;
ts_iap_fgoals1_0_g_20c3m) file="IPCCData/20c3m/ts_A1_iap_fgoals1_0_g_%%.nc";kindname="iap fgoals10g 20c3m";climfield="ts";;
ts_inmcm3_0_20c3m) file="IPCCData/20c3m/ts_A1_inmcm3_0.nc";kindname="inmcm3.0 20c3m";climfield="ts";LSMASK=IPCCData/20c3m/sftlf_A1_inmcm3_0.nc;;
ts_inmcm3_0_sresa2) file="IPCCData/sresa2/ts_A1_inmcm3_0.nc";kindname="inmcm3.0 sresa2";climfield="ts";LSMASK=IPCCData/20c3m/sftlf_A1_inmcm3_0.nc;;
ts_miroc3_2_hires_20c3m) file="IPCCData/20c3m/ts_A1_miroc3_2_hires.nc";kindname="miroc 3.2 hi 20c3m";climfield="ts";LSMASK="IPCCData/20c3m/sftlf_A1_miroc3_2_hires.nc";;
ts_miroc3_2_hires_1pctto2x) file="IPCCData/1pctto2x/ts_A1_miroc3_2_hires.nc";kindname="miroc 3.2 hi 1pctto2x";climfield="ts";LSMASK="IPCCData/20c3m/sftlf_A1_miroc3_2_hires.nc";;
ts_miroc3_2_medres_20c3m) file="IPCCData/20c3m/ts_A1_miroc3_2_medres_%%.nc";kindname="miroc 3.2 med 20c3m";climfield="ts";LSMASK="IPCCData/20c3m/sftlf_A1_miroc3_2_medres.nc";;
ts_miroc3_2_medres_sresa2) file="IPCCData/sresa2/ts_A1_miroc3_2_medres_%%.nc";kindname="miroc 3.2 med sresa2";climfield="ts";LSMASK="IPCCData/20c3m/sftlf_A1_miroc3_2_medres.nc";;
ts_mpi_echam5_20c3m) file="IPCCData/20c3m/ts_A1_mpi_echam5_%%.nc";kindname="mpi echam5 20c3m";climfield="ts";LSMASK="IPCCData/20c3m/lsmask_mpi_echam5.nc";;
ts_mpi_echam5_sresa2) file="IPCCData/sresa2/ts_A1_mpi_echam5_%%.nc";kindname="mpi echam5 sresa2";climfield="ts";LSMASK="IPCCData/20c3m/lsmask_mpi_echam5.nc";;
ts_mri_cgcm2_3_2a_20c3m) file="IPCCData/20c3m/ts_A1_mri_cgcm2_3_2a_%%.nc";kindname="mri cgcm232a 20c3m";climfield="ts";LSMASK="IPCCData/20c3m/sftlf_A1_mri_cgcm2_3_2a.nc";;
ts_mri_cgcm2_3_2a_sresa2) file="IPCCData/sresa2/ts_A1_mri_cgcm2_3_2a_%%.nc";kindname="mri cgcm232a sresa2";climfield="ts";LSMASK="IPCCData/20c3m/sftlf_A1_mri_cgcm2_3_2a.nc";;
ts_ncar_ccsm3_0_20c3m) file="IPCCData/20c3m/ts_A1.20C3M_%%.CCSM.atmm.1870-01_cat_1999-12.nc";kindname="ccsm 3.0 20c3m";climfield="ts";LSMASK="IPCCData/20c3m/sftlf_A1.20C3M.CCSM.atmm.nc";;
ts_ncar_pcm1_20c3m) file="IPCCData/20c3m/ts_A1.20C3M_%%.PCM1.atmm.1890-01_cat_1999-12.nc";kindname="pcm1 20c3m";climfield="ts";LSMASK="IPCCData/20c3m/sftlf_A1.20C3M.PCM1.atmm.nc";;
ts_ncar_pcm1_sresa2) file="IPCCData/sresa2/ts_A1.SRESA2_1.PCM1.atmm.2000-01_cat_2099-12.nc";kindname="pcm1 sresa2";climfield="ts";LSMASK="IPCCData/20c3m/sftlf_A1.20C3M.PCM1.atmm.nc";;
ts_ukmo_hadcm3_20c3m) file="IPCCData/20c3m/ts_A1_ukmo_hadcm3_%%.nc";kindname="hadcm3 20c3m";climfield="ts";LSMASK="IPCCData/20c3m/sftlf_A1_ukmo_hadcm3.nc";;
ts_ukmo_hadcm3_sresa2) file="IPCCData/sresa2/ts_A1_ukmo_hadcm3.nc";kindname="hadcm3";climfield="ts";LSMASK="IPCCData/20c3m/sftlf_A1_ukmo_hadcm3.nc";;

pr_cmip3_all_sresa1b) file="IPCCData/sresa1b/pr_cmip3_%%_144.nc";kindname="CMIP3 20c3m/sresa1b all members";climfield="pr";LSMASK=IPCCData/sresa1b/lsmask_cmip3_144.nc;;
pr_cmip3_ave_sresa1b) file="IPCCData/sresa1b/pr_cmip3_ave_%%_144.nc";kindname="CMIP3 20c3m/sresa1b all models";climfield="pr";LSMASK=IPCCData/sresa1b/lsmask_cmip3_144.nc;;
pr_cmip3_ave_mean_sresa1b) file="IPCCData/sresa1b/pr_cmip3_ave_mean_144.nc";kindname="CMIP3 20c3m/sresa1b multi-model mean";climfield="pr";LSMASK=IPCCData/sresa1b/lsmask_cmip3_144.nc;;
pr_cmip3_volcano_all_sresa1b) file="IPCCData/sresa1b/pr_cmip3_volcano_%%_144.nc";kindname="CMIP3 20c3m/sresa1b volcano members";climfield="pr";LSMASK=IPCCData/sresa1b/lsmask_cmip3_144.nc;;
pr_cmip3_volcano_ave_sresa1b) file="IPCCData/sresa1b/pr_cmip3_volcano_ave_%%_144.nc";kindname="CMIP3 20c3m/sresa1b volcano models";climfield="pr";LSMASK=IPCCData/sresa1b/lsmask_cmip3_144.nc;;
pr_cmip3_volcano_ave_mean_sresa1b) file="IPCCData/sresa1b/pr_cmip3_volcano_ave_mean_144.nc";kindname="CMIP3 20c3m/sresa1b volcano mean";climfield="pr";LSMASK=IPCCData/sresa1b/lsmask_cmip3_144.nc;;
pr_cmip3_novolcano_all_sresa1b) file="IPCCData/sresa1b/pr_cmip3_novolcano_%%_144.nc";kindname="CMIP3 20c3m/sresa1b novolcano members";climfield="pr";LSMASK=IPCCData/sresa1b/lsmask_cmip3_144.nc;;
pr_cmip3_novolcano_ave_sresa1b) file="IPCCData/sresa1b/pr_cmip3_novolcano_ave_%%_144.nc";kindname="CMIP3 20c3m/sresa1b novolcano models";climfield="pr";LSMASK=IPCCData/sresa1b/lsmask_cmip3_144.nc;;
pr_cmip3_novolcano_ave_mean_sresa1b) file="IPCCData/sresa1b/pr_cmip3_novolcano_ave_mean_144.nc";kindname="CMIP3 20c3m/sresa1b novolcano mean";climfield="pr";LSMASK=IPCCData/sresa1b/lsmask_cmip3_144.nc;;
pr_bccr_bcm2_0_20c3m) file="IPCCData/20c3m/pr_A1_bccr_bcm2_0.nc";kindname="bccr bcm2.0 20c3m";climfield="pr";LSMASK=IPCCData/20c3m/sftlf_A1_bccr_bcm2_0.ctl;;
pr_A2_bccr_bcm2_0_20c3m) file="IPCCData/20c3m_daily/pr_A2_bccr_bcm2_0_1961_2000.nc";kindname="bccr bcm2.0 20c3m";climfield="pr";LSMASK=IPCCData/20c3m/sftlf_A1_bccr_bcm2_0.ctl;NPERYEAR=366;;
pr_bccr_bcm2_0_sresa1b) file="IPCCData/sresa1b/pr_A1_bccr_bcm2_0.nc";kindname="bccr bcm2.0 sresa1b";climfield="pr";LSMASK=IPCCData/20c3m/sftlf_A1_bccr_bcm2_0.ctl;;
pr_A2_bccr_bcm2_0_sresa2_20) file="IPCCData/sresa2_daily/pr_A2_bccr_bcm2_0_2046_2065.nc";kindname="bccr bcm2.0 sresa2";climfield="pr";LSMASK=IPCCData/20c3m/sftlf_A1_bccr_bcm2_0.ctl;NPERYEAR=366;;
pr_A2_bccr_bcm2_0_sresa2_21) file="IPCCData/sresa2_daily/pr_A2_bccr_bcm2_0_2081_2100.nc";kindname="bccr bcm2.0 sresa2";climfield="pr";LSMASK=IPCCData/20c3m/sftlf_A1_bccr_bcm2_0.ctl;NPERYEAR=366;;
pr_cccma_cgcm3_1_20c3m) file="IPCCData/20c3m/pr_a1_20c3m_%%_cgcm3.1_t47_1850_2000.nc";kindname="cccma cgcm3.1 20c3m";climfield="pr";LSMASK=IPCCData/20c3m/sftlf_a1_20c3m_cgcm3.1_t47.nc;;
pr_cccma_cgcm3_1_sresa1b) file="IPCCData/sresa1b/pr_a1_sresa1b_%%_cgcm3.1_t47.nc";kindname="cccma cgcm3.1 sresa1b";climfield="pr";LSMASK=IPCCData/20c3m/sftlf_a1_20c3m_cgcm3.1_t47.nc;;
pr_A2_cccma_cgcm3_1_sresa1b_20) file="IPCCData/sresa1b_daily/pr_a2_sresa1b_%%_cgcm3.1_t47_2046_2065.nc";kindname="cccma cgcm3.1 sresa1b";climfield="pr";LSMASK=IPCCData/20c3m/sftlf_a1_20c3m_cgcm3.1_t47.nc;NPERYEAR=365;;
pr_A2_cccma_cgcm3_1_sresa1b_21) file="IPCCData/sresa1b_daily/pr_a2_sresa1b_%%_cgcm3.1_t47_2081_2100.nc";kindname="cccma cgcm3.1 sresa1b";climfield="pr";LSMASK=IPCCData/20c3m/sftlf_a1_20c3m_cgcm3.1_t47.nc;NPERYEAR=365;;
pr_cccma_cgcm3_1_sresa2) file="IPCCData/sresa2/pr_a1_sresa2_1_cgcm3.1_t47_2001_2100.nc";kindname="cccma cgcm3.1 sresa2";climfield="pr";LSMASK=IPCCData/20c3m/sftlf_a1_20c3m_cgcm3.1_t47.nc;;
pr_A2_cccma_cgcm3_1_sresa2_20) file="IPCCData/sresa2_daily/pr_a2_sresa2_%%_cgcm3.1_t47_2046_2065.nc";kindname="cccma cgcm3.1 sresa2";climfield="pr";LSMASK=IPCCData/20c3m/sftlf_a1_20c3m_cgcm3.1_t47.nc;NPERYEAR=365;;
pr_A2_cccma_cgcm3_1_sresa2_21) file="IPCCData/sresa2_daily/pr_a2_sresa2_%%_cgcm3.1_t47_2081_2100.nc";kindname="cccma cgcm3.1 sresa2";climfield="pr";LSMASK=IPCCData/20c3m/sftlf_a1_20c3m_cgcm3.1_t47.nc;NPERYEAR=365;;
pr_cccma_cgcm3_1_sresb1) file="IPCCData/sresb1/pr_a1_sresb1_%%_cgcm3.1_t47.nc";kindname="cccma cgcm3.1 sresb1";climfield="pr";LSMASK=IPCCData/20c3m/sftlf_a1_20c3m_cgcm3.1_t47.nc;;
pr_cccma_cgcm3_1_1pctto2x) file="IPCCData/1pctto2x/pr_a1_1pctto2x_1_cgcm3.1_t47_1850_2069.nc";kindname="cccma cgcm3.1 1pctto2x";climfield="pr";LSMASK=IPCCData/20c3m/sftlf_a1_20c3m_cgcm3.1_t47.nc;;
pr_cccma_cgcm3_1_1pctto4x) file="IPCCData/1pctto4x/pr_a1_1pctto4x_1_cgcm3.1_t47_1850_2139.nc";kindname="cccma cgcm3.1 1pctto4x";climfield="pr";LSMASK=IPCCData/20c3m/sftlf_a1_20c3m_cgcm3.1_t47.nc;;
pr_cccma_cgcm3_1_t63_20c3m) file="IPCCData/20c3m/pr_a1_20c3m_1_cgcm3.1_t63_1850_2000.nc";kindname="cccma cgcm3.1 t63 20c3m";climfield="pr";LSMASK=IPCCData/20c3m/sftlf_a1_20c3m_cgcm3.1_t63.nc;;
pr_A2_cccma_cgcm3_1_t63_20c3m) file="IPCCData/20c3m_daily/pr_a2_20c3m_1_cgcm3.1_t63_1961_2000.nc";kindname="cccma cgcm3.1 t63 20c3m";climfield="pr";LSMASK=IPCCData/20c3m/sftlf_a1_20c3m_cgcm3.1_t47.nc;NPERYEAR=365;;
pr_A2_cccma_cgcm3_1_20c3m) file="IPCCData/20c3m_daily/pr_a2_cccma_cgcm3_1_%%.nc";kindname="cccma cgcm3.1 20c3m";climfield="pr";LSMASK=IPCCData/20c3m/sftlf_a1_20c3m_cgcm3.1_t47.nc;NPERYEAR=365;;
psl_A2_cccma_cgcm3_1_t63_20c3m) file="IPCCData/20c3m_daily/psl_a2_20c3m_1_cgcm3.1_t63_1961_2000.nc";kindname="cccma cgcm3.1 t63 20c3m";climfield="psl";LSMASK=IPCCData/20c3m/sftlf_a1_20c3m_cgcm3.1_t63.nc;NPERYEAR=365;;
pr_cccma_cgcm3_1_t63_sresa1b) file="IPCCData/sresa1b/pr_a1_sresa1b_1_cgcm3.1_t63_1850_2300.nc";kindname="cccma cgcm3.1 t63 sresa1b";climfield="pr";LSMASK=IPCCData/20c3m/sftlf_a1_20c3m_cgcm3.1_t63.nc;;
pr_cccma_cgcm3_1_t63_sresb1) file="IPCCData/sresb1/pr_a1_sresb1_1_cgcm3.1_t63_2001_2260.nc";kindname="cccma cgcm3.1 t63 sresb1";climfield="pr";LSMASK=IPCCData/20c3m/sftlf_a1_20c3m_cgcm3.1_t63.nc;;
pr_A2_cccma_cgcm3_1_t63_sresa1b_21) file="IPCCData/sresa1b_daily/pr_a2_sresa1b_1_cgcm3.1_t63_2081_2100.nc";kindname="cccma cgcm3.1 t63 sresa1b";climfield="pr";LSMASK=IPCCData/20c3m/sftlf_a1_20c3m_cgcm3.1_t63.nc;NPERYEAR=365;;
pr_A2_cccma_cgcm3_1_t63_sresa1b_22) file="IPCCData/sresa1b_daily/pr_a2_sresa1b_1_cgcm3.1_t63_2181_2200.nc";kindname="cccma cgcm3.1 t63 sresa1b";climfield="pr";LSMASK=IPCCData/20c3m/sftlf_a1_20c3m_cgcm3.1_t63.nc;NPERYEAR=365;;
pr_A2_cccma_cgcm3_1_t63_sresa1b_daily) file="IPCCData/sresa1b_daily/pr_a2_sresa1b_1_cgcm3.1_t63.nc";kindname="cccma cgcm3.1 t63 sresa1b";climfield="pr";LSMASK=IPCCData/20c3m/sftlf_a1_20c3m_cgcm3.1_t63.nc;NPERYEAR=365;;
pr_cnrm_cm3_20c3m) file="IPCCData/20c3m/pr_A1_cnrm_cm3.nc";kindname="cnrm cm3 20c3m";climfield="pr";LSMASK=IPCCData/20c3m/sftlf_A1_cnrm_cm3.nc;;
pr_A2_cnrm_cm3_20c3m) file="IPCCData/20c3m_daily/pr_A2_cnrm_cm3.nc";kindname="cnrm cm3 20c3m";climfield="pr";LSMASK=IPCCData/20c3m/sftlf_A1_cnrm_cm3.nc;NPERYEAR=366;;
pr_cnrm_cm3_sresa1b) file="IPCCData/sresa1b/pr_A1_cnrm_cm3.nc";kindname="cnrm cm3 sresa1b";climfield="pr";LSMASK=IPCCData/20c3m/sftlf_A1_cnrm_cm3.nc;;
pr_A2_cnrm_cm3_sresa1b_20) file="IPCCData/sresa1b_daily/pr_A2_cnrm_cm3_2046_2065.nc";kindname="cnrm cm3 sresa1b";climfield="pr";LSMASK=IPCCData/20c3m/sftlf_A1_cnrm_cm3.nc;NPERYEAR=366;;
pr_A2_cnrm_cm3_sresa1b_21) file="IPCCData/sresa1b_daily/pr_A2_cnrm_cm3_2081_2100.nc";kindname="cnrm cm3 sresa1b";climfield="pr";LSMASK=IPCCData/20c3m/sftlf_A1_cnrm_cm3.nc;NPERYEAR=366;;
pr_cnrm_cm3_sresa2) file="IPCCData/sresa2/pr_A1_cnrm_cm3.nc";kindname="cnrm cm3 sresa2";climfield="pr";LSMASK=IPCCData/20c3m/sftlf_A1_cnrm_cm3.nc;;
pr_A2_cnrm_cm3_sresa2_20) file="IPCCData/sresa2_daily/pr_A2_cnrm_cm3_2046_2065.nc";kindname="cnrm cm3 sresa2";climfield="pr";LSMASK=IPCCData/20c3m/sftlf_A1_cnrm_cm3.nc;NPERYEAR=366;;
pr_A2_cnrm_cm3_sresa2_21) file="IPCCData/sresa2_daily/pr_A2_cnrm_cm3_2081_2100.nc";kindname="cnrm cm3 sresa2";climfield="pr";LSMASK=IPCCData/20c3m/sftlf_A1_cnrm_cm3.nc;NPERYEAR=366;;
pr_csiro_mk3_0_20c3m) file="IPCCData/20c3m/pr_A1_csiro_mk3_0_%%.nc";kindname="csiro mk3.0 20c3m";climfield="pr";LSMASK=IPCCData/20c3m/sftlf_A1_csiro_mk3_0.nc;;
pr_A2_csiro_mk3_0_20c3m) file="IPCCData/20c3m_daily/pr_A2_csiro_mk3_0_%%.nc";kindname="csiro mk3.0 20c3m";climfield="pr";LSMASK=IPCCData/20c3m/sftlf_A1_csiro_mk3_0.nc;NPERYEAR=365;;
pr_csiro_mk3_0_sresa1b) file="IPCCData/sresa1b/pr_A1_csiro_mk3_0.nc";kindname="csiro mk3.0 sresa1b";climfield="pr";LSMASK=IPCCData/20c3m/sftlf_A1_csiro_mk3_0.nc;;
pr_A2_csiro_mk3_0_sresa1b_20) file="IPCCData/sresa1b_daily/pr_A2_csiro_mk3_0_2046_2065.nc";kindname="csiro mk3.0 sresa1b";climfield="pr";LSMASK=IPCCData/20c3m/sftlf_A1_csiro_mk3_0.nc;NPERYEAR=365;;
pr_A2_csiro_mk3_0_sresa1b_21) file="IPCCData/sresa1b_daily/pr_A2_csiro_mk3_0_2081_2100.nc";kindname="csiro mk3.0 sresa1b";climfield="pr";LSMASK=IPCCData/20c3m/sftlf_A1_csiro_mk3_0.nc;NPERYEAR=365;;
pr_csiro_mk3_0_sresa2) file="IPCCData/sresa2/pr_A1_csiro_mk3_0.nc";kindname="csiro mk3.0 sresa2";climfield="pr";LSMASK=IPCCData/20c3m/sftlf_A1_csiro_mk3_0.nc;;
pr_A2_csiro_mk3_0_sresa2_20) file="IPCCData/sresa2_daily/pr_A2_csiro_mk3_0_2046_2065.nc";kindname="csiro mk3.0 sresa2";climfield="pr";LSMASK=IPCCData/20c3m/sftlf_A1_csiro_mk3_0.nc;NPERYEAR=365;;
pr_A2_csiro_mk3_0_sresa2_21) file="IPCCData/sresa2_daily/pr_A2_csiro_mk3_0_2081_2100.nc";kindname="csiro mk3.0 sresa2";climfield="pr";LSMASK=IPCCData/20c3m/sftlf_A1_csiro_mk3_0.nc;NPERYEAR=365;;
pr_csiro_mk3_5_20c3m) file="IPCCData/20c3m/pr_A1_csiro_mk3_5_%%.nc";kindname="csiro mk3.5 20c3m";climfield="pr";LSMASK=IPCCData/20c3m/sftlf_A1_csiro_mk3_5.nc;;
pr_A2_csiro_mk3_5_20c3m) file="IPCCData/20c3m_daily/pr_A2_csiro_mk3_5_%%_1961_2000.nc";kindname="csiro mk3.0 20c3m";climfield="pr";LSMASK=IPCCData/20c3m/sftlf_A1_csiro_mk3_5.nc;NPERYEAR=365;;
pr_csiro_mk3_5_sresa1b) file="IPCCData/sresa1b/pr_A1_csiro_mk3_5.nc";kindname="csiro mk3.5 sresa1b";climfield="pr";LSMASK=IPCCData/20c3m/sftlf_A1_csiro_mk3_5.nc;;
pr_A2_csiro_mk3_5_sresa2_20) file="IPCCData/sresa2_daily/pr_A2_csiro_mk3_5_2046_2065.nc";kindname="csiro mk3.0 sresa2";climfield="pr";LSMASK=IPCCData/20c3m/sftlf_A1_csiro_mk3_5.nc;NPERYEAR=365;;
pr_A2_csiro_mk3_5_sresa2_21) file="IPCCData/sresa2_daily/pr_A2_csiro_mk3_5_2081_2100.nc";kindname="csiro mk3.0 sresa2";climfield="pr";LSMASK=IPCCData/20c3m/sftlf_A1_csiro_mk3_5.nc;NPERYEAR=365;;
pr_gfdl_cm2_0_20c3m) file="IPCCData/20c3m/pr_A1_gfdl_cm2_0_%%.186101-200012.nc";kindname="gfdl 2.0 20c3m";climfield="pr";LSMASK="IPCCData/20c3m/sftlf_A1_gfdl_cm2_0.nc";;
pr_A2_gfdl_cm2_0_20c3m) file="IPCCData/20c3m_daily/pr_A2_gfdl_cm2_0.nc";kindname="gfdl 2.0 20c3m";climfield="pr";LSMASK="IPCCData/20c3m/sftlf_A1_gfdl_cm2_0.nc";NPERYEAR=365;;
pr_gfdl_cm2_0_sresa1b) file="IPCCData/sresa1b/pr_A1_gfdl_cm2_0.nc";kindname="gfdl 2.0 sresa1b";climfield="pr";LSMASK="IPCCData/20c3m/sftlf_A1_gfdl_cm2_0.nc";;
pr_A2_gfdl_cm2_0_sresa1b_20) file="IPCCData/sresa1b_daily/pr_A2_gfdl_cm2_0_2046-2065.nc";kindname="gfdl 2.0 sresa1b";climfield="pr";LSMASK="IPCCData/20c3m/sftlf_A1_gfdl_cm2_0.nc";NPERYEAR=365;;
pr_A2_gfdl_cm2_0_sresa1b_21) file="IPCCData/sresa1b_daily/pr_A2_gfdl_cm2_0_2081-2100.nc";kindname="gfdl 2.0 sresa1b";climfield="pr";LSMASK="IPCCData/20c3m/sftlf_A1_gfdl_cm2_0.nc";NPERYEAR=365;;
pr_gfdl_cm2_0_sresa2) file="IPCCData/sresa2/pr_A1_gfdl_cm2_0.200101-210012.nc";kindname="gfdl 2.0 sresa2";climfield="pr";LSMASK="IPCCData/20c3m/sftlf_A1_gfdl_cm2_0.nc";;
pr_A2_gfdl_cm2_0_sresa2_20) file="IPCCData/sresa2_daily/pr_A2_gfdl_cm2_0_2046_2065.nc";kindname="gfdl 2.0 sresa2";climfield="pr";LSMASK="IPCCData/20c3m/sftlf_A1_gfdl_cm2_0.nc";NPERYEAR=365;;
pr_A2_gfdl_cm2_0_sresa2_21) file="IPCCData/sresa2_daily/pr_A2_gfdl_cm2_0_2081_2100.nc";kindname="gfdl 2.0 sresa2";climfield="pr";LSMASK="IPCCData/20c3m/sftlf_A1_gfdl_cm2_0.nc";NPERYEAR=365;;
pr_gfdl_cm2_1_20c3m) file="IPCCData/20c3m/pr_A1_gfdl_cm2_1_%%.186101-200012.nc";kindname="gfdl 2.1 20c3m";climfield="pr";LSMASK="IPCCData/20c3m/sftlf_A1_gfdl_cm2_1.nc";;
pr_A2_gfdl_cm2_1_20c3m) file="IPCCData/20c3m_daily/pr_A2_gfdl_cm2_1.nc";kindname="gfdl 2.1 20c3m";climfield="pr";LSMASK="IPCCData/20c3m/sftlf_A1_gfdl_cm2_1.nc";NPERYEAR=365;;
psl_A2_gfdl_cm2_1_20c3m) file="IPCCData/20c3m_daily/psl_A2_gfdl_cm2_1.nc";kindname="gfdl 2.1 20c3m";climfield="psl";LSMASK="IPCCData/20c3m/sftlf_A1_gfdl_cm2_1.nc";NPERYEAR=365;;
pr_gfdl_cm2_1_sresa1b) file="IPCCData/sresa1b/pr_A1_gfdl_cm2_1.nc";kindname="gfdl 2.1 sresa1b";climfield="pr";LSMASK="IPCCData/20c3m/sftlf_A1_gfdl_cm2_1.nc";;
pr_A2_gfdl_cm2_1_sresa1b) file="IPCCData/sresa1b_daily/pr_A2.20010101-21001231.nc";kindname="gfdl 2.1 sresa1b";climfield="pr";LSMASK="IPCCData/20c3m/sftlf_A1_gfdl_cm2_1.nc";NPERYEAR=365;;
pr_A2_gfdl_cm2_1_sresa1b_20) file="IPCCData/sresa1b_daily/pr_A2_gfdl_cm2_1_2046-2065.nc";kindname="gfdl 2.1 sresa1b";climfield="pr";LSMASK="IPCCData/20c3m/sftlf_A1_gfdl_cm2_1.nc";NPERYEAR=365;;
pr_A2_gfdl_cm2_1_sresa1b_21) file="IPCCData/sresa1b_daily/pr_A2_gfdl_cm2_1_2081-2100.nc";kindname="gfdl 2.1 sresa1b";climfield="pr";LSMASK="IPCCData/20c3m/sftlf_A1_gfdl_cm2_1.nc";NPERYEAR=365;;
pr_A2_gfdl_cm2_1_sresa1b_22) file="IPCCData/sresa1b_daily/pr_A2_gfdl_cm2_1_2181-2200.nc";kindname="gfdl 2.1 sresa1b";climfield="pr";LSMASK="IPCCData/20c3m/sftlf_A1_gfdl_cm2_1.nc";NPERYEAR=365;;
pr_A2_gfdl_cm2_1_sresa1b_23) file="IPCCData/sresa1b_daily/pr_A2_gfdl_cm2_1_2281-2300.nc";kindname="gfdl 2.1 sresa1b";climfield="pr";LSMASK="IPCCData/20c3m/sftlf_A1_gfdl_cm2_1.nc";NPERYEAR=365;;
psl_A2_gfdl_cm2_1_sresa1b_21) file="IPCCData/sresa1b_daily/psl_A2_gfdl_cm2_1_2081-2100.nc";kindname="gfdl 2.1 sresa1b";climfield="psl";LSMASK="IPCCData/20c3m/sftlf_A1_gfdl_cm2_1.nc";NPERYEAR=365;;
psl_A2_gfdl_cm2_1_sresa1b_22) file="IPCCData/sresa1b_daily/psl_A2_gfdl_cm2_1_2181-2200.nc";kindname="gfdl 2.1 sresa1b";climfield="psl";LSMASK="IPCCData/20c3m/sftlf_A1_gfdl_cm2_1.nc";NPERYEAR=365;;
psl_A2_gfdl_cm2_1_sresa1b_23) file="IPCCData/sresa1b_daily/psl_A2_gfdl_cm2_1_2281-2300.nc";kindname="gfdl 2.1 sresa1b";climfield="psl";LSMASK="IPCCData/20c3m/sftlf_A1_gfdl_cm2_1.nc";NPERYEAR=365;;
pr_gfdl_cm2_1_sresa2) file="IPCCData/sresa2/pr_A1_gfdl_cm2_1.200101-210012.nc";kindname="gfdl 2.1 sresa2";climfield="pr";LSMASK="IPCCData/20c3m/sftlf_A1_gfdl_cm2_1.nc";;
pr_A2_gfdl_cm2_1_sresa2_20) file="IPCCData/sresa2_daily/pr_A2_gfdl_cm2_1_2046_2065.nc";kindname="gfdl 2.1 sresa2";climfield="pr";LSMASK="IPCCData/20c3m/sftlf_A1_gfdl_cm2_1.nc";NPERYEAR=365;;
pr_A2_gfdl_cm2_1_sresa2_21) file="IPCCData/sresa2_daily/pr_A2_gfdl_cm2_1_2081_2100.nc";kindname="gfdl 2.1 sresa2";climfield="pr";LSMASK="IPCCData/20c3m/sftlf_A1_gfdl_cm2_1.nc";NPERYEAR=365;;
pr_gfdl_cm2_1_sresb1) file="IPCCData/sresb1/pr_A1_gfdl_cm2_1.nc";kindname="gfdl 2.1 sresb1";climfield="pr";LSMASK="IPCCData/20c3m/sftlf_A1_gfdl_cm2_1.nc";;
pr_gfdl_cm2_1_1pctto4x) file="IPCCData/1pctto4x/pr_A1_gfdl_cm2_1.nc";kindname="gfdl 2.1 1pctto4x";climfield="pr";LSMASK="IPCCData/20c3m/sftlf_A1_gfdl_cm2_1.nc";;
pr_giss_aom_20c3m) file="IPCCData/20c3m/pr_A1_giss_aom_%%.nc";kindname="giss aom 20c3m";climfield="pr";LSMASK=IPCCData/20c3m/lsmask_giss_aom.nc;;
pr_giss_aom_sresa1b) file="IPCCData/sresa1b/pr_A1_giss_aom_%%.nc";kindname="giss aom sresa1b";climfield="pr";LSMASK=IPCCData/20c3m/lsmask_giss_aom.nc;;
pr_giss_model_e_h_20c3m) file="IPCCData/20c3m/pr_A1.GISS3.20C3M.%%.nc";kindname="giss eh 20c3m";climfield="pr";LSMASK=IPCCData/20c3m/lsmask_giss_model_e_h.nc;;
pr_giss_model_e_h_sresa1b) file="IPCCData/sresa1b/pr_A1.GISS3.SRESA1B.%%.nc";kindname="giss eh sresa1b";climfield="pr";LSMASK=IPCCData/20c3m/lsmask_giss_model_e_h.nc;;
pr_giss_model_e_r_20c3m) file="IPCCData/20c3m/pr_A1.GISS1.20C3M.%%.nc";kindname="giss er 20c3m";climfield="pr";LSMASK=IPCCData/20c3m/lsmask_giss_model_e_r.nc;;
pr_A2_giss_model_e_r_20c3m) file="IPCCData/20c3m_daily/pr_A2.GISS1.20C3M.run1.nc";kindname="giss er 20c3m";climfield="pr";LSMASK=IPCCData/20c3m/lsmask_giss_model_e_r.nc;NPERYEAR=365;;
pr_giss_model_e_r_sresa1b) file="IPCCData/sresa1b/pr_A1.GISS1.SRESA1B.%%.nc";kindname="giss er sresa1b";climfield="pr";LSMASK=IPCCData/20c3m/lsmask_giss_model_e_r.nc;;
pr_giss_model_e_r_sresa2) file="IPCCData/sresa2/pr_A1.GISS1.SRESA2.nc";kindname="giss er sresa2";climfield="pr";LSMASK=IPCCData/20c3m/lsmask_giss_model_e_r.nc;;
pr_A2_giss_model_e_r_sresa2_20) file="IPCCData/sresa2_daily/pr_A2.GISS1.SRESA2.2046to2065.nc";kindname="giss er sresa2";climfield="pr";LSMASK=IPCCData/20c3m/lsmask_giss_model_e_r.nc;NPERYEAR=365;;
pr_A2_giss_model_e_r_sresa2_21) file="IPCCData/sresa2_daily/pr_A2.GISS1.SRESA2.2081to2100.nc";kindname="giss er sresa2";climfield="pr";LSMASK=IPCCData/20c3m/lsmask_giss_model_e_r.nc;NPERYEAR=365;;
pr_iap_fgoals1_0_g_20c3m) file="IPCCData/20c3m/pr_A1_iap_fgoals1_0_g_%%.nc";kindname="iap fgoals10g 20c3m";climfield="pr";;
pr_ingv_echam4_20c3m) file="IPCCData/20c3m/pr_A1_ingv_echam4.nc";kindname="ingv_echam4 20c3m";climfield="pr";LSMASK=IPCCData/20c3m/sftlf_A1_ingv_echam4.nc;;
pr_A2_ingv_echam4_20c3m) file="IPCCData/20c3m_daily/pr_A2_ingv_echam4_1961_2000.nc";kindname="ingv_echam4 20c3m";climfield="pr";LSMASK=IPCCData/20c3m/sftlf_A1_ingv_echam4.nc;NPERYEAR=360;;
pr_ingv_echam4_sresa1b) file="IPCCData/sresa1b/pr_A1_ingv_echam4.nc";kindname="ingv_echam4 sresa1b";climfield="pr";LSMASK=IPCCData/20c3m/sftlf_A1_ingv_echam4.nc;;
pr_A2_ingv_echam4_sresa2_20) file="IPCCData/sresa2_daily/pr_A2_ingv_echam4_2046_2065.nc";kindname="ingv_echam4 sresa2";climfield="pr";LSMASK=IPCCData/20c3m/sftlf_A1_ingv_echam4.nc;NPERYEAR=360;;
pr_A2_ingv_echam4_sresa2_21) file="IPCCData/sresa2_daily/pr_A2_ingv_echam4_2081_2100.nc";kindname="ingv_echam4 sresa2";climfield="pr";LSMASK=IPCCData/20c3m/sftlf_A1_ingv_echam4.nc;NPERYEAR=360;;
pr_inmcm3_0_20c3m) file="IPCCData/20c3m/pr_A1_inmcm3_0.nc";kindname="inmcm3.0 20c3m";climfield="pr";LSMASK=IPCCData/20c3m/sftlf_A1_inmcm3_0.nc;;
pr_A2_inmcm3_0_20c3m) file="IPCCData/20c3m_daily/pr_A2_inmcm3_0_1961_2000.nc";kindname="inmcm3.0 20c3m";climfield="pr";LSMASK=IPCCData/20c3m/sftlf_A1_inmcm3_0.nc;NPERYEAR=365;;
pr_inmcm3_0_sresa1b) file="IPCCData/sresa1b/pr_A1_inmcm3_0.nc";kindname="inmcm3.0 sresa1b";climfield="pr";LSMASK=IPCCData/20c3m/sftlf_A1_inmcm3_0.nc;;
pr_inmcm3_0_sresa2) file="IPCCData/sresa2/pr_A1_inmcm3_0.nc";kindname="inmcm3.0 sresa2";climfield="pr";LSMASK=IPCCData/20c3m/sftlf_A1_inmcm3_0.nc;;
pr_A2_inmcm3_0_sresa2_20) file="IPCCData/sresa2_daily/pr_A2_inmcm3_0_2046_2065.nc";kindname="inmcm3.0 sresa2";climfield="pr";LSMASK=IPCCData/20c3m/sftlf_A1_inmcm3_0.nc;NPERYEAR=365;;
pr_A2_inmcm3_0_sresa2_21) file="IPCCData/sresa2_daily/pr_A2_inmcm3_0_2081_2100.nc";kindname="inmcm3.0 sresa2";climfield="pr";LSMASK=IPCCData/20c3m/sftlf_A1_inmcm3_0.nc;NPERYEAR=365;;
pr_ipsl_cm4_20c3m) file="IPCCData/20c3m/pr_A1_ipsl_cm4_1860-2000.nc";kindname="ipsl cm4 20c3m";climfield="pr";LSMASK=IPCCData/20c3m/sftlf_A1_ipsl_cm4.nc;;
pr_A2_ipsl_cm4_20c3m) file="IPCCData/20c3m_daily/pr_A2_ipsl_cm4_%%.nc";kindname="ipsl cm4 20c3m";climfield="pr";LSMASK=IPCCData/20c3m/sftlf_A1_ipsl_cm4.nc;NPERYEAR=360;;
pr_ipsl_cm4_sresa1b) file="IPCCData/sresa1b/pr_A1_ipsl_cm4.nc";kindname="ipsl cm4 sresa1b";climfield="pr";LSMASK=IPCCData/20c3m/sftlf_A1_ipsl_cm4.nc;;
pr_A2_ipsl_cm4_sresa1b_20) file="IPCCData/sresa1b_daily/pr_A2_ipsl_cm4_2046-2065.nc";kindname="ipsl cm4 sresa1b";climfield="pr";LSMASK=IPCCData/20c3m/sftlf_A1_ipsl_cm4.nc;NPERYEAR=360;;
pr_A2_ipsl_cm4_sresa1b_21) file="IPCCData/sresa1b_daily/pr_A2_ipsl_cm4_2081-2100.nc";kindname="ipsl cm4 sresa1b";climfield="pr";LSMASK=IPCCData/20c3m/sftlf_A1_ipsl_cm4.nc;NPERYEAR=360;;
pr_ipsl_cm4_sresa2) file="IPCCData/sresa2/pr_A1_ipsl_cm4_2000-2100.nc";kindname="ipsl cm4 sresa2";climfield="pr";LSMASK=IPCCData/20c3m/sftlf_A1_ipsl_cm4.nc;;
pr_A2_ipsl_cm4_sresa2_20) file="IPCCData/sresa2_daily/pr_A2_ipsl_cm4_2046_2065.nc";kindname="ipsl cm4 sresa2";climfield="pr";LSMASK=IPCCData/20c3m/sftlf_A1_ipsl_cm4.nc;NPERYEAR=360;;
pr_A2_ipsl_cm4_sresa2_21) file="IPCCData/sresa2_daily/pr_A2_ipsl_cm4_2081_2100.nc";kindname="ipsl cm4 sresa2";climfield="pr";LSMASK=IPCCData/20c3m/sftlf_A1_ipsl_cm4.nc;NPERYEAR=360;;
pr_miroc3_2_hires_20c3m) file="IPCCData/20c3m/pr_A1_miroc3_2_hires.nc";kindname="miroc 3.2 hi 20c3m";climfield="pr";LSMASK="IPCCData/20c3m/sftlf_A1_miroc3_2_hires.nc";;
pr_A2_miroc3_2_hires_20c3m) file="IPCCData/20c3m_daily/pr_A2_miroc3_2_hires.nc";kindname="miroc 3.2 hi 20c3m";climfield="pr";LSMASK="IPCCData/20c3m/sftlf_A1_miroc3_2_hires_nh.nc";NPERYEAR=366;;
psl_A2_miroc3_2_hires_20c3m_nh) file="IPCCData/20c3m_daily/psl_A2_miroc3_2_hires_1961-2000_nh.nc";kindname="miroc 3.2 hi 20c3m";climfield="psl";LSMASK="IPCCData/20c3m/sftlf_A1_miroc3_2_hires_nh.nc";NPERYEAR=366;;
pr_miroc3_2_hires_sresa1b) file="IPCCData/sresa1b/pr_A1_miroc3_2_hires.nc";kindname="miroc 3.2 hi sresa1b";climfield="pr";LSMASK="IPCCData/20c3m/sftlf_A1_miroc3_2_hires.nc";;
pr_A2_miroc3_2_hires_sresa1b) file="IPCCData/sresa1b_daily/pr_A2_miroc3_2_hires_2081-2100.nc";kindname="miroc 3.2 hi sresa1b";climfield="pr";LSMASK="IPCCData/20c3m/sftlf_A1_miroc3_2_hires.nc";NPERYEAR=366;;
psl_A2_miroc3_2_hires_sresa1b) file="IPCCData/sresa1b_daily/psl_A2_miroc3_2_hires_2081-2100.nc";kindname="miroc 3.2 hi sresa1b";climfield="psl";LSMASK="IPCCData/20c3m/sftlf_A1_miroc3_2_hires.nc";NPERYEAR=366;;
pr_miroc3_2_hires_sresb1) file="IPCCData/sresb1/pr_A1_miroc3_2_hires.nc";kindname="miroc 3.2 hi sresb1";climfield="pr";LSMASK="IPCCData/20c3m/sftlf_A1_miroc3_2_hires.nc";;
pr_miroc3_2_hires_1pctto2x) file="IPCCData/1pctto2x/pr_A1_miroc3_2_hires.nc";kindname="miroc 3.2 hi 1pctto2x";climfield="pr";LSMASK="IPCCData/20c3m/sftlf_A1_miroc3_2_hires.nc";;
pr_miroc3_2_medres_20c3m) file="IPCCData/20c3m/pr_A1_miroc3_2_medres_%%.nc";kindname="miroc 3.2 med 20c3m";climfield="pr";LSMASK="IPCCData/20c3m/sftlf_A1_miroc3_2_medres.nc";;
pr_A2_miroc3_2_medres_20c3m) file="IPCCData/20c3m_daily/pr_A2_miroc3_2_medres_%%.nc";kindname="miroc 3.2 med 20c3m";climfield="pr";LSMASK="IPCCData/20c3m/sftlf_A1_miroc3_2_medres.nc";NPERYEAR=366;;
pr_miroc3_2_medres_sresa1b) file="IPCCData/sresa1b/pr_A1_miroc3_2_medres_%%.nc";kindname="miroc 3.2 med sresa1b";climfield="pr";LSMASK="IPCCData/20c3m/sftlf_A1_miroc3_2_medres.nc";;
pr_A2_miroc3_2_medres_sresa1b_20) file="IPCCData/sresa1b_daily/pr_A2_miroc3_2_medres_%%_2046_2065.nc";kindname="miroc 3.2 med sresa1b";climfield="pr";LSMASK="IPCCData/20c3m/sftlf_A1_miroc3_2_medres.nc";NPERYEAR=366;;
pr_A2_miroc3_2_medres_sresa1b_21) file="IPCCData/sresa1b_daily/pr_A2_miroc3_2_medres_%%_2081_2100.nc";kindname="miroc 3.2 med sresa1b";climfield="pr";LSMASK="IPCCData/20c3m/sftlf_A1_miroc3_2_medres.nc";NPERYEAR=366;;
pr_miroc3_2_medres_sresa2) file="IPCCData/sresa2/pr_A1_miroc3_2_medres_%%.nc";kindname="miroc 3.2 med sresa2";climfield="pr";LSMASK="IPCCData/20c3m/sftlf_A1_miroc3_2_medres.nc";;
pr_A2_miroc3_2_medres_sresa2_20) file="IPCCData/sresa2_daily/pr_A2_miroc3_2_medres_%%_2046_2065.nc";kindname="miroc 3.2 med sresa2";climfield="pr";LSMASK="IPCCData/20c3m/sftlf_A1_miroc3_2_medres.nc";NPERYEAR=366;;
pr_A2_miroc3_2_medres_sresa2_21) file="IPCCData/sresa2_daily/pr_A2_miroc3_2_medres_%%_2081_2100.nc";kindname="miroc 3.2 med sresa2";climfield="pr";LSMASK="IPCCData/20c3m/sftlf_A1_miroc3_2_medres.nc";NPERYEAR=366;;
pr_miroc3_2_medres_sresb1) file="IPCCData/sresb1/pr_A1_miroc3_2_medres_%%.nc";kindname="miroc 3.2 med sresb1";climfield="pr";LSMASK="IPCCData/20c3m/sftlf_A1_miroc3_2_medres.nc";;
pr_miroc3_2_medres_1pctto4x) file="IPCCData/1pctto4x/pr_A1_miroc3_2_medres_%%.nc";kindname="miroc 3.2 med 1pctto4x";climfield="pr";LSMASK="IPCCData/20c3m/sftlf_A1_miroc3_2_medres.nc";;
pr_miub_echo_g_20c3m) file="IPCCData/20c3m/pr_A1_miub_echo_g_%%_0007-0147.nc";kindname="miub echo g 20c3m";climfield="pr";LSMASK="IPCCData/20c3m/sftlf_A1_miub_echo_g.nc";;
pr_A2_miub_echo_g_20c3m) file="IPCCData/20c3m_daily/pr_A2_miub_echo_g_%%.nc";kindname="miub echo g 20c3m";climfield="pr";LSMASK="IPCCData/20c3m/sftlf_A1_miub_echo_g.nc";NPERYEAR=360;;
pr_miub_echo_g_sresa1b) file="IPCCData/sresa1b/pr_A1_miub_echo_g_%%.nc";kindname="miub echo g sresa1b";climfield="pr";LSMASK="IPCCData/20c3m/sftlf_A1_miub_echo_g.nc";;
pr_A2_miub_echo_g_sresa1b_20) file="IPCCData/sresa1b_daily/pr_A2_miub_echo_g_%%_2046_2065.nc";kindname="miub echo g sresa1b";climfield="pr";LSMASK="IPCCData/20c3m/sftlf_A1_miub_echo_g.nc";NPERYEAR=360;;
pr_A2_miub_echo_g_sresa1b_21) file="IPCCData/sresa1b_daily/pr_A2_miub_echo_g_%%_2081_2100.nc";kindname="miub echo g sresa1b";climfield="pr";LSMASK="IPCCData/20c3m/sftlf_A1_miub_echo_g.nc";NPERYEAR=360;;
pr_miub_echo_g_sresa2) file="IPCCData/sresa2/pr_A1_miub_echo_g_%%_0148-0247.nc";kindname="miub echo g sresa2";climfield="pr";LSMASK="IPCCData/20c3m/sftlf_A1_miub_echo_g.nc";;
pr_A2_miub_echo_g_sresa2_20) file="IPCCData/sresa2_daily/pr_A2_miub_echo_g_%%_2046_2065.nc";kindname="miub echo g sresa2";climfield="pr";LSMASK="IPCCData/20c3m/sftlf_A1_miub_echo_g.nc";NPERYEAR=360;;
pr_A2_miub_echo_g_sresa2_21) file="IPCCData/sresa2_daily/pr_A2_miub_echo_g_%%_2081_2100.nc";kindname="miub echo g sresa2";climfield="pr";LSMASK="IPCCData/20c3m/sftlf_A1_miub_echo_g.nc";NPERYEAR=360;;
pr_miub_echo_g_sresb1) file="IPCCData/sresb1/pr_A1_miub_echo_g_%%.nc";kindname="miub echo g sresb1";climfield="pr";LSMASK="IPCCData/20c3m/sftlf_A1_miub_echo_g.nc";;
pr_mpi_echam5_20c3m) file="IPCCData/20c3m/pr_A1_mpi_echam5_%%.nc";kindname="mpi echam5 20c3m";climfield="pr";LSMASK="IPCCData/20c3m/lsmask_mpi_echam5.nc";;
pr_A2_mpi_echam5_20c3m) file="IPCCData/20c3m_daily/pr_A2_mpi_echam5_%%_1961-2000.nc";kindname="mpi echam5 20c3m";climfield="pr";LSMASK="IPCCData/20c3m/lsmask_mpi_echam5.nc";NPERYEAR=366;;
psl_A2_mpi_echam5_20c3m) file="IPCCData/20c3m_daily/psl_A2_mpi_echam5_1961-2000.nc";kindname="mpi echam5 20c3m";climfield="psl";LSMASK="IPCCData/20c3m/lsmask_mpi_echam5.nc";NPERYEAR=366;;
pr_mpi_echam5_sresa1b) file="IPCCData/sresa1b/pr_A1_mpi_echam5_%%.nc";kindname="mpi echam5 sresa1b";climfield="pr";LSMASK="IPCCData/20c3m/lsmask_mpi_echam5.nc";;
pr_A2_mpi_echam5_sresa2_20) file="IPCCData/sresa2_daily/pr_A2_mpi_echam5_2046-2065.nc";kindname="mpi echam5 sresa2";climfield="pr";LSMASK="IPCCData/20c3m/lsmask_mpi_echam5.nc";NPERYEAR=366;;
pr_A2_mpi_echam5_sresa2_21) file="IPCCData/sresa2_daily/pr_A2_mpi_echam5_2081-2100.nc";kindname="mpi echam5 sresa2";climfield="pr";LSMASK="IPCCData/20c3m/lsmask_mpi_echam5.nc";NPERYEAR=366;;
pr_mpi_echam5_picntrl) file="IPCCData/picntrl/pr_mpi_echam5.nc";kindname="mpi echam5 picntrl";climfield="pr";LSMASK="IPCCData/20c3m/lsmask_mpi_echam5.nc";;
pr_A2_mpi_echam5_sresa1b_20) file="IPCCData/sresa1b_daily/pr_A2_mpi_echam5_%%_2046_2065.nc";kindname="mpi echam5 sresa1b";climfield="pr";LSMASK="IPCCData/20c3m/lsmask_mpi_echam5.nc";NPERYEAR=366;;
pr_A2_mpi_echam5_sresa1b_21) file="IPCCData/sresa1b_daily/pr_A2_mpi_echam5_%%_2081-2100.nc";kindname="mpi echam5 sresa1b";climfield="pr";LSMASK="IPCCData/20c3m/lsmask_mpi_echam5.nc";NPERYEAR=366;;
pr_A2_mpi_echam5_sresa1b_22) file="IPCCData/sresa1b_daily/pr_A2_mpi_echam5_2181-2200.nc";kindname="mpi echam5 sresa1b";climfield="pr";LSMASK="IPCCData/20c3m/lsmask_mpi_echam5.nc";NPERYEAR=366;;
pr_A2_mpi_echam5_sresa1b_23) file="IPCCData/sresa1b_daily/pr_A2_mpi_echam5_2281-2300.nc";kindname="mpi echam5 sresa1b";climfield="pr";LSMASK="IPCCData/20c3m/lsmask_mpi_echam5.nc";NPERYEAR=366;;
psl_A2_mpi_echam5_sresa1b_21) file="IPCCData/sresa1b_daily/psl_A2_mpi_echam5_2081-2100.nc";kindname="mpi echam5 sresa1b";climfield="psl";LSMASK="IPCCData/20c3m/lsmask_mpi_echam5.nc";NPERYEAR=366;;
psl_A2_mpi_echam5_sresa1b_22) file="IPCCData/sresa1b_daily/psl_A2_mpi_echam5_2181-2200.nc";kindname="mpi echam5 sresa1b";climfield="psl";LSMASK="IPCCData/20c3m/lsmask_mpi_echam5.nc";NPERYEAR=366;;
psl_A2_mpi_echam5_sresa1b_23) file="IPCCData/sresa1b_daily/psl_A2_mpi_echam5_2281-2300.nc";kindname="mpi echam5 sresa1b";climfield="psl";LSMASK="IPCCData/20c3m/lsmask_mpi_echam5.nc";NPERYEAR=366;;
pr_mpi_echam5_sresa2) file="IPCCData/sresa2/pr_A1_mpi_echam5_%%.nc";kindname="mpi echam5 sresa2";climfield="pr";LSMASK="IPCCData/20c3m/lsmask_mpi_echam5.nc";;
pr_mpi_echam5_sresb1) file="IPCCData/sresb1/pr_A1_mpi_echam5_%%.nc";kindname="mpi echam5 sresb1";climfield="pr";LSMASK="IPCCData/20c3m/lsmask_mpi_echam5.nc";;
pr_mpi_echam5_picntrl) file="IPCCData/picntrl/pr_A1_mpi_echam5_%%.nc";kindname="mpi echam5 picntrl";climfield="pr";LSMASK="IPCCData/20c3m/lsmask_mpi_echam5.nc";;
pr_mpi_echam5_1pctto2x) file="IPCCData/1pctto2x/pr_A1_mpi_echam5_%%.nc";kindname="mpi echam5 1pctto2x";climfield="pr";LSMASK="IPCCData/20c3m/lsmask_mpi_echam5.nc";;
pr_mpi_echam5_1pctto4x) file="IPCCData/1pctto4x/pr_A1_mpi_echam5.nc";kindname="mpi echam5 1pctto4x";climfield="pr";LSMASK="IPCCData/20c3m/lsmask_mpi_echam5.nc";;
pr_mri_cgcm2_3_2a_20c3m) file="IPCCData/20c3m/pr_A1_mri_cgcm2_3_2a_%%.nc";kindname="mri cgcm232a 20c3m";climfield="pr";LSMASK="IPCCData/20c3m/sftlf_A1_mri_cgcm2_3_2a.nc";;
pr_A2_mri_cgcm2_3_2a_20c3m) file="IPCCData/20c3m_daily/pr_A2_mri_cgcm2_3_2a_%%.nc";kindname="mri cgcm232a 20c3m";climfield="pr";LSMASK="IPCCData/20c3m/sftlf_A1_mri_cgcm2_3_2a.nc";NPERYEAR=365;;
pr_mri_cgcm2_3_2a_sresa1b) file="IPCCData/sresa1b/pr_A1_mri_cgcm2_3_2a_%%.nc";kindname="mri cgcm232a sresa1b";climfield="pr";LSMASK="IPCCData/20c3m/sftlf_A1_mri_cgcm2_3_2a.nc";;
pr_A2_mri_cgcm2_3_2a_sresa1b_20) file="IPCCData/sresa1b_daily/pr_A2_mri_cgcm2_3_2a_%%_2046-2065.nc";kindname="mri cgcm232a sresa1b";climfield="pr";LSMASK="IPCCData/20c3m/sftlf_A1_mri_cgcm2_3_2a.nc";NPERYEAR=365;;
pr_A2_mri_cgcm2_3_2a_sresa1b_21) file="IPCCData/sresa1b_daily/pr_A2_mri_cgcm2_3_2a_%%_2081-2100.nc";kindname="mri cgcm232a sresa1b";climfield="pr";LSMASK="IPCCData/20c3m/sftlf_A1_mri_cgcm2_3_2a.nc";NPERYEAR=365;;
pr_mri_cgcm2_3_2a_sresa2) file="IPCCData/sresa2/pr_A1_mri_cgcm2_3_2a_%%.nc";kindname="mri cgcm232a sresa2";climfield="pr";LSMASK="IPCCData/20c3m/sftlf_A1_mri_cgcm2_3_2a.nc";;
pr_A2_mri_cgcm2_3_2a_sresa2_20) file="IPCCData/sresa2_daily/pr_A2_mri_cgcm2_3_2a_%%_2046-2065.nc";kindname="mri cgcm232a sresa2";climfield="pr";LSMASK="IPCCData/20c3m/sftlf_A1_mri_cgcm2_3_2a.nc";NPERYEAR=365;;
pr_A2_mri_cgcm2_3_2a_sresa2_21) file="IPCCData/sresa2_daily/pr_A2_mri_cgcm2_3_2a_%%_2081-2100.nc";kindname="mri cgcm232a sresa2";climfield="pr";LSMASK="IPCCData/20c3m/sftlf_A1_mri_cgcm2_3_2a.nc";NPERYEAR=365;;
pr_ncar_ccsm3_0_20c3m) file="IPCCData/20c3m/pr_A1.20C3M_%%.CCSM.atmm.1870-01_cat_1999-12.nc";kindname="ccsm 3.0 20c3m";climfield="pr";LSMASK="IPCCData/20c3m/sftlf_A1.20C3M.CCSM.atmm.nc";;
pr_A2_ncar_ccsm3_0_20c3m) file="IPCCData/20c3m_daily/pr_A2.20C3M_%%.CCSM.atmd.1960-01-01_cat_1999-12-31.nc";kindname="ccsm 3.0 20c3m";climfield="pr";LSMASK="IPCCData/20c3m/sftlf_A1.20C3M.CCSM.atmm.nc";NPERYEAR=365;;
pr_ncar_ccsm3_0_sresa1b) file="IPCCData/sresa1b/pr_A1_ncar_ccsm3_0_%%.nc";kindname="ccsm 3.0 sresa1b";climfield="pr";LSMASK="IPCCData/20c3m/sftlf_A1.20C3M.CCSM.atmm.nc";;
pr_ncar_ccsm3_0_sresa2) file="IPCCData/sresa2/pr_A1_ncar_ccsm3_0_%%.nc";kindname="ccsm 3.0 sresa2";climfield="pr";LSMASK="IPCCData/20c3m/sftlf_A1.20C3M.CCSM.atmm.nc";;
pr_A2_ncar_ccsm3_0_sresa2_20) file="IPCCData/sresa2_daily/pr_A2_ncar_ccsm3_0_%%_2046_2065.nc";kindname="ccsm 3.0 sresa2";climfield="pr";LSMASK="IPCCData/20c3m/sftlf_A1.20C3M.CCSM.atmm.nc";NPERYEAR=365;;
pr_A2_ncar_ccsm3_0_sresa2_21) file="IPCCData/sresa2_daily/pr_A2_ncar_ccsm3_0_%%_2080_2099.nc";kindname="ccsm 3.0 sresa2";climfield="pr";LSMASK="IPCCData/20c3m/sftlf_A1.20C3M.CCSM.atmm.nc";NPERYEAR=365;;
pr_ncar_pcm1_20c3m) file="IPCCData/20c3m/pr_A1.20C3M_%%.PCM1.atmm.1890-01_cat_1999-12.nc";kindname="pcm1 20c3m";climfield="pr";LSMASK="IPCCData/20c3m/sftlf_A1.20C3M.PCM1.atmm.nc";;
pr_A2_ncar_pcm1_20c3m) file="IPCCData/20c3m_daily/pr_A2_ncar_pcm1_%%_1960_1999.nc";kindname="pcm1 20c3m";climfield="pr";LSMASK="IPCCData/20c3m/sftlf_A1.20C3M.PCM1.atmm.nc";NPERYEAR=365;;
pr_ncar_pcm1_sresa1b) file="IPCCData/sresa1b/pr_A1.SRESA1B_%%.PCM1.atmm.nc";kindname="pcm1 sresa1b";climfield="pr";LSMASK="IPCCData/20c3m/sftlf_A1.20C3M.PCM1.atmm.nc";;
pr_ncar_pcm1_sresa2) file="IPCCData/sresa2/pr_A1.SRESA2_1.PCM1.atmm.2000-01_cat_2099-12.nc";kindname="pcm1 sresa2";climfield="pr";LSMASK="IPCCData/20c3m/sftlf_A1.20C3M.PCM1.atmm.nc";;
pr_A2_ncar_pcm1_sresa2_20) file="IPCCData/sresa2_daily/pr_A2_ncar_pcm1_00_2046_2065.nc";kindname="pcm1 sresa2";climfield="pr";LSMASK="IPCCData/20c3m/sftlf_A1.20C3M.PCM1.atmm.nc";NPERYEAR=365;;
pr_A2_ncar_pcm1_sresa2_21) file="IPCCData/sresa2_daily/pr_A2_ncar_pcm1_00_2080_2099.nc";kindname="pcm1 sresa2";climfield="pr";LSMASK="IPCCData/20c3m/sftlf_A1.20C3M.PCM1.atmm.nc";NPERYEAR=365;;
pr_ukmo_hadcm3_20c3m) file="IPCCData/20c3m/pr_A1_ukmo_hadcm3_%%.nc";kindname="hadcm3 20c3m";climfield="pr";LSMASK="IPCCData/20c3m/sftlf_A1_ukmo_hadcm3.nc";;
pr_A2_ukmo_hadcm3_20c3m) file="IPCCData/20c3m_daily/pr_A2_ukmo_hadcm3.nc";kindname="hadcm3 20c3m";climfield="pr";LSMASK="IPCCData/20c3m/sftlf_A1_ukmo_hadcm3.nc";NPERYEAR=360;;
pr_ukmo_hadcm3_sresa1b) file="IPCCData/sresa1b/pr_A1_ukmo_hadcm3.nc";kindname="hadcm3 sresa1b";climfield="pr";LSMASK="IPCCData/20c3m/sftlf_A1_ukmo_hadcm3.nc";;
pr_ukmo_hadcm3_sresa2) file="IPCCData/sresa2/pr_A1_ukmo_hadcm3.nc";kindname="hadcm3 sresa2";climfield="pr";LSMASK="IPCCData/20c3m/sftlf_A1_ukmo_hadcm3.nc";;
pr_A2_ukmo_hadcm3_sresa2_21) file="IPCCData/sresa2_daily/pr_A2_ukmo_hadcm3_2080_2099.nc";kindname="hadcm3 sresa2";climfield="pr";LSMASK="IPCCData/20c3m/sftlf_A1_ukmo_hadcm3.nc";NPERYEAR=360;;
pr_ukmo_hadcm3_sresb1) file="IPCCData/sresb1/pr_A1_ukmo_hadcm3.nc";kindname="hadcm3 sresb1";climfield="pr";LSMASK="IPCCData/20c3m/sftlf_A1_ukmo_hadcm3.nc";;
pr_ukmo_hadgem1_picntrl) file="IPCCData/picntrl/pr_A1_ukmo_hadgem1.nc";kindname="hadgem1 picntrl";climfield="pr";LSMASK="IPCCData/picntrl/sftlf_A1_ukmo_hadgem1.nc";;
pr_ukmo_hadgem1_20c3m) file="IPCCData/20c3m/pr_A1_ukmo_hadgem1_%%.nc";kindname="hadgem1 20c3m";climfield="pr";LSMASK="IPCCData/picntrl/sftlf_A1_ukmo_hadgem1.nc";;
pr_ukmo_hadgem1_1pctto2x) file="IPCCData/1pctto2x/pr_A1_ukmo_hadgem1.nc";kindname="hadgem1 1pctto2x";climfield="pr";LSMASK="IPCCData/picntrl/sftlf_A1_ukmo_hadgem1.nc";;
pr_ukmo_hadgem1_sresa1b) file="IPCCData/sresa1b/pr_A1_ukmo_hadgem1.nc";kindname="hadgem1 sresa1b";climfield="pr";LSMASK="IPCCData/picntrl/sftlf_A1_ukmo_hadgem1.nc";;
pr_ukmo_hadgem1_sresa2) file="IPCCData/sresa2/pr_A1_ukmo_hadgem1.nc";kindname="hadgem1 sresa2";climfield="pr";LSMASK="IPCCData/picntrl/sftlf_A1_ukmo_hadgem1.nc";;

psl_cmip3_all_sresa1b) file="IPCCData/sresa1b/psl_cmip3_%%_144.nc";kindname="CMIP3 20c3m/sresa1b all members";climfield="psl";LSMASK=IPCCData/sresa1b/lsmask_cmip3_144.nc;;
psl_cmip3_ave_sresa1b) file="IPCCData/sresa1b/psl_cmip3_ave_%%_144.nc";kindname="CMIP3 20c3m/sresa1b all models";climfield="psl";LSMASK=IPCCData/sresa1b/lsmask_cmip3_144.nc;;
psl_cmip3_ave_mean_sresa1b) file="IPCCData/sresa1b/psl_cmip3_ave_mean_144.nc";kindname="CMIP3 20c3m/sresa1b mult-model mean";climfield="psl";LSMASK=IPCCData/sresa1b/lsmask_cmip3_144.nc;;
psl_cmip3_volcano_all_sresa1b) file="IPCCData/sresa1b/psl_cmip3_volcano_%%_144.nc";kindname="CMIP3 20c3m/sresa1b volcano members";climfield="psl";LSMASK=IPCCData/sresa1b/lsmask_cmip3_144.nc;;
psl_cmip3_volcano_ave_sresa1b) file="IPCCData/sresa1b/psl_cmip3_volcano_ave_%%_144.nc";kindname="CMIP3 20c3m/sresa1b volcano models";climfield="psl";LSMASK=IPCCData/sresa1b/lsmask_cmip3_144.nc;;
psl_cmip3_volcano_ave_mean_sresa1b) file="IPCCData/sresa1b/psl_cmip3_volcano_ave_mean_144.nc";kindname="CMIP3 20c3m/sresa1b volcano mean";climfield="psl";LSMASK=IPCCData/sresa1b/lsmask_cmip3_144.nc;;
psl_cmip3_novolcano_all_sresa1b) file="IPCCData/sresa1b/psl_cmip3_novolcano_%%_144.nc";kindname="CMIP3 20c3m/sresa1b novolcano members";climfield="psl";LSMASK=IPCCData/sresa1b/lsmask_cmip3_144.nc;;
psl_cmip3_novolcano_ave_sresa1b) file="IPCCData/sresa1b/psl_cmip3_novolcano_ave_%%_144.nc";kindname="CMIP3 20c3m/sresa1b novolcano models";climfield="psl";LSMASK=IPCCData/sresa1b/lsmask_cmip3_144.nc;;
psl_cmip3_novolcano_ave_mean_sresa1b) file="IPCCData/sresa1b/psl_cmip3_novolcano_ave_mean_144.nc";kindname="CMIP3 20c3m/sresa1b novolcano mean";climfield="psl";LSMASK=IPCCData/sresa1b/lsmask_cmip3_144.nc;;
psl_bcc_cm1_20c3m) file="IPCCData/20c3m/psl_A1_bcc_cm1_%%_1871_2003.nc";kindname="bcc cm1 20c3m";climfield="psl";;
psl_bccr_bcm2_0_20c3m) file="IPCCData/20c3m/psl_A1_bccr_bcm2_0.nc";kindname="bccr bcm2.0 20c3m";climfield="psl";LSMASK=IPCCData/20c3m/sftlf_A1_bccr_bcm2_0.ctl;;
psl_bccr_bcm2_0_sresa1b) file="IPCCData/sresa1b/psl_A1_bccr_bcm2_0.nc";kindname="bccr bcm2.0 sresa1b";climfield="psl";LSMASK=IPCCData/20c3m/sftlf_A1_bccr_bcm2_0.ctl;;
psl_cccma_cgcm3_1_20c3m) file="IPCCData/20c3m/psl_a1_20c3m_%%_cgcm3_1_t47_1850_2000.nc";kindname="cccma cgcm3.1 20c3m";climfield="psl";LSMASK=IPCCData/20c3m/sftlf_a1_20c3m_cgcm3.1_t47.nc;;
psl_cccma_cgcm3_1_1pctto2x) file="IPCCData/1pctto2x/psl_a1_1pctto2x_1_cgcm3.1_t47_1850_2069.nc";kindname="cccma cgcm3.1 1pctto2x";climfield="psl";LSMASK=IPCCData/20c3m/sftlf_a1_20c3m_cgcm3.1_t47.nc;;
psl_cccma_cgcm3_1_sresa1b) file="IPCCData/sresa1b/psl_a1_cgcm3_1_t47_%%.nc";kindname="cccma cgcm3.1 sresa1b";climfield="psl";LSMASK=IPCCData/20c3m/sftlf_a1_20c3m_cgcm3.1_t47.nc;;
psl_cccma_cgcm3_1_sresa2) file="IPCCData/sresa2/psl_a1_sresa2_1_cgcm3.1_t47_2001_2100.nc";kindname="cccma cgcm3.1 sresa2";climfield="psl";LSMASK=IPCCData/20c3m/sftlf_a1_20c3m_cgcm3.1_t47.nc;;
psl_cccma_cgcm3_1_t63_20c3m) file="IPCCData/20c3m/psl_a1_20c3m_1_cgcm3.1_t63_1850_2000.nc";kindname="cccma cgcm3.1 t63 20c3m";climfield="psl";LSMASK=IPCCData/20c3m/sftlf_a1_20c3m_cgcm3.1_t63.nc;;
psl_cccma_cgcm3_1_t63_sresa1b) file="IPCCData/sresa1b/psl_a1_sresa1b_1_cgcm3.1_t63_1850_2300.nc";kindname="cccma cgcm3.1 t63 sresa1b";climfield="psl";LSMASK=IPCCData/20c3m/sftlf_a1_20c3m_cgcm3.1_t63.nc;;
psl_A2_cccma_cgcm3_1_t63_sresa1b_21) file="IPCCData/sresa1b_daily/psl_a2_sresa1b_1_cgcm3.1_t63_2081_2100.nc";kindname="cccma cgcm3.1 t63 sresa1b";climfield="psl";LSMASK=IPCCData/20c3m/sftlf_a1_20c3m_cgcm3.1_t63.nc;NPERYEAR=365;;
psl_A2_cccma_cgcm3_1_t63_sresa1b_22) file="IPCCData/sresa1b_daily/psl_a2_sresa1b_1_cgcm3.1_t63_2181_2200.nc";kindname="cccma cgcm3.1 t63 sresa1b";climfield="psl";LSMASK=IPCCData/20c3m/sftlf_a1_20c3m_cgcm3.1_t63.nc;NPERYEAR=365;;
psl_cnrm_cm3_20c3m) file="IPCCData/20c3m/psl_A1_cnrm_cm3.nc";kindname="cnrm cm3 20c3m";climfield="psl";LSMASK=IPCCData/20c3m/sftlf_A1_cnrm_cm3.nc;;
psl_cnrm_cm3_sresa2) file="IPCCData/sresa2/psl_A1_cnrm_cm3.nc";kindname="cnrm cm3 sresa2";climfield="psl";LSMASK=IPCCData/20c3m/sftlf_A1_cnrm_cm3.nc;;
psl_cnrm_cm3_sresa1b) file="IPCCData/sresa1b/psl_A1_cnrm_cm3.nc";kindname="cnrm cm3 sresa1b";climfield="psl";LSMASK=IPCCData/20c3m/sftlf_A1_cnrm_cm3.nc;;
psl_csiro_mk3_0_20c3m) file="IPCCData/20c3m/psl_A1_csiro_mk3_0.nc";kindname="csiro mk3.0 20c3m";climfield="psl";LSMASK=IPCCData/20c3m/sftlf_A1_csiro_mk3_0.nc;;
psl_csiro_mk3_0_sresa2) file="IPCCData/sresa2/psl_A1_csiro_mk3_0.nc";kindname="csiro mk3.0 sresa2";climfield="psl";LSMASK=IPCCData/20c3m/sftlf_A1_csiro_mk3_0.nc;;
psl_csiro_mk3_0_sresa1b) file="IPCCData/sresa1b/psl_A1_csiro_mk3_0.nc";kindname="csiro mk3.0 sresa1b";climfield="psl";LSMASK=IPCCData/20c3m/sftlf_A1_csiro_mk3_0.nc;;
psl_csiro_mk3_5_20c3m) file="IPCCData/20c3m/psl_A1_csiro_mk3_5_%%.nc";kindname="csiro mk3.5 20c3m";climfield="psl";LSMASK=IPCCData/20c3m/sftlf_A1_csiro_mk3_5.nc;;
psl_csiro_mk3_5_sresa1b) file="IPCCData/sresa1b/psl_A1_csiro_mk3_5.nc";kindname="csiro mk3.5 sresa1b";climfield="psl";LSMASK=IPCCData/20c3m/sftlf_A1_csiro_mk3_5.nc;;
psl_gfdl_cm2_0_20c3m) file="IPCCData/20c3m/psl_A1_gfdl_cm2_0_%%.186101-200012.nc";kindname="gfdl 2.0 20c3m";climfield="psl";LSMASK="IPCCData/20c3m/sftlf_A1_gfdl_cm2_0.nc";;
psl_gfdl_cm2_0_sresa1b) file="IPCCData/sresa1b/psl_A1_gfdl_cm2_0.nc";kindname="gfdl 2.0 sresa1b";climfield="psl";LSMASK="IPCCData/20c3m/sftlf_A1_gfdl_cm2_0.nc";;
psl_gfdl_cm2_0_sresa2) file="IPCCData/sresa2/psl_A1_gfdl_cm2_0.200101-210012.nc";kindname="gfdl 2.0 sresa2";climfield="psl";LSMASK="IPCCData/20c3m/sftlf_A1_gfdl_cm2_0.nc";;
psl_gfdl_cm2_1_20c3m) file="IPCCData/20c3m/psl_A1_gfdl_cm2_1_%%.186101-200012.nc";kindname="gfdl 2.1 20c3m";climfield="psl";LSMASK="IPCCData/20c3m/sftlf_A1_gfdl_cm2_1.nc";;
psl_gfdl_cm2_1_sresa1b) file="IPCCData/sresa1b/psl_A1_gfdl_cm2_1.nc";kindname="gfdl 2.1 sresa1b";climfield="psl";LSMASK="IPCCData/20c3m/sftlf_A1_gfdl_cm2_1.nc";;
psl_gfdl_cm2_1_sresa2) file="IPCCData/sresa2/psl_A1_gfdl_cm2_1.200101-210012.nc";kindname="gfdl 2.1 sresa2";climfield="psl";LSMASK="IPCCData/20c3m/sftlf_A1_gfdl_cm2_1.nc";;
psl_giss_aom_20c3m) file="IPCCData/20c3m/psl_A1_giss_aom_%%.nc";kindname="giss aom 20c3m";climfield="psl";LSMASK=IPCCData/20c3m/lsmask_giss_aom.nc;;
psl_giss_aom_sresa1b) file="IPCCData/sresa1b/psl_A1_giss_aom_%%.nc";kindname="giss aom sresa1b";climfield="psl";LSMASK=IPCCData/20c3m/lsmask_giss_aom.nc;;
psl_giss_model_e_h_20c3m) file="IPCCData/20c3m/psl_A1.GISS3.20C3M.%%.nc";kindname="giss eh 20c3m";climfield="psl";LSMASK=IPCCData/20c3m/lsmask_giss_model_e_h.nc;;
psl_giss_model_e_h_sresa1b) file="IPCCData/sresa1b/psl_A1.GISS3.SRESA1B.%%.nc";kindname="giss eh sresa1b";climfield="psl";LSMASK=IPCCData/20c3m/lsmask_giss_model_e_h.nc;;
psl_giss_model_e_h_1pctto2x) file="IPCCData/1pctto2x/psl_A1.GISS3.1pctto2.nc";kindname="giss eh 1pctto2x";climfield="psl";LSMASK=IPCCData/20c3m/lsmask_giss_model_e_h.nc;;
psl_giss_model_e_r_20c3m) file="IPCCData/20c3m/psl_A1.GISS1.20C3M.%%.nc";kindname="giss er 20c3m";climfield="psl";LSMASK=IPCCData/20c3m/lsmask_giss_model_e_r.nc;;
psl_giss_model_e_r_sresa1b) file="IPCCData/sresa1b/psl_A1.GISS1.SRESA1B.%%.nc";kindname="giss er sresa1b";climfield="psl";LSMASK=IPCCData/20c3m/lsmask_giss_model_e_r.nc;;
psl_giss_model_e_r_sresa2) file="IPCCData/sresa2/psl_A1.GISS1.SRESA2.nc";kindname="giss er sresa2";climfield="psl";LSMASK=IPCCData/20c3m/lsmask_giss_model_e_r.nc;;
psl_iap_fgoals1_0_g_20c3m) file="IPCCData/20c3m/psl_A1_iap_fgoals1_0_g_%%.nc";kindname="iap fgoals10g 20c3m";climfield="psl";;
psl_iap_fgoals1_0_g_sresa1b) file="IPCCData/sresa1b/psl_A1_iap_fgoals1_0_g_%%.nc";kindname="iap fgoals10g sresa1b";climfield="psl";;
psl_ingv_echam4_20c3m) file="IPCCData/20c3m/psl_A1_ingv_echam4.nc";kindname="ingv_echam4 20c3m";climfield="psl";LSMASK=IPCCData/20c3m/sftlf_A1_ingv_echam4.nc;;
psl_ingv_echam4_sresa1b) file="IPCCData/sresa1b/psl_A1_ingv_echam4.nc";kindname="ingv_echam4 sresa1b";climfield="psl";LSMASK=IPCCData/20c3m/sftlf_A1_ingv_echam4.nc;;
psl_inmcm3_0_20c3m) file="IPCCData/20c3m/psl_A1_inmcm3_0.nc";kindname="inmcm3.0 20c3m";climfield="psl";LSMASK=IPCCData/20c3m/sftlf_A1_inmcm3_0.nc;;
psl_inmcm3_0_sresa1b) file="IPCCData/sresa1b/psl_A1_inmcm3_0.nc";kindname="inmcm3.0 sresa1b";climfield="psl";LSMASK=IPCCData/20c3m/sftlf_A1_inmcm3_0.nc;;
psl_inmcm3_0_sresa2) file="IPCCData/sresa2/psl_A1_inmcm3_0.nc";kindname="inmcm3.0 sresa2";climfield="psl";LSMASK=IPCCData/20c3m/sftlf_A1_inmcm3_0.nc;;
psl_ipsl_cm4_20c3m) file="IPCCData/20c3m/psl_A1_ipsl_cm4_1860-2000.nc";kindname="ipsl cm4 20c3m";climfield="psl";LSMASK=IPCCData/20c3m/sftlf_A1_ipsl_cm4.nc;;
psl_ipsl_cm4_sresa1b) file="IPCCData/sresa1b/psl_A1_ipsl_cm4.nc";kindname="ipsl cm4 sresa1b";climfield="psl";LSMASK=IPCCData/20c3m/sftlf_A1_ipsl_cm4.nc;;
psl_ipsl_cm4_sresa2) file="IPCCData/sresa2/psl_A1_ipsl_cm4_2000-2100.nc";kindname="ipsl cm4 sresa2";climfield="psl";LSMASK=IPCCData/20c3m/sftlf_A1_ipsl_cm4.nc;;
psl_miroc3_2_hires_20c3m) file="IPCCData/20c3m/psl_A1_miroc3_2_hires.nc";kindname="miroc 3.2 hi 20c3m";climfield="psl";LSMASK="IPCCData/20c3m/sftlf_A1_miroc3_2_hires.nc";;
psl_miroc3_2_hires_sresa1b) file="IPCCData/sresa1b/psl_A1_miroc3_2_hires.nc";kindname="miroc 3.2 hi sresa1b";climfield="psl";LSMASK="IPCCData/20c3m/sftlf_A1_miroc3_2_hires.nc";;
psl_miroc3_2_hires_1pctto2x) file="IPCCData/1pctto2x/psl_A1_miroc3_2_hires.nc";kindname="miroc 3.2 hi 1pctto2x";climfield="psl";LSMASK="IPCCData/20c3m/sftlf_A1_miroc3_2_hires.nc";;
psl_miroc3_2_medres_20c3m) file="IPCCData/20c3m/psl_A1_miroc3_2_medres_%%.nc";kindname="miroc 3.2 med 20c3m";climfield="psl";LSMASK="IPCCData/20c3m/sftlf_A1_miroc3_2_medres.nc";;
psl_miroc3_2_medres_sresa1b) file="IPCCData/sresa1b/psl_A1_miroc3_2_medres_%%.nc";kindname="miroc 3.2 med sresa1b";climfield="psl";LSMASK="IPCCData/20c3m/sftlf_A1_miroc3_2_medres.nc";;
psl_miroc3_2_medres_sresa2) file="IPCCData/sresa2/psl_A1_miroc3_2_medres_%%.nc";kindname="miroc 3.2 med sresa2";climfield="psl";LSMASK="IPCCData/20c3m/sftlf_A1_miroc3_2_medres.nc";;
psl_miub_echo_g_20c3m) file="IPCCData/20c3m/psl_A1_miub_echo_g_%%_0007-0147.nc";kindname="miub echo g 20c3m";climfield="psl";LSMASK="IPCCData/20c3m/sftlf_A1_miub_echo_g.nc";;
psl_miub_echo_g_sresa1b) file="IPCCData/sresa1b/psl_A1_miub_echo_g_%%.nc";kindname="miub echo g sresa1b";climfield="psl";LSMASK="IPCCData/20c3m/sftlf_A1_miub_echo_g.nc";;
psl_mpi_echam5_20c3m) file="IPCCData/20c3m/psl_A1_mpi_echam5_%%.nc";kindname="mpi echam5 20c3m";climfield="psl";LSMASK="IPCCData/20c3m/lsmask_mpi_echam5.nc";;
psl_mpi_echam5_sresa1b) file="IPCCData/sresa1b/psl_A1_mpi_echam5_%%.nc";kindname="mpi echam5 sresa1b";climfield="psl";LSMASK="IPCCData/20c3m/lsmask_mpi_echam5.nc";;
psl_mpi_echam5_sresa2) file="IPCCData/sresa2/psl_A1_mpi_echam5_%%.nc";kindname="mpi echam5 sresa2";climfield="psl";LSMASK="IPCCData/20c3m/lsmask_mpi_echam5.nc";;
psl_mpi_echam5_picntrl) file="IPCCData/picntrl/psl_mpi_echam5.nc";kindname="mpi echam5 picntrl";climfield="psl";LSMASK="IPCCData/20c3m/lsmask_mpi_echam5.nc";;
psl_mpi_echam5_1pctto2x) file="IPCCData/1pctto2x/psl_A1_mpi_echam5_%%.nc";kindname="mpi echam5 1pctto2x";climfield="psl";LSMASK="IPCCData/20c3m/lsmask_mpi_echam5.nc";;
psl_mpi_echam5_1pctto4x) file="IPCCData/1pctto4x/psl_A1_mpi_echam5.nc";kindname="mpi echam5 1pctto4x";climfield="psl";LSMASK="IPCCData/20c3m/lsmask_mpi_echam5.nc";;
psl_mri_cgcm2_3_2a_20c3m) file="IPCCData/20c3m/psl_A1_mri_cgcm2_3_2a_%%.nc";kindname="mri cgcm232a 20c3m";climfield="psl";LSMASK="IPCCData/20c3m/sftlf_A1_mri_cgcm2_3_2a.nc";;
psl_mri_cgcm2_3_2a_sresa1b) file="IPCCData/sresa1b/psl_A1_mri_cgcm2_3_2a_%%.nc";kindname="mri cgcm232a sresa1b";climfield="psl";LSMASK="IPCCData/20c3m/sftlf_A1_mri_cgcm2_3_2a.nc";;
psl_mri_cgcm2_3_2a_sresa2) file="IPCCData/sresa2/psl_A1_mri_cgcm2_3_2a_%%.nc";kindname="mri cgcm232a sresa2";climfield="psl";LSMASK="IPCCData/20c3m/sftlf_A1_mri_cgcm2_3_2a.nc";;
psl_ncar_ccsm3_0_20c3m) file="IPCCData/20c3m/psl_A1.20C3M_%%.CCSM.atmm.1870-01_cat_1999-12.nc";kindname="ccsm 3.0 20c3m";climfield="psl";LSMASK="IPCCData/20c3m/sftlf_A1.20C3M.CCSM.atmm.nc";;
psl_ncar_ccsm3_0_sresa1b) file="IPCCData/sresa1b/psl_A1.SRESA1B_%%.CCSM.atmm.nc";kindname="ccsm 3.0 sresa1b";climfield="psl";LSMASK="IPCCData/20c3m/sftlf_A1.20C3M.CCSM.atmm.nc";;
psl_ncar_ccsm3_0_sresa2) file="IPCCData/sresa2/psl_A1.SRESA2_%%.CCSM.atmm.2000-01_cat_2099-12.nc";kindname="ccsm 3.0 sresa2";climfield="psl";LSMASK="IPCCData/20c3m/sftlf_A1.20C3M.CCSM.atmm.nc";;
psl_ncar_pcm1_20c3m) file="IPCCData/20c3m/psl_A1.20C3M_%%.PCM1.atmm.1890-01_cat_1999-12.nc";kindname="pcm1 20c3m";climfield="psl";LSMASK="IPCCData/20c3m/sftlf_A1.20C3M.PCM1.atmm.nc";;
psl_ncar_pcm1_sresa1b) file="IPCCData/sresa1b/psl_A1.SRESA1B_%%.PCM1.atmm.nc";kindname="pcm1 sresa1b";climfield="psl";LSMASK="IPCCData/20c3m/sftlf_A1.20C3M.PCM1.atmm.nc";;
psl_ncar_pcm1_sresa2) file="IPCCData/sresa2/psl_A1.SRESA2_%%.PCM1.atmm.2000-01_cat_2099-12.nc";kindname="pcm1 sresa2";climfield="psl";LSMASK="IPCCData/20c3m/sftlf_A1.20C3M.PCM1.atmm.nc";;
psl_ukmo_hadcm3_20c3m) file="IPCCData/20c3m/psl_A1_ukmo_hadcm3_%%.nc";kindname="hadcm3 20c3m";climfield="psl";LSMASK="IPCCData/20c3m/sftlf_A1_ukmo_hadcm3.nc";;
psl_ukmo_hadcm3_sresa1b) file="IPCCData/sresa1b/psl_A1_ukmo_hadcm3.nc";kindname="hadcm3 sresa1b";climfield="psl";LSMASK="IPCCData/20c3m/sftlf_A1_ukmo_hadcm3.nc";;
psl_ukmo_hadcm3_sresa2) file="IPCCData/sresa2/psl_A1_ukmo_hadcm3.nc";kindname="hadcm3 sresa2";climfield="psl";LSMASK="IPCCData/20c3m/sftlf_A1_ukmo_hadcm3.nc";;
psl_ukmo_hadgem1_picntrl) file="IPCCData/picntrl/psl_A1_ukmo_hadgem1.nc";kindname="hadgem1 picntrl";climfield="psl";LSMASK="IPCCData/picntrl/sftlf_A1_ukmo_hadgem1.nc";;
psl_ukmo_hadgem1_20c3m) file="IPCCData/20c3m/psl_A1_ukmo_hadgem1_%%.nc";kindname="hadgem1 20c3m";climfield="psl";LSMASK="IPCCData/picntrl/sftlf_A1_ukmo_hadgem1.nc";;
psl_ukmo_hadgem1_1pctto2x) file="IPCCData/1pctto2x/psl_A1_ukmo_hadgem1.nc";kindname="hadgem1 1pctto2x";climfield="psl";LSMASK="IPCCData/picntrl/sftlf_A1_ukmo_hadgem1.nc";;
psl_ukmo_hadgem1_sresa1b) file="IPCCData/sresa1b/psl_A1_ukmo_hadgem1.nc";kindname="hadgem1 sresa1b";climfield="psl";LSMASK="IPCCData/picntrl/sftlf_A1_ukmo_hadgem1.nc";;

tauu_cccma_cgcm3_1_20c3m) file="IPCCData/20c3m/tauu_a1_20c3m_1_cgcm3.1_t47_1850_2000.nc";kindname="cccma cgcm3.1 20c3m";climfield="tauu";;
tauu_cccma_cgcm3_1_1pctto2x) file="IPCCData/1pctto2x/tauu_a1_1pctto2x_1_cgcm3.1_t47_1850_2069.nc";kindname="cccma cgcm3.1 1pctto2x";climfield="tauu";;
tauu_cnrm_cm3_20c3m) file="IPCCData/20c3m/tauu_A1_cnrm_cm3.nc";kindname="cnrm cm3 20c3m";climfield="tauu";LSMASK=IPCCData/20c3m/sftlf_A1_cnrm_cm3.nc;;
tauu_cnrm_cm3_sresa2) file="IPCCData/sresa2/tauu_A1_cnrm_cm3.nc";kindname="cnrm cm3 sresa2";climfield="tauu";LSMASK=IPCCData/20c3m/sftlf_A1_cnrm_cm3.nc;;
tauu_csiro_mk3_0_20c3m) file="IPCCData/20c3m/tauu_A1_csiro_mk3_0.nc";kindname="csiro mk3.0 20c3m";climfield="tauu";LSMASK=IPCCData/20c3m/sftlf_A1_csiro_mk3_0.nc;;
tauu_gfdl_cm2_0_20c3m) file="IPCCData/20c3m/tauu_A1_gfdl_cm2_0_%%.186101-200012.nc";kindname="gfdl 2.0 20c3m";climfield="tauu";;
tauu_gfdl_cm2_0_sresa1b) file="IPCCData/sresa1b/tauu_A1_gfdl_cm2_0.220101-230012.nc";kindname="gfdl 2.0 sresa1b";climfield="tauu";;
tauu_gfdl_cm2_0_sresa2) file="IPCCData/sresa2/tauu_A1_gfdl_cm2_0.200101-210012.nc";kindname="gfdl 2.0 sresa2";climfield="tauu";;
tauu_gfdl_cm2_1_20c3m) file="IPCCData/20c3m/tauu_A1_gfdl_cm2_1_%%.186101-200012.nc";kindname="gfdl 2.1 20c3m";climfield="tauu";LSMASK="IPCCData/20c3m/sftlf_A1_gfdl_cm2_1.nc";;
tauu_gfdl_cm2_1_sresa1b) file="IPCCData/sresa1b/tauu_A1_gfdl_cm2_1.220101-230012.nc";kindname="gfdl 2.1 sresa1b";climfield="tauu";LSMASK="IPCCData/20c3m/sftlf_A1_gfdl_cm2_1.nc";;
tauu_giss_aom_20c3m) file="IPCCData/20c3m/tauu_A1_giss_aom_%%.nc";kindname="giss aom 20c3m";climfield="tauu";LSMASK=IPCCData/20c3m/lsmask_giss_aom.nc;;
tauu_giss_model_e_h_20c3m) file="IPCCData/20c3m/tauu_A1.GISS3.20C3M.%%.nc";kindname="giss eh 20c3m";climfield="tauu";LSMASK=IPCCData/20c3m/lsmask_giss_model_e_h.nc;;
tauu_giss_model_e_r_20c3m) file="IPCCData/20c3m/tauu_A1.GISS1.20C3M.%%.nc";kindname="giss er 20c3m";climfield="tauu";LSMASK=IPCCData/20c3m/lsmask_giss_model_e_r.nc;;
tauu_giss_model_e_r_sresa2) file="IPCCData/sresa2/tauu_A1.GISS1.SRESA2.nc";kindname="giss er sresa2";climfield="tauu";LSMASK=IPCCData/20c3m/lsmask_giss_model_e_r.nc;;
tauu_iap_fgoals1_0_g_20c3m) file="IPCCData/20c3m/tauu_A1_iap_fgoals1_0_g_%%.nc";kindname="iap fgoals10g 20c3m";climfield="tauu";;
tauu_inmcm3_0_20c3m) file="IPCCData/20c3m/tauu_A1_inmcm3_0.nc";kindname="inmcm3.0 20c3m";climfield="tauu";LSMASK=IPCCData/20c3m/sftlf_A1_inmcm3_0.nc;;
tauu_inmcm3_0_sresa2) file="IPCCData/sresa2/tauu_A1_inmcm3_0.nc";kindname="inmcm3.0 sresa2";climfield="tauu";LSMASK=IPCCData/20c3m/sftlf_A1_inmcm3_0.nc;;
tauu_ipsl_cm4_20c3m) file="IPCCData/20c3m/tauu_A1_ipsl_cm4_1860-2000.nc";kindname="ipsl cm4 20c3m";climfield="tauu";LSMASK=IPCCData/20c3m/sftlf_A1_ipsl_cm4.nc;;
tauu_miroc3_2_hires_20c3m) file="IPCCData/20c3m/tauu_A1_miroc3_2_hires.nc";kindname="miroc 3.2 hi 20c3m";climfield="tauu";LSMASK="IPCCData/20c3m/sftlf_A1_miroc3_2_hires.nc";;
tauu_miroc3_2_hires_1pctto2x) file="IPCCData/1pctto2x/tauu_A1_miroc3_2_hires.nc";kindname="miroc 3.2 hi 1pctto2x";climfield="tauu";LSMASK="IPCCData/20c3m/sftlf_A1_miroc3_2_hires.nc";;
tauu_miroc3_2_medres_20c3m) file="IPCCData/20c3m/tauu_A1_miroc3_2_medres_%%.nc";kindname="miroc 3.2 med 20c3m";climfield="tauu";LSMASK="IPCCData/20c3m/sftlf_A1_miroc3_2_medres.nc";;
tauu_miroc3_2_medres_sresa1b) file="IPCCData/sresa1b/tauu_A1_miroc3_2_medres_%%.nc";kindname="miroc 3.2 med sresa1b";climfield="tauu";LSMASK="IPCCData/20c3m/sftlf_A1_miroc3_2_medres.nc";;
#tauu_miroc3_2_medres_sresa1b) file="IPCCData/sresa1b/tauu_A1_sresa1b_00.medres.2201_2300.nc";kindname="miroc 3.2 med sresa1b";climfield="tauu";LSMASK="IPCCData/20c3m/sftlf_A1_miroc3_2_medres.nc";;
tauu_miroc3_2_medres_sresa2) file="IPCCData/sresa2/tauu_A1_miroc3_2_medres_%%.nc";kindname="miroc 3.2 med sresa2";climfield="tauu";LSMASK="IPCCData/20c3m/sftlf_A1_miroc3_2_medres.nc";;
tauu_mpi_echam5_20c3m) file="IPCCData/20c3m/tauu_A1_mpi_echam5_%%.nc";kindname="mpi echam5 20c3m";climfield="tauu";LSMASK="IPCCData/20c3m/lsmask_mpi_echam5.nc";;
tauu_mpi_echam5_sresa1b) file="IPCCData/sresa1b/tauu_A1.mpi_echam.220101-230012.nc";kindname="mpi echam5 sresa1b";climfield="tauu";LSMASK="IPCCData/20c3m/lsmask_mpi_echam5.nc";;
tauu_mri_cgcm2_3_2a_20c3m) file="IPCCData/20c3m/tauu_A1_mri_cgcm2_3_2a_%%.nc";kindname="mri cgcm232a 20c3m";climfield="tauu";LSMASK="IPCCData/20c3m/sftlf_A1_mri_cgcm2_3_2a.nc";;
tauu_mri_cgcm2_3_2a_sresa2) file="IPCCData/sresa2/tauu_A1_mri_cgcm2_3_2a_%%.nc";kindname="mri cgcm232a sresa2";climfield="tauu";LSMASK="IPCCData/20c3m/sftlf_A1_mri_cgcm2_3_2a.nc";;
tauu_ncar_ccsm3_0_20c3m) file="IPCCData/20c3m/tauu_A1.20C3M_%%.CCSM.atmm.1870-01_cat_1999-12.nc";kindname="ccsm 3.0 20c3m";climfield="tauu";LSMASK="IPCCData/20c3m/sftlf_A1.20C3M.CCSM.atmm.nc";;
tauu_ncar_pcm1_20c3m) file="IPCCData/20c3m/tauu_A1.20C3M_%%.PCM1.atmm.1890-01_cat_1999-12.nc";kindname="pcm1 20c3m";climfield="tauu";LSMASK="IPCCData/20c3m/sftlf_A1.20C3M.PCM1.atmm.nc";;
tauu_ncar_pcm1_sresa2) file="IPCCData/sresa2/tauu_A1.SRESA2_1.PCM1.atmm.2000-01_cat_2099-12.nc";kindname="pcm1 sresa2";climfield="tauu";LSMASK="IPCCData/20c3m/sftlf_A1.20C3M.PCM1.atmm.nc";;
tauu_ukmo_hadcm3_20c3m) file="IPCCData/20c3m/tauu_A1_ukmo_hadcm3_%%.nc";kindname="hadcm3 20cm3";climfield="tauu";LSMASK="IPCCData/20c3m/sftlf_A1_ukmo_hadcm3.nc";;
tauu_ukmo_hadcm3_sresa1b) file="IPCCData/sresa1b/tauu_A1_ukmo_hadcm3.nc";kindname="hadcm3 sresa1b";climfield="tauu";LSMASK="IPCCData/20c3m/sftlf_A1_ukmo_hadcm3.nc";;
tauu_ukmo_hadcm3_sresa2) file="IPCCData/sresa2/tauu_A1_ukmo_hadcm3.nc";kindname="hadcm3 sresa2";climfield="tauu";LSMASK="IPCCData/20c3m/sftlf_A1_ukmo_hadcm3.nc";;
tauu_ukmo_hadgem1_picntrl) file="IPCCData/picntrl/tauu_A1_ukmo_hadgem1.nc";kindname="hadgem1 picntrl";climfield="tauu";LSMASK="IPCCData/picntrl/sftlf_A1_ukmo_hadgem1.nc";;
tauu_ukmo_hadgem1_1pctto2x) file="IPCCData/1pctto2x/tauu_A1_ukmo_hadgem1.nc";kindname="hadgem1 1pctto2x";climfield="tauu";LSMASK="IPCCData/picntrl/sftlf_A1_ukmo_hadgem1.nc";;

tauv_cccma_cgcm3_1_20c3m) file="IPCCData/20c3m/tauv_a1_20c3m_1_cgcm3.1_t47_1850_2000.nc";kindname="cccma cgcm3.1 20c3m";climfield="tauv";;
tauv_cccma_cgcm3_1_1pctto2x) file="IPCCData/1pctto2x/tauv_a1_1pctto2x_1_cgcm3.1_t47_1850_2069.nc";kindname="cccma cgcm3.1 1pctto2x";climfield="tauv";;
tauv_cnrm_cm3_20c3m) file="IPCCData/20c3m/tauv_A1_cnrm_cm3.nc";kindname="cnrm cm3 20c3m";climfield="tauv";LSMASK=IPCCData/20c3m/sftlf_A1_cnrm_cm3.nc;;
tauv_cnrm_cm3_sresa2) file="IPCCData/sresa2/tauv_A1_cnrm_cm3.nc";kindname="cnrm cm3 sresa2";climfield="tauv";LSMASK=IPCCData/20c3m/sftlf_A1_cnrm_cm3.nc;;
tauv_csiro_mk3_0_20c3m) file="IPCCData/20c3m/tauv_A1_csiro_mk3_0.nc";kindname="csiro mk3.0 20c3m";climfield="tauv";LSMASK=IPCCData/20c3m/sftlf_A1_csiro_mk3_0.nc;;
tauv_gfdl_cm2_0_20c3m) file="IPCCData/20c3m/tauv_A1_gfdl_cm2_0_%%.186101-200012.nc";kindname="gfdl 2.0 20c3m";climfield="tauv";;
tauv_gfdl_cm2_0_sresa1b) file="IPCCData/sresa1b/tauv_A1_gfdl_cm2_0.220101-230012.nc";kindname="gfdl 2.0 sresa1b";climfield="tauv";;
tauv_gfdl_cm2_0_sresa2) file="IPCCData/sresa2/tauv_A1_gfdl_cm2_0.200101-210012.nc";kindname="gfdl 2.0 sresa2";climfield="tauv";;
tauv_gfdl_cm2_1_20c3m) file="IPCCData/20c3m/tauv_A1_gfdl_cm2_1_%%.186101-200012.nc";kindname="gfdl 2.1 20c3m";climfield="tauv";LSMASK="IPCCData/20c3m/sftlf_A1_gfdl_cm2_1.nc";;
tauv_gfdl_cm2_1_sresa1b) file="IPCCData/sresa1b/tauv_A1_gfdl_cm2_1.220101-230012.nc";kindname="gfdl 2.1 sresa1b";climfield="tauv";LSMASK="IPCCData/20c3m/sftlf_A1_gfdl_cm2_1.nc";;
tauv_giss_aom_20c3m) file="IPCCData/20c3m/tauv_A1_giss_aom_%%.nc";kindname="giss aom 20c3m";climfield="tauv";LSMASK=IPCCData/20c3m/lsmask_giss_aom.nc;;
tauv_giss_model_e_h_20c3m) file="IPCCData/20c3m/tauv_A1.GISS3.20C3M.%%.nc";kindname="giss eh 20c3m";climfield="tauv";LSMASK=IPCCData/20c3m/lsmask_giss_model_e_h.nc;;
tauv_giss_model_e_r_20c3m) file="IPCCData/20c3m/tauv_A1.GISS1.20C3M.%%.nc";kindname="giss er 20c3m";climfield="tauv";LSMASK=IPCCData/20c3m/lsmask_giss_model_e_r.nc;;
tauv_giss_model_e_r_sresa2) file="IPCCData/sresa2/tauv_A1.GISS1.SRESA2.nc";kindname="giss er sresa2";climfield="tauv";LSMASK=IPCCData/20c3m/lsmask_giss_model_e_r.nc;;
tauv_iap_fgoals1_0_g_20c3m) file="IPCCData/20c3m/tauv_A1_iap_fgoals1_0_g_%%.nc";kindname="iap fgoals10g 20c3m";climfield="tauv";;
tauv_inmcm3_0_20c3m) file="IPCCData/20c3m/tauv_A1_inmcm3_0.nc";kindname="inmcm3.0 20c3m";climfield="tauv";LSMASK=IPCCData/20c3m/sftlf_A1_inmcm3_0.nc;;
tauv_inmcm3_0_sresa2) file="IPCCData/sresa2/tauv_A1_inmcm3_0.nc";kindname="inmcm3.0 sresa2";climfield="tauv";LSMASK=IPCCData/20c3m/sftlf_A1_inmcm3_0.nc;;
tauv_ipsl_cm4_20c3m) file="IPCCData/20c3m/tauv_A1_ipsl_cm4_1860-2000.nc";kindname="ipsl cm4 20c3m";climfield="tauv";LSMASK=IPCCData/20c3m/sftlf_A1_ipsl_cm4.nc;;
tauv_miroc3_2_hires_20c3m) file="IPCCData/20c3m/tauv_A1_miroc3_2_hires.nc";kindname="miroc 3.2 hi 20c3m";climfield="tauv";LSMASK="IPCCData/20c3m/sftlf_A1_miroc3_2_hires.nc";;
tauv_miroc3_2_hires_1pctto2x) file="IPCCData/1pctto2x/tauv_A1_miroc3_2_hires.nc";kindname="miroc 3.2 hi 1pctto2x";climfield="tauv";LSMASK="IPCCData/20c3m/sftlf_A1_miroc3_2_hires.nc";;
tauv_miroc3_2_medres_20c3m) file="IPCCData/20c3m/tauv_A1_miroc3_2_medres_%%.nc";kindname="miroc 3.2 med 20c3m";climfield="tauv";LSMASK="IPCCData/20c3m/sftlf_A1_miroc3_2_medres.nc";;
tauv_miroc3_2_medres_sresa1b) file="IPCCData/sresa1b/tauv_A1_miroc3_2_medres.nc";kindname="miroc 3.2 med sresa1b";climfield="tauv";LSMASK="IPCCData/20c3m/sftlf_A1_miroc3_2_medres.nc";;
tauv_miroc3_2_medres_sresa2) file="IPCCData/sresa2/tauv_A1_miroc3_2_medres_%%.nc";kindname="miroc 3.2 med sresa2";climfield="tauv";LSMASK="IPCCData/20c3m/sftlf_A1_miroc3_2_medres.nc";;
tauv_mpi_echam5_20c3m) file="IPCCData/20c3m/tauv_A1_mpi_echam5_%%.nc";kindname="mpi echam5 20c3m";climfield="tauv";LSMASK="IPCCData/20c3m/lsmask_mpi_echam5.nc";;
tauv_mri_cgcm2_3_2a_20c3m) file="IPCCData/20c3m/tauv_A1_mri_cgcm2_3_2a_%%.nc";kindname="mri cgcm232a 20c3m";climfield="tauv";LSMASK="IPCCData/20c3m/sftlf_A1_mri_cgcm2_3_2a.nc";;
tauv_mri_cgcm2_3_2a_sresa2) file="IPCCData/sresa2/tauv_A1_mri_cgcm2_3_2a_%%.nc";kindname="mri cgcm232a sresa2";climfield="tauv";LSMASK="IPCCData/20c3m/sftlf_A1_mri_cgcm2_3_2a.nc";;
tauv_ncar_ccsm3_0_20c3m) file="IPCCData/20c3m/tauv_A1.20C3M_%%.CCSM.atmm.1870-01_cat_1999-12.nc";kindname="ccsm 3.0 20c3m";climfield="tauv";LSMASK="IPCCData/20c3m/sftlf_A1.20C3M.CCSM.atmm.nc";;
tauv_ncar_pcm1_20c3m) file="IPCCData/20c3m/tauv_A1.20C3M_%%.PCM1.atmm.1890-01_cat_1999-12.nc";kindname="pcm1 20c3m";climfield="tauv";LSMASK="IPCCData/20c3m/sftlf_A1.20C3M.PCM1.atmm.nc";;
tauv_ncar_pcm1_sresa2) file="IPCCData/sresa2/tauv_A1.SRESA2_1.PCM1.atmm.2000-01_cat_2099-12.nc";kindname="pcm1 sresa2";climfield="tauv";LSMASK="IPCCData/20c3m/sftlf_A1.20C3M.PCM1.atmm.nc";;
tauv_ukmo_hadcm3_20c3m) file="IPCCData/20c3m/tauv_A1_ukmo_hadcm3_%%.nc";kindname="hadcm3 20c3m";climfield="tauv";LSMASK="IPCCData/20c3m/sftlf_A1_ukmo_hadcm3.nc";;
tauv_ukmo_hadcm3_sresa1b) file="IPCCData/sresa1b/tauv_A1_ukmo_hadcm3.nc";kindname="hadcm3 sresa1b";climfield="tauv";LSMASK="IPCCData/20c3m/sftlf_A1_ukmo_hadcm3.nc";;
tauv_ukmo_hadcm3_sresa2) file="IPCCData/sresa2/tauv_A1_ukmo_hadcm3.nc";kindname="hadcm3 sresa2";climfield="tauv";LSMASK="IPCCData/20c3m/sftlf_A1_ukmo_hadcm3.nc";;
tauv_ukmo_hadgem1_picntrl) file="IPCCData/picntrl/tauv_A1_ukmo_hadgem1.nc";kindname="hadgem1 picntrl";climfield="tauv";LSMASK="IPCCData/picntrl/sftlf_A1_ukmo_hadgem1.nc";;
tauv_ukmo_hadgem1_1pctto2x) file="IPCCData/1pctto2x/tauv_A1_ukmo_hadgem1.nc";kindname="hadgem1 1pctto2x";climfield="tauv";LSMASK="IPCCData/picntrl/sftlf_A1_ukmo_hadgem1.nc";;

mrso_cccma_cgcm3_1_20c3m) file="IPCCData/20c3m/mrso_a1_20c3m_%%_cgcm3.1_t47_1850_2000.nc";kindname="cccma cgcm3.1 20c3m";climfield="mrso";LSMASK=IPCCData/20c3m/sftlf_a1_20c3m_cgcm3.1_t47.nc;;
mrso_cccma_cgcm3_1_sresa2) file="IPCCData/sresa2/mrso_a1_sresa2_%%_cgcm3.1_t47_2001_2100.nc";kindname="cccma cgcm3.1 sresa2";climfield="mrso";LSMASK=IPCCData/20c3m/sftlf_a1_20c3m_cgcm3.1_t47.nc;;
mrso_cccma_cgcm3_1_t63_20c3m) file="IPCCData/20c3m/mrso_a1_20c3m_1_cgcm3.1_t63_1850_2000.nc";kindname="cccma cgcm3.1 t63 20c3m";climfield="mrso";LSMASK=IPCCData/20c3m/sftlf_a1_20c3m_cgcm3.1_t63.nc;;
mrso_gfdl_cm2_0_20c3m) file="IPCCData/20c3m/mrso_A1_gfdl_cm2_0_%%_186101-200012.nc";kindname="gfdl cm2.0 20c3m";climfield="mrso";LSMASK="IPCCData/20c3m/sftlf_A1_gfdl_cm2_0.nc";;
mrso_gfdl_cm2_0_sresa2) file="IPCCData/sresa2/mrso_A1_gfdl_cm2_0.nc";kindname="gfdl cm2.0 sresa2";climfield="mrso";LSMASK="IPCCData/20c3m/sftlf_A1_gfdl_cm2_0.nc";;
mrso_gfdl_cm2_1_20c3m) file="IPCCData/20c3m/mrso_A1_gfdl_cm2_1_%%_186101-200012.nc";kindname="gfdl cm2.1 20c3m";climfield="mrso";LSMASK="IPCCData/20c3m/sftlf_A1_gfdl_cm2_1.nc";;
mrso_gfdl_cm2_1_sresa2) file="IPCCData/sresa2/mrso_A1_gfdl_cm2_1.nc";kindname="gfdl cm2.1 sresa2";climfield="mrso";LSMASK="IPCCData/20c3m/sftlf_A1_gfdl_cm2_1.nc";;
mrso_giss_aom_20c3m) file="IPCCData/20c3m/mrso_A1_giss_aom_%%.nc";kindname="giss aom 20c3m";climfield="mrso";LSMASK=IPCCData/20c3m/lsmask_giss_aom.nc;;
mrso_giss_model_e_h_20c3m) file="IPCCData/20c3m/mrso_A1.GISS3.20C3M.%%.nc";kindname="giss model eh 20c3m";climfield="mrso";LSMASK=IPCCData/20c3m/lsmask_giss_model_e_h.nc;;
mrso_giss_model_e_r_20c3m) file="IPCCData/20c3m/mrso_A1.GISS1.20C3M.%%.nc";kindname="giss model er 20c3m";climfield="mrso";LSMASK=IPCCData/20c3m/lsmask_giss_model_e_r.nc;;
mrso_giss_model_e_r_sresa2) file="IPCCData/sresa2/mrso_A1.GISS1.SRESA2.nc";kindname="giss model er sresa2";climfield="mrso";LSMASK=IPCCData/20c3m/lsmask_giss_model_e_r.nc;;
mrso_iap_fgoals1_0_g_20c3m) file="IPCCData/20c3m/mrso_A1_iap_fgoals1_0_g_%%.nc";kindname="iap fgoals1.0.g 20c3m";climfield="mrso";;
mrso_ingv_echam4_20c3m) file="IPCCData/20c3m/mrso_A1_ingv_echam4.nc";kindname="ingv echam4 20c3m";climfield="mrso";LSMASK=IPCCData/20c3m/sftlf_A1_ingv_echam4.n;;
mrso_ingv_echam4_sresa2) file="IPCCData/sresa2/mrso_A1_ingv_echam4.nc";kindname="ingv echam4 sresa2";climfield="mrso";LSMASK=IPCCData/20c3m/sftlf_A1_ingv_echam4.nc;;
mrso_inmcm3_0_20c3m) file="IPCCData/20c3m/mrso_A1_inmcm3_0.nc";kindname="inmcm3.0 20c3m";climfield="mrso";LSMASK=IPCCData/20c3m/sftlf_A1_inmcm3_0.nc;;
mrso_inmcm3_0_sresa2) file="IPCCData/sresa2/mrso_A1_inmcm3_0.nc";kindname="inmcm3.0 sresa2";climfield="mrso";LSMASK=IPCCData/20c3m/sftlf_A1_inmcm3_0.nc;;
mrso_ipsl_cm4_20c3m) file="IPCCData/20c3m/mrso_A1_ipsl_cm4_%%.nc";kindname="ipsl cm4 20c3m";climfield="mrso";LSMASK=IPCCData/20c3m/sftlf_A1_ipsl_cm4.nc;;
mrso_ipsl_cm4_sresa2) file="IPCCData/sresa2/mrso_A1_ipsl_cm4.nc";kindname="ipsl cm4 sresa2";climfield="mrso";LSMASK=IPCCData/20c3m/sftlf_A1_ipsl_cm4.nc;;
mrso_miroc3_2_hires_20c3m) file="IPCCData/20c3m/mrso_A1_miroc3_2_hires.nc";kindname="miroc3.2 hires 20c3m";climfield="mrso";LSMASK="IPCCData/20c3m/sftlf_A1_miroc3_2_hires.nc";;
mrso_miroc3_2_medres_20c3m) file="IPCCData/20c3m/mrso_A1_miroc3_2_medres_%%.nc";kindname="miroc3.2 medres 20c3m";climfield="mrso";LSMASK="IPCCData/20c3m/sftlf_A1_miroc3_2_medres.nc";;
mrso_miroc3_2_medres_sresa2) file="IPCCData/sresa2/mrso_A1_miroc3_2_medres_%%.nc";kindname="miroc3.2 medres sresa2";climfield="mrso";LSMASK="IPCCData/20c3m/sftlf_A1_miroc3_2_medres.nc";;
mrso_miub_echo_g_20c3m) file="IPCCData/20c3m/mrso_A1_miub_echo_g_%%.nc";kindname="miub echo g 20c3m";climfield="mrso";LSMASK="IPCCData/20c3m/sftlf_A1_miub_echo_g.nc";;
mrso_miub_echo_g_sresa2) file="IPCCData/sresa2/mrso_A1_miub_echo_g_%%.nc";kindname="miub echo g sresa2";climfield="mrso";LSMASK="IPCCData/20c3m/sftlf_A1_miub_echo_g.nc";;
mrso_mpi_echam5_20c3m) file="IPCCData/20c3m/mrso_A1_mpi_echam5_%%.nc";kindname="mpi echam5 20c3m";climfield="mrso";LSMASK="IPCCData/20c3m/lsmask_mpi_echam5.nc";;
mrso_mpi_echam5_sresa2) file="IPCCData/sresa2/mrso_A1_mpi_echam5_%%.nc";kindname="mpi echam5 sresa2";climfield="mrso";LSMASK="IPCCData/20c3m/lsmask_mpi_echam5.nc";;
mrso_mri_cgcm2_3_2a_20c3m) file="IPCCData/20c3m/mrso_A1_mri_cgcm2_3_2a_%%.nc";kindname="mri cgcm2.3.2a 20c3m";climfield="mrso";LSMASK="IPCCData/20c3m/sftlf_A1_mri_cgcm2_3_2a.nc";;
mrso_mri_cgcm2_3_2a_sresa2) file="IPCCData/sresa2/mrso_A1_mri_cgcm2_3_2a_%%.nc";kindname="mri cgcm2.3.2a sresa2";climfield="mrso";LSMASK="IPCCData/20c3m/sftlf_A1_mri_cgcm2_3_2a.nc";;
mrso_ncar_ccsm3_0_20c3m) file="IPCCData/20c3m/mrso_A1.20C3M_%%.CCSM.lndm.1870-01_cat_1999-12.nc";kindname="ncar ccsm3.0 20c3m";climfield="mrso";LSMASK="IPCCData/20c3m/sftlf_A1.20C3M.CCSM.atmm.nc";;
mrso_ncar_ccsm3_0_sresa2) file="IPCCData/sresa2/mrso_A1_ncar_ccsm3_0_%%.nc";kindname="ncar ccsm3.0 sresa2";climfield="mrso";LSMASK="IPCCData/20c3m/sftlf_A1.20C3M.CCSM.atmm.nc";;
mrso_ncar_pcm1_20c3m) file="IPCCData/20c3m/mrso_A1.20C3M_%%.PCM1.lndm.1890-01_cat_1999-12.nc";kindname="ncar pcm1 20c3m";climfield="mrso";LSMASK="IPCCData/20c3m/sftlf_A1.20C3M.PCM1.atmm.nc";;
mrso_ncar_pcm1_sresa2) file="IPCCData/sresa2/mrso_A1.SRESA2_%%.PCM1.lndm.1890-01_cat_2099-12.nc";kindname="ncar pcm1 sresa2";climfield="mrso";LSMASK="IPCCData/20c3m/sftlf_A1.20C3M.PCM1.atmm.nc";;
mrso_ukmo_hadcm3_20c3m) file="IPCCData/20c3m/mrso_A1_ukmo_hadcm3_%%.nc";kindname="ukmo hadcm3 20c3m";climfield="mrso";LSMASK="IPCCData/20c3m/sftlf_A1_ukmo_hadcm3.nc";;
mrso_ukmo_hadcm3_sresa2) file="IPCCData/sresa2/mrso_A1_ukmo_hadcm3.nc";kindname="ukmo hadcm3 sresa2";climfield="mrso";LSMASK="IPCCData/20c3m/sftlf_A1_ukmo_hadcm3.nc";;
mrso_ukmo_hadgem1_20c3m) file="IPCCData/20c3m/mrso_A1_ukmo_hadgem1_%%.nc";kindname="ukmo hadgem1 20c3m";climfield="mrso";LSMASK="IPCCData/picntrl/sftlf_A1_ukmo_hadgem1.nc";;
mrso_ukmo_hadgem1_sresa2) file="IPCCData/sresa2/mrso_A1_ukmo_hadgem1.nc";kindname="ukmo hadgem1 sresa2";climfield="mrso";LSMASK="IPCCData/picntrl/sftlf_A1_ukmo_hadgem1.nc";;

tos_cmip3_all_sresa1b) file="IPCCData/sresa1b/tos_cmip3_%%_144.nc";kindname="CMIP3 20c3m/sresa1b all members";climfield="tos";LSMASK=IPCCData/sresa1b/lsmask_cmip3_144.nc;;
tos_cmip3_ave_sresa1b) file="IPCCData/sresa1b/tos_cmip3_ave_%%_144.nc";kindname="CMIP3 20c3m/sresa1b all models";climfield="tos";LSMASK=IPCCData/sresa1b/lsmask_cmip3_144.nc;;
tos_cmip3_ave_mean_sresa1b) file="IPCCData/sresa1b/tos_cmip3_ave_mean_144.nc";kindname="CMIP3 20c3m/sresa1b multi-model mean";climfield="tos";LSMASK=IPCCData/sresa1b/lsmask_cmip3_144.nc;;
tos_cmip3_volcano_all_sresa1b) file="IPCCData/sresa1b/tos_cmip3_volcano_%%_144.nc";kindname="CMIP3 20c3m/sresa1b volcano members";climfield="tos";LSMASK=IPCCData/sresa1b/lsmask_cmip3_144.nc;;
tos_cmip3_volcano_ave_sresa1b) file="IPCCData/sresa1b/tos_cmip3_volcano_ave_%%_144.nc";kindname="CMIP3 20c3m/sresa1b volcano models";climfield="tos";LSMASK=IPCCData/sresa1b/lsmask_cmip3_144.nc;;
tos_cmip3_volcano_ave_mean_sresa1b) file="IPCCData/sresa1b/tos_cmip3_volcano_ave_mean_144.nc";kindname="CMIP3 20c3m/sresa1b volcano mean";climfield="tos";LSMASK=IPCCData/sresa1b/lsmask_cmip3_144.nc;;
tos_cmip3_novolcano_all_sresa1b) file="IPCCData/sresa1b/tos_cmip3_novolcano_%%_144.nc";kindname="CMIP3 20c3m/sresa1b novolcano members";climfield="tos";LSMASK=IPCCData/sresa1b/lsmask_cmip3_144.nc;;
tos_cmip3_novolcano_ave_sresa1b) file="IPCCData/sresa1b/tos_cmip3_novolcano_ave_%%_144.nc";kindname="CMIP3 20c3m/sresa1b novolcano models";climfield="tos";LSMASK=IPCCData/sresa1b/lsmask_cmip3_144.nc;;
tos_cmip3_novolcano_ave_mean_sresa1b) file="IPCCData/sresa1b/tos_cmip3_novolcano_ave_mean_144.nc";kindname="CMIP3 20c3m/sresa1b novolcano mean";climfield="tos";LSMASK=IPCCData/sresa1b/lsmask_cmip3_144.nc;;
tos_bccr_bcm2_0_20c3m) file="IPCCData/20c3m/tos_O1b_bccr_bcm2_0.nc";kindname="bccr bcm2.0 20c3m";climfield="tos";;
tos_bccr_bcm2_0_sresa1b) file="IPCCData/sresa1b/tos_O1b_bccr_bcm2_0.nc";kindname="bccr bcm2.0 sresa1b";climfield="tos";;
tos_cccma_cgcm3_1_20c3m) file="IPCCData/20c3m/tos_o1_20c3m_%%_cgcm3.1_t47_1850_2000.nc";kindname="cccma cgcm3.1 20c3m";climfield="tos";;
tos_cccma_cgcm3_1_sresa1b) file="IPCCData/sresa1b/tos_o1_sresa1b_%%_cgcm3.1_t47.nc";kindname="cccma cgcm3.1 sresa1b";climfield="tos";;
tos_cccma_cgcm3_1_sresa2) file="IPCCData/sresa2/tos_o1_sresa2_1_cgcm3.1_t47_2001_2100.nc";kindname="cccma cgcm3.1 sresa2";climfield="tos";;
tos_cccma_cgcm3_1_1pctto2x) file="IPCCData/1pctto2x/sst_1pctto2x_1_cgcm3.1_t47_1850_2069.nc";kindname="cccma cgcm3.1 1pctto2x";climfield="sst";;
tos_cccma_cgcm3_1_t63_20c3m) file="IPCCData/20c3m/tos_o1_20c3m_1_cgcm3.1_t63_1850_2000.nc";kindname="cccma cgcm3.1 t63 20c3m";climfield="tos";;
tos_cccma_cgcm3_1_t63_sresa1b) file="IPCCData/sresa1b/tos_o1_sresa1b_1_cgcm3.1_t63_1850_2300.nc";kindname="cccma cgcm3.1 t63 sresa1b";climfield="tos";;
tos_cnrm_cm3_20c3m) file="IPCCData/20c3m/tos_O1_cnrm_cm3.nc";kindname="cnrm cm3 20c3m";climfield="tos";;
tos_cnrm_cm3_sresa1b) file="IPCCData/sresa1b/tos_O1_cnrm_cm3.nc";kindname="cnrm cm3 sresa1b";climfield="tos";;
tos_cnrm_cm3_sresa2) file="IPCCData/sresa2/tos_O1_cnrm_cm3.nc";kindname="cnrm cm3 sresa2";climfield="tos";;
tos_csiro_mk3_0_20c3m) file="IPCCData/20c3m/tos_O1_csiro_mk3_0.nc";kindname="csiro mk3.0 20c3m";climfield="tos";;
tos_csiro_mk3_0_sresa1b) file="IPCCData/sresa1b/tos_O1_csiro_mk3_0.nc";kindname="csiro mk3.0 sresa1b";climfield="tos";;
tos_csiro_mk3_0_sresa2) file="IPCCData/sresa2/tos_O1_csiro_mk3_0.nc";kindname="csiro mk3.0 sresa2";climfield="tos";;
tos_csiro_mk3_5_20c3m) file="IPCCData/20c3m/tos_O1_csiro_mk3_5_%%.nc";kindname="csiro mk3.5 20c3m";climfield="tos";;
tos_csiro_mk3_5_sresa1b) file="IPCCData/sresa1b/tos_O1_csiro_mk3_5.nc";kindname="csiro mk3.5 sresa1b";climfield="tos";;
tos_gfdl_cm2_0_20c3m) file="IPCCData/20c3m/tos_O1_gfdl_cm2_0_%%.nc";kindname="gfdl 2.0 20c3m";climfield="tos";;
sst_gfdl_cm2_0_20c3m) file="IPCCData/20c3m/sst_gfdl_cm2_0_%%.186101-200012.nc";kindname="gfdl 2.0 20c3m";climfield="sst";;
tos_gfdl_cm2_0_sresa1b) file="IPCCData/sresa1b/tos_O1_gfdl_cm2_0.nc";kindname="gfdl 2.0 sresa1b";climfield="tos";;
tos_gfdl_cm2_0_sresa2) file="IPCCData/sresa2/tos_O1_gfdl_cm2_0.200101-210012.nc";kindname="gfdl 2.0 sresa2";climfield="tos";;
sst_gfdl_cm2_0_sresa2) file="IPCCData/sresa2/sst_gfdl_cm2_0.200101-210012.nc";kindname="gfdl 2.0 sresa2";climfield="sst";;
tos_gfdl_cm2_1_20c3m) file="IPCCData/20c3m/tos_O1_gfdl_cm2_1_%%.186101-200012.nc";kindname="gfdl 2.1 20c3m";climfield="tos";;
sst_gfdl_cm2_1_20c3m) file="IPCCData/20c3m/sst_gfdl_cm2_1_%%.186101-200012.nc";kindname="gfdl 2.1 20c3m";climfield="sst";LSMASK="IPCCData/20c3m/sftlf_A1_gfdl_cm2_1.nc";;
tos_gfdl_cm2_1_sresa1b) file="IPCCData/sresa1b/tos_O1_gfdl_cm2_1.nc";kindname="gfdl 2.1 sresa1b";climfield="tos";;
sst_gfdl_cm2_1_sresa2) file="IPCCData/sresa2/sst_gfdl_cm2_1.200101-210012.nc";kindname="gfdl 2.1 sresa2";climfield="sst";LSMASK="IPCCData/20c3m/sftlf_A1_gfdl_cm2_1.nc";;
tos_giss_aom_20c3m) file="IPCCData/20c3m/tos_O1_giss_aom_%%.nc";kindname="giss aom 20c3m";climfield="tos";;
tos_giss_aom_sresa1b) file="IPCCData/sresa1b/tos_O1_giss_aom_%%.nc";kindname="giss aom sresa1b";climfield="tos";;
tos_giss_model_e_h_20c3m) file="IPCCData/20c3m/tos_O1.GISS3.20C3M.%%.nc";kindname="giss eh 20c3m";climfield="tos";;
tos_giss_model_e_h_sresa1b) file="IPCCData/sresa1b/tos_O1.GISS3.SRESA1B.%%.nc";kindname="giss eh sresa1b";climfield="tos";;
tos_giss_model_e_h_1pctto2x) file="IPCCData/1pctto2x/tos_O1.GISS3.1pctto2x.nc";kindname="giss eh 1pctto2x";climfield="tos";;
tos_giss_model_e_r_20c3m) file="IPCCData/20c3m/tos_O1.GISS1.20C3M.%%.nc";kindname="giss er 20c3m";climfield="tos";;
tos_giss_model_e_r_sresa1b) file="IPCCData/sresa1b/tos_O1.GISS1.SRESA1B.%%.nc";kindname="giss er sresa1b";climfield="tos";;
tos_giss_model_e_r_sresa2) file="IPCCData/sresa2/tos_O1.GISS1.SRESA2.nc";kindname="giss er sresa2";climfield="tos";;
tos_iap_fgoals1_0_g_20c3m) file="IPCCData/20c3m/tos_O1_iap_fgoals1_0_g_%%.nc";kindname="iap fgoals10g 20c3m";climfield="tos";;
tos_iap_fgoals1_0_g_sresa1b) file="IPCCData/sresa1b/tos_O1_iap_fgoals1_0_g_%%.nc";kindname="iap fgoals10g sresa1b";climfield="tos";;
tos_ingv_echam4_20c3m) file="IPCCData/20c3m/tos_O1_ingv_echam4.nc";kindname="ingv echam4 20c3m";climfield="tos";;
tos_ingv_echam4_sresa1b) file="IPCCData/sresa1b/tos_O1_ingv_echam4.nc";kindname="ingv echam4 sresa1b";climfield="tos";;
tos_inmcm3_0_20c3m) file="IPCCData/20c3m/tos_O1_inmcm3_0.nc";kindname="inmcm3.0 20c3m";climfield="tos";;
tos_inmcm3_0_sresa1b) file="IPCCData/sresa1b/tos_O1_inmcm3_0.nc";kindname="inmcm3.0 sresa1b";climfield="tos";;
tos_inmcm3_0_sresa2) file="IPCCData/sresa2/tos_O1_inmcm3_0.nc";kindname="inmcm3.0 sresa2";climfield="tos";;
tos_ipsl_cm4_20c3m) file="IPCCData/20c3m/tos_O1_ipsl_cm4_1860-2000.nc";kindname="ipsl cm4 20c3m";climfield="tos";;
tos_ipsl_cm4_sresa1b) file="IPCCData/sresa1b/tos_O1_ipsl_cm4.nc";kindname="ipsl cm4 sresa1b";climfield="tos";;
tos_ipsl_cm4_sresa2) file="IPCCData/sresa2/tos_O1_ipsl_cm4.nc";kindname="ipsl cm4 sresa2";climfield="tos";;
tos_miroc3_2_hires_20c3m) file="IPCCData/20c3m/tos_O1_miroc3_2_hires.nc";kindname="miroc 3.2 hi 20c3m";climfield="tos";;
tos_miroc3_2_hires_sresa1b) file="IPCCData/sresa1b/tos_O1_miroc3_2_hires.nc";kindname="miroc 3.2 hi sresa1b";climfield="tos";;
tos_miroc3_2_hires_1pctto2x) file="IPCCData/1pctto2x/tos_O1_miroc3_2_hires.nc";kindname="miroc 3.2 hi 1pctto2x";climfield="tos";;
tos_miroc3_2_medres_20c3m) file="IPCCData/20c3m/tos_O1_miroc3_2_medres_%%.nc";kindname="miroc 3.2 med 20c3m";climfield="tos";;
tos_miroc3_2_medres_sresa1b) file="IPCCData/sresa1b/tos_O1_miroc3_2_medres_%%.nc";kindname="miroc 3.2 med sresa1b";climfield="tos";;
#tos_miroc3_2_medres_sresa1b) file="IPCCData/sresa1b/tos_O1_sresa1b_00.medres.2201_2300.nc";kindname="miroc 3.2 med sresa1b";climfield="tos";;
tos_miroc3_2_medres_sresa2) file="IPCCData/sresa2/tos_O1_miroc3_2_medres_%%.nc";kindname="miroc 3.2 med sresa2";climfield="tos";;
tos_miub_echo_g_20c3m) file="IPCCData/20c3m/tos_O1_miub_echo_g_%%.nc";kindname="miub echo g 20c3m";climfield="tos";;
tos_miub_echo_g_sresa1b) file="IPCCData/sresa1b/tos_O1_miub_echo_g_%%.nc";kindname="miub echo g sresa1b";climfield="tos";;
tos_mpi_echam5_20c3m) file="IPCCData/20c3m/tos_O1_mpi_echam5_%%.nc";kindname="mpi echam5 20c3m";climfield="tos";;
sst_mpi_echam5_20c3m) file="IPCCData/20c3m/sst_mpi_echam5_%%.nc";kindname="mpi echam5 20c3m";climfield="sst";;
tos_mpi_echam5_sresa1b) file="IPCCData/sresa1b/tos_O1_mpi_echam5_%%.nc";kindname="mpi echam5 sresa1b";climfield="tos";;
sst_mpi_echam5_sresa1b) file="IPCCData/sresa1b/sst_mpi_echam5_%%.nc";kindname="mpi echam5 sresa1b";climfield="sst";;
tos_mpi_echam5_sresa2) file="IPCCData/sresa2/tos_mpi_echam5_%%.nc";kindname="mpi echam5 sresa2";climfield="tos";;
sst_mpi_echam5_sresa2) file="IPCCData/sresa2/sst_mpi_echam5_%%.nc";kindname="mpi echam5 sresa2";climfield="sst";;
sst_mpi_echam5_picntrl) file="IPCCData/picntrl/sst_mpi_echam5.nc";kindname="mpi echam5 picntrl";climfield="sst";;
sst_mpi_echam5_1pctto4x) file="IPCCData/1pctto4x/sst_mpi_echam5.nc";kindname="mpi echam5 1pctto4x";climfield="sst";;
tos_mri_cgcm2_3_2a_20c3m) file="IPCCData/20c3m/tos_O1_mri_cgcm2_3_2a_%%.nc";kindname="mri cgcm232a 20c3m";climfield="tos";;
tos_mri_cgcm2_3_2a_sresa1b) file="IPCCData/sresa1b/tos_O1_mri_cgcm2_3_2a_%%.nc";kindname="mri cgcm232a sresa1b";climfield="tos";;
tos_mri_cgcm2_3_2a_sresa2) file="IPCCData/sresa2/tos_O1_mri_cgcm2_3_2a_%%.nc";kindname="mri cgcm232a sresa2";climfield="tos";;
tos_ncar_ccsm3_0_20c3m) file="IPCCData/20c3m/tos_O1.20C3M_1.CCSM.ocnm.1870-01-01_cat_1999-12.nc";kindname="ccsm 3.0 20c3m";climfield="tos";;
sst_ncar_ccsm3_0_20c3m) file="IPCCData/20c3m/sst.20C3M_%%.CCSM.nc";kindname="ccsm 3.0 20c3m";climfield="sst";;
sst_ncar_ccsm3_0_sresa2) file="IPCCData/sresa2/sst.SRESA2_%%.CCSM.nc";kindname="ccsm 3.0 sresa2";climfield="sst";;
tos_ncar_pcm1_20c3m) file="IPCCData/20c3m/tos_O1.20C3M_%%.PCM1.atmm.1890-01_cat_1999-12.nc";kindname="pcm1 20c3m";climfield="tos";;
tos_ncar_pcm1_sresa1b) file="IPCCData/sresa1b/tos_O1.SRESA1B_%%.PCM1.ocnm.2000-01_cat_2199-12.nc";kindname="pcm1 sresa1b";climfield="tos";;
tos_ncar_pcm1_sresa2) file="IPCCData/sresa2/tos_O1.SRESA2_1.PCM1.atmm.2000-01_cat_2099-12.nc";kindname="pcm1 sresa2";climfield="tos";;
tos_ukmo_hadcm3_20c3m) file="IPCCData/20c3m/tos_O1_ukmo_hadcm3_%%.nc";kindname="hadcm3 20c3m";climfield="tos";;
tos_ukmo_hadcm3_sresa1b) file="IPCCData/sresa1b/tos_O1_ukmo_hadcm3.nc";kindname="hadcm3 sresa1b";climfield="tos";;
tos_ukmo_hadcm3_sresa2) file="IPCCData/sresa2/tos_O1_ukmo_hadcm3.nc";kindname="hadcm3 sresa2";climfield="tos";;
tos_ukmo_hadgem1_picntrl) file="IPCCData/picntrl/tos_O1_ukmo_hadgem1.nc";kindname="hadgem1 picntrl";climfield="tos";;
tos_ukmo_hadgem1_20c3m) file="IPCCData/20c3m/tos_O1_ukmo_hadgem1_%%.nc";kindname="hadgem1 20c3m";climfield="tos";;
tos_ukmo_hadgem1_1pctto2x) file="IPCCData/1pctto2x/tos_O1_ukmo_hadgem1.nc";kindname="hadgem1 1pctto2x";climfield="tos";;
tos_ukmo_hadgem1_sresa1b) file="IPCCData/sresa1b/tos_O1_ukmo_hadgem1.nc";kindname="hadgem1 sresa1b";climfield="tos";;
tos_ukmo_hadgem1_sresa2) file="IPCCData/sresa2/tos_O1_ukmo_hadgem1.nc";kindname="hadgem1 sresa2";climfield="tos";;

zos_cccma_cgcm3_1_20c3m) file="IPCCData/20c3m/sst_20c3m_1_cgcm3.1_t47_1850_2000.nc";kindname="cccma cgcm3.1 20c3m";climfield="sst";;
zos_cccma_cgcm3_1_1pctto2x) file="IPCCData/1pctto2x/sst_1pctto2x_1_cgcm3.1_t47_1850_2069.nc";kindname="cccma cgcm3.1 1pctto2x";climfield="sst";;
zos_cnrm_cm3_20c3m) file="IPCCData/20c3m/zos_O1_cnrm_cm3.nc";kindname="cnrm cm3 20c3m";climfield="zos";;
zos_cnrm_cm3_sresa2) file="IPCCData/sresa2/zos_O1_cnrm_cm3.nc";kindname="cnrm cm3 sresa2";climfield="zos";;
zos_csiro_mk3_0_20c3m) file="IPCCData/20c3m/zos_O1_csiro_mk3_0.nc";kindname="csiro mk3.0 20c3m";climfield="zos";;
zos_gfdl_cm2_0_20c3m) file="IPCCData/20c3m/zos_O1_gfdl_cm2_0_%%.186101-200012.nc";kindname="gfdl 2.0 20c3m";climfield="zos";;
zos_gfdl_cm2_0_sresa2) file="IPCCData/sresa2/zos_O1_gfdl_cm2_0.200101-210012.nc";kindname="gfdl 2.0 sresa2";climfield="zos";;
zos_giss_aom_20c3m) file="IPCCData/20c3m/zos_O1_giss_aom_%%.nc";kindname="giss aom 20c3m";climfield="zos";;
zos_giss_model_e_h_20c3m) file="IPCCData/20c3m/zos_O1.GISS3.20C3M.%%.nc";kindname="giss eh 20c3m";climfield="zos";;
zos_giss_model_e_r_20c3m) file="IPCCData/20c3m/zos_O1.GISS1.20C3M.%%.nc";kindname="giss er 20c3m";climfield="zos";;
zos_giss_model_e_r_sresa2) file="IPCCData/sresa2/zos_O1.GISS1.SRESA2.nc";kindname="giss er sresa2";climfield="zos";;
zos_iap_fgoals1_0_g_20c3m) file="IPCCData/20c3m/zos_O1_iap_fgoals1_0_g_%%.nc";kindname="iap fgoals10g 20c3m";climfield="zos";;
zos_inmcm3_0_20c3m) file="IPCCData/20c3m/zos_O1_inmcm3_0.nc";kindname="inmcm3.0 20c3m";climfield="zos";;
zos_inmcm3_0_sresa2) file="IPCCData/sresa2/zos_O1_inmcm3_0.nc";kindname="inmcm3.0 sresa2";climfield="zos";;
zos_ipsl_cm4_20c3m) file="IPCCData/20c3m/zos_O1_ipsl_cm4_1860-2000.nc";kindname="ipsl cm4 20c3m";climfield="zos";;
zos_ipsl_cm4_sresa2) file="IPCCData/sresa2/zos_O1_ipsl_cm4_2000-2100.nc";kindname="ipsl cm4 sresa2";climfield="zos";;
zos_miroc3_2_hires_20c3m) file="IPCCData/20c3m/zos_O1_miroc3_2_hires.nc";kindname="miroc 3.2 hi 20c3m";climfield="zos";;
zos_miroc3_2_hires_1pctto2x) file="IPCCData/1pctto2x/zos_O1_miroc3_2_hires.nc";kindname="miroc 3.2 hi 1pctto2x";climfield="zos";;
zos_miroc3_2_medres_20c3m) file="IPCCData/20c3m/zos_O1_miroc3_2_medres_%%.nc";kindname="miroc 3.2 med 20c3m";climfield="zos";;
zos_miroc3_2_medres_sresa2) file="IPCCData/sresa2/zos_O1_miroc3_2_medres_%%.nc";kindname="miroc 3.2 med sresa2";climfield="zos";;
zos_miroc3_2_medres_sresa1b) file="IPCCData/sresa1b/zos_O1_miroc3_2_medres_%%.nc";kindname="miroc 3.2 med sresa1b";climfield="zos";;
zos_mpi_echam5_sresa1b) file="IPCCData/sresa1b/zos_O1_mpi_echam5_%%.nc";kindname="mpi echam5 sresa1b";climfield="zos";;
zos_mri_cgcm2_3_2a_20c3m) file="IPCCData/20c3m/zos_O1_mri_cgcm2_3_2a_%%.nc";kindname="mri cgcm232a 20c3m";climfield="zos";;
zos_mri_cgcm2_3_2a_sresa2) file="IPCCData/sresa2/zos_O1_mri_cgcm2_3_2a_%%.nc";kindname="mri cgcm232a sresa2";climfield="zos";;
zos_mri_cgcm2_3_2a_sresa1b) file="IPCCData/sresa1b/zos_O1_mri_cgcm2_3_2a_%%.nc";kindname="mri cgcm232a sresa1b";climfield="zos";;
zos_ncar_ccsm3_0_20c3m) file="IPCCData/20c3m/zos_O1.20C3M_%%.CCSM.ocnm.1870-01_cat_1999-12.nc";kindname="ccsm 3.0 20c3m";climfield="zos";;
zos_ncar_pcm1_20c3m) file="IPCCData/20c3m/zos_O1.20C3M_%%.PCM1.atmm.1890-01_cat_1999-12.nc";kindname="pcm1 20c3m";climfield="zos";;
zos_ncar_pcm1_sresa2) file="IPCCData/sresa2/zos_O1.SRESA2_1.PCM1.atmm.2000-01_cat_2099-12.nc";kindname="pcm1 sresa2";climfield="zos";;
zos_ukmo_hadcm3_20c3m) file="IPCCData/20c3m/zos_O1_ukmo_hadcm3_%%.nc";kindname="hadcm3 20c3m";climfield="zos";;
zos_ukmo_hadcm3_sresa2) file="IPCCData/sresa2/zos_O1_ukmo_hadcm3.nc";kindname="hadcm3 sresa2";climfield="zos";;
zos_ukmo_hadcm3_sresa1b) file="IPCCData/sresa1b/zos_O1_ukmo_hadcm3.nc";kindname="hadcm3 sresa1b";climfield="zos";;
zos_ukmo_hadgem1_picntrl) file="IPCCData/picntrl/zos_A1_ukmo_hadgem1.nc";kindname="hadgem1 picntrl";climfield="zos";;
zos_ukmo_hadgem1_1pctto2x) file="IPCCData/1pctto2x/zos_A1_ukmo_hadgem1.nc";kindname="hadgem1 1pctto2x";climfield="zos";;
zos_ukmo_hadgem1_sresa1b) file="IPCCData/sresa1b/zos_O1_ukmo_hadgem1.nc";kindname="hadgem1 sresa1b";climfield="zos";;

z20_cccma_cgcm3_1_20c3m) file="IPCCData/20c3m/z20_thetao_O1_20c3m_1_cgcm3.1_t47_1850_2000.nc";kindname="cccma cgcm3.1 20c3m";climfield="z20";;
z20_cccma_cgcm3_1_1pctto2x) file="IPCCData/1pctto2x/sst_1pctto2x_1_cgcm3.1_t47_1850_2069.nc";kindname="cccma cgcm3.1 1pctto2x";climfield="sst";;
z20_cnrm_cm3_20c3m) file="IPCCData/20c3m/z20_O1_cnrm_cm3.nc";kindname="cnrm cm3 20c3m";climfield="z20";;
z20_cnrm_cm3_sresa2) file="IPCCData/sresa2/z20_O1_cnrm_cm3.nc";kindname="cnrm cm3 sresa2";climfield="z20";;
z20_csiro_mk3_0_20c3m) file="IPCCData/20c3m/z20_O1_csiro_mk3_0.nc";kindname="csiro mk3.0 20c3m";climfield="z20";;
z20_gfdl_cm2_0_20c3m) file="IPCCData/20c3m/z20_O1_gfdl_cm2_0_%%.186101-200012.nc";kindname="gfdl 2.0 20c3m";climfield="z20";;
z24_gfdl_cm2_0_sresa1b) file="IPCCData/sresa1b/z24_O1_gfdl_cm2_0.220101-230012.nc";kindname="gfdl 2.0 sresa1b";climfield="z24";;
z20_gfdl_cm2_0_sresa2) file="IPCCData/sresa2/z20_O1_gfdl_cm2_0.200101-210012.nc";kindname="gfdl 2.0 sresa2";climfield="z20";;
z20_gfdl_cm2_1_20c3m) file="IPCCData/20c3m/z20_O1_gfdl_cm2_1_%%.186101-200012.nc";kindname="gfdl 2.1 20c3m";climfield="z20";;
z24_gfdl_cm2_1_sresa1b) file="IPCCData/sresa1b/z24_O1_gfdl_cm2_1.220101-230012.nc";kindname="gfdl 2.1 sresa1b";climfield="z24";;
z20_giss_aom_20c3m) file="IPCCData/20c3m/z20_O1_giss_aom_%%.nc";kindname="giss aom 20c3m";climfield="z20";;
z20_giss_model_e_h_20c3m) file="IPCCData/20c3m/z20_O1.GISS3.20C3M.%%.nc";kindname="giss eh 20c3m";climfield="z20";;
z20_giss_model_e_r_20c3m) file="IPCCData/20c3m/z20_O1.GISS1.20C3M.%%.nc";kindname="giss er 20c3m";climfield="z20";;
z20_giss_model_e_r_sresa2) file="IPCCData/sresa2/z20_O1.GISS1.SRESA2.nc";kindname="giss er sresa2";climfield="z20";;
z20_iap_fgoals1_0_g_20c3m) file="IPCCData/20c3m/z20_O1_iap_fgoals1_0_g_%%.nc";kindname="iap fgoals10g 20c3m";climfield="z20";;
z20_inmcm3_0_20c3m) file="IPCCData/20c3m/z20_O1_inmcm3_0.nc";kindname="inmcm3.0 20c3m";climfield="z20";;
z20_inmcm3_0_sresa2) file="IPCCData/sresa2/z20_O1_inmcm3_0.nc";kindname="inmcm3.0 sresa2";climfield="z20";;
z20_ipsl_cm4_20c3m) file="IPCCData/20c3m/z20_O1_ipsl_cm4_1860-2000.nc";kindname="ipsl cm4 20c3m";climfield="z20";;
z20_miroc3_2_hires_20c3m) file="IPCCData/20c3m/z20_O1_miroc3_2_hires.nc";kindname="miroc 3.2 hi 20c3m";climfield="z20";;
z20_miroc3_2_hires_1pctto2x) file="IPCCData/1pctto2x/z20_O1_miroc3_2_hires.nc";kindname="miroc 3.2 hi 1pctto2x";climfield="z20";;
z20_miroc3_2_medres_20c3m) file="IPCCData/20c3m/z20_O1_miroc3_2_medres_%%.nc";kindname="miroc 3.2 med 20c3m";climfield="z20";;
z24_miroc3_2_medres_sresa1b) file="IPCCData/sresa1b/z24_O1_miroc3_2_medres_%%.220101-230012.nc";kindname="miroc 3.2 med sresa1b";climfield="z24";;
z20_miroc3_2_medres_sresa2) file="IPCCData/sresa2/z20_O1_miroc3_2_medres_%%.nc";kindname="miroc 3.2 med sresa2";climfield="z20";;
z20_mpi_echam5_20c3m) file="IPCCData/20c3m/z20_O1_mpi_echam5_%%.nc";kindname="mpi echam5 20c3m";climfield="z20";;
z24_mpi_echam5_sresa1b) file="IPCCData/sresa1b/z24_thetao_O1_sresa1b_echam5_2200-2300.nc";kindname="mpi echam5 sresa1b";climfield="z24";;
z20_mpi_echam5_sresa2) file="IPCCData/sresa2/z20_O1_mpi_echam5_%%.nc";kindname="mpi echam5 sresa2";climfield="sst";;
z20_mri_cgcm2_3_2a_20c3m) file="IPCCData/20c3m/z20_O1_mri_cgcm2_3_2a_%%.nc";kindname="mri cgcm232a 20c3m";climfield="z20";;
z20_mri_cgcm2_3_2a_sresa2) file="IPCCData/sresa2/z20_O1_mri_cgcm2_3_2a_%%.nc";kindname="mri cgcm232a sresa2";climfield="z20";;
z20_ncar_ccsm3_0_20c3m) file="IPCCData/20c3m/z20_O1.20C3M_%%.CCSM.atmm.1870-01_cat_1999-12.nc";kindname="ccsm 3.0 20c3m";climfield="z20";;
z20_ncar_pcm1_20c3m) file="IPCCData/20c3m/z20_O1.20C3M_%%.PCM1.atmm.1890-01_cat_1999-12.nc";kindname="pcm1 20c3m";climfield="z20";;
z20_ncar_pcm1_sresa2) file="IPCCData/sresa2/z20_O1.SRESA2_1.PCM1.atmm.2000-01_cat_2099-12.nc";kindname="pcm1 sresa2";climfield="z20";;
z20_ukmo_hadcm3_20c3m) file="IPCCData/20c3m/z20_O1_ukmo_hadcm3_%%.nc";kindname="hadcm3 20c3m";climfield="z20";;
z24_ukmo_hadcm3_sresa1b) file="IPCCData/sresa1b/z24_thetao_O1_sresa1b.hadcm3.2100_to_2199.nc";kindname="hadcm3 sresa1b";climfield="z24";;
z20_ukmo_hadcm3_sresa2) file="IPCCData/sresa2/z20_O1_ukmo_hadcm3.nc";kindname="hadcm3 sresa2";climfield="z20";;
z20_ukmo_hadgem1_picntrl) file="IPCCData/picntrl/z20_O1_ukmo_hadgem1.nc";kindname="hadgem1 picntrl";climfield="z20";;
z20_ukmo_hadgem1_1pctto2x) file="IPCCData/1pctto2x/z20_O1_ukmo_hadgem1.nc";kindname="hadgem1 1pctto2x";climfield="z20";;

z500_cccma_cgcm3_1_20c3m) file="IPCCData/20c3m/z500_20c3m_%%_cgcm3.1_t47_1850-2000.nc";kindname="cccma cgcm3.1 20c3m";climfield="z500";LSMASK=IPCCData/20c3m/sftlf_a1_20c3m_cgcm3.1_t47.nc;;
z500_cccma_cgcm3_1_sresa1b) file="IPCCData/sresa1b/z500_sresa1b_%%_cgcm3.1_t47_1850-2000.nc";kindname="cccma cgcm3.1 sresa1b";climfield="z500";LSMASK=IPCCData/20c3m/sftlf_a1_20c3m_cgcm3.1_t47.nc;;
z500_cnrm_cm3_20c3m) file="IPCCData/20c3m/z500_cnrm_cm3.nc";kindname="cnrm cm3 20c3m";climfield="z500";LSMASK=IPCCData/20c3m/sftlf_A1_cnrm_cm3.nc;;
z500_cnrm_cm3_sresa1b) file="IPCCData/sresa1b/z500_cnrm_cm3.nc";kindname="cnrm cm3 sresa1b";climfield="z500";LSMASK=IPCCData/20c3m/sftlf_A1_cnrm_cm3.nc;;
z500_csiro_mk3_0_20c3m) file="IPCCData/20c3m/z500_csiro_mk3_0_%%.nc";kindname="csiro_mk3_0 20c3m";climfield="z500";LSMASK=IPCCData/20c3m/sftlf_A1_csiro_mk3_0.nc;;
z500_csiro_mk3_0_sresa1b) file="IPCCData/sresa1b/z500_csiro_mk3_0.nc";kindname="csiro_mk3_0 sresa1b";climfield="z500";LSMASK=IPCCData/20c3m/sftlf_A1_csiro_mk3_0.nc;;
z500_gfdl_cm2_0_20c3m) file="IPCCData/20c3m/z500_gfdl_cm2_0_%%.nc";kindname="gfdl 2.0 20c3m";climfield="z500";LSMASK="IPCCData/20c3m/sftlf_A1_gfdl_cm2_0.nc";;
z500_gfdl_cm2_0_sresa1b) file="IPCCData/sresa1b/z500_gfdl_cm2_0.nc";kindname="gfdl 2.0 sresa1b";climfield="z500";LSMASK="IPCCData/20c3m/sftlf_A1_gfdl_cm2_0.nc";;
z500_gfdl_cm2_1_20c3m) file="IPCCData/20c3m/z500_gfdl_cm2_1_%%.nc";kindname="gfdl 2.1 20c3m";climfield="z500";LSMASK="IPCCData/20c3m/sftlf_A1_gfdl_cm2_1.nc";;
z500_gfdl_cm2_1_sresa1b) file="IPCCData/sresa1b/z500_gfdl_cm2_1.nc";kindname="gfdl 2.1 sresa1b";climfield="z500";LSMASK="IPCCData/20c3m/sftlf_A1_gfdl_cm2_1.nc";;
z500_ipsl_cm4_20c3m) file="IPCCData/20c3m/z500_ipsl_cm4_1860-2000.nc";kindname="ipsl cm4 20c3m";climfield="z500";LSMASK=IPCCData/20c3m/sftlf_A1_ipsl_cm4.nc;;
z500_ipsl_cm4_sresa1b) file="IPCCData/sresa1b/z500_ipsl_cm4.nc";kindname="ipsl cm4 sresa1b";climfield="z500";LSMASK=IPCCData/20c3m/sftlf_A1_ipsl_cm4.nc;;
z500_miroc3_2_medres_20c3m) file="IPCCData/20c3m/z500_miroc3_2_medres_%%.nc";kindname="miroc 3.2 med 20c3m";climfield="z500";LSMASK="IPCCData/20c3m/sftlf_A1_miroc3_2_medres.nc";;
z500_miroc3_2_medres_sresa1b) file="IPCCData/sresa1b/z500_miroc3_2_medres_%%.nc";kindname="miroc 3.2 med sresa1b";climfield="z500";LSMASK="IPCCData/20c3m/sftlf_A1_miroc3_2_medres.nc";;
z500_mpi_echam5_20c3m) file="IPCCData/20c3m/z500_mpi_echam5_%%.nc";kindname="mpi echam5 20c3m";climfield="z500";LSMASK="IPCCData/20c3m/lsmask_mpi_echam5.nc";;
z500_mpi_echam5_sresa1b) file="IPCCData/sresa1b/z500_mpi_echam5_%%.nc";kindname="mpi echam5 sresa1b";climfield="z500";LSMASK="IPCCData/20c3m/lsmask_mpi_echam5.nc";;
z500_mpi_echam5_sresa2) file="IPCCData/sresa2/z500_mpi_echam5_%%.nc";kindname="mpi echam5 sresa2";climfield="z500";LSMASK="IPCCData/20c3m/lsmask_mpi_echam5.nc";;
z500_mpi_echam5_1pctto2x) file="IPCCData/1pctto2x/z500_mpi_echam5_%%.nc";kindname="mpi echam5 1pctto2x";climfield="z500";LSMASK="IPCCData/20c3m/lsmask_mpi_echam5.nc";;
z500_mpi_echam5_1pctto4x) file="IPCCData/1pctto4x/z500_mpi_echam5.nc";kindname="mpi echam5 1pctto4x";climfield="z500";LSMASK="IPCCData/20c3m/lsmask_mpi_echam5.nc";;
z500_mri_cgcm2_3_2a_20c3m) file="IPCCData/20c3m/z500_mri_cgcm2_3_2a_%%.nc";kindname="mri cgcm232a 20c3m";climfield="z500";LSMASK="IPCCData/20c3m/sftlf_A1_mri_cgcm2_3_2a.nc";;
z500_mri_cgcm2_3_2a_sresa1b) file="IPCCData/sresa1b/z500_mri_cgcm2_3_2a_%%.nc";kindname="mri cgcm232a sresa1b";climfield="z500";LSMASK="IPCCData/20c3m/sftlf_A1_mri_cgcm2_3_2a.nc";;
z500_ukmo_hadgem1_20c3m) file="IPCCData/20c3m/z500_ukmo_hadgem1_%%.nc";kindname="hadgem1";climfield="z500";LSMASK="IPCCData/picntrl/sftlf_A1_ukmo_hadgem1.nc";;
z500_ukmo_hadgem1_sresa1b) file="IPCCData/sresa1b/z500_ukmo_hadgem1.nc";kindname="hadgem1";climfield="z500";LSMASK="IPCCData/picntrl/sftlf_A1_ukmo_hadgem1.nc";;
z500_ukmo_hadcm3_20c3m) file="IPCCData/20c3m/z500_ukmo_hadcm3_%%.nc";kindname="hadcm3";climfield="z500";LSMASK="IPCCData/20c3m/sftlf_A1_ukmo_hadcm3.nc";;
z500_ukmo_hadcm3_sresa1b) file="IPCCData/sresa1b/z500_ukmo_hadcm3.nc";kindname="hadcm3";climfield="z500";LSMASK="IPCCData/20c3m/sftlf_A1_ukmo_hadcm3.nc";;

t300_cccma_cgcm3_1_t63_20c3m) file="IPCCData/20c3m/t300_a1_20c3m_1_cgcm3.1_t63_1850_2000.nc";kindname="cccma cgcm3.1 t63 20c3m";climfield="t300";LSMASK=IPCCData/20c3m/sftlf_a1_20c3m_cgcm3.1_t63.nc;LSMASK=IPCCData/20c3m/sftlf_a1_20c3m_cgcm3.1_t63.nc;;
t300_cccma_cgcm3_1_t63_sresa1b) file="IPCCData/sresa1b/t300_a1_sresa1b_1_cgcm3.1_t63_2001_2300.nc";kindname="cccma cgcm3.1 t63 sresa1b";climfield="t300";LSMASK=IPCCData/20c3m/sftlf_a1_20c3m_cgcm3.1_t63.nc;;
t300_mpi_echam5_20c3m) file="IPCCData/20c3m/t300_mpi_echam5_%%.nc";kindname="mpi echam5 20c3m";climfield="t300";LSMASK="IPCCData/20c3m/lsmask_mpi_echam5.nc";;
t300_mpi_echam5_sresa1b) file="IPCCData/sresa1b/t300_mpi_echam5_%%.nc";kindname="mpi echam5 sresa1b";climfield="t300";LSMASK="IPCCData/20c3m/lsmask_mpi_echam5.nc";;

t500_cccma_cgcm3_1_t63_20c3m) file="IPCCData/20c3m/t500_a1_20c3m_1_cgcm3.1_t63_1850_2000.nc";kindname="cccma cgcm3.1 t63 20c3m";climfield="t500";LSMASK=IPCCData/20c3m/sftlf_a1_20c3m_cgcm3.1_t63.nc;;
t500_cccma_cgcm3_1_t63_sresa1b) file="IPCCData/sresa1b/t500_a1_sresa1b_1_cgcm3.1_t63_2001_2300.nc";kindname="cccma cgcm3.1 t63 sresa1b";climfield="t500";LSMASK=IPCCData/20c3m/sftlf_a1_20c3m_cgcm3.1_t63.nc;;
t500_mpi_echam5_20c3m) file="IPCCData/20c3m/t500_mpi_echam5_%%.nc";kindname="mpi echam5 20c3m";climfield="t500";LSMASK="IPCCData/20c3m/lsmask_mpi_echam5.nc";;
t500_mpi_echam5_sresa1b) file="IPCCData/sresa1b/t500_mpi_echam5_%%.nc";kindname="mpi echam5 sresa1b";climfield="t500";LSMASK="IPCCData/20c3m/lsmask_mpi_echam5.nc";;

t700_cccma_cgcm3_1_t63_20c3m) file="IPCCData/20c3m/t700_a1_20c3m_1_cgcm3.1_t63_1850_2000.nc";kindname="cccma cgcm3.1 t63 20c3m";climfield="t700";LSMASK=IPCCData/20c3m/sftlf_a1_20c3m_cgcm3.1_t63.nc;;
t700_cccma_cgcm3_1_t63_sresa1b) file="IPCCData/sresa1b/t700_a1_sresa1b_1_cgcm3.1_t63_2001_2300.nc";kindname="cccma cgcm3.1 t63 sresa1b";climfield="t700";LSMASK=IPCCData/20c3m/sftlf_a1_20c3m_cgcm3.1_t63.nc;;
t700_mpi_echam5_20c3m) file="IPCCData/20c3m/t700_mpi_echam5_%%.nc";kindname="mpi echam5 20c3m";climfield="t700";LSMASK="IPCCData/20c3m/lsmask_mpi_echam5.nc";;
t700_mpi_echam5_sresa1b) file="IPCCData/sresa1b/t700_mpi_echam5_%%.nc";kindname="mpi echam5 sresa1b";climfield="t700";LSMASK="IPCCData/20c3m/lsmask_mpi_echam5.nc";;

t850_cccma_cgcm3_1_t63_20c3m) file="IPCCData/20c3m/t850_a1_20c3m_1_cgcm3.1_t63_1850_2000.nc";kindname="cccma cgcm3.1 t63 20c3m";climfield="t850";LSMASK=IPCCData/20c3m/sftlf_a1_20c3m_cgcm3.1_t63.nc;;
t850_cccma_cgcm3_1_t63_sresa1b) file="IPCCData/sresa1b/t850_a1_sresa1b_1_cgcm3.1_t63_2001_2300.nc";kindname="cccma cgcm3.1 t63 sresa1b";climfield="t850";LSMASK=IPCCData/20c3m/sftlf_a1_20c3m_cgcm3.1_t63.nc;;
t850_mpi_echam5_20c3m) file="IPCCData/20c3m/t850_mpi_echam5_%%.nc";kindname="mpi echam5 20c3m";climfield="t850";LSMASK="IPCCData/20c3m/lsmask_mpi_echam5.nc";;
t850_mpi_echam5_sresa1b) file="IPCCData/sresa1b/t850_mpi_echam5_%%.nc";kindname="mpi echam5 sresa1b";climfield="t850";LSMASK="IPCCData/20c3m/lsmask_mpi_echam5.nc";;

t925_cccma_cgcm3_1_t63_20c3m) file="IPCCData/20c3m/t925_a1_20c3m_1_cgcm3.1_t63_1925_2000.nc";kindname="cccma cgcm3.1 t63 20c3m";climfield="t925";LSMASK=IPCCData/20c3m/sftlf_a1_20c3m_cgcm3.1_t63.nc;;
t925_cccma_cgcm3_1_t63_sresa1b) file="IPCCData/sresa1b/t925_a1_sresa1b_1_cgcm3.1_t63_2001_2300.nc";kindname="cccma cgcm3.1 t63 sresa1b";climfield="t925";LSMASK=IPCCData/20c3m/sftlf_a1_20c3m_cgcm3.1_t63.nc;;
t925_mpi_echam5_20c3m) file="IPCCData/20c3m/t925_mpi_echam5_%%.nc";kindname="mpi echam5 20c3m";climfield="t925";LSMASK="IPCCData/20c3m/lsmask_mpi_echam5.nc";;
t925_mpi_echam5_sresa1b) file="IPCCData/sresa1b/t925_mpi_echam5_%%.nc";kindname="mpi echam5 sresa1b";climfield="t925";LSMASK="IPCCData/20c3m/lsmask_mpi_echam5.nc";;

uas_A2_mpi_echam5_20c3m) file="IPCCData/20c3m_daily/uas_A2_mpi_echam5_1961-2000.nc";kindname="mpi echam5 20c3m";climfield="uas";LSMASK="IPCCData/20c3m/lsmask_mpi_echam5.nc";NPERYEAR=366;;
vas_A2_mpi_echam5_20c3m) file="IPCCData/20c3m_daily/vas_A2_mpi_echam5_1961-2000.nc";kindname="mpi echam5 20c3m";climfield="vas";LSMASK="IPCCData/20c3m/lsmask_mpi_echam5.nc";NPERYEAR=366;;

*_miroc3_2_hires_20c3m)
    var=${FORM_field%%_miroc3_2_hires_20c3m}
    file="IPCCData/20c3m/${var}_A1_miroc3_2_hires.nc"
    kindname="miroc 3.2 hi 20c3m"
    climfield="$var"
    LSMASK="IPCCData/20c3m/sftlf_A1_miroc3_2_hires.nc";;
*_ukmo_hadcm3_20c3m)
    var=${FORM_field%%_ukmo_hadcm3_20c3m}
    file="IPCCData/20c3m/${var}_A1_ukmo_hadcm3_%%.nc"
    kindname="hadcm3 20c3m"
    climfield="$var"
    LSMASK="IPCCData/20c3m/sftlf_A1_ukmo_hadcm3.nc";;
*_ukmo_hadgem1_20c3m)
    var=${FORM_field%%_ukmo_hadgem1_20c3m}
    file="IPCCData/20c3m/${var}_A1_ukmo_hadgem1_%%.nc"
    kindname="hadgem1 20c3m"
    climfield="$var"
    LSMASK="IPCCData/picntrl/sftlf_A1_ukmo_hadgem1.nc";;

temp2_essence_a1b) file="ESSENCE/temp2_a1b_%%.nc";kindname="Essence (ECHAM5/MPI-OM)";climfield="t2m";LSMASK="ESSENCE/lsmask.ctl";;
temp2_essence_hosing) file="ESSENCE/temp2_hosing_%%.nc";kindname="Essence hosing";climfield="t2m";LSMASK="ESSENCE/lsmask.ctl";;
temp2_essence_soil) file="ESSENCE/temp2_soil_%%.nc";kindname="Essence soil";climfield="t2m";LSMASK="ESSENCE/lsmask.ctl";;
temp2_essence_climsoil) file="ESSENCE/temp2_051_1950-2100.nc";kindname="Essence soil";climfield="t2m";LSMASK="ESSENCE/lsmask.ctl";;
tslm1_essence_a1b) file="ESSENCE/tslm1_a1b_%%.nc";kindname="Essence (ECHAM5/MPI-OM)";climfield="Tsoil";LSMASK="ESSENCE/lsmask.ctl";;
tsw_essence_a1b) file="ESSENCE/tsw_a1b_%%.nc";kindname="Essence (ECHAM5/MPI-OM)";climfield="sst";LSMASK="ESSENCE/lsmask.ctl";;
tsw_essence_hosing) file="ESSENCE/tsw_hosing_%%.nc";kindname="Essence hosing";climfield="sst";LSMASK="ESSENCE/lsmask.ctl";;
precip_essence_a1b) file="ESSENCE/precip_a1b_%%.nc";kindname="Essence (ECHAM5/MPI-OM)";climfield="prcp";LSMASK="ESSENCE/lsmask.ctl";;
precip_essence_hosing) file="ESSENCE/precip_hosing_%%.nc";kindname="Essence hosing";climfield="prcp";LSMASK="ESSENCE/lsmask.ctl";;
aps_essence_a1b) file="ESSENCE/aps_a1b_%%.nc";kindname="Essence (ECHAM5/MPI-OM)";climfield="aps";LSMASK="ESSENCE/lsmask.ctl";;
slp_essence_a1b) file="ESSENCE/slp_a1b_%%.nc";kindname="Essence (ECHAM5/MPI-OM)";climfield="slp";LSMASK="ESSENCE/lsmask.ctl";;
slp_essence_hosing) file="ESSENCE/slp_hosing_%%.nc";kindname="Essence hosing";climfield="slp";LSMASK="ESSENCE/lsmask.ctl";;
ahfl_essence_a1b) file="ESSENCE/ahfl_a1b_%%.nc";kindname="Essence (ECHAM5/MPI-OM)";climfield="latent heat flux";LSMASK="ESSENCE/lsmask.ctl";;
ahfs_essence_a1b) file="ESSENCE/ahfs_a1b_%%.nc";kindname="Essence (ECHAM5/MPI-OM)";climfield="sensible heat flux";LSMASK="ESSENCE/lsmask.ctl";;
srads_essence_a1b) file="ESSENCE/srads_a1b_%%.nc";kindname="Essence (ECHAM5/MPI-OM)";climfield="Qsw";LSMASK="ESSENCE/lsmask.ctl";;
srad0_essence_a1b) file="ESSENCE/srad0_a1b_%%.nc";kindname="Essence (ECHAM5/MPI-OM)";climfield="Qsw TOA";LSMASK="ESSENCE/lsmask.ctl";;
srafs_essence_a1b) file="ESSENCE/srafs_a1b_%%.nc";kindname="Essence (ECHAM5/MPI-OM)";climfield="Qsw clear sky";LSMASK="ESSENCE/lsmask.ctl";;
trads_essence_a1b) file="ESSENCE/trads_a1b_%%.nc";kindname="Essence (ECHAM5/MPI-OM)";climfield="Qlw";LSMASK="ESSENCE/lsmask.ctl";;
trad0_essence_a1b) file="ESSENCE/trad0_a1b_%%.nc";kindname="Essence (ECHAM5/MPI-OM)";climfield="Qlw TOA";LSMASK="ESSENCE/lsmask.ctl";;
rad0_essence_a1b) file="ESSENCE/rad0_a1b_%%.nc";kindname="Essence (ECHAM5/MPI-OM)";climfield="Q TOA";LSMASK="ESSENCE/lsmask.ctl";;
ustr_essence_a1b) file="ESSENCE/ustr_a1b_%%.nc";kindname="Essence (ECHAM5/MPI-OM)";climfield="ustr";LSMASK="ESSENCE/lsmask.ctl";;
ustr_essence_hosing) file="ESSENCE/ustr_hosing_%%.nc";kindname="Essence hosing";climfield="ustr";LSMASK="ESSENCE/lsmask.ctl";;
vstr_essence_a1b) file="ESSENCE/vstr_a1b_%%.nc";kindname="Essence (ECHAM5/MPI-OM)";climfield="vstr";LSMASK="ESSENCE/lsmask.ctl";;
vstr_essence_hosing) file="ESSENCE/vstr_hosing_%%.nc";kindname="Essence hosing";climfield="vstr";LSMASK="ESSENCE/lsmask.ctl";;
z500_essence_a1b) file="ESSENCE/z500_a1b_%%.nc";kindname="Essence (ECHAM5/MPI-OM)";climfield="z500";LSMASK="ESSENCE/lsmask.ctl";;
wl_essence_a1b) file="ESSENCE/wl_a1b_%%.nc";kindname="Essence (ECHAM5/MPI-OM)";climfield="wl";LSMASK="ESSENCE/lsmask.ctl";;
ws_essence_a1b) file="ESSENCE/ws_a1b_%%.nc";kindname="Essence (ECHAM5/MPI-OM)";climfield="ws";LSMASK="ESSENCE/lsmask.ctl";;
sn_essence_a1b) file="ESSENCE/sn_a1b_%%.nc";kindname="Essence (ECHAM5/MPI-OM)";climfield="sn";LSMASK="ESSENCE/lsmask.ctl";;
snc_essence_a1b) file="ESSENCE/snc_a1b_%%.nc";kindname="Essence (ECHAM5/MPI-OM)";climfield="snc";LSMASK="ESSENCE/lsmask.ctl";;
aclcov_essence_a1b) file="ESSENCE/aclcov_a1b_%%.nc";kindname="Essence (ECHAM5/MPI-OM)";climfield="aclcov";LSMASK="ESSENCE/lsmask.ctl";;
albedo_essence_a1b) file="ESSENCE/albedo_a1b_%%.nc";kindname="Essence (ECHAM5/MPI-OM)";climfield="albedo";LSMASK="ESSENCE/lsmask.ctl";;
amld_essence_a1b) file="ESSENCE/AMLD_a1b_%%_latlon.nc";kindname="Essence (ECHAM5/MPI-OM)";climfield="amld";;
tho1_essence_a1b) file="ESSENCE/THO_a1b_%%_1_latlon.nc";kindname="Essence (ECHAM5/MPI-OM)";climfield="T(6m)";;
tho2_essence_a1b) file="ESSENCE/THO_a1b_%%_2_latlon.nc";kindname="Essence (ECHAM5/MPI-OM)";climfield="T(17m)";;
u1_essence_a1b) file="ESSENCE/UKO_a1b_%%_1_latlon.nc";kindname="Essence (ECHAM5/MPI-OM)";climfield="u(6m)";;
v1_essence_a1b) file="ESSENCE/VKE_a1b_%%_1_latlon.nc";kindname="Essence (ECHAM5/MPI-OM)";climfield="v(6m)";;
otatl_essence_a1b) file="ESSENCE/OTATL_a1b_%%_new.nc";kindname="Essence (ECHAM5/MPI-OM)";climfield="Atlantic overturning";NPERYEAR=1;;
otatl_essence_hosing) file="ESSENCE/OTATL_hosing_%%.nc";kindname="Essence hosing";climfield="Atlantic overturning";NPERYEAR=1;;
otinp_essence_a1b) file="ESSENCE/OTINP_a1b_%%_new.nc";kindname="Essence (ECHAM5/MPI-OM)";climfield="Indo-Pacific overturning";NPERYEAR=1;;
otinp_essence_hosing) file="ESSENCE/OTINP_hosing_%%_new.nc";kindname="Essence hosing";climfield="Indo-Pacific overturning";NPERYEAR=1;;
otgbl_essence_a1b) file="ESSENCE/OTGBL_a1b_%%_new.nc";kindname="Essence (ECHAM5/MPI-OM)";climfield="global overturning";NPERYEAR=1;;
otgbl_essence_hosing) file="ESSENCE/OTGBL_hosing_%%_new.nc";kindname="Essence hosing";climfield="global overturning";NPERYEAR=1;;
psiuwe_essence_a1b) file="ESSENCE/PSIUWE_a1b_%%_latlon.nc";kindname="Essence (ECHAM5/MPI-OM)";climfield="barotropic stream function";;
psiuwe_essence_hosing) file="ESSENCE/PSIUWE_hosing_%%_latlon.nc";kindname="Essence hosing";climfield="barotropic stream function";;
heat750_essence_a1b) file="ESSENCE/anom_heat750_a1b_%%.nc";kindname="Essence (ECHAM5/MPI-OM)";climfield="heat content 750m";;
heat300_essence_a1b) file="ESSENCE/heat300_a1b_%%.nc";kindname="Essence (ECHAM5/MPI-OM)";climfield="heat content 300m";;
precip_daily_essence_a1b) file="ESSENCE/precip_daily_a1b_%%.nc";kindname="Essence (ECHAM5/MPI-OM)";climfield="prcp";LSMASK="ESSENCE/lsmask.ctl";NPERYEAR=366;;
precip_decadal_essence_a1b) file="ESSENCE/precip_decadal_a1b_%%.ctl";kindname="Essence (ECHAM5/MPI-OM)";climfield="prcp";LSMASK="ESSENCE/lsmask.ctl";NPERYEAR=36;;

temp2_essence_a1b_ave) file="ESSENCE/temp2_a1b_ave.nc";kindname="Essence (ECHAM5/MPI-OM) ave";climfield="t2m";LSMASK="ESSENCE/lsmask.ctl";;
tslm1_essence_a1b_ave) file="ESSENCE/tslm1_a1b_ave.nc";kindname="Essence (ECHAM5/MPI-OM) ave";climfield="Tsoil";LSMASK="ESSENCE/lsmask.ctl";;
tsw_essence_a1b_ave) file="ESSENCE/tsw_a1b_ave.nc";kindname="Essence (ECHAM5/MPI-OM) ave";climfield="Tsoil";LSMASK="ESSENCE/lsmask.ctl";;
precip_essence_a1b_ave) file="ESSENCE/precip_a1b_ave.nc";kindname="Essence (ECHAM5/MPI-OM) ave";climfield="prcp";LSMASK="ESSENCE/lsmask.ctl";;
aps_essence_a1b_ave) file="ESSENCE/aps_a1b_ave.nc";kindname="Essence (ECHAM5/MPI-OM) ave";climfield="aps";LSMASK="ESSENCE/lsmask.ctl";;
slp_essence_a1b_ave) file="ESSENCE/slp_a1b_ave.nc";kindname="Essence (ECHAM5/MPI-OM) ave";climfield="slp";LSMASK="ESSENCE/lsmask.ctl";;
ahfl_essence_a1b_ave) file="ESSENCE/ahfl_a1b_ave.nc";kindname="Essence (ECHAM5/MPI-OM) ave";climfield="latent heat flux";LSMASK="ESSENCE/lsmask.ctl";;
ahfs_essence_a1b_ave) file="ESSENCE/ahfs_a1b_ave.nc";kindname="Essence (ECHAM5/MPI-OM) ave";climfield="sensible heat flux";LSMASK="ESSENCE/lsmask.ctl";;
srads_essence_a1b_ave) file="ESSENCE/srads_a1b_ave.nc";kindname="Essence (ECHAM5/MPI-OM) ave";climfield="Qsw";LSMASK="ESSENCE/lsmask.ctl";;
srafs_essence_a1b_ave) file="ESSENCE/srafs_a1b_ave.nc";kindname="Essence (ECHAM5/MPI-OM) ave";climfield="Qsw clear sky";LSMASK="ESSENCE/lsmask.ctl";;
trads_essence_a1b_ave) file="ESSENCE/trads_a1b_ave.nc";kindname="Essence (ECHAM5/MPI-OM) ave";climfield="Qlw";LSMASK="ESSENCE/lsmask.ctl";;
ustr_essence_a1b_ave) file="ESSENCE/ustr_a1b_ave.nc";kindname="Essence (ECHAM5/MPI-OM) ave";climfield="ustr";LSMASK="ESSENCE/lsmask.ctl";;
vstr_essence_a1b_ave) file="ESSENCE/vstr_a1b_ave.nc";kindname="Essence (ECHAM5/MPI-OM) ave";climfield="vstr";LSMASK="ESSENCE/lsmask.ctl";;
z500_essence_a1b_ave) file="ESSENCE/z500_a1b_ave.nc";kindname="Essence (ECHAM5/MPI-OM) ave";climfield="z500";LSMASK="ESSENCE/lsmask.ctl";;
wl_essence_a1b_ave) file="ESSENCE/wl_a1b_ave.nc";kindname="Essence (ECHAM5/MPI-OM) ave";climfield="wl";LSMASK="ESSENCE/lsmask.ctl";;
ws_essence_a1b_ave) file="ESSENCE/ws_a1b_ave.nc";kindname="Essence (ECHAM5/MPI-OM) ave";climfield="ws";LSMASK="ESSENCE/lsmask.ctl";;
sn_essence_a1b_ave) file="ESSENCE/sn_a1b_ave.nc";kindname="Essence (ECHAM5/MPI-OM) ave";climfield="sn";LSMASK="ESSENCE/lsmask.ctl";;
snc_essence_a1b_ave) file="ESSENCE/snc_a1b_ave.nc";kindname="Essence (ECHAM5/MPI-OM) ave";climfield="snc";LSMASK="ESSENCE/lsmask.ctl";;
aclcov_essence_a1b_ave) file="ESSENCE/aclcov_a1b_ave.nc";kindname="Essence (ECHAM5/MPI-OM) ave";climfield="aclcov";LSMASK="ESSENCE/lsmask.ctl";;
albedo_essence_a1b_ave) file="ESSENCE/albedo_a1b_ave.nc";kindname="Essence (ECHAM5/MPI-OM) ave";climfield="albedo";LSMASK="ESSENCE/lsmask.ctl";;
amld_essence_a1b_ave) file="ESSENCE/AMLD_a1b_ave_latlon.nc";kindname="Essence (ECHAM5/MPI-OM) ave";climfield="amld";;
tho1_essence_a1b_ave) file="ESSENCE/THO_a1b_ave_1_latlon.nc";kindname="Essence (ECHAM5/MPI-OM) ave";climfield="T(6m)";;
tho2_essence_a1b_ave) file="ESSENCE/THO_a1b_ave_2_latlon.nc";kindname="Essence (ECHAM5/MPI-OM) ave";climfield="T(17m)";;
u1_essence_a1b_ave) file="ESSENCE/UKO_a1b_ave_1_latlon.nc";kindname="Essence (ECHAM5/MPI-OM) ave";climfield="u(6m)";;
v1_essence_a1b_ave) file="ESSENCE/VKE_a1b_ave_1_latlon.nc";kindname="Essence (ECHAM5/MPI-OM) ave";climfield="v(6m)";;
otatl_essence_a1b_ave) file="ESSENCE/OTATL_a1b_ave_new.nc";kindname="Essence (ECHAM5/MPI-OM) ave";climfield="Atlantic overturning";NPERYEAR=1;;
otinp_essence_a1b_ave) file="ESSENCE/OTINP_a1b_ave_new.nc";kindname="Essence (ECHAM5/MPI-OM) ave";climfield="Indo-Pacific overturning";NPERYEAR=1;;
otgbl_essence_a1b_ave) file="ESSENCE/OTGBL_a1b_ave_new.nc";kindname="Essence (ECHAM5/MPI-OM) ave";climfield="global overturning";NPERYEAR=1;;
psiuwe_essence_a1b_ave) file="ESSENCE/PSIUWE_a1b_ave_latlon.nc";kindname="Essence (ECHAM5/MPI-OM) ave";climfield="barotropic stream function";;
heat750_essence_a1b_ave) file="ESSENCE/anom_heat750_a1b_ave.nc";kindname="Essence (ECHAM5/MPI-OM) ave";climfield="heat content 750m";;
u750_essence_a1b_ave) file="ESSENCE/u750_a1b_ave.nc";kindname="Essence (ECHAM5/MPI-OM) ave";climfield="u_int 750m";;
v750_essence_a1b_ave) file="ESSENCE/v750_a1b_ave.nc";kindname="Essence (ECHAM5/MPI-OM) ave";climfield="v_int 750m";;
heat300_essence_a1b_ave) file="ESSENCE/heat300_a1b_ave.nc";kindname="Essence (ECHAM5/MPI-OM) ave";climfield="heat content 300m";;
u300_essence_a1b_ave) file="ESSENCE/u300_a1b_ave.nc";kindname="Essence (ECHAM5/MPI-OM) ave";climfield="u_int 300m";;
v300_essence_a1b_ave) file="ESSENCE/v300_a1b_ave.nc";kindname="Essence (ECHAM5/MPI-OM) ave";climfield="v_int 300m";;

tas_qump) file="QUMP/qump_%%_t1.5.nc"; kindname="HadCM3 QUMP"; climfield="tas";;
pr_qump) file="QUMP/qump_%%_precip.nc"; kindname="HadCM3 QUMP"; climfield="pr";;
psl_qump) file="QUMP/qump_%%_mslp.nc"; kindname="HadCM3 QUMP"; climfield="psl";;

pr_clm_dwd_c20) file="RT2b/pr_CLM_C20.nc";kindname="DWD CLM C20";climfield="pr";NPERYEAR=366;;
pr_clm_dwd_a1b) file="RT2b/pr_CLM_A1B.nc";kindname="DWD CLM A1B";climfield="pr";NPERYEAR=366;;
tas_clm_dwd_c20) file="RT2b/tas_CLM_C20.nc";kindname="DWD CLM C20";climfield="tas";NPERYEAR=366;;
tas_clm_dwd_a1b) file="RT2b/tas_CLM_A1B.nc";kindname="DWD CLM A1B";climfield="tas";NPERYEAR=366;;

tasmax_c4irca3_a1b_hadcm3q16_20) file=RT2b/C4IRCA3_A1B_HadCM3Q16_DM_25km_1961-1990_tasmax_latlon.nc;kindname="C4I RCA3 HadCM3Q16";climfield=tasmax;NPERYEAR=360;;
tasmax_c4irca3_a1b_hadcm3q16_21) file=RT2b/C4IRCA3_A1B_HadCM3Q16_DM_25km_2021-2050_tasmax_latlon.nc;kindname="C4I RCA3 HadCM3Q16";climfield=tasmax;NPERYEAR=360;;
tasmax_c4irca3_a1b_hadcm3q16_22) file=RT2b/C4IRCA3_A1B_HadCM3Q16_DM_25km_2071-2099_tasmax_latlon.nc;kindname="C4I RCA3 HadCM3Q16";climfield=tasmax;NPERYEAR=360;;
tasmax_ethzclm_a1b_hadcm3q0_20) file=RT2b/ETHZ-CLM_SCN_HadCM3Q0_DM_25km_1961-1990_tasmax_latlon.nc;kindname="ETHZ CLM HadCM3Q0";climfield=tasmax;NPERYEAR=360;;
tasmax_ethzclm_a1b_hadcm3q0_21) file=RT2b/ETHZ-CLM_SCN_HadCM3Q0_DM_25km_2021-2050_tasmax_latlon.nc;kindname="ETHZ CLM HadCM3Q0";climfield=tasmax;NPERYEAR=360;;
tasmax_ethzclm_a1b_hadcm3q0_22) file=RT2b/ETHZ-CLM_SCN_HadCM3Q0_DM_25km_2071-2099_tasmax_latlon.nc;kindname="ETHZ CLM HadCM3Q0";climfield=tasmax;NPERYEAR=360;;
tasmax_knmiracmo2_a1b_echam5r3_20) file=RT2b/KNMI-RACMO2_A1B_ECHAM5-r3_DM_25km_1961-1990_tasmax_latlon.nc;kindname="KNMI RACMO2 ECHAM5-r3";climfield=tasmax;NPERYEAR=366;;
tasmax_knmiracmo2_a1b_echam5r3_21) file=RT2b/KNMI-RACMO2_A1B_ECHAM5-r3_DM_25km_2021-2050_tasmax_latlon.nc;kindname="KNMI RACMO2 ECHAM5-r3";climfield=tasmax;NPERYEAR=366;;
tasmax_knmiracmo2_a1b_echam5r3_22) file=RT2b/KNMI-RACMO2_A1B_ECHAM5-r3_DM_25km_2071-2100_tasmax_latlon.nc;kindname="KNMI RACMO2 ECHAM5-r3";climfield=tasmax;NPERYEAR=366;;
tasmax_mpiremo_a1b_echam5_20) file=RT2b/MPI-M-REMO_SCN_ECHAM5_DM_25km_1961-1990_tasmax_latlon.nc;kindname="MPI REMO ECHAM5";climfield=tasmax;NPERYEAR=366;;
tasmax_mpiremo_a1b_echam5_21) file=RT2b/MPI-M-REMO_SCN_ECHAM5_DM_25km_2021-2050_tasmax_latlon.nc;kindname="MPI REMO ECHAM5";climfield=tasmax;NPERYEAR=366;;
tasmax_mpiremo_a1b_acham5_22) file=RT2b/MPI-M-REMO_SCN_ECHAM5_DM_25km_2071-2100_tasmax_latlon.nc;kindname="MPI REMO ECHAM5";climfield=tasmax;NPERYEAR=366;;
tasmax_ukmohadrm3_a1b_hadcm3q0_20) file=RT2b/METO-HC_HadRM3Q0_A1B_HadCM3Q0_DM_25km_1961-1990_tasmax_latlon.nc;kindname="UKMO HadRM3Q0 HadCM3Q0";climfield=tasmax;NPERYEAR=360;;
tasmax_ukmohadrm3_a1b_hadcm3q0_21) file=RT2b/METO-HC_HadRM3Q0_A1B_HadCM3Q0_DM_25km_2021-2050_tasmax_latlon.nc;kindname="UKMO HadRM3Q0 HadCM3Q0";climfield=tasmax;NPERYEAR=360;;
tasmax_ukmohadrm3_a1b_hadcm3q0_22) file=RT2b/METO-HC_HadRM3Q0_A1B_HadCM3Q0_DM_25km_2071-2100_tasmax_latlon.nc;kindname="UKMO HadRM3Q0 HadCM3Q0";climfield=tasmax;NPERYEAR=360;;

wh_txx_india) file=Weather@Home/India/India_tmax_may_Climatology_1.nc;kindname="W@H";climfield="TXx";NPERYEAR=1;;

eurocordex_tasAdjust_day_ens_rcp45) file=CORDEX/EU-11-BC/tasAdjust_day_eu11bc_rcp45_%%.nc;kindname="EURO-CORDEX-11 BC";climfield="tas";NPERYEAR=366;;

RCP*) file="IIASAData/${FORM_field}.nc";kindname=${FORM_field%%_*}
      climfield=${FORM_field%_*}
      climfield=${climfield%_*}
      climfield=${climfield#*_};;

rcp*) file="UNHData/${FORM_field}.ctl";kindname=${FORM_field%%_*}
      climfield=${FORM_field%_*}
      climfield=${climfield#*_}
      NPERYEAR=1;;

data/*|*.info)
file=`head -1 $FORM_field`
c=`echo $file | wc -w`
if [ $c -gt 1 ]; then
    export splitfield=true
fi
export LSMASK=`fgrep 'LSMASK=' $FORM_field | tr '\`!&' ' ' | sed -e 's/^LSMASK=//'`
export NPERYEAR=`fgrep 'NPERYEAR=' $FORM_field | tr '\`!&' ' ' | sed -e 's/^NPERYEAR=//'`
kindname=`tail -2 $FORM_field | head -1`
climfield=`tail -1 $FORM_field`
# the upload routine forgets to set NPERYEAR...
if [ -z "$NPERYEAR" ]; then
    eval `./bin/getunits $file`
    mv $FORM_field /tmp/
    cat > $FORM_field <<EOF
$file
NPERYEAR=$NPERYEAR
$kindname
$climfield
EOF
fi
;;

psl_meti_20c3m)
    file=ECEARTH/MSL_2x2_mon_meti_1940-1989.nc;kindname="meti";climfield=psl;;
psl_metw_20c3m)
    file=ECEARTH/MSL_2x2_mon_metw_1940-1989.nc;kindname="metw";climfield=psl;;
psl_mesr_20c3m)
    file=ECEARTH/MSL_2x2_mesr_mon_1940-1989.nc;kindname="mesr";climfield=psl;;

*_ecearth_20c3m)
    var=`echo $FORM_field | sed -e 's/_.*//'`
    file="ECEARTH/20c3m/${var}_ecearth_%%.nc"
    kindname="EC-EARTH yr$lead"
    climfield=$var;;

*_ecearth_ave_*)
    var=`echo $FORM_field | sed -e 's/_.*//'`
    lead=`echo $FORM_field | sed -e 's/.*_//'`
    file="THOR/${var}_ecearth_${lead}_ave.nc"
    if [ $var = sst ]; then
       LSMASK=THOR/lsm_ocean.nc
    else
       LSMASK=THOR/lsm.nc
    fi
    kindname="EC-EARTH yr$lead"
    climfield=$var;;
*_ecearth_*)
    var=`echo $FORM_field | sed -e 's/_.*//'`
    lead=`echo $FORM_field | sed -e 's/.*_//'`
    file="THOR/${var}_ecearth_${lead}_%%.nc"
    if [ $var = sst ]; then
       LSMASK=THOR/lsm_ocean.nc
    else
       LSMASK=THOR/lsm.nc
    fi
    kindname="EC-EARTH yr$lead"
    climfield=$var;;
*_ecearth24*)
    var=${FORM_field%%_*}
    lead=${FORM_field##*_}
    model=${FORM_field%_*}
    model=${model#*_}
    file="COMBINE/${var}_${model}_${lead}_%%.nc"
    if [ $var = sst ]; then
       LSMASK=COMBINE/lsm_ocean.nc
    else
       LSMASK=COMBINE/landsea1.25.nc
    fi
    kindname="EC-EARTH2.4${model#ecearth24} yr$lead"
    climfield=$var;;

*_ensdec_*) # eg "tas_ifs33r1_ensdec_1.nc"
    var=`echo $FORM_field | sed -e 's/_.*//'`
    model=`echo $FORM_field | sed -e 's/[^_]*_//' -e 's/_.*//'`
    lead=`echo $FORM_field | sed -e 's/.*_//'`
    file="ENSEMBLES_dec/${var}_${model}_%%_${lead}.nc"
    LSMASK=ENSEMBLES_dec/lsm.nc
    kindname="$model yr$lead"
    climfield=$var;;
*_avedec_*) # eg "tas_ifs33r1_avedec_1.nc"
    var=`echo $FORM_field | sed -e 's/_.*//'`
    model=`echo $FORM_field | sed -e 's/[^_]*_//' -e 's/_.*//'`
    lead=`echo $FORM_field | sed -e 's/.*_//'`
    file="ENSEMBLES_dec/${var}_${model}_ave_${lead}.nc"
    LSMASK=ENSEMBLES_dec/lsm.nc
    kindname="$model yr$lead"
    climfield=$var;;

pr_futureweather_gulfcoast)
    file=KNMI14Data/Pgulf/pr_Aday_ECEARTH23_FutureWeather_????0101-????1231_%%%_-97.5--85E_27.5-31N_su.nc
    kindname="FutureWeather"
    climfield="precipitation"
    flipcolor=11
    NPERYEAR=366
    LSMASK=KNMI14Data/Pgulf/lsmask_ECEARTH23_FutureWeather_-97.5--85E_27.5-31N.nc
    map='set lon -100 -82.5
set lat 27 31.5'
    export splitfield=true;;

pr_flor_kenya_preindustrial)
    file=PrincetonData/PIctl_CMIP6volc.precip_ce_mo.nc;kindname="FLOR pre-industrial";climfield="precipitation";flipcolor=11
    map='set lon 33 42
set lat -5 5';;
pr_flor_kenya_2000)
    file=PrincetonData/Control_2000.precip_ce_mo.nc;kindname="FLOR 2000";climfield="precipitation";flipcolor=11
    map='set lon 33 42
set lat -5 5';;
pr_flor_kenya_nudged)
    file=PrincetonData/nudgelongalle.%%_5dy_tigerx86_64.intel16_512PE.precip_ce_mo.nc;kindname="FLOR SST-nudged";climfield="precipitation";flipcolor=11
    map='set lon 33 42
set lat -5 5';;

pr_wah_kenya_actualclim_clim)
    file=Weather@Home/Kenya/pr_wah_ACTUALCLIM_clim_kenya_longrains.nc;kindname="WAH MAM actual climatology";climfield="precipitation";flipcolor=11;NPERYEAR=1
    map='set lon 33 42
set lat -5 5';;

pr_miroc5_kenya_actualclim_clim)
    file=Weather@Home/Kenya/pr_miroc5_ACTUALCLIM_clim_kenya_longrains.nc;kindname="MIROC5 MAM actual climatology";climfield="precipitation";flipcolor=11;NPERYEAR=1
    map='set lon 33 42
set lat -5 5';;


*) echo
[ -x ./myvinkhead.cgi ] && . ./myvinkhead.cgi "Error" "" "noindex,nofollow"
echo "Cannot handle $FORM_field (yet)"
[ -x ./myvinkfoot.cgi ] && . ./myvinkfoot.cgi
[ -x ./myvinkfoot.cgi ] && exit;;

esac
[ "$lwrite" = true ] && echo "FORM_field=$FORM_field<br>file=$file<br>NPERYEAR=$NPERYEAR<br>LSMASK=$LSMASK<br>"

c=`echo $file | fgrep -c %`
if [ $c -gt 0 ]; then
  ENSEMBLE=true
else
  ENSEMBLE=""
fi

if [ -n "$ENSEMBLE" ]; then
  NOMISSING=nomissing
fi
if [ "${FORM_field#era}" != "${FORM_field}" -o "${FORM_field#ecmwf}" != "${FORM_field}" -o "${FORM_field#cfs}" != "${FORM_field}" -o "${FORM_field#csm}" != "${FORM_field}" -o "${FORM_field#demeter}" != "${FORM_field}" ]; then
  NOMISSING=nomissing
fi
if [ "${FORM_field%20c3m}" != "${FORM_field}" -o "${FORM_field%sresa1b}" != "${FORM_field}" -o "${FORM_field%sresa2}" != "${FORM_field}" -o "${FORM_field%picntrl}" != "${FORM_field}" -o "${FORM_field%1pctto4x}" != "${FORM_field}" -o "${FORM_field%1pctto2x}" != "${FORM_field}" ]; then
  NOMISSING=nomissing
fi
fi # rapid

if [ "$NPERYEAR" = 12 -a "${file%_daily.nc}" != "$file" ]; then
    NPERYEAR=366
fi
###echo "file=$file"
