#!/bin/bash

for f in $(find . -name "*.fastq.gz"); do
  new_f=$(echo $f | sed -e s,'./',, | cut -d'_' -f1)
  ln -s $f $new_f.fastq.gz 
done
