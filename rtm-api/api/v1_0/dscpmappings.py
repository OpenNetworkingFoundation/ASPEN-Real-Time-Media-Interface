'''
*
*           VTN-based RTM Network Service 
* 
*   file: \rtm-api\api\v1_0\dscpmappings.py 
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

from flask import request, jsonify
from ..models import db, ClassDscp
from ..decorators import json, paginate, etag
from . import api
import json as default_json
from ..webapijson import WebAPIJSON
from sqlalchemy import desc

#This file implements all the operations for dscpmappings class

#Get All mappings#
@api.route('/dscpmappings/', methods=['GET'])
def get_dscpmappings():
    return jsonify(json_list = [i.to_json() for i in ClassDscp.query.order_by(desc('dscp'))])

#Get a dscp mapping using application class name#
@api.route('/dscpmappings/<path:name>', methods=['GET'])
@json
def get_dscpmapping(name):
    return ClassDscp.query.get_or_404(name)

#Create a new mapping#
@api.route('/dscpmappings/', methods=['POST'])
@json
def add_dscpmapping():
    mapping = ClassDscp().from_json(request.json)
    db.session.add(mapping)
    db.session.commit()
    return request.json, 201

#Delete a mapping#
@api.route('/dscpmappings/<path:name>', methods=['DELETE'])
@json
def delete_dscpmapping(name):
    mapping = ClassDscp.query.get_or_404(name)
    db.session.delete(mapping)
    db.session.commit()
    return {}

#Update a mapping#
@api.route('/dscpmappings/<path:name>', methods=['PUT'])
@json
def update_dscpmapping(name):
    mapping = ClassDscp.query.get_or_404(name)
    mapping.from_json(request.json)
    db.session.add(mapping)
    db.session.commit()
    return {}





