import sys
from clf import *
from comp import *


choice = sys.argv[1]
'''
if choice == 'boost':
    default_mode = 'boost'
    add_timedelta = True
else:
    default_mode = 'SVM'
    add_timedelta = False
'''

from detect import *


out = open('detection/result_on_top1_' + choice + '.txt', 'a+')

print('model:', default_model, file=out)
out.flush()
      
with open('data/msr_repo_list.txt') as f:
    for repo in f.readlines():
        r = repo.strip()
        acc = simulate_timeline_only_dup_pair(r)
        
        print(r, ':', acc, file=out)
        out.flush()

out.close()