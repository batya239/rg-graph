for i in `cat e4-6loop.lst`; do A=`python On.py $i|grep -v phi`; echo "$A $i";  done >On-e4-6loop.lst

