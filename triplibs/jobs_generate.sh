#!/bin/bash

# check for proper invocation
if [ $# -ne 1 ]; then
  echo "Usage: jobs_generate <hpip_root>" 1>&2
  exit 1
fi
hpip_root=$1

# general variables
genome=$hpip_root/data/dm4R6/dmel-all-chromosome-r6.15.fasta
triplibs_dir=$hpip_root/data/triplibs
hpipline_dir=$hpip_root/hpipline/triplibs
reps="rep1 rep2"
runs="iPCR cDNA gDNA"
libs=$(seq 2 12)

# build library names
libnames=""
for lib in $libs; do
  libnames="$libnames lib$lib"
done

# get source Makefiles names
makefile_top=$hpipline_dir/Makefile_top
makefile_rep=$hpipline_dir/Makefile_rep
makefile_lib=$hpipline_dir/Makefile_lib
makefile_noDNA=$hpipline_dir/Makefile_noDNA
makefile_run=$hpipline_dir/Makefile_run

# top-level Makefile creation
cat $makefile_top |\
  sed -e s,@REPS@,"$reps", |\
tee > $triplibs_dir/Makefile

# cycle on the replicates
for rep in $reps; do

  # the directory associated to the replicate
  rep_dir="$triplibs_dir/$rep"
  mkdir -p $rep_dir

  # replicate-level Makefile creation
  cat $makefile_rep |\
    sed -e s,@HPIP_ROOT@,$hpip_root,g |\
    sed -e s,@REP@,$rep, |\
    sed -e s,@libs@,"$libnames",g |\
  tee > $rep_dir/Makefile

  # create "noDNA" runs and regular runs
  for run in $runs; do

    # the directory associated to the noDNA run
    noDNA_run_dir="$triplibs_dir/$rep/$run"_noDNA
    mkdir -p $noDNA_run_dir

    # noDNA Makefile creation
    cat $makefile_noDNA |\
      sed -e s,@HPIP_ROOT@,$hpip_root,g |\
      sed -e s,@RUN@,$run, |\
      sed -e s,@REP@,$rep, |\
    tee > $noDNA_run_dir/Makefile

    # the directory associated to the regular run
    run_dir="$triplibs_dir/$rep/$run"
    mkdir -p $run_dir

    # run Makefile creation
    cat $makefile_run |\
      sed -e s,@HPIP_ROOT@,$hpip_root,g |\
      sed -e s,@RUN@,$run, |\
      sed -e s,@REP@,$rep, |\
    tee > $run_dir/Makefile

  done

  # cycle on the libraries
  for lib in $libs; do
    if [ "$lib" != "undetermined" ] && [ "$lib" != "alltogether" ]; then
      libname="lib$lib"
    else
      libname=$lib
    fi

    # the directory associated to the library
    lib_dir="$rep_dir/$libname"
    mkdir -p $lib_dir

    # library-level Makefile creation
    cat $makefile_lib |\
      sed -e s,@HPIP_ROOT@,$hpip_root,g |\
      sed -e s,@REP@,$rep,g |\
      sed -e s,@LIB@,$lib,g |\
      sed -e s,@GENOME@,$genome,g |\
    tee > $rep_dir/$libname/Makefile
  done
done
