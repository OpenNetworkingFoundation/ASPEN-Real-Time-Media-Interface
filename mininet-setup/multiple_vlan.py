'''
*          MININET STARTUP SCRIPT
* 	   for VTN-based RTM Network Service 
* 
*   file: multiple_vlan.py 
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
This file is used to create a topology that contains only a switch in the core of the network.
The switches that are in the core of the network are assigned to an instance of an SDN Controller (ODL or Floodlight)
and the Edge Switches are assigned to an instance of Opendaylight Virtualization Edition (VTN)
The file automates the VTN topology creation, the OVS Queues configuration and the sflow Agents initiation
The user can run the file using the arguments --all or --file. By running the topology with argument --all then 
all the hosts will be mapped to the VTN. if the user specifies the argument --file then the VTN topology maps only
the ports that are specified in the topo configuration file

'''
 #!/usr/bin/python

from mininet.topo import Topo
from mininet.node import Host
from mininet.net import Mininet
from mininet.util import custom,dumpNodeConnections,quietRun
from mininet.log import setLogLevel
from mininet.cli import CLI
from mininet.node import OVSHtbQosSwitch, OVSKernelSwitch
from mininet.node import Controller,RemoteController
from mininet.link import Link,TCLink
import os
from time import time,sleep
import subprocess
from functools import partial
import sys


# Class that is used for mininet hosts to generate tagged packets
class VLANHost( Host ):

   def config( self, vlan=100, **params ):
        """Configure VLANHost according to (optional) parameters:
           vlan: VLAN ID for default interface"""

        r = super( Host, self ).config( **params )

        intf = self.defaultIntf()
        # remove IP from default, "physical" interface
        self.cmd( 'ifconfig %s inet 0' % intf )
        # create VLAN interface 
        self.cmd( 'vconfig add %s %d' % ( intf, vlan ) )
        # assign the host's IP to the VLAN interface
        self.cmd( 'ifconfig %s.%d inet %s' % ( intf, vlan, params['ip'] ) )
        # update the intf name and host's intf map
        newName = '%s.%d' % ( intf, vlan )
        # update the (Mininet) interface to refer to VLAN interface name
        intf.name = newName
        # add VLAN interface to host's name to intf map
        self.nameToIntf[ newName ] = intf

        return r

hosts = { 'vlan': VLANHost }

def startTopo():
    operation=0
    if(len(sys.argv)<2):
        sys.exit("Oops you didn't specify the operation mode. Specify --all for all the mappings or --file for the mappings that are\
 specified in the topo config file")
    else:
        operation = sys.argv[1]
        if(str(operation)!="--all" and str(operation)!="--file"):
            sys.exit("Unsupported Operation. Supported arguments are --all and --file")

    n=3
    host = partial( VLANHost, vlan=100 )

    net = Mininet(switch=OVSHtbQosSwitch,host=host, link=TCLink, autoStaticArp=True, autoSetMacs=True, controller=None, build=False )
    c0 = net.addController('c0', controller=RemoteController, ip='127.0.0.1')
    c1 = net.addController('c1', controller=RemoteController, ip='192.168.56.107')

    # Open Topology Configuration File#
    config = open('topo_config','r')
    #Create 3 lists. One should store the switches names and the other the number of Hosts per Switch#
    switches = []
    hostsPerSwitch = []
    bandwidths = []
    # Parse the file and fill the 3 lists with the information #
    for line in config:
        if not "*" in line:
            temp = line.split(" ")
            switchName = temp.pop(0)
            if(switchName=='s1'):
                raise Exception("The name s1 represents the core of the network. Please make sure that you don't use it in your config file")
            switches.append(switchName)
            hostsPerSwitch.append(temp.pop(0))
            bandwidths.append(temp.pop(0))

    hostCount=1
    i=0
    # Create the switch that represents the core of the network #
    coreSwitch = net.addSwitch('s1')
    # Iterate through switches #
    for i in range(len(switches)):
        # Create the switch according to the name that is specified in the list and connect it to the core network #
        switch = net.addSwitch(switches[i])
        if(int(bandwidths[i])==0):
            net.addLink(coreSwitch,switch)
        else:
            net.addLink(coreSwitch,switch, bw=int(bandwidths[i]))
        # Create the number of hosts that are specified to the list and connect them to the switch that we created above #
        for j in range(int(hostsPerSwitch[i])):
            host= net.addHost('h%s' %hostCount)    
            net.addLink(host,switch)
            hostCount+=1


    #start the controllers
    net.build()
    c0.start()
    c1.start()
    
    # Assign all the edge switches to the controller zero
    for switch in switches:
        Switch=net.getNodeByName(str(switch))
        Switch.start( [c1])
    #Assign the core network switch to the controller 1
    coreSwitch.start( [ c0 ])
    print "\nApplying VTN Settings..."
    os.system("python createVTNAutomatedOdl.py " + str(operation))
    print "Executing Pingall to identify hosts... Don't worry about the loss."
    net.pingAll()
    print "Applying Queues Configuration..."
    os.system("python vlan_queues.py " + str(len(switches)))
    CLI(net)


if __name__ == '__main__':
	# Tell mininet to print useful information
	setLogLevel('info')
	startTopo()

