'''
*
*           VTN-based RTM Network Service 
* 
*   file: \rtm-api\api\main.py 
* 
* This software contributed by NEC under Apache 2.0 license for open 
* source use. This software is supplied under the terms of the OpenSourceSDN 
* Apache 2.0 license agreement.  

*     Copyright (c) 2015 NEC Europe Ltd. 
* 
* Authors: Savvas Zannettou 
*          Fabian Schneider (fabian.schneider@neclab.eu)
* 		   A. Vorontsov
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

import requests
import json
import sys
from base64 import b64encode
import time

class OFCapi(object):
    http_methods = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
    return_formats = []	
    default_header_content = {"content-type":"application/json"}
    default_body_content = None
    default_http_method = None
    default_return_format = None
    default_ssl_verify=False
#    connection_check_method = None
    auth_type = None
    base_url = None
    send_json = False



    def __init__(self):
        self.default_http_method = self.http_methods[0]
        try:
            self.default_return_format = self.return_formats[0]
        except IndexError:
            self.default_return_format = ''

    def check_response_success(self, response):
        raise NotImplementedError('Please implement in subclass')

    def parse_errors(self, response):
        raise NotImplementedError('Please implement in subclass')


    def create_basic_auth(self, user, password):
        """Creates the header content for HTTP Basic Authentification.

        :param user: Username
        :param password: Password
        :rtype: Base64-encoded auth string
        """

        # Messing around with Python3's strictness about strings
        if sys.version_info >= (3, 0):
            if not isinstance(user, str):
                user = user.decode('utf-8')

            if not isinstance(password, str):
                password = password.decode('utf-8')

            return 'Basic ' + b64encode((user + ":" + password).encode('utf-8')).decode('utf-8')

        else:
            return 'Basic ' + b64encode(user + ":" + password).rstrip()


    def build_content(self, args):
        # takes a dictionary, filters out all the empty stuff
        if 'self' in args:
            del args['self']
        new_args = args.copy()

        for key in args:
            if not args[key]:
                    del new_args[key]
        return new_args


    def do(self, method, content=None, headers=None, ssl_verify=None, http_method=None, return_format=None):

        request_body = self.default_body_content.copy()
        if content is not None:
            request_body.update(content)

        request_headers = self.default_header_content.copy()
        if headers is not None:
            request_headers.update(headers)
        if ssl_verify is None:
            ssl_verify=self.default_ssl_verify
        if http_method is None:
            http_method = self.default_http_method

        if return_format is None:
            if self.default_return_format:
                return_format = "." + self.default_return_format
            else:
                return_format = ''

        request_url = self.base_url + method + return_format
        return self.do_request(http_method, request_url, request_headers, request_body, return_format, ssl_verify)

    def do_request(self, http_method, url, headers, body, return_format, ssl_verify, auth_data=None):

        if self.send_json:
            # We need to make sure that body is jsonified
            try:
                body = json.dumps(body, sort_keys=True)
            except TypeError or ValueError:
                pass

        if http_method.upper() == 'GET':

            r = requests.get(url, headers=headers, auth=auth_data, verify=ssl_verify)

        elif http_method.upper() == 'POST':
            r = requests.post(url, data=body, headers=headers, auth=auth_data, verify=ssl_verify)

        elif http_method.upper() == 'PUT':
            r = requests.put(url, data=body, headers=headers, auth=auth_data, verify=ssl_verify)

        elif http_method.upper() == 'DELETE':
            r = requests.delete(url, data=body, headers=headers, auth=auth_data, verify=ssl_verify)

        elif http_method.upper() == 'OPTIONS':
            r = requests.options(url, data=body, headers=headers, auth=auth_data, verify=ssl_verify)

        else:
            raise Exception("Invalid request method")

        return self.handle_response(r, return_format)

    def handle_response(self, response, return_format):
        try:
            return response.json()
        except (ValueError, TypeError):
            return response.content, response.status_code

