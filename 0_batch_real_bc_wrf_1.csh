#!/bin/csh
#SBATCH --partition c6148
#SBATCH --nodes 6
#SBATCH -n 224
###SBATCH --tasks=224
#SBATCH --job-name 205801
#SBATCH --error %j.err
#SBATCH --output %j.out

limit stacksize unlimited
#module load mathlib/netcdf/4.7.1/impi_pnetcdf

set echo
#-----------------------------------------------------------------------
set start_year  = 2057
set start_month = 12
set start_day   = 28
set end_year    = 2058
set end_month   = 2
set end_day     = 1
set curr_year   = 2057
set curr_month  = 12
set curr_day    = 28

if (( $start_year % 4 ) != 0 ) then
   set is_leap_year = 0
else if( ( $start_year % 400 ) == 0 ) then
   set is_leap_year = 1
else if ( ( $start_year % 100 ) == 0 ) then
   set is_leap_year = 0
else
   set is_leap_year = 1
endif

if ( $is_leap_year ) then
   set numday = ( 31 29 31 30 31 30 31 31 30 31 30 31 )
else
   set numday = ( 31 28 31 30 31 30 31 31 30 31 30 31 )
endif

@ start_fullday = $start_year * 10000 + $start_month * 100 + $start_day
@ curr_fullday = $curr_year * 10000 + $curr_month * 100 + $curr_day
@ end_fullday = $end_year * 10000 + $end_month * 100 + $end_day
echo $start_fullday

while ( $curr_fullday < $end_fullday  )

@ next_day = $curr_day + 1
set next_month = $curr_month
set next_year  = $curr_year

if( $next_day > $numday[$curr_month] )then
	@ next_month = $curr_month + 1
	@ next_day = $next_day - $numday[$curr_month]
	if( $next_month > 12 ) then
		@ next_year = $curr_year + 1
		set next_month = 1
	endif
endif

@ next_fullday = $next_year * 10000 + $next_month * 100 + $next_day
set str_curr_month = `printf "%02d" $curr_month`
set str_curr_day = `printf "%02d" $curr_day`
set str_next_month = `printf "%02d" $next_month`
set str_next_day = `printf "%02d" $next_day`

if (-e namelist.input ) rm -f namelist.input
if (-e wrfbdy_d01 ) rm -f wrfbdy_d01
if (-e wrfinput_d01 ) rm -f wrfinput_d01
if (-e wrfinput_d02 ) rm -f wrfinput_d02

if( $curr_fullday == $start_fullday ) then
  cp namelist.input_SV2 namelist.input.sed0
else
  cp namelist.input_SV2.cheminit namelist.input.sed0  
endif

sed -e "s/start_year               = 2014,2014/start_year               = ${curr_year},${curr_year}/g" namelist.input.sed0 > namelist.input.sed1
sed -e "s/start_month              = 03,03/start_month              = ${str_curr_month},${str_curr_month}/g" namelist.input.sed1 > namelist.input.sed2
sed -e "s/start_day                = 01,01/start_day                = ${str_curr_day},${str_curr_day}/g" namelist.input.sed2 > namelist.input.sed3
sed -e "s/end_year                 = 2014,2014/end_year                 = ${next_year},${next_year}/g" namelist.input.sed3 > namelist.input.sed4
sed -e "s/end_month                = 04,04/end_month                = ${str_next_month},${str_next_month}/g" namelist.input.sed4 > namelist.input.sed5
sed -e "s/end_day                  = 01,01/end_day                  = ${str_next_day},${str_next_day}/g" namelist.input.sed5 > namelist.input.sed6
if( $curr_fullday == 20140930 ) then
  sed -e "s/end_hour                 = 06,06/end_hour                 = 00,00/g" namelist.input.sed6 > namelist.input.sed7
  sed -e "s/end_day                  = 03,03/end_day                  = 01,01/g" namelist.input.sed7 > namelist.input.sed8
  mv -f namelist.input.sed8 namelist.input
