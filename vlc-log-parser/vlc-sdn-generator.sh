#!/bin/sh

# 
#          VLC LOGFILE PARSER and SDN REQUEST GENERATOR
#	   for VTN-based RTM Network Service  
# 
#   file: vlc-sdn-generator.sh
# 
#          NEC Europe Ltd. PROPRIETARY INFORMATION 
# 
# This software is supplied under the terms of a license agreement 
# or nondisclosure agreement with NEC Europe Ltd. and may not be 
# copied or disclosed except in accordance with the terms of that 
# agreement. 
# 
#      Copyright (c) 2015 NEC Europe Ltd. All Rights Reserved. 
# 
# Authors: Savvas Zannettou 
#          Fabian Schneider (fabian.schneider@neclab.eu)
# 
# NEC Europe Ltd. DISCLAIMS ALL WARRANTIES, EITHER EXPRESS OR IMPLIED, 
# INCLUDING BUT NOT LIMITED TO IMPLIED WARRANTIES OF MERCHANTABILITY 
# AND FITNESS FOR A PARTICULAR PURPOSE AND THE WARRANTY AGAINST LATENT 
# DEFECTS, WITH RESPECT TO THE PROGRAM AND THE ACCOMPANYING 
# DOCUMENTATION. 
# 
# No Liability For Consequential Damages IN NO EVENT SHALL NEC Europe 
# Ltd., NEC Corporation OR ANY OF ITS SUBSIDIARIES BE LIABLE FOR ANY 
# DAMAGES WHATSOEVER (INCLUDING, WITHOUT LIMITATION, DAMAGES FOR LOSS 
# OF BUSINESS PROFITS, BUSINESS INTERRUPTION, LOSS OF INFORMATION, OR 
# OTHER PECUNIARY LOSS AND INDIRECT, CONSEQUENTIAL, INCIDENTAL, 
# ECONOMIC OR PUNITIVE DAMAGES) ARISING OUT OF THE USE OF OR INABILITY 
# TO USE THIS PROGRAM, EVEN IF NEC Europe Ltd. HAS BEEN ADVISED OF THE 
# POSSIBILITY OF SUCH DAMAGES. 
# 
#     THIS HEADER MAY NOT BE EXTRACTED OR MODIFIED IN ANY WAY. 
# 



# This wrapper is used to extract information from the vlc logs
# The sends the request to the RTM Network Service
# Decides the requested class according to video quality

# Requires vlc-wrapper from the vlc-nox package


while true; do
	###
	### FIXME: Change path in following line according to your setup ###
	###
	filename=$(inotifywait -e create '/home/user/vlc-logs' | cut -d " " -f3  )
	echo "Found file with name $filename"
	sleep 2
	#Get Source IP
	sourceIP=$(grep 'access_output_udp debug: source' $filename | cut -d " " -f4)
	sourcePort=$(grep 'access_output_udp debug: source' $filename | cut -d " " -f6)
	#Get Destination IP
	destinationIP=$(grep 'access_output_udp debug: destination' $filename | cut -d " " -f4)
	destinationPort=$(grep 'access_output_udp debug: destination' $filename | cut -d " " -f6)
	#Get file path
	fullpath=$(grep 'file=' $filename | grep -m 1 'mkv\|mp4' | cut -d " " -f7 | cut -d '=' -f2 | cut -d "'" -f2)
	#Save media info the info
	quality=$(mediainfo '--Inform=Video;%Height%' $fullpath)
	bitrate=$(mediainfo '--Inform=Video;%BitRate%' $fullpath)
	
	if [ "$quality" -eq "360" ]; then
            requestedClass="af"
        elif [ "$quality" -eq "720" ]; then
            requestedClass="ef"
	else
	     requestedClass="be"
	fi

    sessionid=$(ps -ef | grep -m1 'vlc-wrapper udp $fullpath' | cut -d " " -f7)
    bandwidth=$((${bitrate}*2))
    echo "SourceIP=$sourceIP SourcePort=$sourcePort DestinationIP=$destinationIP DestinationPort=$destinationPort File=$filename Quality=$quality Bitrate=$bitrate Bandwidth=$bandwidth "
    #dump the data to the log file
	{	
		echo "{"	
		echo "\"sessionId\": \"$sessionid\"",
		echo "\"startTime\": \"13.37\"",
		echo "\"groupId\":\"2\"",
		echo "	 \"mediaElement\": {"
		echo "	    \"mediaType\": \"video\","
		echo "       \"ageOutTimer\" : \"1\","
		echo "        \"flowElement\": {"
		echo "            \"ipAddressType\": \"ip\","
		echo "             \"transportType\": \"udp\","
		echo "              \"sourceIpAddress\":\"$sourceIP/8\","
		echo "              \"sourceIpPort\" : \"$sourcePort\","
		echo "              \"destinationIpAddress\" : \"$destinationIP/8\","
		echo " 		    \"destinationIpPort\" : \"$destinationPort\","
		echo " 		    \"flowId\": \"1\""
		echo "               },"  
		echo "	            \"requestedQos\": { " 
		echo "			 \"applicationClass\": \"$requestedClass\","
		echo "                    \"averageBandwidth\":\"$bandwidth\","
		echo "			   \"minBandwidth\":\"$bandwidth\","
		echo "                     \"maxBandwidth\":\"$bandwidth\""
		echo "                },"
		echo "               \"grantedQos\":{"
		echo "                     \"actualClass\":\"\","
		echo "                     \"dscp\":\"\","
		echo "                     \"actualBandwidth\":\"\""
		echo "                  }"
		echo "           }"
		echo "}"
		echo "							"
		
		 

	} >> log.json

	{	
		echo "{\"sessionId\": \"$sessionid\",\"startTime\": \"13.37\",\"groupId\":\"2\",\"mediaElement\": {  \"mediaType\": \"video\",\"ageOutTimer\" : \"1\",\"flowElement\": {  \"ipAddressType\": \"ip\",\"transportType\": \"udp\",\"sourceIpAddress\":\"$sourceIP/8\", \"sourceIpPort\" : \"$sourcePort\",\"destinationIpAddress\" : \"$destinationIP/8\",\"destinationIpPort\" : \"$destinationPort\",\"flowId\": \"1\" }, \"requestedQos\": { \"applicationClass\": \"$requestedClass\",\"averageBandwidth\":\"$bandwidth\", \"minBandwidth\":\"$bandwidth\",\"maxBandwidth\":\"$bandwidth\"},\"grantedQos\":{  \"actualClass\":\"\",  \"dscp\":\"\", \"actualBandwidth\":\"\"  }}}"	
	} >> next.json

	sleep 1
	payload=$(cat next.json)
        
	response=$(curl -v --user root:root -H 'content-type: application/json' -H 'ipaddr:127.0.0.1' -X POST -d "$payload" http://127.0.0.1:5000/api/v1.0/sessions/)
	echo $response
	rm next.json
	rm $filename

done




