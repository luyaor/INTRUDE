from clf import *
from detect import *

out = open('detection/result_on_top1.txt', 'a+')

print('model:', default_model, file=out)
out.flush()
      
with open('data/msr_repo_list.txt') as f:
    for repo in f.readlines():
        r = repo.strip()
        acc = simulate_timeline_only_dup_pair(r)
        
        print(r, ':', acc, file=out)
        out.flush

out.close()