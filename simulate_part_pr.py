import os
import sys

from datetime import datetime, timedelta

import clf
import comp
import git
import fetch_raw_diff

def fetch_pull_from_local(pull):
    repo = pull["base"]["repo"]["full_name"]
    repo_url = 'https://github.com/%s' % repo
    repo_path = '/DATA/luyao/repo/%s' % repo
    
    pull_id = pull["node_id"] if 'node_id' in pull else pull['id']
    
    if not os.path.exists(repo_path):
        os.system('git clone %s %s' % (repo_url, repo_path))
    os.system('git -C %s remote add %s %s' % (repo_path, pull_id, pull["head"]["repo"]["html_url"]))
    os.system('git -C %s fetch %s' % (repo_path, pull_id))


def generate_part_pull(pull):
    repo = pull["base"]["repo"]["full_name"]
    repo_path = '/DATA/luyao/repo/%s' % repo

    fetch_pull_from_local(pull)
    
    out = '/DATA/luyao/commit_diff'

    commits = git.get_pull_commit(pull)
    
    if len(commits[0]["parents"]) > 1:
        raise Exception('have multi parents %s' % commits[0]['sha'])
    
    root_sha = commits[0]["parents"][0]["sha"]
    
    total_message = ''
    
    all_p = []
    
    for c in commits:
        message = c['commit']['message']
        # print(c['commit']['message'])
        
        total_message += message + '\n'
        ti = datetime.strptime(c['commit']['author']['date'], "%Y-%m-%dT%H:%M:%SZ")
        
        out_file = out + '/' + root_sha + '_' + c['sha'] + '.txt'        
        os.system('git -C %s diff %s %s > %s' % (repo_path, root_sha, c['sha'], out_file))
        
        p = commits_to_pull(message, total_message, ti, open(out_file, 'r', encoding="utf-8").read())
        all_p.append(p)
    
    return all_p


def commits_to_pull(message, total_message, ti, raw_diff):
    pull = {}
    pull['number'] = None
    pull['title'] = message
    pull['body'] = total_message
    pull['file_list'] = fetch_raw_diff.parse_files(raw_diff)
    pull['time'] = ti
    pull['merge_commit_flag'] = True
    if len(pull['file_list']) == 0:
        raise Exception('empty commit!')
    return pull


def simulate(repo, num1, num2):    
    p1 = git.get_pull(repo, num1)
    p2 = git.get_pull(repo, num2)
    
    for c1 in git.get_pull_commit(p1):
        for c2 in git.get_pull_commit(p2):
            if c1['commit']['message'] == c2['commit']['message']: # repeat commit
                return 2, -1, []

    try:
        all_pa = generate_part_pull(p1)
        all_pb = generate_part_pull(p2)
    except Exception as e:
        print('error on', repo, num1, num2, ':', e)
        return -1, -1, []

    
    # print('commit len=', len(all_pb), len(all_pb))
    
    max_s, max_t = -1, 0
    history = []
    
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
            # print([x['file_list'] for x in now_a['file_list']])
            # print([x['file_list'] for x in now_b['file_list']])
            # print('------')
            
            # print(now_a['time'], now_b['time'], num_a, num_b)
            
            ret = comp.calc_sim(now_a, now_b)
            s = m.predict_proba([comp.sim_to_vet(ret)])[0][1]
            
            print(ret)
            print(s)
            print('-------------------')
            
            history.append(s)
            
            if s > max_s:
                max_s = s
                max_t = num_a + num_b
    
    
    '''
    for part1 in all_pa:
        for part2 in all_pb:
            ret = calc_sim(part1, part2)
            s = m.predict_proba([sim_to_vet(ret)])[0][1]
            max_s = max(max_s, s)
    '''
    
    return max_s, (l_a + l_b - max_t), history

m = clf.classify()

def run(s):
    r, n1, n2 = s.split()
    clf.init_model_with_repo(r)
    simulate(r, n1, n2)
    
    
if __name__ == '__main__':
    # fetch_pull_from_local()
    # simulate('angular/angular.js', '2522', '3025')

    # print(simulate('JuliaLang/julia', '16942', '16917'))
    
    # print(simulate('JuliaLang/julia', '16942', '16917')) # delete the branch
    
    # print(simulate('ceph/ceph','4276', '4245'))
    
    # print(simulate('almasaeed2010/AdminLTE', '1294', '861'))
        
    # sys.exit()
    
    result = []
    
    # in_file = 'data/multi_commits_second_false.txt'
    # in_file = 'data/msr_multi_commits_no_repeat.txt'
    # in_file = 'data/multi_commits_second_nondup_part.txt'
    # in_file = 'data/multi_commits_second_nondup_part2_1000.txt'
    # in_file = 'data/rly_false_pairs.txt'
    # in_file = 'data/big_false_data.txt'
    in_file = 'data/multi_commits_second_nondup.txt'
    
    out_file = 'detection/' + in_file.replace('.txt','').replace('data/','') + '_newret.txt'
    
    print('input=', in_file)
    print('output=', out_file)
    
    log = open(out_file + '.log', 'w+')
    
    with open(in_file) as f:
        pairs = f.readlines()
        pairs = sorted(pairs, key=lambda x: x[0])
        
        last_repo = None
        for pair in pairs:
            pair_s = pair.split()
            r, n1, n2 = pair_s[0], pair_s[1], pair_s[2]

            if r != last_repo:
                clf.init_model_with_repo(r)
                last_repo = r
            
            print('run on ', r, n1, n2)
            
            try:
                max_s, save_t, history = simulate(r, n1, n2)
            except Exception as e:
                print('error on:', pair, e, file=log)
                continue
            
            
            if max_s >= 0:
                with open(out_file, 'a+') as outf:
                    print(r, n1, n2, -1, max_s, -1, save_t, history, file=outf)
                
            result.append((pair, history))
            
    
    result = sorted(result, key=lambda x: x[1], reverse=True)
    
    with open(out_file + '.whole', 'w') as f:
        print(result, file=f)
    
    log.close()
    