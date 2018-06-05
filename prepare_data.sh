#!/bin/bash

# check invocation
if [ $# -ne 1 ]; then
  echo "Usage: prepare_data.sh <replicate_name>" 1>&2
  exit 1
fi
rep_name=$1

# Marc's data dir (change if on cluster)
mc_datadir=/mnt/ant-login/mcorrales/HPIP

# build directory names
cDNA_dir=$mc_datadir/cDNA/HPIP_cDNA_$rep_name/Data/Intensities/BaseCalls
gDNA_dir=$mc_datadir/gDNA/HPIP_gDNA_$rep_name/Data/Intensities/BaseCalls
iPCR_dir=$mc_datadir/iPCR/HPIP_iPCR_$rep_name/Data/Intensities/BaseCalls

# prepare library names
libs=$(cat lib_names.txt)

# make the data dir and cd to it
mkdir -p $rep_name
cd $rep_name

for lib in $libs; do
  echo "Processing $lib"
  if [ $lib != "Undetermined" ]; then
    # make the subdirectory of the current library
    libname="lib$lib"
    mkdir -p $libname
    # copy files
    cp $cDNA_dir/cDNA"$lib"_* $libname/cDNA.fastq.gz
    cp $gDNA_dir/gDNA"$lib"_* $libname/gDNA.fastq.gz
    cp $iPCR_dir/iPCR"$lib"_*_R1* $libname/iPCR-fwd.fastq.gz
    cp $iPCR_dir/iPCR"$lib"_*_R2* $libname/iPCR-rev.fastq.gz
  else
    # make the subdirectory of the current library
    libname="Undetermined"
    mkdir -p $libname 
    # copy files
    cp $cDNA_dir/"$lib"_* $libname/cDNA.fastq.gz
    cp $gDNA_dir/"$lib"_* $libname/gDNA.fastq.gz
    cp $iPCR_dir/"$lib"_*_R1* $libname/iPCR-fwd.fastq.gz
    cp $iPCR_dir/"$lib"_*_R2* $libname/iPCR-rev.fastq.gz
  fi
done
