import os
import sys
import copy

from datetime import datetime, timedelta

import clf
import comp
import git
import fetch_raw_diff

def generate_part_pull(pull):
    commits = git.get_pull_commit(pull)
    
    total_message = ''
    
    all_p = []
    cur_file_list = []
    
    for c in commits:
        message = c['commit']['message']
        
        total_message += message + '\n'
        ti = datetime.strptime(c['commit']['author']['date'], "%Y-%m-%dT%H:%M:%SZ")
        
        new_f = git.fetch_commit(c['url'])
        
        cur_file_list.extend(new_f)

        p = commits_to_pull(message, total_message, ti, cur_file_list)

        all_p.append(p)
    
    return all_p


def commits_to_pull(message, total_message, ti, file_list):
    pull = {}
    pull['number'] = None
    # pull['title'] = message
    pull['title'] = total_message
    pull['body'] = total_message
    pull['file_list'] = copy.deepcopy(file_list)
    pull['time'] = ti
    pull['merge_commit_flag'] = True
    return pull


l_repo = None

def simulate(repo, num1, num2):
    global l_repo
    if repo != l_repo:
        l_repo = repo
        clf.init_model_with_repo(repo)
        
    p1 = git.get_pull(repo, num1)
    p2 = git.get_pull(repo, num2)
    
    '''
    for c1 in git.get_pull_commit(p1):
        for c2 in git.get_pull_commit(p2):
            if (len(c1['commit']['message']) > 0) and (c1['commit']['message'] == c2['commit']['message']): # repeat commit
                return 2, [], []
    '''
    
    try:
        all_pa = generate_part_pull(p1)
        all_pb = generate_part_pull(p2)
    except Exception as e:
        print('error on', repo, num1, num2, ':', e)
        return -1, [], []
    
    # print('commit len=', len(all_pb), len(all_pb))
    
    history = []
    history_ret = []
    
    l_a, l_b = len(all_pa), len(all_pb)
    num_a, num_b = 0, 0
    now_a, now_b = None, None
    
    while True:
        pa = all_pa[num_a] if num_a < l_a else None
        pb = all_pb[num_b] if num_b < l_b else None
        if (pa is None) and (pb is None):
            break
        
        if (pb is None) or (pa and (pa['time'] < pb['time'])):
            num_a += 1
            now_a = pa
        else:
            num_b += 1
            now_b = pb
        
        if now_a and now_b:
            ret = comp.calc_sim(now_a, now_b)
            s = m.predict_proba([comp.sim_to_vet(ret)])[0][1]
            
            '''
            print(ret)
            print(s)
            print('-------------------')
            '''
            
            history.append(s)
            history_ret.append(ret)
    
    return 1, history, history_ret

m = clf.classify()

def run(s):
    r, n1, n2 = s.split()
    clf.init_model_with_repo(r)
    simulate(r, n1, n2)


if __name__ == '__main__':
    
    # run('dotnet/corefx 23755 18185')
    
    # in_file = 'data/mulc_second_msr_pairs.txt'
    # in_file = 'data/mulc_second_nondup.txt'
    in_file = 'data/clf/second_nondup.txt'
    
    out_file = 'detection/' + in_file.replace('.txt','').replace('data/','').replace('clf/','') + '_okret_tds_z.txt'
    out_log = out_file + '.log'
    
    print('input=', in_file)
    print('output=', out_file)
    
    with open(out_log, 'w') as outf:
        print('start', file=outf)
        
    result = []
    
    with open(in_file) as f:
        pairs = f.readlines()
        pairs = sorted(pairs, key=lambda x: x.split()[0])
        
        last_repo = None
        for pair in pairs:
            pair_s = pair.split()
            r, n1, n2 = pair_s[0], pair_s[1], pair_s[2]

            if r != last_repo:
                clf.init_model_with_repo(r)
                last_repo = r
            
            status, history, history_ret = simulate(r, n1, n2)
            
            result.append((pair, history))
            
            if status >= 0:
                with open(out_file, 'a+') as outf:
                    print(r, n1, n2, history, file=outf)
                with open(out_log, 'a+') as outf:
                    print(r, n1, n2, history_ret, file=outf)


    result = sorted(result, key=lambda x: x[1], reverse=True)
    with open(out_file + '.whole', 'w') as f:
        print(result, file=f)

    