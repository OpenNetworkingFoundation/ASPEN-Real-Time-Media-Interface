'''
*
*           VTN-based RTM Network Service 
* 
*   file: \rtm-api\api\models.py 
* 
*          This software contributed by NEC under Apache 2.0 license for open source use. This software is supplied under the terms of the OpenSourceSDN Apache 2.0 license agreement 
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
 
'''


from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.exceptions import NotFound
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import url_for, current_app
from flask.ext.sqlalchemy import SQLAlchemy
from .helpers import args_from_url
from .errors import ValidationError
import ast
import json
from utilities import ip_address_is_valid, get_base_address, get_prefix,port_range_is_valid, get_start_port, get_end_port

from webapijson import WebAPIJSON

db = SQLAlchemy()
flowfilterentriescounter = 0
pathMapCounter = 0
controller2Exists=1
# Open Configuration file and find the Usernames,passwords and IP's for the controllers #
json_data = open('config')
configData = json.load(json_data)

# Parse the type of markings that the user wants to apply DSCP or Priority #
markings = configData['markings']

controller1Type = configData['controller1']['type']
controller1Ip = configData['controller1']['ipAddress']
controller1Port = configData['controller1']['webApiPort']
controller1Username = configData['controller1']['webApiUserName']
controller1Password = configData['controller1']['webApiPassword']

try:
    controller2Type = configData['controller2']['type']
    controller2Ip = configData['controller2']['ipAddress']
    controller2Port = configData['controller2']['webApiPort']
    controller2Username = configData['controller2']['webApiUserName']
    controller2Password = configData['controller2']['webApiPassword']
except:
    controller2Exists=0


#Information about the connection with the vtn api#
if(controller1Type=="odl"):
    connection = WebAPIJSON(controller1Username, controller1Password)
    connection.base_url="http://"+controller1Ip+":"+controller1Port+"/"
else:
    connection = WebAPIJSON(controller1Username, controller1Password)
    connection.base_url="https://"+controller1Ip+":"+controller1Port+"/"
if(controller2Exists==1):
    if(controller2Type=="odl"):
        connection2 = WebAPIJSON(controller2Username, controller2Password)
        connection2.base_url="http://"+controller2Ip+":"+controller2Port+"/"
    else:
        connection2 = WebAPIJSON(controller2Username, controller2Password)
        connection2.base_url="https://"+controller2Ip+":"+controller2Port+"/"


#class that is used to know which flow filter sequence number is matched to which flowlist#
class FlowfilterEntryMap(db.Model):
    __tablename__='flowfilterentries'
    flowlist = db.Column(db.String(64), primary_key=True)
    flowfilterentry = db.Column(db.String(64))
    path = db.Column(db.String(64))
    
    # method that is used to initiate a new flowfilterentry #
    def init(self, flowfilter, flowlist , path):
        self.flowfilterentry = flowfilter
        self.flowlist = flowlist
        self.path = path
        return self

#Class that is used for mapping purposes. Maps the application class with the DSCP value and the priority#
class ClassDscp(db.Model):
    __tablename__='dscpmappings'
    app_class = db.Column(db.String(64), primary_key=True)
    dscp = db.Column(db.Integer, unique=True)
    priority = db.Column(db.Integer, unique=True)

    def to_json(self):
        return {
            'dscpMapping':{
             'applicationClass': self.app_class,
	         'dscp' :self.dscp,
             'priority' : self.priority
		}
	}
     	
    def from_json(self,json):
        try:
            self.app_class = json['applicationClass']
        except KeyError:
            raise ValidationError('Invalid Input')
        try:
            self.dscp = json['dscp']
            if(int(self.dscp)<0 or int(self.dscp)>63):
                raise ValidationError('Dscp Value should be between 0 and 63')
        except KeyError:
            raise ValidationError('Invalid Input')

        try:
            self.priority = json['priority']
            if(int(self.priority)<0 or int(self.priority)>7):
                raise ValidationError('Priority should be between 0 and 7')
        except KeyError:
            ValidationError('Invalid Input' )
	return self
    
#Class that is used for authentication of the users of the API#
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True)
    password_hash = db.Column(db.String(128))

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_auth_token(self, expires_in=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expires_in)
        return s.dumps({'id': self.id}).decode('utf-8')

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get(data['id'])

#Class that is used for interacting with the database regarding the Session Element#
class Session(db.Model):
    __tablename__ = 'sessions'
    session_id = db.Column('session_id', db.String(64), primary_key=True)
    start_time = db.Column('start_time', db.String(64))
    group_id = db.Column('group_id', db.String(64))
    medias = db.relationship(
        'Media',
        backref=db.backref('Session', lazy='joined'),
         cascade='all, delete, delete-orphan',single_parent=True )
    
    def to_json(self):
        return {
             'sessionElement':{
            'sessionId': self.session_id,
            'startTime': self.start_time,
            'groupId': self.group_id
            }
            
        }

    def from_json(self, json):
        try:
	    self.session_id = json['sessionId']
	    self.start_time = json['startTime']
            self.group_id = json['groupId']
	except KeyError as e:
            raise ValidationError('Invalid Input for Session')
	return self


