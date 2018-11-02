import os
from sklearn.utils import shuffle

from git import *
from clf import *
from comp import *

filter_big = True

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
    

def detect_dup_pr_cross_repo(upstream, q, out_file):
    pr = {}
    num = 0
    tot_len = 0
    for branch in q:
        t = get_repo_info(branch['full_name'], 'pull')
        if len(t) > 0:
            pr[branch['full_name']] = t
    
    print('start on ', out_file)
    print('number of sub repo', len(pr))

    out = open(out_file, 'w')
    #out2 = open(out_file + '.log', 'a')

    c = classify()

    # init_model_with_repo(upstream)
    all_pr = []
    for b in pr:
        all_pr += shuffle(pr[b])[:2000]
    save_id = out_file.replace('/', '_').replace('.txt', '')
    init_model_with_pulls(all_pr, save_id)

    results = []

    for b1 in pr:
        for b2 in pr:
            if b1 < b2:
                if len(pr[b1]) > len(pr[b2]):
                    b1, b2 = b2, b1

                for p1 in pr[b1]:
                    if filter_big and check_too_big(p1):
                        continue

                    li = []
                    for p2 in pr[b2]:
                        if filter_big and check_too_big(p2):
                            continue

                        # print(p2['number'])

                        if p1["user"]["id"] == p2["user"]["id"]:
                            continue

                        feature_vector = get_pr_sim_vector(p1, p2)

                        t = [p1["html_url"], p2["html_url"], feature_vector, c.predict_proba([feature_vector])[0][1], \
                             p1["user"]["id"] == p2["user"]["id"], \
                            ]
                        li.append(t)

                        # print(t, file=out2)

                    li = sorted(li, key=lambda x: x[3], reverse=True)
                    if li[0][3] > 0.55:
                        print(li[0])
                        print(li[0], file=out)

    out.close()
    #out2.close()


def detect_on_pr(repo):
    out_file = 'evaluation/' + repo.replace('/', '_') + '_cross_forks.txt'

    if os.path.exists(out_file):
        return
    
    q = list(filter(lambda x: int(x['forks_count']) > 0, get_all_fork_list(repo)))
    
    '''
    q = [{'full_name': 'MarlinFirmware/Marlin'},\
    {'full_name': 'Ultimaker/Ultimaker2Marlin'},\
    {'full_name': 'RichCattell/Marlin'},\
    {'full_name': 'jcrocholl/Marlin'}]
    '''
    detect_dup_pr_cross_repo(repo, q, out_file)


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
    
def run_cross_repo(r1, r2):
    q =[{'full_name': r1}, {'full_name': r2}]
    
    out_file = 'evaluation/' + (r1 + '_' + r2).replace('/', '_') + '_cross_forks_version2.txt'

    if os.path.exists(out_file) and (os.path.getsize(out_file) > 0):
        print('Already run before =', r1, r2)
        return

    detect_dup_pr_cross_repo(r2, q, out_file)
    
if __name__ == "__main__":
    if len(sys.argv) == 3:
        r1 = sys.argv[1].strip()
        r2 = sys.argv[2].strip()
        run_cross_repo(r1, r2)
        sys.exit()

    hard_forks = open('data/hard_forks.txt').readlines()

    for repo_pair in hard_forks:
        r1, r2 = repo_pair.strip().split()
        run_cross_repo(r1, r2)
        

    '''
    if len(sys.argv) == 2:
        r = sys.argv[1].strip()
        detect_on_pr(r)
    else:
        t = open('data/repoList_morethan200PR.txt').readlines()
        # t = open('data/repoList_rly.txt').readlines()
        for repo in t:
            r = repo.strip()
            detect_on_pr(r)
    '''
