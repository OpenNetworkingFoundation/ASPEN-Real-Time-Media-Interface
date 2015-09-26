''' 
*          MININET STARTUP SCRIPT
*  		   for VTN-based RTM Network Service 
* 
*   file: createVTNAutomatedOdl.py 
* 
*          NEC Europe Ltd. PROPRIETARY INFORMATION 
* 
* This software is supplied under the terms of a license agreement 
* or nondisclosure agreement with NEC Europe Ltd. and may not be 
* copied or disclosed except in accordance with the terms of that 
* agreement. 
* 
*      Copyright (c) 2015 NEC Europe Ltd. All Rights Reserved. 
* 
* Authors: Savvas Zannettou 
*          Fabian Schneider (fabian.schneider@neclab.eu)
* 
* NEC Europe Ltd. DISCLAIMS ALL WARRANTIES, EITHER EXPRESS OR IMPLIED, 
* INCLUDING BUT NOT LIMITED TO IMPLIED WARRANTIES OF MERCHANTABILITY 
* AND FITNESS FOR A PARTICULAR PURPOSE AND THE WARRANTY AGAINST LATENT 
* DEFECTS, WITH RESPECT TO THE PROGRAM AND THE ACCOMPANYING 
* DOCUMENTATION. 
* 
* No Liability For Consequential Damages IN NO EVENT SHALL NEC Europe 
* Ltd., NEC Corporation OR ANY OF ITS SUBSIDIARIES BE LIABLE FOR ANY 
* DAMAGES WHATSOEVER (INCLUDING, WITHOUT LIMITATION, DAMAGES FOR LOSS 
* OF BUSINESS PROFITS, BUSINESS INTERRUPTION, LOSS OF INFORMATION, OR 
* OTHER PECUNIARY LOSS AND INDIRECT, CONSEQUENTIAL, INCIDENTAL, 
* ECONOMIC OR PUNITIVE DAMAGES) ARISING OUT OF THE USE OF OR INABILITY 
* TO USE THIS PROGRAM, EVEN IF NEC Europe Ltd. HAS BEEN ADVISED OF THE 
* POSSIBILITY OF SUCH DAMAGES. 
* 
*     THIS HEADER MAY NOT BE EXTRACTED OR MODIFIED IN ANY WAY. 
''' 


#!/usr/bin/python
'''
This file is used to automate the creation of VTN topology for our mininet topology. The idea is that if the user chooses the
argument --all then we need to map all the hosts in the VTN. If the user chooses the argument --file then we must map only the 
ports that are specified in the topo config file.

To achieve that we retrieve the topology information from the VTN 
Coordinator and we map all the ports of the Edge Switches (the topology information have only the information of the edge switches)

This file is called from multiple_vlan.py
'''

from webapijson import WebAPIJSON
import urllib
from time import time,sleep
import sys
# the user specifies the operation of the mappings. If zero then map all the switch ports else map all ports that are specified to the
#topo config file
operation = sys.argv[1]
requiredPorts = []
# if the user wants to specify the ports that will be mapped to the vtn open and parse the topo_config file
if(operation=="--file"):
	config = open('topo_config','r')
	for line in config:
		if not "*" in line:
			temp = line.split(" ")
			listPorts= temp.pop(3)
			ports = listPorts.split(",")
			for port in ports:
				requiredPorts.append(port.rstrip())


# connection information
#Make sure that VTN Coordinator is running and has ip address 192.168.56.102
connection = WebAPIJSON("admin", "adminpass")
connection.base_url="http://192.168.56.102:8083/vtn-webapi/"
controllerName = 'controllerone'
vtnName = 'vtn1'
managerIpAddr = '192.168.56.107'

#first of all create a Controller
connection.CreateController(controller_id=controllerName,ipaddr=managerIpAddr,controller_type='odc',version='1.0',audit_status='enable')

#create a vtn
connection.CreateVTN(vtnName)
# this is to make sure that the vtn coordinator will get the topology information from the VTN Manager
sleep(60)
vBridgeCounter=1
vBridgeInterfaceCounter=1
if(operation=="--all"):
	switches = connection.ListSwitches(controller_id=controllerName)
	for switch in switches['switches']:
		switchId=switch['switch_id']
		
		#Construct vbridge name
		vBridgeName = 'br' + str(vBridgeCounter)
		vBridgeCounter+=1
		#Create the Vbridge
		connection.CreateVBridgeODL(vtnName,vBridgeName, controllerName, "(DEFAULT)")
		# for each port of the real switch

		ports = connection.ListSwitchPorts(controller_id=controllerName,switch_id=switchId)
		for port in ports['ports']:
			portId=port['port_name']

			#create a vbridge interface
			vBridgeInterfaceName = 'if' + str(vBridgeInterfaceCounter)
			vBridgeInterfaceCounter+=1
			connection.CreatevBrIf(vtnName,vBridgeName,vBridgeInterfaceName)
			#add the mapping between the vbridge interface and the real switch port
			connection.ConfigureMapping(vtn_name=vtnName,vbr_name=vBridgeName,if_name=vBridgeInterfaceName,switch_id=switchId,port_id=portId,vlan_id='100',tagged='true')
else:
	switches = connection.ListSwitches(controller_id=controllerName)
	for switch in switches['switches']:
		switchId=switch['switch_id']

		
		#Construct vbridge name
		vBridgeName = 'br' + str(vBridgeCounter)
		vBridgeCounter+=1
		#Create the Vbridge
		connection.CreateVBridgeODL(vtnName,vBridgeName, controllerName, "(DEFAULT)")
		# for each port of the real switch

		ports = connection.ListSwitchPorts(controller_id=controllerName,switch_id=switchId)
		for port in ports['ports']:
			portId=port['port_name']
			if portId in requiredPorts:
				#create a vbridge interface
				vBridgeInterfaceName = 'if' + str(vBridgeInterfaceCounter)
				vBridgeInterfaceCounter+=1
				connection.CreatevBrIf(vtnName,vBridgeName,vBridgeInterfaceName)
				#add the mapping between the vbridge interface and the real switch port
				connection.ConfigureMapping(vtn_name=vtnName,vbr_name=vBridgeName,if_name=vBridgeInterfaceName,switch_id=switchId,port_id=portId,vlan_id='100',tagged='true')