#Class that is interacting with the database for the Media Element#
class Media(db.Model):
    #class attributes#
    __tablename__ = 'media'
    media_type = db.Column('type',db.String(64), primary_key=True)
    session_id = db.Column('session_id', db.String(64), db.ForeignKey('sessions.session_id'),primary_key=True) 
    age_out_timer = db.Column(db.String(64))
    flow_id = db.Column(db.String(64))
    ip_address_type = db.Column(db.String(64))
    source_ip_address = db.Column(db.String(64))
    source_ip_port = db.Column(db.String(64))
    destination_ip_address =db.Column(db.String(64))
    destination_ip_port = db.Column(db.String(64))
    transport = db.Column(db.String(64))
    actual_class = db.Column(db.String(64))
    dscp = db.Column(db.String(64))
    priority = db.Column(db.String(64))
    actual_bandwidth = db.Column(db.String(64))
    application_class = db.Column(db.String(64))
    average_bandwidth = db.Column(db.String(64))
    min_bandwidth = db.Column(db.String(64))
    max_bandwidth = db.Column(db.String(64))

    

    #Method that converts the atrributes of the Class to json#
    def to_json(self):
        return {
            'mediaElement':{
    	        'mediaType': self.media_type,
                'ageOutTimer':self.age_out_timer,
                'flowElement':{
                    'ipAddressType': self.ip_address_type,
    	           ' transportType': self.transport,
                    'sourceIpAddress': self.source_ip_address,
                    'sourceIpPort' : self.source_ip_port,
    	            'destinationIpAddress': self.destination_ip_address,
                    'destinationIpPort': self.destination_ip_port,
    	            'flowId': self.flow_id
                },
                'requestedQos':{
            	    'applicationClass': self.application_class,
            	    'averageBandwidth': self.average_bandwidth,
            	    'minBandwidth': self.min_bandwidth,
            	    'maxBandwidth': self.max_bandwidth
    	     },	
    	        'grantedQos':{
        	       'actualClass': self.actual_class,
        	       'dscp' : self.dscp,
                   'priority':self.priority,
        	       'actualBandwidth': self.actual_bandwidth
                }

                }
            }

    def set_session_id(self,id):
        self.session_id=id
    # Parses input json to the model class attributes #
    def from_json(self, json):
        try:
            self.session_id = json['sessionId']
        except KeyError:
            self.session_id=""
        #These fields are mandatory#
        try:

            #Parse and Validate mediaType#
            self.media_type = json['mediaElement']['mediaType']
            if(self.media_type != "video" and self.media_type != "audio" and self.media_type != "conference"):
                raise ValidationError('Invalid mediaType')

            #Parse and Validate ipAddressType#
            self.ip_address_type = json['mediaElement']['flowElement']['ipAddressType']
            if(self.ip_address_type != "ip" and self.ip_address_type != "ipv6"):
                raise ValidationError('Invalid ipAddressType')

            #Parse and Validate transportType#
            self.transport = json['mediaElement']['flowElement']['transportType']
            if(self.transport!="udp" and self.transport!="tcp"):
                raise ValidationError('Invalid transportType')
            #Parse and Validate sourceIpAddress#
            self.source_ip_address = json['mediaElement']['flowElement']['sourceIpAddress']
            if(ip_address_is_valid(self.source_ip_address) == False):
                raise ValidationError('Invalid sourceIpAddress (valid format xxx.xxx.xxx.xxx/prefix)')
            #Parse and Validate SourceIpPort#
            self.source_ip_port = json['mediaElement']['flowElement']['sourceIpPort']
            try:
                source_port_value = int(self.source_ip_port)
                if(source_port_value<0 or source_port_value>65535):
                    raise ValidationError('Invalid sourceIpPort value')
            except ValueError:
                raise ValidationError('Invalid sourceIpPort')

            #Parse and Validate destinationIpaddress#
            self.destination_ip_address = json['mediaElement']['flowElement']['destinationIpAddress']
            if(ip_address_is_valid(self.destination_ip_address) == False):
                raise ValidationError('Invalid destinationIpAddress (valid format xxx.xxx.xxx.xxx/prefix)')
            #Parse and Validate destinationIpPort#
            self.destination_ip_port = json['mediaElement']['flowElement']['destinationIpPort']
    	    try:
                destination_port_value = int(self.destination_ip_port)
                if(destination_port_value<0 or destination_port_value>65535):
                    raise ValidationError('Invalid destinationIpPort value')
            except ValueError:
                raise ValidationError('Invalid destinationIpPort')     
       
            self.flow_id = json['mediaElement']['flowElement']['flowId']
        
            #Parse and Validate applicationClass#
            self.application_class = json['mediaElement']['requestedQos']['applicationClass']
            try:
                res=ClassDscp.query.get_or_404(self.application_class)
            except:
                raise ValidationError('Invalid applicationClass. Make sure that the class is defined in dscpmappings')

            #Parse and Validate averageBandwidth#
            self.average_bandwidth = json['mediaElement']['requestedQos']['averageBandwidth']
            try:
                average_bandwidth_value = int(self.average_bandwidth)
                if(average_bandwidth_value<0):
                   raise ValidationError('averageBandwidth should be positive') 
            except ValueError:
                raise ValidationError('Invalid averageBandwidth')
        except KeyError as e: 
            raise ValidationError('Invalid Input')
           
        #These fields are optional so if not specified add space#
        try:
            self.actual_class = json['mediaElement']['grantedQos']['actualClass']
            try:
                if(len(self.actual_class)>0):
                    res=ClassDscp.query.get_or_404(self.actual_class)
            except:
                raise ValidationError('Invalid actual Class. Make sure that the class is defined in dscpmappings')
        except KeyError:
            self.actual_class=""

        #Parse and Validate dscp#
        try:
            self.dscp = json['mediaElement']['grantedQos']['dscp']
            try:
                dscp_value = int(self.dscp)
                if(dscp_value<0 or dscp_value>63):
                    raise ValidationError('Invalid dscp value')
            except ValueError:
                #This check is for the case that the user specified the element with empty string as value#
                if(len(self.dscp)>0):
                    raise ValidationError('Invalid dscp')
        except KeyError:
            self.dscp=""

        # Parse and Validate Priority#
        try:
            self.priority = json['mediaElement']['grantedQos']['priority']
            try:
                if(int(self.priority)<0 or int(self.priority)>7):
                    raise ValidationError('Invalid priority value')
            except ValueError:
                if(len(priority)>0):
                    raise ValidationError('Invalid priority')
        except KeyError:
            self.priority=""
           

        #Parse and Validate actualBandwidth#        
        try:
            self.actual_bandwidth= json['mediaElement']['grantedQos']['actualBandwidth']
            try:
                actual_bandwidth_value = int(self.actual_bandwidth)
                if(actual_bandwidth_value<0):
                    raise ValidationError('Invalid actualBandwidth value')
            except ValueError:
                if(len(self.actual_bandwidth)>0):
                    raise ValidationError('Invalid actualBandwidth')            
        except KeyError:
            self.actual_bandwidth=""

        #Parse and Validate minBandwidth#
        try: 	
            self.min_bandwidth = json['mediaElement']['requestedQos']['minBandwidth']
            try:
                min_bandwidth_value = int(self.min_bandwidth)
                if(min_bandwidth_value<0):
                    raise ValidationError('Invalid minBandwidth value')
            except ValueError:
                if(len(self.min_bandwidth)>0):
                    raise ValidationError('Invalid minBandwidth')
        except KeyError:
            self.min_bandwidth=""
            

        #Parse and Validate maxBandwidth#
        try:
            self.max_bandwidth= json['mediaElement']['requestedQos']['maxBandwidth']
            try:
                max_bandwidth_value = int(self.max_bandwidth)
                if(max_bandwidth_value<0):
                    raise ValidationError('Invalid maxBandwidth value')
            except ValueError:
                if(len(self.max_bandwidth)>0):
                    raise ValidationError('Invalid maxBandwidth')
        except KeyError:
            self.max_bandwidth=""

        #Parse and Validate ageOutTimer#
        try:
           self.age_out_timer = json['mediaElement']['ageOutTimer']
           try:
               age_out_timer_value = int(self.age_out_timer)
               if(age_out_timer_value<0):
                   raise ValidationError('Invalid ageOutTimer value')
           except ValueError:
               if(len(self.age_out_timer)>0):
                   raise ValidationError('Invalid ageOutTimer')
        except KeyError:
            self.age_out_timer=""
        return self

    #The reason of a new method is because all the fields are mandatory in Patch operation#
    def from_json_patch(self,json):
        
        try:
            a = json['mediaElement']
        except KeyError:
            raise ValidationError('Invalid Input. Missing mediaElement')

        #This is because on create a new media to an existing session the user doesn't add the session id as json. 
        #SO we check if the length equals zero then we add the session id that the user specified in the url.
        #
        try:
            self.session_id = json['sessionId']
        except KeyError:
            self.session_id=""
        
        #These fields are mandatory#

        #Parse and Validate mediaType#
        try:
            self.media_type = json['mediaElement']['mediaType']
            if(self.media_type != "video" and self.media_type != "audio" and self.media_type != "conference"):
                raise ValidationError('Invalid mediaType')
        except KeyError:
            pass
        #Parse and Validate ipAddressType#     
        try:
            self.ip_address_type = json['mediaElement']['flowElement']['ipAddressType']
            if(self.ip_address_type != "ip" and self.ip_address_type != "ipv6"):
                raise ValidationError('Invalid ipAddressType')
        except KeyError:
            pass

        #Parse and Validate transportType#
        try:
            self.transport = json['mediaElement']['flowElement']['transportType']
            if(self.transport!="udp" and self.transport!="tcp"):
                raise ValidationError('Invalid transportType')
        except KeyError:
            pass

        #Parse and Validate sourceIpAddress#
        try:
            self.source_ip_address = json['mediaElement']['flowElement']['sourceIpAddress']
            if(ip_address_is_valid(self.source_ip_address) == False):
                raise ValidationError('Invalid sourceIpAddress (valid format xxx.xxx.xxx.xxx/prefix)')
        except KeyError:
            pass

        #Parse and Validate SourceIpPort#
        try:
            self.source_ip_port = json['mediaElement']['flowElement']['sourceIpPort']
            try:
                source_port_value = int(self.source_ip_port)
                if(source_port_value<0 or source_port_value>65535):
                    raise ValidationError('Invalid sourceIpPort value')
            except ValueError:
                raise ValidationError('Invalid sourceIpPort')
        except KeyError:
            pass

        #Parse and Validate destinationIpaddress#
        try:
            self.destination_ip_address = json['mediaElement']['flowElement']['destinationIpAddress']
            if(ip_address_is_valid(self.destination_ip_address) == False):
                raise ValidationError('Invalid destinationIpAddress (valid format xxx.xxx.xxx.xxx/prefix)')
            #Parse and Validate destinationIpPort#
            self.destination_ip_port = json['mediaElement']['flowElement']['destinationIpPort']
            try:
                destination_port_value = int(self.destination_ip_port)
                if(destination_port_value<0 or destination_port_value>65535):
                    raise ValidationError('Invalid destinationIpPort value')
            except ValueError:
                raise ValidationError('Invalid destinationIpPort')
        except KeyError:
            pass     
        try:
            self.flow_id = json['mediaElement']['flowElement']['flowId']
        except KeyError:
            pass
        #Parse and Validate applicationClass#
        try:
            self.application_class = json['mediaElement']['requestedQos']['applicationClass']
            try:
                res=ClassDscp.query.get_or_404(self.application_class)
            except: 
                raise ValidationError('Invalid Class. Make sure that the class is defined in dscpmappings')
        except KeyError:
            pass
        #Parse and Validate averageBandwidth#
        try:
            self.average_bandwidth = json['mediaElement']['requestedQos']['averageBandwidth']
            try:
                average_bandwidth_value = int(self.average_bandwidth)
                if(average_bandwidth_value<0):
                   raise ValidationError('averageBandwidth should be positive') 
            except ValueError:
                raise ValidationError('Invalid averageBandwidth')
        except KeyError: 
            pass
           
        #These fields are optional so if not specified add space#
        try:
            self.actual_class = json['mediaElement']['grantedQos']['actualClass']
            try:
                if(len(self.actual_class)>0):
                    res=ClassDscp.query.get_or_404(self.actual_class)
            except: 
                raise ValidationError('Invalid Class. Make sure that the class is defined in dscpmappings')
        except KeyError:
            pass

        #Parse and Validate dscp#
        try:
            self.dscp = json['mediaElement']['grantedQos']['dscp']
            try:
                dscp_value = int(self.dscp)
                if(dscp_value<0 or dscp_value>63):
                    raise ValidationError('Invalid dscp value')
            except ValueError:
                #This check is for the case that the user specified the element with empty string as value#
                if(len(self.dscp)>0):
                    raise ValidationError('Invalid dscp')
        except KeyError:
            pass

        #Parse and Validate priority#
        try:
            self.priority = json['mediaElement']['grantedQos']['priority']
            try:
                if(int(self.priority)<0 or int(self.priority)>7):
                    raise ValidationError('Invalid priority value')
            except ValueError:
                #This check is for the case that the user specified the element with empty string as value#
                if(len(self.priority)>0):
                    raise ValidationError('Invalid priority')
        except KeyError:
            pass

           

        #Parse and Validate actualBandwidth #       
        try:
            self.actual_bandwidth= json['mediaElement']['grantedQos']['actualBandwidth']
            try:
                actual_bandwidth_value = int(self.actual_bandwidth)
                if(actual_bandwidth_value<0):
                    raise ValidationError('Invalid actualBandwidth value')
            except ValueError:
                if(len(self.actual_bandwidth)>0):
                    raise ValidationError('Invalid actualBandwidth')            
        except KeyError:
            pass

        #Parse and Validate minBandwidth#
        try:    
            self.min_bandwidth = json['mediaElement']['requestedQos']['minBandwidth']
            try:
                min_bandwidth_value = int(self.min_bandwidth)
                if(min_bandwidth_value<0):
                    raise ValidationError('Invalid minBandwidth value')
            except ValueError:
                if(len(self.min_bandwidth)>0):
                    raise ValidationError('Invalid minBandwidth')
        except KeyError:
            pass
            

        #Parse and Validate maxBandwidth#
        try:
            self.max_bandwidth= json['mediaElement']['requestedQos']['maxBandwidth']
            try:
                max_bandwidth_value = int(self.max_bandwidth)
                if(max_bandwidth_value<0):
                    raise ValidationError('Invalid maxBandwidth value')
            except ValueError:
                if(len(self.max_bandwidth)>0):
                    raise ValidationError('Invalid maxBandwidth')
        except KeyError:
            pass

        #Parse and Validate ageOutTimer#
        try:
           self.age_out_timer = json['mediaElement']['ageOutTimer']
           try:
               age_out_timer_value = int(self.age_out_timer)
               if(age_out_timer_value<0):
                   raise ValidationError('Invalid ageOutTimer value')
           except ValueError:
               if(len(self.age_out_timer)>0):
                   raise ValidationError('Invalid ageOutTimer')
        except KeyError:
            pass
        return self

    # Method that is used to install flowlists and flowfilters to Controller1 1 and Path Policies and Path Maps to Controller2 #
    def create_vtn_config(self,dscp_value, path, priority):
        #access the global variables. We use globals to make sure  that we don't overwrite already existing entries
        global flowfilterentriescounter
        global pathMapCounter
        global markings
        pathMapCounter=pathMapCounter+1
        flowfilterentriescounter=flowfilterentriescounter+1

        # retrieve vtn info according to controller type#
        if(controller1Type=='pfc'):
            list_vtns = connection.ListVTN()
            my_vtn=list_vtns['vtns'][0]['vtn_name']
        else:
            list_vtns = connection.VTNManagerListVTN()
            my_vtn=list_vtns['vtn'][0]['name']

        flowlist_seqnum=1
        flowlistname = self.session_id + '_' + self.media_type

        # Find protocol number according to protocol #
        proto_number=0
        if(self.transport=="udp"):
            proto_number=17
        elif(self.transport=="tcp"):
            proto_number=6
        #Create flowlist for controller 1
        if(controller1Type=="pfc"):
            connection.CreateFlowlist(fl_name=flowlistname,ip_version='ip')
        # if controller 2 exists create the same config as above
        if(controller2Exists==1):
            connection2.CreateFlowlist(fl_name=flowlistname,ip_version='ip')


        #create a flowlist entries
        if(controller1Type=="pfc"):
            connection.CreateFlowlistEntry(fl_name=flowlistname,seqnum=flowlist_seqnum,ipdstaddr = get_base_address(\
                self.destination_ip_address), ipdstaddrprefix=get_prefix(self.destination_ip_address), ipsrcaddr = get_base_address(\
                self.source_ip_address), ipsrcaddrprefix=get_prefix(self.source_ip_address), l4dstport = self.destination_ip_port,\
                l4srcport=self.source_ip_port,ipproto=str(proto_number))

        # if controller 2 exists create the same config as above
        if(controller2Exists==1):
            connection2.CreateFlowlistEntry(fl_name=flowlistname,seqnum=flowlist_seqnum,ipdstaddr = get_base_address(\
                self.destination_ip_address), ipdstaddrprefix=get_prefix(self.destination_ip_address), ipsrcaddr = get_base_address(\
                self.source_ip_address), ipsrcaddrprefix=get_prefix(self.source_ip_address), l4dstport = self.destination_ip_port,\
                l4srcport=self.source_ip_port,ipproto=str(proto_number))
        
        #create another flowlistEntry with the opposite direction#
        flowlist_seqnum = flowlist_seqnum+1
        if(controller1Type=='pfc'):
            connection.CreateFlowlistEntry(fl_name=flowlistname,seqnum=flowlist_seqnum,ipdstaddr = get_base_address(\
                self.source_ip_address), ipdstaddrprefix=get_prefix(self.source_ip_address), ipsrcaddr = get_base_address(\
                self.destination_ip_address), ipsrcaddrprefix=get_prefix(self.destination_ip_address), l4dstport = self.source_ip_port,\
                l4srcport=self.destination_ip_port, ipproto=str(proto_number))
        if(controller2Exists==1):
            connection2.CreateFlowlistEntry(fl_name=flowlistname,seqnum=flowlist_seqnum,ipdstaddr = get_base_address(\
                self.source_ip_address), ipdstaddrprefix=get_prefix(self.source_ip_address), ipsrcaddr = get_base_address(\
                self.destination_ip_address), ipsrcaddrprefix=get_prefix(self.destination_ip_address), \
                l4dstport = self.source_ip_port, l4srcport=self.destination_ip_port, ipproto=str(proto_number))
            connection2.createVTNPathMapEntry(vtn_name=my_vtn,seqnum=pathMapCounter, fl_name=flowlistname, policy_id=path )

        # if this is the first time that we call the method then create the flow filter
        if( flowfilterentriescounter==1 and controller1Type=="pfc"):
            connection.CreateVtnFlowfilter(vtn_name=my_vtn,ff_type="in")

        # If the controller is odl create the configuration using VTN Manager Rest Api #
        # We use VTN Manager due to Bugs to VTN Coordinator
        if(controller1Type=="odl"):
            connection.VTNManagerCreateFlowCondition(fl_name=flowlistname, ipsrc=get_base_address(self.source_ip_address),\
             ipdst=get_base_address(self.destination_ip_address),srcport=int(self.source_ip_port),\
             dstport=int(self.destination_ip_port),protocol=self.transport)

            connection.VTNManagerCreateFlowFilter(vtn_name=my_vtn, seqnum=flowfilterentriescounter, fl_name=flowlistname, \
                priority=int(priority))

        #Create flowfilterentries in the case of Pflow Controller
        # We have to take into account which controller we use because of a difference in the Rest api between 
        #ODL and PFC (flowfilterentry) 
        if(controller1Type=="pfc"):
            if(markings=="dscp"):
                connection.CreateVtnFlowfilterEntry(vtn_name=my_vtn, ff_type="in",seqnum=flowfilterentriescounter,\
                    fl_name=flowlistname, action_type="pass", set=1, dscp = str(dscp_value) )
            else:
                 connection.CreateVtnFlowfilterEntry(vtn_name=my_vtn, ff_type="in",seqnum=flowfilterentriescounter,\
                    fl_name=flowlistname, action_type="pass", set=1, priority = str(priority) )
        #We return this data because we need to store it to Database. See sessions.py for more info
        return {"flowfilter":flowfilterentriescounter, "pathentry":pathMapCounter }

    # Method that is used to delete existing flowlists and flowfilters from Controller1 and existing Path Maps from Controller2#
    def delete_vtn_config(self,flowfilterentry, pathmapentry):
        #retrieve vtn name according to the controller type
        if(controller1Type=='pfc'):
            list_vtns = connection.ListVTN()
            my_vtn=list_vtns['vtns'][0]['vtn_name']
        else:
            list_vtns = connection.VTNManagerListVTN()
            my_vtn=list_vtns['vtn'][0]['name']
        flowlistname = self.session_id + '_' + self.media_type
        #delete flowlists and flowfilters according to the controller type
        if(controller1Type=="odl"):
            connection.VTNManagerDeleteFlowFilter(vtn_name=my_vtn,seqnum=flowfilterentry)
            connection.VTNManagerDeleteFlowCondition(flowlistname)

        else:
            connection.DeleteVtnFlowfilterEntry(vtn_name=my_vtn,ff_type="in",seqnum=flowfilterentry)
            connection.DeleteFlowlist(flowlistname)
        # also if a controller 2 exists delete flowlists and path map entries
        if(controller2Exists):
            connection2.DeleteFlowlist(flowlistname)
            connection2.deleteVTNPathMapEntry(vtn_name=my_vtn,seqnum=pathmapentry)



    # Method that is used to update the flowfilter entry from Controller1 in case that the user changed the application class using
    #PUT or PATCH request
    #
    def update_vtn_config(self,flowlist,flowfilterentry,new_dscp,path,policyId, priority):
        # find VTN Name #
        if(controller1Type=='pfc'):
            list_vtns = connection.ListVTN()
            my_vtn=list_vtns['vtns'][0]['vtn_name']
        else:
            list_vtns = connection.VTNManagerListVTN()
            my_vtn=list_vtns['vtn'][0]['name']
        #according to the type of the controller update  the flowfilters #
        if(controller1Type=="pfc"):
            if(markings=="dscp"):
                connection.UpdateVtnFlowfilterEntry(vtn_name=my_vtn, ff_type="in", seqnum=flowfilterentry, fl_name=flowlist,\
                    action_type="pass", op="add", dscp=new_dscp)
            else:
                connection.UpdateVtnFlowfilterEntry(vtn_name=my_vtn, ff_type="in", seqnum=flowfilterentry, fl_name=flowlist,\
                    action_type="pass", op="add", priority=priority)
        else:
            connection.VTNManagerCreateFlowFilter(vtn_name=my_vtn, seqnum=flowfilterentry, fl_name=flowlist, priority=int(priority))
        # if controller 2 exists update vtnpathmap
        if(controller2Exists==1):
            connection2.updateVTNPathMapEntry(vtn_name=my_vtn, seqnum=str(path),fl_name=flowlist,policy_id=policyId)


