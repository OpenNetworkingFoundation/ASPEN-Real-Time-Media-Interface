'''
*
*           VTN-based RTM Network Service 
* 
*   file: \rtm-api\api\testManager.py 
* 
*  This software contributed by NEC under Apache 2.0 license for open source use. This software is supplied under the terms of the OpenSourceSDN Apache 2.0 license agreement 
*     Copyright (c) 2015 NEC Europe Ltd. 
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
*     
'''

#!/usr/bin/python


from webapijson import WebAPIJSON

connection = WebAPIJSON("admin", "admin")
connection.base_url="http://192.168.56.107:8080/"
a=connection.VTNManagerCreateFlowCondition(fl_name='flowlist1',ipsrc="10.0.0.1", ipdst="10.0.0.5", srcport=25001, dstport=50001, protocol="tcp")
#print a

coordinator = WebAPIJSON("admin","adminpass")
coordinator.base_url = "http://192.168.56.102:8083/vtn-webapi/"
b=connection.VTNManagerCreateFlowFilter(vtn_name="vtn1", fl_name="flowlist12", seqnum=12 , priority=5)
print b

c= connection.VTNManagerDeleteFlowFilter(vtn_name="vtn1",seqnum=12 )
print c