else
  mv -f namelist.input.sed6 namelist.input
endif
rm -f namelist.input.sed?

echo \!\!---start running real for ${curr_year}-${str_curr_month}-${str_curr_day}

#srun --mpi=none --kill-on-bad-exit ./real.exe
#srun --kill-on-bad-exit ./real.exe

srun --mpi=pmi2 ./real.exe

### check if segmentation fault occurs, SJW, 4/03/2022
set i = 1
set btr = `find ./ -name "*btr"|wc -l`
echo $btr >> batch.log
while (($btr != 0)  && ($i <= 3) )
echo "D1/2 Segmentation Fault**********************************" >> batch.log
echo "Current Time is:" >> batch.log
echo "Let's do real again**************************************" >> batch.log
date >> batch.log
echo "                                                             " >> batch.log
mv *btr ./seg_fau/.
srun --mpi=pmi2 ./real.exe
@ btr = `find ./ -name "*btr"|wc -l`
@ i ++
end

### check D1/2 REAL.EXE

set status = `tail -n 3 rsl.out.0000 | grep "SUCCESS" | cut -c 34-40`
if (${status} == "SUCCESS") then

echo "D1/2 REAL **********************************************" >> batch.log
echo "Current Time is:" >> batch.log
date >> batch.log
echo Successful finished D1/2_REAL for ${curr_year}-${str_curr_month}-${str_curr_day} >> batch.log
echo "                                                             " >> batch.log

else

echo "D1/2 REAL FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF" >> batch.log
echo "Opps, Failed, Current Time is:" >> batch.log
date >> batch.log
echo Failed ${curr_year}-${str_curr_month}-${str_curr_day} in D1/2_REAL >> batch.log
echo "                                                             " >> batch.log
exit
endif

if ( ! -d LOG_D12_REAL ) mkdir LOG_D12_REAL
mv rsl* LOG_D12_REAL



#####add bio in wrfinput by DaGao 
ncl add_bio.ncl

echo \!\!---start running mozbc for ${curr_year}-${str_curr_month}-${str_curr_day}
if( $curr_fullday == $start_fullday ) then
   ./mozbc < cambc_8bin_d01.inp > log.mozbc.d01
##   ./mozbc < cambc_8bin_d02.inp > log.mozbc.d02
   set status1 = `tail -n 1 log.mozbc.d01 | grep "successfully" | cut -c 23-34`
##   set status2 = `tail -n 1 log.mozbc.d02 | grep "successfully" | cut -c 23-34`
   set status2 = "successfully"
else
   ./mozbc < cambc_8bin_d01_bconly.inp > log.mozbc.d01_bconly
   set status1 = `tail -n 1 log.mozbc.d01_bconly | grep "successfully" | cut -c 23-34`
   set status2 = "successfully"
endif

if (${status1} == "successfully" && ${status2} == "successfully") then

echo "D1/2 mozbc **********************************************" >> batch.log
echo "Current Time is:" >> batch.log
date >> batch.log
echo Successful finished mozbc for ${curr_year}-${str_curr_month}-${str_curr_day} >> batch.log
echo "                                                             " >> batch.log

else

echo "D1/2 mozbc FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF" >> batch.log
echo "Opps, Failed, Current Time is:" >> batch.log
date >> batch.log
echo Failed ${curr_year}-${str_curr_month}-${str_curr_day} in mozbc >> batch.log
echo "                                                             " >> batch.log
exit
endif

if ( ! -d LOG_D12_MOZBC ) mkdir LOG_D12_MOZBC
mv -f log.mozbc.d* LOG_D12_MOZBC

#echo \!\!---start running add_ion for ${curr_year}-${str_curr_month}-${str_curr_day}
#ncl add_ion_prod_rate_d01.ncl >& log.add_ion.d01
#ncl add_ion_prod_rate_d02.ncl >& log.add_ion.d02
#set status1 = `wc -l log.add_ion.d01 |cut -c 1-1`
#set status2 = `wc -l log.add_ion.d02 |cut -c 1-1`

