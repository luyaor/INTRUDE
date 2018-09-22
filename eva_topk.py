import sys
from clf import *
from comp import *
from detect import *

way = 'new'

out = open('detection/result_on_topk_%s.txt' % way, 'a+')

print(way)

cnt_num = 0
top_acc = [0 for i in range(30)]

with open('data/clf/second_msr_pairs_nolarge.txt') as f:
    for t in f.readlines():
        r, n1, n2 = t.strip().split()
        if n1 > n2:
            n1, n2 = n2, n1
        
        li = [int(x[0]) for x in get_topK(r, n2, 30, True, way)]

        cnt_num += 1
        for i in range(30):
            if int(n1) in li[:i]:
                top_acc[i] += 1

        print('now=', r, cnt_num, 'top1 acc =', 1.0 * top_acc[0] / cnt_num)
        
        
print('end!')
for i in range(30):
    t = 1.0 * top_acc[i] / cnt_num
    top_acc[i] = t
    print('top%d acc =%.4f' % (i+1, t), file=out)

out.close()