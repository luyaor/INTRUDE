import os
import sys
import clf

leave_way = 'text'
if len(sys.argv) > 1:
    leave_way = sys.argv[1].strip()

infile = 'rlog/sample_small_data.txt'
if len(sys.argv) > 2:
    infile = sys.argv[2].strip()

way = 'leave_' + leave_way
print('way=', way)
print('infile=', infile)


if leave_way == 'text':
    clf.part_params = [0,0,1,1,1,1,1,1,1]
elif leave_way == 'code':
    clf.part_params = [1,1,0,0,1,1,1,1,1]
elif leave_way == 'file_list':
    clf.part_params = [1,1,1,1,0,0,1,1,1]
elif leave_way == 'location':
    clf.part_params = [1,1,1,1,1,1,0,0,1]
elif leave_way == 'pattern':
    clf.part_params = [1,1,1,1,1,1,1,1,0]
else:
    print('------error!-----')

import detect


out = infile + '_' + way + '.out'


detect.speed_up = True
detect.filter_create_after_merge = True


def load(file):
    runned = set()
    if not os.path.exists(file):
        return runned

    with open(file) as f:
        for t in f.readlines():
            r, n2 = t.split(':')[0].strip().split(' ')
            runned.add((r, n2))
    return runned

runned_cases = load(out)

with open(infile) as f:
    for t in f.readlines():
        ts = t.strip().split()
        
        r, n2 = ts[0], ts[1]
        
        if (r, n2) in runned_cases:
            print('pass', (r, n2))
            continue

        ret = detect.get_topK(r, n2, 30, True, way)
        
        with open(out, 'a') as outf:
            print(r, n2, ':', ret, file=outf)
            