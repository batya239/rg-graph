#!/bin/bash
#for i in `ls | grep c`; do sed -i 's\/home/mkompan*/\\'   $i; done
#for i in `ls | grep c`; do sed -i 's\work/rg-graph*/\\'   $i; done
for i in `ls | grep '.*_O__Ei[0-9]\.c$'`; do sed -i 's\phi_*/\\'   $i; done

