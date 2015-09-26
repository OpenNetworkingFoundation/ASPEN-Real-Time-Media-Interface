import socket
import urllib2
import json

'''method that checks if the input is a valid Ip Address'''
def ip_address_is_valid(address):

    split_result = address.split('/')
    address_main = split_result[0]
    try:
        address_prefix = split_result[1]
    except:
        return False
    try:
        prefix_int = int(address_prefix)
        if(prefix_int<0 or prefix_int>32):
            return False
    except:
        return False

    try: 
        socket.inet_aton(address_main)
    except socket.error: 
        return False
    else:
        return address_main.count('.') == 3

''' method that splits the base address from the prefix length. Return the base address '''
def get_base_address(address):
    split_result = address.split('/')
    return split_result[0]
'''
method that gets the address in the format xxx.xxx.xxx.xxx/prefix and return the prefix
'''
def get_prefix(address):
    split_result = address.split('/')
    return split_result[1]
'''
method that is used to check the input from the user.
The input should be in the format of <startPort>-<endPort>
Where startPort and endPort be between 0-65535 and also the endPort to be greater or equal to the startPort
'''
def port_range_is_valid(ports):
    try:
        split_result = ports.split('-')
        start = split_result[0]
        end = split_result[1]
  
        if(int(start)>0 and int(start)<=65535 and int(end)>0 and int(end)<=65535 and int(end)>=int(start)):
            return True
        return False
    except:
        return False


''' Splits the range and returns the startPort '''
def get_start_port(ports):
    split_result = ports.split('-')
    return split_result[0]

''' Splits the range and returns the endPort '''
def get_end_port(ports):
    split_result = ports.split('-')
    return split_result[1]

