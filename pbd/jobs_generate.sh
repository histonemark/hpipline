#!/bin/bash

# check for proper invocation
if [ $# -ne 1 ]; then
  echo "Usage: jobs_generate <hpip_root>" 1>&2
  exit 1
fi
hpip_root=$1

# generate directory names
pbd_datadir=$hpip_root/data/pbd
raw_datadir=$hpip_root/data/raw/libraries

# input makefiles
makefile_pbd_in=$hpip_root/hpipline/pbd/Makefile_pbd
makefile_pbd_lib_in=$hpip_root/hpipline/pbd/Makefile_pbd_lib

# generate toplevel makefile
makefile_pbd_out=$pbd_datadir/Makefile
cat $makefile_pbd_in |\
  sed -e s,@HPIP_ROOT@,$hpip_root,g |\
tee > $makefile_pbd_out

# generate the directories for the pbd libraries
for libdir in $(find $raw_datadir -mindepth 1 -maxdepth 1 -type d); do

  # make the library subdirectory
  libname="${libdir#$raw_datadir/}"
  lib_out_dir=$pbd_datadir/pbd_libs/$libname
  mkdir -p $lib_out_dir

  # extract the promoters that were used from the sample sheet
  sample_sheet=$libdir/SampleSheet.csv
  promoters=""
  for promoter in $(grep '^1' $sample_sheet | cut -d',' -f3); do
    promoters="$promoters $promoter"
  done

  # make the Makefile associated to the library
  makefile_pbd_lib_out=$lib_out_dir/Makefile
  cat $makefile_pbd_lib_in |\
    sed -e s,@HPIP_ROOT@,$hpip_root,g |\
    sed -e s,@LIBNAME@,"$libname", |\
    sed -e s,@PROMOTERS@,"$promoters", |\
    sed -s s,@PROMOTERS_FASTQ@,"$promoters_fastq", |\
  tee > $makefile_pbd_lib_out
done
