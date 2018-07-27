import os
from git import *
import fetch_raw_diff
from comparer import *
import main

def fetch_pull_from_local(pull):
    repo = 'dodgepudding/wechat-php-sdk'
    pull = get_pull(repo, '318')
    
    main_stream = 'https://github.com/%s' % repo

    os.system('git clone %s /DATA/luyao/repo' % main_stream)
    os.system('git remote add %s %s' % (pull["user"]["id"], pull["head"]["repo"]["html_url"]))
    os.system('git fetch %s' % pull["user"]["id"])

    out = '/DATA/luyao/commit_diff'

    commits = get_pull_commit(pull)
    for c in commits:
        out_file = out + '/' + c['sha'] + '.txt'
        os.system('git diff %s > %s' % (c['sha'], out_file))

        with open(out_file) as f:
            s = f.read()

def fetch_merge_commit(sha_point1, sha_point2):
    pass

def commits_to_pull():
    pull['number'] = None
    pull['title'] = pull['body'] = 
    pull['file_list'] = fetch_raw_diff.parse_files()
    pull['merge_commit_flag'] = True
    
    
def stimulate(pullA, pullB):
    commitsA = get_pull_commit(pullA)
    commitsb = get_pull_commit(pullB)
    
    merge_p_a = 
    merge_p_b = 
    
    m = main.classify()
    
    max_s = -1
    for cA in commitsA:
        for cB in commitsb:
            p1 = fetch_merge_commit(cA['sha'], merge_p_a)
            p2 = fetch_merge_commit(cB['sha'], merge_p_b)
            ret = calc_sim(commits_to_pull(p1), commits_to_pull(p2))
            s = m.predict_proba([sim_to_vet(ret)])[0][1]
            
            if s > max_s:
                max_s = s
    
    return max_s

            