#if (${status1} == "5" && ${status2} == "5") then
#echo "D1/2 add_ion **********************************************" >> batch.log
#echo "Current Time is:" >> batch.log
#date >> batch.log
#echo Successful finished add_ion for ${curr_year}-${str_curr_month}-${str_curr_day} >> batch.log
#echo "                                                             " >> batch.log

#else

#echo "D1/2 add_ion FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF" >> batch.log
#echo "Opps, Failed, Current Time is:" >> batch.log
#date >> batch.log
#echo Failed ${curr_year}-${str_curr_month}-${str_curr_day} in add_ion >> batch.log
#echo "                                                             " >> batch.log
#exit
#endif

#mv -f log.add_ion.d* LOG_D12_MOZBC

echo \!\!---start running wrf for ${curr_year}-${str_curr_month}-${str_curr_day}
#srun --mpi=none --kill-on-bad-exit ./wrf.exe
#srun --kill-on-bad-exit ./wrf.exe
srun --mpi=pmi2 ./wrf.exe

set status = `tail -n 3 rsl.out.0000 | grep "SUCCESS" | cut -c 30-36`
if (${status} == "SUCCESS") then

echo "D1/2 WRF.EXE **********************************************" >> batch.log
echo "Current Time is:" >> batch.log
date >> batch.log
echo Successful finished D1/2_WRF >> batch.log
echo "                                                             " >> batch.log

else

echo "D1/2 WRF FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF" >> batch.log
echo "Opps, Failed, Current Time is:" >> batch.log
date >> batch.log
echo Failed ${curr_year}-${str_curr_month}-${str_curr_day} in D1/2_WRF >> batch.log
echo "                                                             " >> batch.log
exit
endif

if ( ! -d LOG_D12_WRF ) mkdir LOG_D12_WRF
mv rsl* LOG_D12_WRF

if ( ! -d DUST_D12_WRF ) mkdir DUST_D12_WRF
rm wrfout_d0?_${curr_year}-${str_curr_month}-${str_curr_day}_00:00:00 
rm wrfout_d0?_${curr_year}-${str_curr_month}-${str_curr_day}_01:00:00 
rm wrfout_d0?_${curr_year}-${str_curr_month}-${str_curr_day}_02:00:00 
rm wrfout_d0?_${curr_year}-${str_curr_month}-${str_curr_day}_03:00:00 
rm wrfout_d0?_${curr_year}-${str_curr_month}-${str_curr_day}_04:00:00 
rm wrfout_d0?_${curr_year}-${str_curr_month}-${str_curr_day}_05:00:00 
rm wrfout_d0?_${curr_year}-${str_curr_month}-${str_curr_day}_06:00:00 

if ( ! -d OUT_D12_WRF ) mkdir OUT_D12_WRF
mv wrfout_d0?_????-??-??_??:00:00 OUT_D12_WRF

if ( ! -d ICBC_${curr_year}-${str_curr_month}-${str_curr_day} ) mkdir ICBC_${curr_year}-${str_curr_month}-${str_curr_day}
mv wrfinput_d* wrfbdy_d* wrf_chem_input_d0* ICBC_${curr_year}-${str_curr_month}-${str_curr_day}

# prepare for next day
mv -f wrfrst_d01_${next_year}-${str_next_month}-${str_next_day}_00:00:00 wrf_chem_input_d01
#mv -f wrfrst_d02_${next_year}-${str_next_month}-${str_next_day}_00:00:00 wrf_chem_input_d02

set curr_year 	= $next_year
set curr_month	= $next_month
set curr_day	= $next_day
set curr_fullday	= $next_fullday


end
#sbatch batch_real_bc_wrf_2.csh
#chmod u+x batch_2_01_real_mozbc_wrf.csh
#qsub  batch_2_01_real_mozbc_wrf.csh

