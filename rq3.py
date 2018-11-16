import os
import sys

way = 'new'
# way = 'old'

if len(sys.argv) == 2:
    way = sys.argv[1].strip()

file = 'evaluation/result_on_topk_%s.txt' % way

last_run = {}
if os.path.exists(file):
    with open(file) as f:
        for t in f.readlines():
            ps = t.replace(',','').replace('[','').replace(']','').split()
            r, n1, n2 = ps[0], ps[1], ps[2]
            last_run[(r, n1, n2)] = [int(x) for x in ps[3:]]

# print(last_run)
print('last_run', len(last_run))

import detect

detect.speed_up = False
detect.filter_larger_number = True
detect.filter_out_too_old_pull_flag = True
detect.filter_already_cite = False
detect.filter_create_after_merge = False
detect.filter_overlap_author = False
detect.filter_out_too_big_pull_flag = False
detect.filter_same_author_and_already_mentioned = True

out = open(file, 'a+')

print(way)

cnt_num = 0
top_acc = [0 for i in range(30)]

input_pairs = 'data/clf/second_msr_pairs.txt'

with open(input_pairs) as f:
    for t in f.readlines():
        r, n1, n2 = t.strip().split()
        if n1 > n2:
            n1, n2 = n2, n1
        
        # noise in MSR dataset
        if (r, n1, n2) == ('joomla/joomla-cms', '15618', '15633'):
            continue
        if (r, n1, n2) == ('cocos2d/cocos2d-x', '11441', '11583'):
            continue

        if (r, n1, n2) in last_run:
            li = last_run[(r, n1, n2)]
        else:
            li = [int(x[0]) for x in detect.get_topK(r, n2, 30, True, way)]            
            print(r, n1, n2, 'ret =', li)
            print(r, n1, n2, li, file=out)
            out.flush()

print('end!')
out.close()
