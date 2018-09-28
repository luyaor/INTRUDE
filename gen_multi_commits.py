from git import *
from sklearn.utils import shuffle

with open('data/clf/second_nondup.txt') as f:
    pairs = f.readlines()

w = 0

out = open('data/multi_commits_second_nondup.txt', 'w')

pairs = sorted(pairs, key=lambda x: x.split()[0])
last_repo = None

cnt = 0

pairs = shuffle(pairs, random_state=12345)

for pair in pairs:
    repo, num1, num2 = pair.split()
    
    cnt += 1
    
    if cnt % 100 == 0:
        print('cnt=', cnt)

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
    
    print(pair.strip(), file=out)
    out.flush()

    w += 1
    if w % 100 == 0:
        print(w)

out.close()
print(w)