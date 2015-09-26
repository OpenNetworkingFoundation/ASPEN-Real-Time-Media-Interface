'''
*
*           VTN-based RTM Network Service 
* 
*   file: \rtm-api\api\v1_0\__init__.py 
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

from flask import Blueprint, g
from ..errors import ValidationError, bad_request, not_found
from ..auth import auth
from ..decorators import rate_limit

api = Blueprint('api', __name__)


@api.errorhandler(ValidationError)
def validation_error(e):
    return bad_request(e.args[0])


@api.errorhandler(400)
def bad_request_error(e):
    return bad_request('invalid request')


@api.errorhandler(404)
def not_found_error(e):
    return not_found('item not found')


@api.before_request
@rate_limit(limit=5, per=15)
@auth.login_required
def before_request():
    pass


@api.after_request
def after_request(response):
    if hasattr(g, 'headers'):
        response.headers.extend(g.headers)
    return response

'''do this last to avoid circular dependencies'''
from . import  sessions, policies, dscpmappings
