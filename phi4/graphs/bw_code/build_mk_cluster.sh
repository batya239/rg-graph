#!/bin/bash

sd_dir="$HOME/workspace/bogner-sector-decomposition/sector_decomposition-1.1.0/"
sd_dir="/net/192.168.10.103/hpc_home/users/mkompan/workspace/bogner-sector-decomposition/sector_decomposition-1.1.0/"
sd_dir="/net/192.168.127.105/home/mkompan/workspace/bogner-sector-decomposition/sector_decomposition-1.1.0/"

export name=$1
basename=`echo $name|sed 's/.cc$//'`

g++ -DHAVE_CONFIG_H -I. -I. -I$sd_dir -I/usr/include    -g -O2 -MT .o -MD -MP  -c -o ${basename}.o $name

${sd_dir}libtool --mode=link g++  -g -O2   -o $basename  ${basename}.o $sd_dir/sector_decomposition/libsector_decomposition.la  
#/bin/sh ${sd_dir}libtool --mode=link g++  -g -O2   -o $basename  ${basename}.o $sd_dir/sector_decomposition/libsector_decomposition.la  