class Policy(db.Model):
    __tablename__ = 'policies'
    policy_id = db.Column( db.Integer,primary_key=True,autoincrement=True) 
    realm = db.Column(db.String(64))
    ip_address_type = db.Column(db.String(64))
    source_ip_address_range = db.Column(db.String(64))
    source_ip_port_range = db.Column(db.String(64))
    destination_ip_address_range =db.Column(db.String(64))
    destination_ip_port_range = db.Column(db.String(64))
    transport = db.Column(db.String(64))
    actual_class = db.Column(db.String(64))
    dscp = db.Column(db.String(64))
    actual_bandwidth = db.Column(db.String(64))
    application_class = db.Column(db.String(64))
    average_bandwidth = db.Column(db.String(64))
    min_bandwidth = db.Column(db.String(64))
    max_bandwidth = db.Column(db.String(64))
      
    
    
    
    
    def from_json(self,json):
        #Mandatory Fields#
    	try:
    	    #Parse and Validate ipAddressType#
            self.ip_address_type = json['policyElement']['flowSpecElement']['ipAddressType']
            if(self.ip_address_type!="ip" and self.ip_address_type!="ipv6"):
                raise ValidationError('Invalid ipAddressType')
    	    
            #Parse and Validate transportType#
            self.transport = json['policyElement']['flowSpecElement']['transportType']
            if(self.transport!="udp" and self.transport!="tcp"):
                raise ValidationError('Invalid transport Type')
               
    	   
            #Parse and Validate destinationIpaddress#
            self.source_ip_address_range = json['policyElement']['flowSpecElement']['sourceIpAddressRange']
            if(ip_address_is_valid(self.source_ip_address_range) == False):
                raise ValidationError('Invalid sourceIpAddressRange (valid format xxx.xxx.xxx.xxx/prefix)')

            #Parse and Validate sourceIpPortRange#
    	    self.source_ip_port_range = json['policyElement']['flowSpecElement']['sourceIpPortRange']
    	    if(port_range_is_valid(self.source_ip_port_range)==False):
                raise ValidationError('Invalid sourceIpPortRange')
    	    
            #Parse and Validate destinationIpRange#    
            self.destination_ip_address_range = json['policyElement']['flowSpecElement']['destinationIpAddressRange']
            if(ip_address_is_valid(self.destination_ip_address_range)==False):
                raise ValidationError('Invalid destinationIpAddressRange (valid format xxx.xxx.xxx.xxx/prefix)')

    	    #Parse and validate destinationIpPortRange#
            self.destination_ip_port_range = json['policyElement']['flowSpecElement']['destinationIpPortRange']
            if(port_range_is_valid(self.destination_ip_port_range)==False):
                raise ValidationError('Invalid destinationIpPortRange')
    	    
    	    
            #parse and Validate applicationClass#
            self.application_class = json['policyElement']['requestedQos']['applicationClass']
    	    try:
                res=ClassDscp.query.get_or_404(self.application_class)
            except: 
                raise ValidationError('Invalid Class. Make sure that the class is defined in dscpmappings')

    	    #parse and Validate averageBandwidth#
    	    self.average_bandwidth = json['policyElement']['requestedQos']['averageBandwidth']
    	    try:
                average_bandwidth_value = int(self.average_bandwidth)
                if(average_bandwidth_value<0):
                    raise ValidationError('averageBandwidth should be positive') 
            except ValueError:
                raise ValidationError('Invalid averageBandwidth')

    	except KeyError:
                raise ValidationError('Invalid input')
    	#Optional Fields. If are not set add assign them empty string#
     	try:
    	    self.actual_class = json['policyElement']['grantedQos']['actualClass']
            try:
                if(len(actual_class)):
                    res=ClassDscp.query.get_or_404(self.actual_class)
            except: 
                raise ValidationError('Invalid Class. Make sure that the class is defined in dscpmappings')
    	except KeyError:
    	    self.actual_class=""

            #Parse and Validate dscp#
            try:
    	        self.dscp = json['policyElement']['grantedQos']['dscp']
                try:
                    dscp_value = int(self.dscp)
                    if(dscp_value<0 or dscp_value>63):
                        raise ValidationError('Invalid dscp value')
                except ValueError:
                    #This check is for the case that the user specified the element with empty string as value#
                    if(len(self.dscp)>0):
                        raise ValidationError('Invalid dscp')
    	    except KeyError:
    	        self.dscp=""
    	
        #Parse and Validate actualBandwidth#        
    	try:
    	    self.actual_bandwidth= json['policyElement']['grantedQos']['actualBandwidth']
            try:
                actual_bandwidth_value = int(self.actual_bandwidth)
                if(actual_bandwidth_value<0):
                    raise ValidationError('Invalid actualBandwidth value')
            except ValueError:
                if(len(self.actual_bandwidth)>0):
                    raise ValidationError('Invalid actualBandwidth')            
    	except KeyError:
            self.actual_bandwidth=""

        #Parse and Validate minBandwidth#
    	try: 	
    	    self.min_bandwidth = json['policyElement']['requestedQos']['minBandwidth']
            try:
                min_bandwidth_value = int(self.min_bandwidth)
                if(min_bandwidth_value<0):
                    raise ValidationError('Invalid minBandwidth value')
            except ValueError:
                if(len(self.min_bandwidth)>0):
                    raise ValidationError('Invalid minBandwidth')
    	except KeyError:
                self.min_bandwidth=""

        #Parse and Validate maxBandwidth#
        try:
    	    self.max_bandwidth= json['policyElement']['requestedQos']['maxBandwidth']
            try:
                max_bandwidth_value = int(self.max_bandwidth)
                if(max_bandwidth_value<0):
                    raise ValidationError('Invalid maxBandwidth value')
            except ValueError:
                if(len(self.max_bandwidth)>0):
                    raise ValidationError('Invalid maxBandwidth')
        except KeyError:
            self.max_bandwidth=""
    	return self


    def from_json_patch(self,json):

        try:
            a = json['policyElement']
        except KeyError:
            raise ValidationError('Invalid Input. Missing policyElement')
        #Mandatory Fields#
        
        #Parse and Validate ipAddressType#
        try:
            self.ip_address_type = json['policyElement']['flowSpecElement']['ipAddressType']
            if(self.ip_address_type!="ip" and self.ip_address_type!="ipv6"):
                raise ValidationError('Invalid ipAddressType')
        except KeyError:
            pass

        #Parse and Validate transportType#
        try:
            self.transport = json['policyElement']['flowSpecElement']['transportType']
            if(self.transport!="udp" and self.transport!="tcp"):
                raise ValidationError('Invalid transport Type')
        except KeyError:
            pass
        #Parse and Validate sourceIpAddressRange#  
        try:    
            self.source_ip_address_range = json['policyElement']['flowSpecElement']['sourceIpAddressRange']
            if(ip_address_is_valid(self.source_ip_address_range)==False):
                raise ValidationError('Invalid sourceIpAddressRange (valid format xxx.xxx.xxx.xxx/prefix)')
        except KeyError:
            pass
        
        #Parse and Validate sourceIpPortRange#
        try:
            self.source_ip_port_range = json['policyElement']['flowSpecElement']['sourceIpPortRange']
            if(port_range_is_valid(self.source_ip_port_range)==False):
                raise ValidationError('Invalid sourceIpPortRange')
        except KeyError:
            pass

        #Parse and Validate destinationIpAddressRange#
        try:
            self.destination_ip_address_range = json['policyElement']['flowSpecElement']['destinationIpAddressRange']
            if(ip_address_is_valid(self.destination_ip_address_range)==False):
                raise ValidationError('Invalid destinationIpAddressRange (valid format xxx.xxx.xxx.xxx/prefix)')
        except KeyError:
            pass

        #Parse and validate destinationIpPortRange#
        try:
            self.destination_ip_port_range = json['policyElement']['flowSpecElement']['destinationIpPortRange']
            if(port_range_is_valid(self.destination_ip_port_range)==False):
                raise ValidationError('Invalid destinationIpPortRange')
        except KeyError:
            pass

        #parse and Validate applicationClass#  
        try: 
            self.application_class = json['policyElement']['requestedQos']['applicationClass']
            try:
                res=ClassDscp.query.get_or_404(self.application_class)
            except: 
                raise ValidationError('Invalid Class. Make sure that the class is defined in dscpmappings')
        except KeyError:
            pass

        #parse and Validate averageBandwidth#
        try:
            self.average_bandwidth = json['policyElement']['requestedQos']['averageBandwidth']
            try:
                average_bandwidth_value = int(self.average_bandwidth)
                if(average_bandwidth_value<0):
                    raise ValidationError('averageBandwidth should be positive') 
            except ValueError:
                raise ValidationError('Invalid averageBandwidth')
        except KeyError:
            pass

        #Parse and Validate actualClass#
        try:
            self.actual_class = json['policyElement']['grantedQos']['actualClass']
            try:
                if(len(self.actial_class)>0):
                    res=ClassDscp.query.get_or_404(self.actual)
            except: 
                raise ValidationError('Invalid Class. Make sure that the class is defined in dscpmappings')
        except KeyError:
            pass

        #Parse and Validate dscp#
        try:
            self.dscp = json['policyElement']['grantedQos']['dscp']
            try:
                dscp_value = int(self.dscp)
                if(dscp_value<0 or dscp_value>63):
                    raise ValidationError('Invalid dscp value')
            except ValueError:
                #This check is for the case that the user specified the element with empty string as value#
                if(len(self.dscp)>0):
                    raise ValidationError('Invalid dscp')
        except KeyError:
            pass
    
        #Parse and Validate actualBandwidth#        
        try:
            self.actual_bandwidth= json['policyElement']['grantedQos']['actualBandwidth']
            try:
                actual_bandwidth_value = int(self.actual_bandwidth)
                if(actual_bandwidth_value<0):
                    raise ValidationError('Invalid actualBandwidth value')
            except ValueError:
                if(len(self.actual_bandwidth)>0):
                    raise ValidationError('Invalid actualBandwidth')            
        except KeyError:
            pass

        #Parse and Validate minBandwidth#
        try:    
            self.min_bandwidth = json['policyElement']['requestedQos']['minBandwidth']
            try:
                min_bandwidth_value = int(self.min_bandwidth)
                if(min_bandwidth_value<0):
                    raise ValidationError('Invalid minBandwidth value')
            except ValueError:
                if(len(self.min_bandwidth)>0):
                    raise ValidationError('Invalid minBandwidth')
        except KeyError:
            pass

        #Parse and Validate maxBandwidth#
        try:
            self.max_bandwidth= json['policyElement']['requestedQos']['maxBandwidth']
            try:
                max_bandwidth_value = int(self.max_bandwidth)
                if(max_bandwidth_value<0):
                    raise ValidationError('Invalid maxBandwidth value')
            except ValueError:
                if(len(self.max_bandwidth)>0):
                    raise ValidationError('Invalid maxBandwidth')
        except KeyError:
            pass
        return self
    
    #Method that converts the atrributes of the Class to json#
    def to_json(self):
        return {
            'policyElement':{
            'policyId': self.policy_id,
            'flowSpecElement':{
	    'ipAddressType': self.ip_address_type,
            'transportType': self.transport,
            'sourceIpAddressRange': self.source_ip_address_range,
            'sourceIpPortRange' : self.source_ip_port_range,
	    'destinationIpAddressRange': self.destination_ip_address_range,
            'destinationIpPortRange': self.destination_ip_port_range
            },
            'requestedQos':{
	    'applicationClass': self.application_class,
	    'averageBandwidth': self.average_bandwidth,
	    'minBandwidth': self.min_bandwidth,
	    'maxBandwidth': self.max_bandwidth
	     },	
	    'grantedQos':{
	    'actualClass': self.actual_class,
	    'dscp' : self.dscp,
	    'actualBandwidth': self.actual_bandwidth
             }

            }
        }

    def create_vtn_config(self,dscp_value):
        global flowfilterentriescounter
        flowfilterentriescounter=flowfilterentriescounter+1
        if(controller1Type=='pfc'):
            list_vtns = connection.ListVTN()
            my_vtn=list_vtns['vtns'][0]['vtn_name']
        else:
            list_vtns = connection.VTNManagerListVTN()
            my_vtn=list_vtns['vtn'][0]['name']
        flowlist_seqnum=1
        flowlistname = 'flowlist' + str(self.policy_id)
        proto_number=0
        if(self.transport=="udp"):
            proto_number=17
        elif(self.transport=="tcp"):
            proto_number=6
        connection.CreateFlowlist(fl_name=flowlistname,ip_version='ip')
        #create a flowlist entry #
        connection.CreateFlowlistEntry(fl_name=flowlistname,seqnum=flowlist_seqnum,ipdstaddr = get_base_address(\
            self.destination_ip_address_range), ipdstaddrprefix=get_prefix(self.destination_ip_address_range),\
            ipsrcaddr = get_base_address(self.source_ip_address_range), ipsrcaddrprefix=get_prefix(self.source_ip_address_range),\
            l4dstport = get_start_port(self.destination_ip_port_range), l4dstendport = get_end_port(self.destination_ip_port_range),\
            l4srcport=get_start_port(self.source_ip_port_range), l4srcendport=get_end_port(self.source_ip_port_range),\
            ipproto=str(proto_number))

        if( flowfilterentriescounter==1):
            connection.CreateVtnFlowfilter(vtn_name=my_vtn,ff_type="in")
        connection.CreateVtnFlowfilterEntry(vtn_name=my_vtn, ff_type="in",seqnum=flowfilterentriescounter,fl_name=flowlistname,\
         action_type="pass", set=1, dscp = str(dscp_value) )

        return flowfilterentriescounter

    def delete_vtn_config(self,flowfilterentry):
        if(controller1Type=='pfc'):
            list_vtns = connection.ListVTN()
            my_vtn=list_vtns['vtns'][0]['vtn_name']
        else:
            list_vtns = connection.VTNManagerListVTN()
            my_vtn=list_vtns['vtn'][0]['name']
        connection.DeleteVtnFlowfilterEntry(vtn_name=my_vtn,ff_type="in",seqnum=flowfilterentry)
        flowlistname = 'flowlist' + str(self.policy_id)
        connection.DeleteFlowlist(flowlistname)

    def update_vtn_config(self,flowlist,flowfilterentry,new_dscp):
        if(controller1Type=='pfc'):
            list_vtns = connection.ListVTN()
            my_vtn=list_vtns['vtns'][0]['vtn_name']
        else:
            list_vtns = connection.VTNManagerListVTN()
            my_vtn=list_vtns['vtn'][0]['name']
        connection.UpdateVtnFlowfilterEntry(vtn_name=my_vtn, ff_type="in", seqnum=flowfilterentry, fl_name=flowlist,\
            action_type="pass", op="add", dscp=new_dscp)
        
	


