#!/usr/bin/env python

import sys
sys.path.append('../src/')
from vdy import vdy

def verify(value1, value2):
    return value1 == value2

def result(strValue1, value2):
    print strValue1, '=>', verify(eval(strValue1), value2)

example01 = vdy('example01.vdy').assign()
result("example01['expected_Status_Post']", [201])
result("example01['headers_empty_body']", {"Accept":"application/json", "Accept-Encoding":"gzip, deflate"})

example02 = vdy('example02.vdy').assign()
result("example02['str_1']", 'official value 1')
result("example02['str_2']", 'the value in element_2_dic.key_2')
result("example02['str_3']", 'value 2')
result("example02['str_4']", 'list value 0')

vdy02 = vdy('example02.vdy')
example02 = vdy02.join({"key_str_2": "my_key_2", "value_1": "my value 1", "my_dict_1": "$element_1_dic"}).assign()
result("example02['my_dict_1']", {'key_1': 'my value 1', 'my_key_2': 'value 2'}) 
