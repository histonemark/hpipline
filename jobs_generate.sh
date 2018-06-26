#!/bin/bash

# check for proper invocation
if [ $# -ne 1 ]; then
  echo "Usage: jobs_generate <hpip_root>" 1>&2
  exit 1
fi

# the main variable
hpip_root=$1

# general variables
hpipline_dir=$hpip_root/hpipline
data_dir=$hpip_root/data

# get source Makefiles names
makefile_master=$hpipline_dir/Makefile_master

# master-level Makefile creation
cat $makefile_master |\
  sed -e s,@HPIP_ROOT@,$hpip_root, |\
tee > $data_dir/Makefile

# the current directory
root_dir=$(pwd)

# invoke the other two "jobs_generate" scripts
cd $hpipline_dir/pbd
bash jobs_generate.sh $hpip_root

cd $hpipline_dir/triplibs
bash jobs_generate.sh $hpip_root

# return to the current directory
cd $root_dir
