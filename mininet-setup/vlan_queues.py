__author__ = 's.zannettou'

''' 
*          MININET STARTUP SCRIPT
* 		   for VTN-based RTM Network Service 
* 
*   file: vlan_queues.py 
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

'''
This file is used to configure the queues in the core of the network so we will be able to simulate the vlan priority aware underlay.
We configure all the ports of the switch that represents the core of the network.
We also configure some static flows to match the appropriate traffic to the appropriate queue.

This file is called from multiple_vlan.py.  
'''

import os
import sys
#we retrieve the the number of switches that are connected to the core switch. With that number we know the ports of the core switch
# We apply the queues to every single port of the core switch
switches = sys.argv[1]
for i in range(int(switches)):
	port = 's1-eth' + str(i+1)
	os.system('sudo ovs-vsctl set port '+ port + ' qos=@newqos -- --id=@newqos create qos type=linux-htb  queues=0=@q0,1=@q1,2=@q2\
	 -- --id=@q0 create queue other-config:min-rate=1000000 -- --id=@q1 create queue other-config:min-rate=2000000 -- --id=@q2\
	  create queue other-config:min-rate=6000000')



#Static flow mods. Assignment of flows to different queues according to the dscp value (tos_value = dscp * 4)
#if you want to support more dscp values then you should modify the above command to create more queues and add
# the flow mods in a similar manner as below
os.system('sudo ovs-ofctl add-flow s1 udp,vlan_pcp=0,actions=enqueue=2:0,local')
os.system('sudo ovs-ofctl add-flow s1 udp,vlan_pcp=5,actions=enqueue=2:1,local')
os.system('sudo ovs-ofctl add-flow s1 udp,vlan_pcp=7,actions=enqueue=2:2,local')
'''
os.system('sudo ovs-ofctl add-flow s1 tcp,vlan_pcp=0,actions=enqueue=2:0,normal')
os.system('sudo ovs-ofctl add-flow s1 tcp,vlan_pcp=5,actions=enqueue=2:1,normal')
os.system('sudo ovs-ofctl add-flow s1 tcp,vlan_pcp=7,actions=enqueue=2:2,normal')
'''
