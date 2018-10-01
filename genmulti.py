import sys
sys.path.append('/home/luyao/PR_get/INTRUDE')

from git import *

from datetime import datetime, timedelta

def checkt(repo, num1, num2):    
    p1 = get_pull(repo, num1)
    p2 = get_pull(repo, num2)
    
    all_pa = get_pull_commit(p1)
    all_pb = get_pull_commit(p2)
    
    l_a, l_b = len(all_pa), len(all_pb)
    num_a, num_b = 0, 0
    now_a, now_b = None, None
    
    numt = 0
    while True:
        pa = all_pa[num_a] if num_a < l_a else None
        pb = all_pb[num_b] if num_b < l_b else None
        if (pa is None) and (pb is None):
            break
        
        if pa:
            pat = datetime.strptime(pa['commit']['author']['date'], "%Y-%m-%dT%H:%M:%SZ")
        if pb:
            pbt = datetime.strptime(pb['commit']['author']['date'], "%Y-%m-%dT%H:%M:%SZ")
        
        if (pb is None) or (pa and (pat < pbt)):
            num_a += 1
            now_a = pa
        else:
            num_b += 1
            now_b = pb
        
        if now_a and now_b:
            if (num_a < l_a) or (num_b < l_b):
                numt += 1
    
    if numt > 0:
        return True
    else:
        return False
    

with open('data/clf/second_nondup.txt') as f:
    pairs = f.readlines()

w = 0

out = open('data/multi_commits_second_nondup.txt', 'w')

pairs = sorted(pairs, key=lambda x: x.split()[0])
last_repo = None

for pair in pairs:
    repo, num1, num2 = pair.strip().split()
    
    #print(repo, num1, num2)
    '''
    if repo != last_repo:
        last_repo = repo
        init_model_with_repo(repo)
    '''
    
    p1 = get_pull(repo, num1)
    p2 = get_pull(repo, num2)
    
    cl1 = get_pull_commit(p1)
    cl2 = get_pull_commit(p2)
    
    
    #t = get_pr_sim_vector(p1, p2)
    #o = m.predict_proba([t])[0][1]
    
    if (len(cl1) == 1) and (len(cl2) == 1):
        continue
        
    if (len(cl1) == 0) or (len(cl2) == 0):
        continue
    
    if (len(cl1) > 100) or (len(cl2) > 100):
        continue

    if check_large(p1) or check_large(p2):
        continue
    
    if not checkt(repo, num1, num2):
        continue

    print(pair.strip(), file=out)
    out.flush()

    w += 1
    if w % 100 == 0:
        print(w)

out.close()
print(w)