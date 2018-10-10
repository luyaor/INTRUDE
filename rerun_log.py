import os
from val import *

files = os.listdir('rlog')

to_run = []

runned = {}
for file in files:
    if 'log' not in file:
        continue
    
    print('file=', file)
    with open('rlog/' + file) as f:
        for t in f.readlines():            
            rs, vs = t.strip().split(':')
            r, n_big = rs.strip().split()
            
            op = vs.strip()[2:-2].split('), (')
            
            for can in op:
                n_small, proba = can.split(',')
                proba = float(proba)
                '''
                if (r, n_big, n_small) in runned:
                    if abs(runned[(r, n_big, n_small)]-proba)>1e-4:
                        print('conflict', r, n_big, runned[(r, n_big, n_small)], proba)
                '''
                runned[(r, n_big, n_small)] = proba
                
            to_run.append((r, n_big))


mark = {}
with open('rlog/all_with_mark_no_repeat.txt') as f:
    for t in f.readlines():
        r, n1, n2, v, status = t.split()
        mark[(r, n1)] = [n2, v, status]


import clf
c = classify()

to_run = sorted(to_run, key=lambda x: x[0])

lastr = None


for (repo, n2) in to_run:
    if repo != lastr:
        lastr = repo
        init_model_with_repo(repo)

    
    pulls = get_repo_info(repo, 'pull')

    pullA = get_pull(repo, n2)
    for pull in pulls:
        n1 = int(pull["number"])

        if n1 >= int(n2):
            continue
        
        if check_ok_new(pull, pullA):
            if is_filter_before(pull, pullA):
                feature_vector = get_pr_sim_vector(pullA, pull)
                value = c.predict_proba([feature_vector])[0][1]
                
                if value >= 0.59:
                    with open('rlog/cases.txt', 'a') as outf:
                        print(repo, n2, n1, value, file=outf)

                
    

