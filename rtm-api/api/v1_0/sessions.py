'''
*
*           VTN-based RTM Network Service 
* 
*   file: \rtm-api\api\v1_0\sessions.py 
* 
*  This software contributed by NEC under Apache 2.0 license for open source use. This software is supplied under the terms of the OpenSourceSDN Apache 2.0 license agreement 
*     Copyright (c) 2015 NEC Europe Ltd.    Copyright (c) 2015 NEC Europe Ltd. 
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

from flask import request, jsonify
from ..models import db, Session, Media, ClassDscp,FlowfilterEntryMap
from ..errors import ValidationError, conflict
from ..decorators import json, paginate, etag
from . import api
import json as default_json
from sqlalchemy.ext.declarative import DeclarativeMeta
import sqlalchemy.orm
from sqlalchemy import desc
import urllib2

'''
This file implements all the operations for Session class
Also at the end of the file there are some methods for Admission Control and Traffic Engineering
'''

# Parse the configuration file to get the details regarding the sflow agent #
json_data = open('config')
configData = default_json.load(json_data)

sflowIp = configData['sflow']['sflowIp']
sflowPort = configData['sflow']['sflowPort']
sflowAgent1 = configData['sflow']['agents']['agent1Ip']
sflowAgent2 = configData['sflow']['agents']['agent2Ip']
controller2Exists=1
try:
    controller2Type = configData['controller2']['type']
except:
    controller2Exists=0





#Get all sessions#
@api.route('/sessions/', methods=['GET'])
def get_sessions():
    
    result =dict()
    i=1
    sessions= Session.query.all()
    for session in sessions:
        medias = Media.query.filter(Media.session_id==session.session_id).all()
        session_res = session.to_json()
        result['session'+str(i)] = session_res
        j=1
        for media in medias:
            result['session'+str(i)]['sessionElement']['media'+str(j)]=media.to_json()
            j=j+1
        i=i+1
    return jsonify(result)

    
    

#Get a specific session#
@api.route('/sessions/<int:id>', methods=['GET'])
def get_session_id(id):
    #Get all medias for the session. The problem is how to create a json with the jsonify result encapsulated#
    session = Session.query.get_or_404(id)
    json_res  = session.to_json()
    medias = Media.query.filter(Media.session_id==id).all()
    i=1
    for media in medias:
        json_res['sessionElement']['media'+str(i)] = media.to_json()
        i=i+1    
    return jsonify(json_res)

#create a new session#
@api.route('/sessions/', methods=['POST'])
def new_session():
    #add the new session to the database#
    session = Session().from_json(request.json)
    media = Media().from_json(request.json)

    '''
    1. Get Least Congested path
    2. Find the Congestion of the least Congested path
    3. Decide the granted Class
    '''
    path=1
    try:
        path = getLeastCongestedPath()
        pathCongestion = getPathCongestion(path)
        grantedClass = decideClass(path,pathCongestion,media.average_bandwidth,media.application_class)
        media.actual_class = grantedClass
    except:
        media.actual_class = media.application_class
    
    try:
        #query database to find the dscp value to the give application class#
        mapping = ClassDscp.query.get_or_404(media.actual_class)  
        media.dscp = mapping.dscp 
        media.priority = mapping.priority    
        db.session.add(session)
        db.session.add(media)
        db.session.commit()
    except:
       raise ValidationError('Duplicate Session or Media')
    
    #create the appropriate vtn configuration (flowlist and flowfilter) according to media element information#
    flowfilter_path=media.create_vtn_config(mapping.dscp, str(path),mapping.priority)

    flowfilter = flowfilter_path['flowfilter']
    pathentry = flowfilter_path['pathentry']
    flowlistname = media.session_id + '_' + media.media_type
    #store in the database which flowlist is mapped to which sequence number of the flowfilter#
    entry = FlowfilterEntryMap().init(flowfilter,flowlistname, pathentry)
    db.session.add(entry)
    db.session.commit()
    return get_session_id(session.session_id)

#delete a session#
@api.route('/sessions/<int:id>',methods=['DELETE'])
@json
def delete_session(id):
    session = Session.query.get_or_404(id)
    #before deleting we have to delete all the vtn configuration for all the media elements of the session#
    medias = Media.query.filter(Media.session_id==id).all()
    for media in medias:
        flowlistname = media.session_id + '_' + media.media_type
        entry = FlowfilterEntryMap.query.get_or_404(flowlistname)
        media.delete_vtn_config(entry.flowfilterentry, entry.path)
        db.session.delete(entry)
    db.session.delete(session)
    db.session.commit()
    return {}

#TODO# 
#update a session to be decided#
@api.route('/sessions/<int:id>', methods=['PUT'])
@json
def edit_session(id):

    return {}


#Adds a new media element to an existing session#
@api.route('/sessions/<int:id>/media/', methods=['POST'])
def new_media(id):
    try:
        media = Media().from_json(request.json)
        media.set_session_id(id)

        '''
        1. Get Least Congested path
        2. Find the Congestion of the least Congested path
        3. Decide the granted Class
        '''
        path=1
        try:
            path = getLeastCongestedPath()
            pathCongestion = getPathCongestion(path)
            grantedClass = decideClass(path,pathCongestion,media.average_bandwidth,media.application_class)
            media.actual_class = grantedClass
        except:
            media.actual_class=media.application_class
        
        #query database to find the dscp value to the give application class#
        mapping = ClassDscp.query.get_or_404(media.actual_class)  
        media.dscp = mapping.dscp
        media.priority = mapping.priority     
           
        db.session.add(media)
        db.session.commit()
    except:
        raise ValidationError('Duplicate Media Element')

    #create the appropriate vtn configuration (flowlist and flowfilter) according to media element information#
    flowfilter_path=media.create_vtn_config(mapping.dscp,str(path),mapping.priority)
    flowfilter = flowfilter_path['flowfilter']
    pathentry = flowfilter_path['pathentry']
    #store in the database which flowlist is mapped to which sequence number of the flowfilter#
    flowlistname = media.session_id + '_' + media.media_type
    entry = FlowfilterEntryMap().init(flowfilter,flowlistname,pathentry)
    db.session.add(entry)
    db.session.commit()
    return get_media(media.session_id,media.media_type)


#Deletes a media element from a session#
@api.route('/sessions/<int:id>/media/<path:type>', methods=['DELETE'])
@json
def delete_media(id,type):
    media = Media.query.get_or_404((type,id))
    #before deleting remove the vtn configuration for the media element#
    flowlistname = media.session_id + '_' + media.media_type
    entry = FlowfilterEntryMap.query.get_or_404(flowlistname)
    media.delete_vtn_config(entry.flowfilterentry,entry.path)
    #also delete the flowfilterentrymap from the database#
    db.session.delete(entry)
    #delete the media info from the database#
    db.session.delete(media)
    db.session.commit()
    return {}

#Get a media element for a session#
@api.route('/sessions/<int:id>/media/<path:type>', methods=['GET'])
@json
def get_media(id,type):
    return Media.query.get_or_404((type,id))

#Get all media elements for a session#
@api.route('/sessions/<int:id>/media/', methods=['GET'])

def get_medias(id):
    return jsonify(json_list = [i.to_json() for i in Media.query.filter(Media.session_id==id).all()])
    

#Update a media element for a session#
@api.route('/sessions/<int:id>/media/<path:type>', methods=['PUT'])
def update_media(id,type):
    media = Media.query.get_or_404((type,id))
    #Save temporary the previous values of the fields that we don't want to allow the user to change them#
    prev_type = media.media_type
    prev_source_ip = media.source_ip_address
    prev_source_port = media.source_ip_port
    prev_destination_ip = media.destination_ip_address
    prev_destination_port = media.destination_ip_port
    #Load to the media element the data that the user provided from json#
    media.from_json(request.json)
    #check if any of the above fields are changed. If yes raise a validation error and don't proceed#
    if(prev_type!=media.media_type):
        raise ValidationError('Can not change the mediaType')
    if(prev_source_ip!=media.source_ip_address):
        raise ValidationError('Can not change the sourceIpAddress')
    if(prev_source_port!=media.source_ip_port):
        raise ValidationError('Can not change the sourceIpPort')
    if(prev_destination_ip!=media.destination_ip_address):
        raise ValidationError('Can not change the destinationIpAddress')
    if(prev_destination_port!=media.destination_ip_port):
        raise ValidationError('Can not change the destinationIpPort')
    media.set_session_id(id)


    '''
    1. Get Least Congested path
    2. Find the Congestion of the least Congested path
    3. Decide the granted Class
    '''
    path=1
    try:
        path = getLeastCongestedPath()
        pathCongestion = getPathCongestion(path)
        grantedClass = decideClass(path,pathCongestion,media.average_bandwidth,media.application_class)
        media.actual_class = grantedClass
    except:
        media.actual_class = media.application_class

    #Before updating the database update the vtn configuration. If the application class is changed then we have to change the dscp
    #value of the flowfilter entry
    flowlistname = str(media.session_id) + '_' + str(media.media_type)
    entry = FlowfilterEntryMap.query.get_or_404(flowlistname)
    #get the new dscp value by querying the mapping table using the application class#
    mapping = ClassDscp.query.get_or_404(media.actual_class)
    media.update_vtn_config(flowlistname,entry.flowfilterentry, mapping.dscp, path, entry.path, mapping.priority)
    media.dscp = mapping.dscp
    media.priority = mapping.priority
    db.session.add(media)
    db.session.commit()
    return get_media(media.session_id,media.media_type)
        
#Patch a media element for a session#
@api.route('/sessions/<int:id>/media/<path:type>', methods=['PATCH'])
def patch_media(id,type):
    media = Media.query.get_or_404((type,id))
    
    #Save temporary the previous values of the fields that we don't want to allow the user to change them#
    prev_type = media.media_type
    prev_source_ip = media.source_ip_address
    prev_source_port = media.source_ip_port
    prev_destination_ip = media.destination_ip_address
    prev_destination_port = media.destination_ip_port
    
    #Load to the media element the data that the user provided from json#
    media.from_json_patch(request.json)
    
    #check if any of the above fields are changed. If yes raise a validation error and don't proceed#
    if(prev_type!=media.media_type):
        raise ValidationError('Can not change the mediaType')
    if(prev_source_ip!=media.source_ip_address):
        raise ValidationError('Can not change the sourceIpAddress')
    if(prev_source_port!=media.source_ip_port):
        raise ValidationError('Can not change the sourceIpPort')
    if(prev_destination_ip!=media.destination_ip_address):
        raise ValidationError('Can not change the destinationIpAddress')
    if(prev_destination_port!=media.destination_ip_port):
        raise ValidationError('Can not change the destinationIpPort')
    
    media.set_session_id(id)

    
    '''
    1. Get Least Congested path
    2. Find the Congestion of the least Congested path
    3. Decide the granted Class
    '''
    path=1
    try:
        path = getLeastCongestedPath()
        pathCongestion = getPathCongestion(path)
        grantedClass = decideClass(path,pathCongestion,media.average_bandwidth,media.application_class)
        media.actual_class = grantedClass
    except:
        media.actual_class = media.application_class


    #Before updating the database update the vtn configuration. If the application class is changed then we have to change the dscp
    #value of the flowfilter entry#
    flowlistname = str(media.session_id) + '_' + str(media.media_type)
    entry = FlowfilterEntryMap.query.get_or_404(flowlistname)
    #get the new dscp value by querying the mapping table using the application class#
    mapping = ClassDscp.query.get_or_404(media.actual_class)
    media.update_vtn_config(flowlistname,entry.flowfilterentry, mapping.dscp, path, entry.path, mapping.priority)
    media.dscp = mapping.dscp
    media.priority = mapping.priority

    db.session.add(media)
    db.session.commit()
    return get_media(media.session_id,media.media_type)


'''
Module that decides which class would be assigned to a request with requestedClass
Takes into consideration the path congestion that is provided. 
'''

def decideClass(path,pathCongestion, requestedBandwidth,requestedClass):
    # Get all the registered classes and their DSCP value#
    classes_dscps=ClassDscp.query.order_by(desc('dscp'))
    classes = []
    for class_dscp in classes_dscps:
        classes.append(class_dscp.app_class)
    
    availableBandwidth = float(10000000) - float(pathCongestion) 
    requested_safety = float(requestedBandwidth)+float(2000000)
    #if network is not congested assign the requested class#
    if(availableBandwidth> requested_safety or (getClassCongestion(path,classes[len(classes)-1])>getClassCongestion(path,classes[0]))):
        grantedClass = requestedClass
    elif(availableBandwidth>=float(requestedBandwidth)):
        if(classes.index(requestedClass)!=len(classes)-1):
            grantedClass = classes[classes.index(requestedClass)+1]
        else:
            grantedClass = classes[len(classes)-1]
            
    else:
        grantedClass= classes[len(classes)-1]
    return grantedClass

'''Method that calculates the Congestion of the two available paths in our topology and Returns
    the index of the path with the less congestion
    1. Calculate the congestion for all the paths
    2. If the congestion difference is less than 1Mbits/s return the path with the lower priority traffic
    3. Else return the path with the lower overall bandwidth

