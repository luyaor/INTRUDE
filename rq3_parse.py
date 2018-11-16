import os
import sys

way = 'new'
# way = 'old'

if len(sys.argv) == 2:
    way = sys.argv[1].strip()

file = 'evaluation/result_on_topk_%s.txt' % way

cnt_num = 0
top_acc = [0 for i in range(30)]

last_run = {}
if os.path.exists(file):
    with open(file) as f:
        for t in f.readlines():
            ps = t.replace(',','').replace('[','').replace(']','').split()
                        
            r, n1, n2 = ps[0], ps[1], ps[2]
            li = [int(x) for x in ps[3:]]
            
            cnt_num += 1
            for i in range(30):
                if int(n1) in li[:i+1]:
                    top_acc[i] += 1

            # print('now=', r, cnt_num, 'top1 acc =', 1.0 * top_acc[0] / cnt_num)


print('cnt = ', cnt_num)
for i in range(30):
    t = 1.0 * top_acc[i] / cnt_num
    top_acc[i] = t
    print('%d \t %.4f' % (i+1, t))
