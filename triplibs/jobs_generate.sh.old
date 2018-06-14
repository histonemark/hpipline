#!/bin/bash

# general stuff
source ~/work/tools/my_env.sh

# get the forcing parameter
if [ $# -lt 1 ]; then
  force=0
else
  force=$1
fi

# init generate log
generate_log="jobs_generate.log"
rm -rf $generate_log

# first, check that the hpipline repository is clean
hpipline_dir=$HOME/work/CRG/projects/hpip/hpipline
check_git_clean_workdir $hpipline_dir
if [ $? -ne 0 ]; then
  error_message "hpipline dir not clean!"
  exit 1
fi
 
# get the ID of the last commit
hpipline_commit=$(get_last_git_commit $hpipline_dir)
log_message "Running against hpipline commit $hpipline_commit" >> $generate_log

# get source Makefiles names
makefile_top=$hpipline_dir/Makefile_top
makefile_rep=$hpipline_dir/Makefile_rep
makefile_lib=$hpipline_dir/Makefile_lib

# get libs
libs=$(cat lib_names.txt)
libnames=""
for lib in $libs; do
  if [ "$lib" != "Undetermined" ]; then
    libname=lib$lib
  else
    libname=$lib
  fi
  libnames="$libnames $libname"
done

# replicate names
repnames="rep1 rep2"

# source PBS script for rep computing
pbs_in="hpipline.pbs.in"

for rep in $repnames; do
  # replicate-level Makefile creation
  cat $makefile_rep |\
    sed -e s,@libs@,"$libnames",g |\
  tee > $rep/Makefile

  # replicate-level PBS script creation
  cat $pbs_in |\
    sed -e s,@REP@,"$rep",g |\
  tee > $rep/hpipline.pbs

  for libname in $libnames; do 
    # library-level Makefile creation
    cat $makefile_lib |\
      sed -e s,@LIBNAME@,$libname,g |\
    tee > $rep/$libname/Makefile
  done 
done
