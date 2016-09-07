for i in `seq 1 300`;
do
	iotop -n 1 -k| head -1|awk '{print ($4+$10)}' 1>> io`echo $1`
	eval $(awk '/^cpu /{print "previdle=" $5 "; prevtotal=" $2+$3+$4+$5 }' /proc/stat); sleep 0.4; eval $(awk '/^cpu /{print "idle=" $5 "; total=" $2+$3+$4+$5 }' /proc/stat); intervaltotal=$((total-${prevtotal:-0})); echo "$((100*( (intervaltotal) - ($idle-${previdle:-0}) ) / (intervaltotal) ))" 1>> cpu`echo $1`
	free -m|head -2|tail -1|awk '{print ($3*100/$2)}' 1>> ram`echo $1`
	sleep 1
done