'''
def getLeastCongestedPath():

    # In case that a second controller is not available then we have only one path so return 1 #
    if(controller2Exists==0):
        return 1

    # Get all the registered classes and their DSCP value#
    classes_dscps=ClassDscp.query.order_by(desc('dscp'))
    classes = []
    for class_dscp in classes_dscps:
        classes.append(class_dscp.app_class)

    path1 = []
    path2 = []
    #Get each class congestion for path1 #
    for class_name in classes:
        content = default_json.loads(urllib2.urlopen('http://'+sflowIp+':'+sflowPort+'/dump/'+sflowAgent1+'/'+class_name+'/json').read())
        if(len(str(content))>10):
            path1.append(content[0]['metricValue'])
        else:
            path1.append(0.0)

    #Get each class congestion for path2#
    for class_name in classes:
        content = default_json.loads(urllib2.urlopen('http://'+sflowIp+':'+sflowPort+'/dump/'+sflowAgent2+'/'+class_name+'/json').read())
        if(len(str(content))>10):
            path2.append(content[0]['metricValue'])
        else:
            path2.append(0.0)
    

    sum_path1 = 0
    sum_path2 = 0
    for ban1 in path1:
        sum_path1 = sum_path1 + float(ban1)
    for ban2 in path2:
        sum_path2 = sum_path2 + float(ban2)

    if(sum_path1 - sum_path2 < 1 ):
        return 1
    difference = sum_path1- sum_path2
    if(sum_path1 > sum_path2):
        # If the congestion of the paths is approximately the same #
        if(difference<=1000000):
            # Return the path with the smaller higher priority traffic #
            if(path1[0]>path2[0]):
                return 2
            else:
                return 1
        return 2
    else:
        return 1

''' Method that calculates the congestion of the given path
    Return a float representation of active throughput

