#!/bin/bash

# check for proper invocation
if [ $# -ne 1 ]; then
  echo "Usage: jobs_generate <hpip_root>" 1>&2
  exit 1
fi
hpip_root=$1

# general variables
triplibs_dir=$hpip_root/data/triplibs
hpipline_dir=$hpip_root/hpipline/triplibs
reps="rep1 rep2"
runs="iPCR cDNA gDNA"
libs=$(seq 12)

# get source Makefiles names
makefile_top=$hpipline_dir/Makefile_top
makefile_rep=$hpipline_dir/Makefile_rep
makefile_lib=$hpipline_dir/Makefile_lib
makefile_noDNA=$hpipline_dir/Makefile_noDNA

# build library names
libnames=""
for lib in $libs; do
  libname="lib$lib"
  libnames="$libnames $libname"
done

# cycle on the replicates
for rep in $reps; do

  # the directory associated to the replicate
  rep_dir="$triplibs_dir/$rep"
  mkdir -p $rep_dir

  # replicate-level Makefile creation
  cat $makefile_rep |\
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

  done

  # cycle on the libraries
  for libname in $libnames; do

    # the directory associated to the library
    lib_dir="$rep_dir/$libname"
    mkdir -p $lib_dir

    # library-level Makefile creation
    cat $makefile_lib |\
      sed -e s,@HPIP_ROOT@,$hpip_root,g |\
      sed -e s,@LIBNAME@,$libname,g |\
    tee > $rep_dir/$libname/Makefile
  done
done
