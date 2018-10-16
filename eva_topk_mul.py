import os
import sys

import clf

from util import localfile

clf.part_params = [0,0,1,1,1,1,1,1,1]

way = 'leave_text'

file_dir = 'detection/result_on_topk/%s' % way

localfile.write_to_file(file_dir + '/create_flag.json', 'start')

import detect

from multiprocessing import Pool

print(way)

input_pairs = 'data/clf/second_msr_pairs.txt'
# input_pairs = 'data/clf/second_msr_pairs_nolarge.txt'

def doit(t):
    r, n1, n2 = t.strip().split()
    if n1 > n2:
        n1, n2 = n2, n1
    
    if (r, n1, n2) == ('joomla/joomla-cms', '15618', '15633'):
        return
    if (r, n1, n2) == ('cocos2d/cocos2d-x', '11441', '11583'):
        return

    
    li = [int(x[0]) for x in detect.get_topK(r, n2, 30, True, way)]
    
    file = file_dir + '/' + r.replace('/','_') + '_' + n2 + '.txt'
    with open(file, 'w') as f:
        print(r, n1, n2, li, file=f)
    
    return [r, n1, n2, li]

with open(input_pairs) as f:    
    pairs = f.readlines()
    
with Pool(processes=10) as pool:
    all_result = pool.map(doit, pairs)

localfile.write_to_file(file_dir + '/all.json', all_result)