'''
def getPathCongestion(path):
    if(path==1):
        agent = sflowAgent1
    else:
        agent = sflowAgent2

    # Get all the registered classes and their DSCP value#
    classes_dscps=ClassDscp.query.order_by(desc('dscp'))
    classes = []
    for class_dscp in classes_dscps:
        classes.append(class_dscp.app_class)

    path_bandwidths = []

    for class_name in classes:
        content = default_json.loads(urllib2.urlopen('http://'+sflowIp+':'+sflowPort+'/dump/'+agent+'/'+class_name+'/json').read())
        if(len(str(content))>10):
            path_bandwidths.append(content[0]['metricValue'])

    #compute the overall bandwidth#
    overall_bandwidth =0
    for ban in path_bandwidths:
        overall_bandwidth = overall_bandwidth + float(ban)

    #convert Mbytes to Mbits#
    overall_bandwidth = overall_bandwidth * 8
    return overall_bandwidth
   
'''
    Method that calculates the congestion for a specific path and a specific class
    Returns a float representation of the active throughput
'''
def getClassCongestion(path,className):
    if(path==1):
        agent = sflowAgent1
    else:
        agent = sflowAgent2
    url = 'http://'+sflowIp+':'+sflowPort+'/dump/'+ agent+'/'+className+'/json'
    content = default_json.loads(urllib2.urlopen(url).read())
    if(len(str(content))>10):
        return float(content[0]['metricValue'])
    return float(0)
