#!/bin/bash

echo "Insert the path of the pcap file"
read path

echo "Choose your protocol"
read protocol

if [ $protocol == "phs" ]
then
	tshark -r $path -z io,phs
else
	echo "Choose time interval"
	read interval
	tshark -r $path -z io,stat,$interval,$protocol
fi
