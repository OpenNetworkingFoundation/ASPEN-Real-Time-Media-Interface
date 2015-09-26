''' 
*          MININET STARTUP SCRIPT
* 		   for VTN-based RTM Network Service  
* 
*   file: webapijson.py 
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
* 		   Peer Hasselmeyer (peer.hasselmeyer@neclab.eu)
*		   A. Vorontsov 
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
This file is used as wrapper for the REST Api calls to the VTN Interface. Most of the calls work for Pflow and Opendaylight.
For the calls that have differences we implemented some extra methos especially for Opendaylight's VTN. 
Also because of some bugs in the VTN Coordinator we implememented some methods for VTN Manager (end of file)
'''
from main import OFCapi
import urllib
class WebAPIJSON(OFCapi):
    auth_user = ''
    auth_pass = ''

    http_methods = ['GET', 'POST', 'DELETE']
    return_formats = []
    default_body_content = {}
    auth_type = 'BASIC_AUTH'
#    connection_check_method = ['GET', '#', 'current_user_url', '']
    base_url = ''
    send_json = True


    def __init__(self, auth_user, auth_pass, default_http_method=None, default_return_format=None):
        super(WebAPIJSON, self).__init__()
        self.auth_user = auth_user
        self.auth_pass = auth_pass
        self.default_header_content = {
            'Authorization': self.create_basic_auth(self.auth_user, self.auth_pass),
	    'content-type' : 'application/json'
        }

        if default_http_method:
            self.default_http_method = default_http_method

        if default_return_format or default_return_format == '':
            self.default_return_format = default_return_format

    def GetAPIversion(self):
        method='pfc_webapi_version.json'
        return self.do(method, http_method='GET')

    def ShowRealTopology(self, details=0):
        """
        Function implements methods described in 3.5.1 and 3.5.2
        """
        if details==0:
            method='realnetwork/topologies.json'
        elif details==1:
            method='realnetwork/topologies/detail.json'
        else:
            return Exception
        return self.do(method, http_method='GET')


    def ShowOFSList(self, description=0):
        """
        Function implements methods described in 3.6.1 and 3.6.2
        """
        if description==0:
            method='realnetwork/ofses.json'
        elif description==1:
            method='realnetwork/ofses/description.json'
        else:
            return Exception
        return self.do(method, http_method='GET')

    def ShowOFS(self,dpid, details=0, description=0):
        """
         Function implements methods described in 3.6.3, 3.6.4 and 3.6.5
        """
        if details==0 and description==0:
            method='realnetwork/ofses/'+ dpid+'.json'
        elif details==1 and description==0:
            method='realnetwork/ofses/' + dpid + '/detail.json'
        elif details==0 and description==1:
            method='realnetwork/ofses/' + dpid + '/description.json'
        else:
            return ValueError

        return self.do(method, http_method='GET')


    def GetRealFlows(self, details=0):
        if details==0:
            method='realnetwork/dataflows.json'
        elif details==1:
            method='realnetwork/dataflows/detail.json'
        else:
            return ValueError

        return self.do(method, http_method='GET')


    #VTN operations

    def ListVTN(self):
        method='vtns.json'
        return (self.do(method, http_method='GET'))

    def CreateVTN(self, vtn_name):
        payload={"vtn" : {"vtn_name" : vtn_name}}
        method='vtns.json'
        return self.do(method,content=self.build_content(payload), http_method='POST')

    def DeleteVTN(self, vtn_name):
        method='vtns/'+ vtn_name +'.json'
        return self.do(method, http_method='DELETE')

    def ShowVTN(self, vtn_name, details=0):
        if details==0:
            method='vtns/'+vtn_name+'.json'
        elif details==1:
            method='vtns/'+vtn_name+'/detail.json'
        else:
            return ValueError
        return self.do(method,http_method='GET')

    def ShowVTNTopology(self,vtn_name):
        method='vtns/'+vtn_name+'/topologies.json'
        return self.do(method, http_method='GET')

    def ShowVTNFlows(self, vtn_name, details=0):
        if details==0:
            method='vtns/'+vtn_name+'/dataflows.json'
        elif details==1:
            method='vtns/'+vtn_name+'/dataflows/detail.json'
        else:
            return ValueError
        return self.do(method, http_method='GET')


    # OSF Path policy

    def SetPathPolicy(self,ppol_idx):
        method="realnetwork/pathpolicies.json"
        payload={
                "pathpolicy" : {
                "ppol_idx" : ppol_idx
                }}
        return self.do(method,content=self.build_content(payload), http_method='POST')

    # vBridge operations

    def ListvBridges(self, vtn_name):
        method='vtns/'+ vtn_name +'/vbridges.json'
        return self.do(method, http_method='GET')


    def CreatevBridge(self,vtn_name, vbr_name):
        method='vtns/'+ vtn_name +'/vbridges.json'
        payload={"vbridge" : {"vbr_name" : vbr_name}}
        return self.do(method,content=self.build_content(payload), http_method='POST')


    def ShowvBridge(self,vtn_name, vbr_name, details=0):
        if details==0:
            method='vtns/'+ vtn_name +'/vbridges/'+vbr_name+'.json'
        elif details==1:
            method='vtns/'+vtn_name+'/vbridges/'+vbr_name+'/detail.json'
        else:
            return ValueError
        return self.do(method, http_method='GET')

    def DeletevBridge(self,vtn_name, vbr_name):
        method='vtns/'+vtn_name+'/vbridges/'+vbr_name+'.json'
        return self.do(method, http_method='DELETE')

    def RegvBridgeIP(self,vtn_name, vbr_name, ipaddr, netmask='', prefix=''):
        method='vtns/'+vtn_name+'/vbridges/'+vbr_name+'/ipaddress.json'
        if len(netmask)>0 and len(prefix)==0:
            payload={"hostaddress" : {"ipaddr" : ipaddr,"netmask" : netmask}}
        elif len(prefix)>0 and len(netmask)==0:
            payload={"hostaddress" : {"ipaddr" : ipaddr,"prefix" : prefix}}
        else:
            return ValueError
        return self.do(method,content=self.build_content(payload), http_method='POST')

    def ShowvBridgeIP(self,vtn_name, vbr_name):
        method='vtns/'+vtn_name+'/vbridges/'+ vbr_name+'/ipaddress.json'
        return self.do(method, http_method='GET')

    def DeletevBridgeIP(self, vtn_name, vbr_name, ipaddr, prefix='', netmask=''):
        if len(prefix)>0 and len(netmask)==0:
            method='vtns/'+vtn_name+'/vbridges/'+vbr_name+'/ipaddress.json?ipaddr='+ipaddr+'&prefix='+prefix
        elif len(netmask)>0 and len(prefix)==0:
            method='vtns/'+vtn_name+'/vbridges/'+vbr_name+'/ipaddress.json?ipaddr='+ipaddr+'&netmask='+netmask
        else:
            return ValueError
        return self.do(method, http_method='DELETE')

    # vBridge interfaces operations

    def ListvBrIf(self, vtn_name, vbr_name):
        method='vtns/'+vtn_name+'/vbridges/'+vbr_name+'/interfaces.json'
        return self.do(method, http_method='GET')

    def CreatevBrIf(self, vtn_name, vbr_name, if_name=''):
        method='vtns/'+vtn_name+'/vbridges/'+vbr_name+'/interfaces.json'
        if len(if_name)>0:
            payload={"interface" : {"if_name" : if_name}}
        else:
            payload=''
        return self.do(method, content=self.build_content(payload), http_method='POST')

    def ShowvBrIf(self,vtn_name, vbr_name, if_name, details=0):
        if details==0:
            method=urllib.quote('vtns/'+vtn_name+'/vbridges/'+vbr_name+'/interfaces/'+if_name+'.json')
        elif details==1:
            method='vtns/'+vtn_name+'/vbridges/'+vbr_name+'/interfaces/'+if_name+'/detail.json'
        else:
            return ValueError
        return self.do(method, http_method='GET')

    def DeletevBrIf(self,vtn_name, vbr_name, if_name):
        method='vtns/'+vtn_name+'/vbridges/'+vbr_name+'/interfaces/'+if_name+'.json'
        return self.do(method, http_method='DELETE')

    def ShowvBRMACTable(self,vtn_name, vbr_name, type='', if_name=''):
        #TODO: Implement processing of type and if_name parameters. 4.7.1 webapi_user_guide
        method='vtns/'+vtn_name+'/vbridges/'+vbr_name+'/macentries.json'
        return self.do(method, http_method='GET')


    #vLinks

    def ListvLinks(self, vtn_name):
        method='vtns/'+vtn_name+'/vlinks.json'
        return self.do(method, http_method='GET')

    def CreatevBrvLink(self, vtn_name, vbr_name, if_name, vtnnode_name, vtnnode_if_name, vlk_name=''):
        method='vtns/'+vtn_name+'/vlinks.json'
        payload={"vlink" : {"vbr_name" : vbr_name,"if_name" : if_name,
                            "vtnnode_name" : vtnnode_name,"vtnnode_if_name" : vtnnode_if_name}}
        if len(vlk_name)>0:
            payload['vlink']['vlk_name']=vlk_name
        a=self.do(method,content=self.build_content(payload), http_method='POST')
        return a
    #VLAN Operations

    def MapVlanvBr(self):
        """
        4.8.1 Map VLAN to vBridge
        Before specifying dp_id, input the "vlan-connect enable" command on pfcshell. When not specifying
        dp_id, do not input this command!
        I do not know why so, API and CLI configuration should not depend on each other.
        """
        #TODO Implement this strange function

    def ShowVlanvBR(self, vtn_name, vbr_name):
        method='vtns/vtn_name/vbridges/'+vbr_name+'/vlanmaps.json'
        return self.do(method, http_method='GET')



    def UnmapVlanvBr(self, vtn_name, vbr_name, dp_id, ):
        """
        vlanmap_id specified in the URI and dp_id, vlan_id, and no_vlan_id specified in the query character
        string must match those returned by the response body described in "4.8.1 Map VLAN to vBridge
        (page 123)" and "4.8.2 Show VLAN map on vBridge (page 126)" .
        """
        method='vtns/'+vtn_name+'/vbridges/'+vbr_name+'/vlanmaps/vlanmap_id.json'



    #vRouter Operations

    def ListvRouters(self,vtn_name):
        method = 'vtns/'+vtn_name+'/vrouters.json'
        return self.do(method, http_method='GET')

    def CreatevRouter(self, vtn_name, vrt_name):
        method = 'vtns/'+vtn_name+'/vrouters.json'
        payload = {"vrouter" : {"vrt_name" : vrt_name}}
        return self.do(method, content=self.build_content(payload), http_method='POST')

    def ShowvRouter(self, vtn_name, vrt_name, details=0):
        if details == 0:
            method = 'vtns/'+vtn_name+'/vrouters/'+vrt_name+'.json'
        elif details == 1:
            method= 'vtns/'+vtn_name+'/vrouters/'+vrt_name+'/detail.json'
        else:
            return ValueError
        return self.do(method, http_method='GET')

    def DeletevRouter(self, vtn_name, vrt_name):
        method='vtns/'+vtn_name+'/vrouters/'+vrt_name+'.json'
        return self.do(method, http_method='DELETE')


    #vRouter Interfaces

    def ListvRouterIf(self, vtn_name, vrt_name):
        method='vtns/'+vtn_name+'/vrouters/'+vrt_name+'/interfaces.json'
        return self.do(method, http_method='GET')

    def CreatevRouterIf(self, vtn_name, vrt_name, if_name=''):
        method='vtns/'+vtn_name+'/vrouters/'+vrt_name+'/interfaces.json'
        payload={"interface" : {}  }
        if len(if_name)>0:
            payload['interface']['if_name']=if_name
        a=self.do(method, content=self.build_content(payload), http_method='POST')
        return a

    def RegvRouterIfIP(self, vtn_name, vrt_name, if_name, ipaddr, netmask='', prefix=''):
        method='vtns/'+vtn_name+'/vrouters/'+vrt_name+'/interfaces/'+if_name+'/ipaddress.json'
        if len(netmask)>0 and len(prefix)==0:
            payload={"interface" : {"ipaddr" : ipaddr, "netmask" : netmask}}
        elif len(prefix)>0 and len(netmask)==0:
            payload={"hostaddress" : {"ipaddr" : ipaddr, "prefix" : prefix}}
        else:
            return ValueError
        return self.do(method,content=self.build_content(payload), http_method='POST')

		
    #vExternals

    def ListVEX(self, vtn_name):
        method='vtns/'+vtn_name+'/vexternals.json'
        return self.do(method, http_method='GET')

    def CreateVEX(self,vtn_name, vex_name):
        method='vtns/'+vtn_name+'/vexternals.json'
        payload={"vexternal" : {"vex_name" : vex_name}}
        return self.do(method, content=self.build_content(payload), http_method='POST')

    def ShowVEX(self,vtn_name, vex_name, details=0):
        if details==0:
            method='vtns/'+vtn_name+'/vexternals/'+vex_name+'.json'
        elif details==1:
            method='vtns/'+vtn_name+'/vexternals/'+vex_name+'/detail.json'
        else:
            return ValueError
        return self.do(method, http_method='GET')

    def DeleteVEX(self, vtn_name, vex_name):
        method='vtns/'+vtn_name+'/vexternals/'+vex_name+'.json'
        return self.do(method, http_method='DELETE')

    def CreateVEXIf(self, vtn_name, vex_name, if_name=''):
        method='vtns/'+vtn_name+'/vexternals/'+vex_name+'/interfaces.json'
        if len(if_name)>0:
            payload={"interface" : {"if_name" : if_name}}
        else:
            payload=''
        return self.do(method, content=self.build_content(payload), http_method='POST')

    def MapPortVEX(self,vtn_name, vex_name, dp_id, port_name):
        """
        A combination of dp_id and port_name cannot be specified with trunk_port_name at the same time.
        :param vtn_name: Up to 31 characters including one-byte alphanumeric characters and underbars
        :param vex_name: Up to 31 characters including one-byte alphanumeric characters and underbars
        :param dp_id: hhhh-hhhh-hhhh-hhhh format (h: Hexadecimal number)
        :param trunk_port_name: Up to 31 characters including one-byte alphanumeric characters and underbars
        :param port_name: Up to 15 characters including ascii alphanumeric characters except for a question mark (?)
        :param vlan_id: Decimal number (1 to 4095) - optional, mandatory if vlan-connect enable
        :param tagged: {true|false} - optional
        """
        method='vtns/'+vtn_name+'/vexternals/'+vex_name+'/ofsmap.json'
        payload={"ofsmap" : {
            "dp_id" : dp_id,
            "port_name" : port_name,
            }}
        return self.do(method, content=self.build_content(payload), http_method='PUT')

    def ShowPortVEX(self,vtn_name, vex_name):
        method='vtns/'+vtn_name+'/vexternals/'+vex_name+'/ofsmap.json'
        return self.do(method, http_method='GET')

    def UnmapPortVEX(self, vtn_name, vex_name, dp_id, port_name, trunk_port_name, vlan_id, tagged):
         method='vtns/'+vtn_name+'/vexternals/'+vex_name+'/ofsmap.json'
         payload={"ofsmap" : {
            "dp_id" : dp_id,
            "trunk_port_name" : trunk_port_name,
            "port_name" : port_name,
            "vlan_id" : vlan_id,
            "tagged" : tagged
            }}
         return self.do(method, http_method='DELETE', content=self.build_content(payload))

    #TODO Modify to support restrict functionality
    def CreateFlowlist(self, fl_name, ip_version):
        method='flowlists.json'
        payload ={ "flowlist" : {
            "fl_name" : fl_name,
            "ip_version" : ip_version
            }}

        return self.do(method, http_method='POST', content=self.build_content(payload))


    def CreateFlowlistEntry(self, fl_name, seqnum, macdstaddr='', macsrcaddr='', macethertype='', macvlanpriority='', ipdstaddr='', ipdstaddrprefix='',
                            ipsrcaddr='', ipsrcaddrprefix='',  ipdscp='',ipproto='', l4dstport='', l4dstendport='', l4srcport='', l4srcendport= '',
                            icmptypenum='', icmpcodenum=''):
        method='flowlists/'+fl_name+'/flowlistentries.json'
        payload= { "flowlistentry" : {
            "seqnum" : seqnum,
            }}

        #check optional paramaters. if they are set add them to the payload

        if(len(macdstaddr)>0):
            payload["flowlistentry"]["macdstaddr"] = macdstaddr

        if(len(macsrcaddr)>0):
            payload["flowlistentry"]["macsrcaddr"] = macsrcaddr

        if(len(macethertype) >0):
            payload["flowlistentry"]["macethertype"] = macethertype

        if(len(macvlanpriority) >0):
            payload["flowlistentry"]["macvlanpriority"] = macvlanpriority

        if(len(ipdstaddr) >0):
            if(len(ipdstaddrprefix) > 0):
                payload['flowlistentry']['ipdstaddr'] = ipdstaddr
                payload['flowlistentry']['ipdstaddrprefix'] = ipdstaddrprefix
            else:
                return ValueError

            if(len(ipsrcaddr)>0):
                if(len(ipsrcaddrprefix)>0):
                    payload['flowlistentry']['ipsrcaddr'] = ipsrcaddr
                    payload['flowlistentry']['ipsrcaddrprefix'] = ipsrcaddrprefix
                else:
                    return ValueError

            if(len(ipdscp)>0):
                payload['flowlistentry']['ipdscp'] = ipdscp

            if(len(ipproto)>0):
                payload['flowlistentry']['ipproto'] = ipproto

            if(len(l4dstport)>0):
                payload["flowlistentry"]["l4dstport"] = l4dstport

            if(len(l4dstendport)>0):
                payload["flowlistentry"]["l4dstendport"] = l4dstendport

            if(len(l4srcport)>0):
                payload["flowlistentry"]["l4srcport"] = l4srcport

            if(len(l4srcendport)>0):
                payload["flowlistentry"]["l4srcendport"] = l4srcendport

            if(len(icmptypenum)>0):
                payload["flowlistentry"]["icmptypenum"] = icmptypenum

            if(len(icmpcodenum)>0):
                payload["flowlistentry"]["icmpcodenum"] =icmpcodenum

        return self.do(method, http_method='POST', content=self.build_content(payload))


    def CreatevBrFlowfilter(self, vtn_name, vbr_name, if_name, ff_type ):
        method = 'vtns/'+vtn_name+'/vbridges/'+vbr_name+'/interfaces/'+if_name+'/flowfilters.json'
        payload= { "flowfilter" : {
            "ff_type" : ff_type,
            }}
        return self.do(method, http_method='POST', content=self.build_content(payload))

    def CreateVtnFlowfilter(self, vtn_name, ff_type):
        method='vtns/'+vtn_name+'/flowfilters.json'
        payload = { "flowfilter" :{
            "ff_type" : ff_type
        }}
        return self.do(method, http_method='POST', content=self.build_content(payload))

    def CreateVtnFlowfilterEntry(self, vtn_name, ff_type, seqnum,fl_name, action_type, set=0, priority='',dscp='',nmg_name=''):
        method = 'vtns/'+vtn_name+'/flowfilters/'+ff_type+'/flowfilterentries.json'

        if(set==0):
            payload= {"flowfilterentry" : {
                "action_type": action_type,
                "seqnum": seqnum,
                "fl_name": fl_name
            }}
        else:
             payload= {"flowfilterentry" : {
                "action_type": action_type,
                "seqnum": seqnum,
                "fl_name": fl_name,
                "set": {}
            }}
        #check optional paramaters and if they are set add them to the payload
        if(set!=0):
            if(len(priority) >0):
                payload["flowfilterentry"]["set"]["priority"] = priority
            if(len(dscp) >0):
                payload["flowfilterentry"]["set"]["dscp"] = dscp
            if len(priority) == 0 and len(dscp) == 0:
                return ValueError
        #in case that the controller is ODL
        else:
            if(len(priority) >0):
                payload["flowfilterentry"]["priority"] = priority
            if(len(dscp) >0):
                payload["flowfilterentry"]["dscp"] = dscp
            if len(priority) == 0 and len(dscp) == 0:
                return ValueError




        if(len(nmg_name)>0):
            payload["flowfilterentry"]["nmg_name"] = nmg_name
        return self.do(method, http_method='POST', content=self.build_content(payload))

    def UpdateVtnFlowfilterEntry(self,vtn_name, ff_type, seqnum,fl_name,action_type, dscp="", priority="",op="" ):
        method = 'vtns/'+vtn_name+'/flowfilters/'+ff_type+'/flowfilterentries/'+seqnum+'.json'
        if(len(op)>0 ):
            payload= {"flowfilterentry" : {
                "action_type": action_type,
                "seqnum": seqnum,
                "fl_name": fl_name,
                "op" : op,
                "set": {
                    "dscp" : dscp,
                    "priority": priority

                }
            }}
        else:
            payload= {"flowfilterentry" : {
                "action_type": action_type,
                "seqnum": seqnum,
                "fl_name": fl_name,    
                "dscp" : dscp,
                "priority":priority
            
            }}
        return self.do(method, http_method='PUT', content=self.build_content(payload))

    def DeleteVtnFlowfilterEntry(self,vtn_name,ff_type,seqnum):
        method='vtns/'+vtn_name+'/flowfilters/'+ff_type+'/flowfilterentries/'+seqnum+'.json'
        return self.do(method, http_method='DELETE')

    def DeleteFlowlist(self,fl_name):
        method='flowlists/'+fl_name+'.json'
        return self.do(method, http_method='DELETE')

    def CreatevBrFlowfilterEntry(self, vtn_name, vbr_name, if_name, ff_type, seqnum, fl_name, action_type, set=0, priority='', dscp='',
                                 nmg_name=''):
        method = 'vtns/'+vtn_name+'/vbridges/'+vbr_name+'/interfaces/'+if_name+'/flowfilters/'+ff_type+'/flowfilterentries.json'
        if(set==0):
            payload= {"flowfilterentry" : {
                "action_type": action_type,
                "seqnum": seqnum,
                "fl_name": fl_name
            }}
        else:
             payload= {"flowfilterentry" : {
                "action_type": action_type,
                "seqnum": seqnum,
                "fl_name": fl_name,
                "set": {}
            }}
        #check optional paramaters and if they are set add them to the payload
        if(set!=0):
            if(len(priority) >0):
                payload["flowfilterentry"]["set"]["priority"] = priority
            if(len(dscp) >0):
                payload["flowfilterentry"]["set"]["dscp"] = dscp
            if len(priority) == 0 and len(dscp) == 0:
                return ValueError




        if(len(nmg_name)>0):
            payload["flowfilterentry"]["nmg_name"] = nmg_name

        return self.do(method, http_method='POST', content=self.build_content(payload))

    def ShowVTNStations(self):
         method='vtnstations.json'
         return self.do(method, http_method='GET')

    def getAlarms(self):
        method = 'pfc/alarms'
        return str(self.do(method, http_method='GET'))


   
    ''' Path Policy Operations'''
    def showPathPolicies(self):
        method='realnetwork/pathpolicies.json'
        return self.do(method,http_method='GET')

    def createPathPolicy(self,policy_id):
        method = 'realnetwork/pathpolicies.json'
        payload = {
            "pathpolicy":{
                "ppol_idx" : policy_id
            }
        }
        return self.do(method, http_method='POST', content=self.build_content(payload))

    def showPathPolicy(self,policy_id):
        method = 'realnetwork/pathpolicies/'+policy_id+'.json'
        return self.do(method,http_method='GET')

    def deletePathPolicy(self,policy_id):
        method = 'realnetwork/pathpolicies/'+policy_id+'.json'
        return self.do(method,http_method='DELETE')
    

    '''LinkWeight Operations'''

    def showLinkWeights(self,policy_id):
        method = 'realnetwork/pathpolicies/'+policy_id+'/linkweights.json'
        return self.do(method,http_method='GET')

    def addLinkWeight(self,policy_id, dp_id, port_name, weight):
        method = 'realnetwork/pathpolicies/'+policy_id+'/linkweights.json'
        payload = {
            "linkweight": {
                "dp_id" : dp_id,
                "port_name" : port_name,
                "weight" : weight,
                "op" : "add"
            }
        }
        return self.do(method, http_method="PUT", content=self.build_content(payload))

    def deleteLinkWeight(self,policy_id, dp_id, port_name, weight):
        method = 'realnetwork/pathpolicies/'+policy_id+'/linkweights.json'
        payload = {
            "linkweight": {
                "dp_id" : dp_id,
                "port_name" : port_name,
                "weight" : weight,
                "op" : "delete"
            }
        }
        return self.do(method, http_method="PUT", content=self.build_content(payload))

    ''' VTN Path Map Operations '''    
    def createVTNPathMapEntry(self,vtn_name,seqnum,fl_name,policy_id):
        method = 'vtns/'+vtn_name+'/pathmap/pathmapentries.json'
        payload = {
            "pathmapentry" : {
                "seqnum" : seqnum,
                "fl_name" : fl_name,
                "ppol_idx" : policy_id
            }
        }
        return self.do(method, http_method='POST', content=self.build_content(payload))

    def deleteVTNPathMapEntry(self, vtn_name, seqnum):
        method = 'vtns/'+vtn_name+'/pathmap/pathmapentries/'+seqnum+'.json'
        return self.do(method, http_method='DELETE')

    def updateVTNPathMapEntry(self,vtn_name,seqnum,fl_name,policy_id,age_out_timer=""):
        method = 'vtns/'+vtn_name+'/pathmap/pathmapentries/'+seqnum+'.json'
        payload = {
            "pathmapentry":{
                "fl_name" : fl_name,
                "ppol_idx" : policy_id,
                "op":"add"

            }
        }
        if(len(age_out_timer)>0):
            payload['pathmapentry']['ageout_time'] = age_out_timer

        return self.do(method, http_method='PUT', content=self.build_content(payload))

    def showVTNPathMap(self,vtn_name):
        method = 'vtns/'+vtn_name+'/pathmap.json'
        return self.do(method,http_method='GET')

    def showVTNPathMapDetails(self,vtn_name):
        method = 'vtns/'+vtn_name+'/pathmap/detail.json'
        return self.do(method,http_method='GET')

    def listSequenceNumbersVTNPathMapEntry(self,vtn_name):
        method = 'vtns/'+vtn_name+'/pathmap/pathmapentries.json'
        return self.do(method,http_method='GET')

    def showVTNPathMapEntry(self,vtn_name,seqnum):
        method = 'vtns/'+vtn_name+'/pathmap/pathmapentries/'+seqnum+'.json'
        return self.do(method,http_method='GET')

    def showVTNPathMapEntryDetails(self,vtn_name,seqnum):
        method = 'vtns/'+vtn_name+'/pathmap/pathmapentries/'+seqnum+'/detail.json'
        return self.do(method,http_method='GET')

    ''' QoS Rate Limiting 3 colors '''
    ''' Operate Policing Profile '''
    def createPolicingProfile(self,profile_name):
        method = 'policing/profiles.json'
        payload = {
            "policing": {
                "profile" :{
                    "prf_name" : profile_name
                }
            }
        }
        return self.do(method,http_method='POST',content=self.build_content(payload))

    def listPolicingProfiles(self):
        method = 'policing/profiles.json'
        return self.do(method,http_method='GET')

    def showPolicyProfile(self,profile_name):
        method = 'policing/profiles/'+profile_name+'.json'
        return self.do(method,http_method='GET')

    def deletePolicingProfile(self,profile_name):
        method = 'policing/profiles/'+profile_name+'.json'
        return self.do(method,http_method="DELETE")

    ''' Operate Policing Profile Entry'''
    def createPolicingProfileEntry(self,profile_name,seqnum,fl_name,rate_unit,cir,pir,green_action,yellow_action,red_action,ga_dscp="",
        ga_drop_precedence="",ya_priority="",ya_dscp="",ya_drop_precedence="",cbs="",pbs="",ga_priority="",ra_priority="",ra_dscp="",
        ra_drop_precedence=""):

        method = 'policing/profiles/'+profile_name+'/profileentries.json'
        payload = {
            "profileentry":{
                "seqnum" : seqnum,
                "fl_name" : fl_name,
                "tworatethreecolor" : {
                    "meter":{
                        "rateunit": rate_unit,
                        "cir" : cir,
                        "pir" : pir
                    },
                    "greenaction" : {
                        "green_action" : green_action
                    },
                    "yellowaction":{
                        "yellow_action" : yellow_action
                    },
                    "redaction":{
                        "red_action" : red_action
                    }

                }
            }
        }
        # add optional parameters if specified
        if(len(cbs)>0):
            payload['profileentry']['tworatethreecolor']['meter']['cbs'] = cbs
        if(len(pbs)>0):
            payload['profileentry']['tworatethreecolor']['meter']['pbs'] = pbs
        if(len(ga_priority)>0):
            payload['profileentry']['tworatethreecolor']['greenaction']['ga_priority'] = ga_priority
        if(len(ga_dscp)>0):
            payload['profileentry']['tworatethreecolor']['greenaction']['ga_dscp'] = ga_dscp
        if(len(ga_drop_precedence)>0):
            payload['profileentry']['tworatethreecolor']['greenaction']['ga_drop_precedence'] = ga_drop_precedence
        if(len(ya_priority)>0):
            payload['profileentry']['tworatethreecolor']['yellowaction']['ya_priority'] = ya_priority
        if(len(ya_dscp)>0):
            payload['profileentry']['tworatethreecolor']['yellowaction']['ya_dscp'] = ya_dscp
        if(len(ya_drop_precedence)>0):
            payload['profileentry']['tworatethreecolor']['yellowaction']['ya_drop_precedence'] = ya_drop_precedence
        if(len(ra_priority)>0):
            payload['profileentry']['tworatethreecolor']['redaction']['ra_priority'] = ra_priority
        if(len(ra_dscp)>0):
            payload['profileentry']['tworatethreecolor']['redaction']['ra_dscp'] = ra_dscp
        if(len(ra_drop_precedence)>0):
            payload['profileentry']['tworatethreecolor']['redaction']['ra_drop_precedence'] = ra_drop_precedence

        return self.do(method,http_method='POST',content=self.build_content(payload))



    ''' Extra Methods. These methods are to be executed for VTN Manager only '''
    def VTNManagerCreateFlowCondition(self,fl_name,ipsrc,ipdst,srcport,dstport,protocol):
        method= 'controller/nb/v2/vtn/default/flowconditions/'+fl_name
        payload = {
            "name" : fl_name,
            "match" : [ 
            {
                "index" : 1 , 
                "inetMatch" : {
                    "inet4": {
                        "src" : ipsrc,
                        "dst" : ipdst
                    }
                },
                "l4Match":{
                    protocol : {
                        "src" : srcport,
                        "dst" : dstport
                    }
                }
            },
            {
              "index" : 2 , 
                "inetMatch" : {
                    "inet4": {
                        "src" : ipdst,
                        "dst" : ipsrc
                    }
                },
                "l4Match":{
                    protocol : {
                        "src" : dstport,
                        "dst" : srcport
                    }
                }
            }
            ]
        }

        return self.do(method,http_method='PUT',content=self.build_content(payload))


    def VTNManagerCreateFlowFilter(self,vtn_name, seqnum, fl_name, priority):
        method = 'controller/nb/v2/vtn/default/vtns/'+vtn_name+'/flowfilters/'+str(seqnum)
        payload = {
            "index": seqnum,
            "condition": fl_name,
            "filterType" : { "pass" :{}},
            "actions" : [ {
                "vlanpcp" : {"priority": priority}
            }
            ] 
        }

        return self.do(method,http_method='PUT', content=self.build_content(payload))
        
    def VTNManagerDeleteFlowCondition(self,fl_name):
        method = 'controller/nb/v2/vtn/default/flowconditions/'+fl_name
        return self.do(method,http_method='DELETE')

    def VTNManagerDeleteFlowFilter(self,vtn_name,seqnum):
        method = 'controller/nb/v2/vtn/default/vtns/'+vtn_name+'/flowfilters/'+ str(seqnum)
        return self.do(method,http_method='DELETE')


    def VTNManagerListVTN(self):
        method = 'controller/nb/v2/vtn/default/vtns'
        return self.do(method,http_method='GET')
    ''' Extra methods for VTN Coordinator'''
    def CreateController(self,controller_id,ipaddr,controller_type,version,audit_status):
        method = 'controllers.json'
        payload = {
            'controller' :{
                'controller_id' : controller_id,
                'ipaddr' : ipaddr,
                'type' : controller_type,
                'version': version,
                'auditstatus' : audit_status
            }
        }
        return self.do(method, http_method='POST',content=self.build_content(payload))

    def ListSwitches(self,controller_id):
        method = 'controllers/'+controller_id + '/switches.json'
        return self.do(method, http_method='GET')

    def ListSwitchPorts(self,controller_id,switch_id):
        method = 'controllers/'+controller_id + '/switches/'+switch_id+'/ports.json'
        return self.do(method,http_method='GET')

    def ConfigureMapping(self,vtn_name,vbr_name,if_name,switch_id,port_id,vlan_id,tagged):
        method = 'vtns/'+vtn_name+'/vbridges/'+vbr_name+'/interfaces/'+if_name+'/portmap.json'
        logical_port_id = 'PP-OF:' + switch_id + '-'+ port_id
        payload = {
            'portmap':{
                'logical_port_id' : logical_port_id,
                'vlan_id' : vlan_id,
                'tagged' : tagged
            }
        }
        return self.do(method,http_method='PUT', content=self.build_content(payload))

    def CreateVBridgeODL(self, vtn_name, vbr_name,controller_id,domain_id):
        method = 'vtns/'+vtn_name+'/vbridges.json'
        payload = {
            "vbridge":{
                "vbr_name" : vbr_name,
                "controller_id" : controller_id,
                "domain_id" : domain_id
            }
        }
        return self.do(method,http_method='POST',content=self.build_content(payload))



