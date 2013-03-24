#!/bin/bash
for i in `ls | grep c`; do sed -i 's\/home/mkompan*/\\' $i; done
for i in `ls | grep c`; do sed -i 's\work/rg-graph*/\\' $i; done
