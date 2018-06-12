#!/bin/bash

source ~/work/tools/my_env.sh

# init run log
root_dir=$(pwd)
run_log="$root_dir/jobs_run.log"
rm -f $run_log

# run the scripts
repnames="rep1 rep2"
for rep in $repnames; do
  cd $rep
  jid=$(qsub -terse hpipline.pbs)
  log_message "$rep: $jid" >> $run_log
  cd $root_dir
done
