import os
import sys

way = 'pre'

file = 'detection/result_on_topk_%s.txt' % way

last_run = {}
if os.path.exists(file):
    with open(file) as f:
        for t in f.readlines():
            ps = t.replace(',','').replace('[','').replace(']','').split()
            r, n1, n2 = ps[0], ps[1], ps[2]
            last_run[(r, n1, n2)] = [int(x) for x in ps[3:]]

# print(last_run)
print('last_run', len(last_run))


from clf import *
from comp import *
from detect import *

out = open(file, 'a+')

print(way)

cnt_num = 0
top_acc = [0 for i in range(30)]


with open('data/clf/second_msr_pairs_nolarge.txt') as f:
    for t in f.readlines():
        r, n1, n2 = t.strip().split()
        if n1 > n2:
            n1, n2 = n2, n1
        
        if (r, n1, n2) in last_run:
            li = last_run[(r, n1, n2)]
        else:
            li = [int(x[0]) for x in get_topK(r, n2, 30, True, way)]
            
            print(r, n1, n2, 'ret =', li[0])
            print(r, n1, n2, li, file=out)
            out.flush()

        cnt_num += 1
        for i in range(30):
            if int(n1) in li[:i+1]:
                top_acc[i] += 1
        print('now=', r, cnt_num, 'top1 acc =', 1.0 * top_acc[0] / cnt_num)
        
print('end!')
for i in range(30):
    t = 1.0 * top_acc[i] / cnt_num
    top_acc[i] = t
    print('top%d acc =%.4f' % (i+1, t), file=out)

out.close()
