import os

from git import *
from main import *
from comparer import *

include_self_flag = True

def get_all_fork_list(repo):
    q = [api.get('repos/%s' % repo)]
    i = 0
    while i < len(q):
        try:
            if int(q[i]['forks_count']) > 0:
                t = get_fork_list(q[i]['full_name'])
                q += t
        except:
            q[i]['forks_count'] = 0

        i += 1
    return q
    
    
def detect_on_pr(repo):
    if include_self_flag:
        out_file = 'detection/' + repo.replace('/', '_') + '_cross_forks_v2.txt'        
    else:
        out_file = 'detection/' + repo.replace('/', '_') + '_cross_forks.txt'
    
    if os.path.exists(out_file):
        return

    
    q = list(filter(lambda x: int(x['forks_count']) > 0, get_all_fork_list(repo)))
    
    '''
    q = [{'full_name': 'MarlinFirmware/Marlin'},\
    {'full_name': 'Ultimaker/Ultimaker2Marlin'},\
    {'full_name': 'RichCattell/Marlin'},\
    {'full_name': 'jcrocholl/Marlin'}]
    '''
    
    pr = {}
    num = 0
    tot_len = 0
    for branch in q:
        if not include_self_flag:
            if branch['full_name'] == repo:
                continue
        
        t = get_pull_list(branch['full_name'])
        if len(t) > 0:
            pr[branch['full_name']] = t
    
    
    print('number of sub repo', len(pr))

    out = open(out_file, 'w')
    out2 = open('detection/' + repo.replace('/', '_') + '_cross_forks_all.txt', 'a')

    c = classify()

    init_model_with_repo(repo)

    results = []

    for b1 in pr:
        for b2 in pr:
            if b1 < b2:
                if len(pr[b1]) > len(pr[b2]):
                    b1, b2 = b2, b1

                for p1 in pr[b1]:
                    li = []
                    for p2 in pr[b2]:

                        # if p1["user"]["id"] == p2["user"]["id"]:
                        #     continue

                        feature_vector = get_sim_vector(p1, p2)

                        t = [p1["html_url"], p2["html_url"], feature_vector, c.predict_proba([feature_vector])[0][1], \
                             p1["user"]["id"] == p2["user"]["id"], \
                            ]
                        li.append(t)

                        # print(t, file=out2)

                    li = sorted(li, key=lambda x: x[3], reverse=True)
                    if li[0][3] > 0.8:
                        print(li[0])
                        print(li[0], file=out)

    out.close()
    out2.close()

'''
def detect_on_commit(repo):
    init_model_with_repo(repo)
    li = get_all_fork_list(repo)
    
    for t in li:
        r = t['full_name']
        if r == repo:
            continue
        
        branch_list = get_branch_list(r)
''' 
    
    
if __name__ == "__main__":
    if len(sys.argv) == 2:
        r = sys.argv[1].strip()
        detect_on_pr(r)
    else:
        t = open('data/repoList_morethan200PR.txt').readlines()
        # t = open('data/repoList_rly.txt').readlines()
        for repo in t:
            r = repo.strip()
            detect_on_pr(r)
