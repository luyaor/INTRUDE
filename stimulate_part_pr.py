import os
from git import *
import fetch_raw_diff
from comparer import *
import main

def fetch_pull_from_local(pull):
    # repo = 'Chatie/wechaty'
    # pull = get_pull(repo, '1182')
    # pull = get_pull(repo, num)
    repo = pull["base"]["repo"]["full_name"]
    repo_url = 'https://github.com/%s' % repo
    repo_path = '/DATA/luyao/repo/%s' % repo

    if not os.path.exists(repo_path):
        os.system('git clone %s %s' % (repo_url, repo_path))
    os.system('git -C %s remote add %s %s' % (repo_path, pull["user"]["id"], pull["head"]["repo"]["html_url"]))
    os.system('git -C %s fetch %s' % (repo_path, pull["user"]["id"]))


def generate_part_pull(pull):
    repo = pull["base"]["repo"]["full_name"]
    repo_path = '/DATA/luyao/repo/%s' % repo

    fetch_pull_from_local(pull)
    
    out = '/DATA/luyao/commit_diff'

    commits = get_pull_commit(pull)
    
    root_sha = commits[0]["parents"][0]["sha"]
    
    total_message = ''
    
    all_p = []
    
    for c in commits:
        message = c['commit']['message']
        total_message += message + '\n'
        
        out_file = out + '/' + root_sha + '_' + c['sha'] + '.txt'        
        os.system('git -C %s diff %s %s > %s' % (repo_path, root_sha, c['sha'], out_file))
        
        p = commits_to_pull(message, total_message, open(out_file).read())
        
        all_p.append(p)
    
    return all_p

def commits_to_pull(message, total_message, raw_diff):
    pull = {}
    pull['number'] = None
    pull['title'] = message
    pull['body'] = total_message
    pull['file_list'] = fetch_raw_diff.parse_files(raw_diff)
    pull['merge_commit_flag'] = True
    return pull

def stimulate():
    repo = 'angular/angular.js'
    num1 = '2522'
    num2 = '3025'
    
    main.init_model_with_repo(repo)
    
    p1 = get_pull(repo, num1)
    p2 = get_pull(repo, num2)
    
    all_pa = generate_part_pull(p1)
    all_pb = generate_part_pull(p2)
    
    m = main.classify()
    
    max_s = -1
    for part1 in all_pa:
        for part2 in all_pb:
            ret = calc_sim(part1, part2)
            s = m.predict_proba([sim_to_vet(ret)])[0][1]
            
            
            # print(part1['body'])
            # print(part2['body'])
            print(s)
            print(ret)
            print('----------------------')
            
            
            if s > max_s:
                max_s = s
    
    return max_s


if __name__ == '__main__':
    # fetch_pull_from_local()
    stimulate()
    
    