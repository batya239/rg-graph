for i in `cat e2-6loop.lst`; do A=`python On.py $i|grep -v phi`; echo "$A $i";  done >On-e2-6loop.lst

