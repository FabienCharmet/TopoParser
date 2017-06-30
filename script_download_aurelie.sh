#!/bin/bash

for hour in 00 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23
do
	for minutes in 00 15 30 45 
	do
		download="http://mawi.nezu.wide.ad.jp/mawi/ditl/ditl2017/20170412" 
		download+=$hour 
		download+=$minutes 
		download+=".pcap.gz"
		wget $download
	done
	download=""
done
