'''
*
*           VTN-based RTM Network Service 
* 
*   file: \rtm-api\api\v1_0\policies.py 
* 
* This software contributed by NEC under Apache 2.0 license for open source use. This software is supplied under the terms of the OpenSourceSDN Apache 2.0 license agreement 
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

from flask import request, jsonify
from ..models import db, Policy, ClassDscp, FlowfilterEntryMap
from ..decorators import json, paginate, etag
from . import api


#Get All policies#
@api.route('/policies/', methods=['GET'])
def get_policies():
    return jsonify(json_list = [i.to_json() for i in Policy.query.all()])

#Get a policy using the Policy id#
@api.route('/policies/<int:id>', methods=['GET'])
@json
def get_policy_by_id(id):
    return Policy.query.get_or_404(id)

#Create a new policy#
@api.route('/policies/', methods=['POST'])
@json
def add_policy():
    #add the policy to the database#
    policy = Policy().from_json(request.json)
    db.session.add(policy)
    db.session.commit()

    #create the vtn configuration according to policy information#
    mapping = ClassDscp.query.get_or_404(policy.application_class)
    flowfilter=policy.create_vtn_config(mapping.dscp)

    #save the mapping between flowlist and flowfilter entry for future reference#
    flowlistname = 'flowlist'+ str(policy.policy_id)
    entry = FlowfilterEntryMap().init(flowfilter,flowlistname)
    db.session.add(entry)
    db.session.commit()

   
    return request.json, 201

#Delete a policy#
@api.route('/policies/<int:id>', methods=['DELETE'])
@json
def delete_policy(id):
    policy = Policy.query.get_or_404(id)

    #before deleting remove the vtn configuration for the policy element#
    flowlistname = 'flowlist' + str(policy.policy_id)
    entry = FlowfilterEntryMap.query.get_or_404(flowlistname)
    policy.delete_vtn_config(entry.flowfilterentry)

    #also delete the flowfilterentrymap from the database#
    db.session.delete(entry)
    db.session.delete(policy)
    db.session.commit()
    return {}

#Update a policy#
@api.route('/policies/<int:id>', methods=['PUT'])
@json
def update_policy(id):
    policy = Policy.query.get_or_404(id)
    policy.from_json(request.json)

    
    #Before updating the database update the vtn configuration. If the application class is changed then we have to change the dscp
    #value of the flowfilter entry
    flowlistname = 'flowlist' + str(policy.policy_id)
    entry = FlowfilterEntryMap.query.get_or_404(flowlistname)

    #get the new dscp value by querying the mapping table using the application class#
    mapping = ClassDscp.query.get_or_404(policy.application_class)
    policy.update_vtn_config(flowlistname,entry.flowfilterentry, mapping.dscp)
    db.session.add(policy)
    db.session.commit()
    return {}

@api.route('/policies/<int:id>', methods=['PATCH'])
@json
def patch_policy(id):
    policy= Policy.query.get_or_404(id)
    policy.from_json_patch(request.json)

    
    #Before updating the database update the vtn configuration. If the application class is changed then we have to change the dscp
    #value of the flowfilter entry
    
    flowlistname = 'flowlist' + str(policy.policy_id)
    entry = FlowfilterEntryMap.query.get_or_404(flowlistname)

    #get the new dscp value by querying the mapping table using the application class#
    mapping = ClassDscp.query.get_or_404(policy.application_class)
    policy.update_vtn_config(flowlistname,entry.flowfilterentry, mapping.dscp)
    db.session.add(policy)
    db.session.commit()
    return {}