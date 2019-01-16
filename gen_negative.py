import random
import json

from git import *
from comp import *
from util import localfile

select_set = set()

all_pr_flag = True

def random_pairs():
    global select_set
    
    # repos = os.listdir('/DATA/luyao/pr_data')
    
    # choose = ['saltstack/salt']
    
    choose = ['mozilla-b2g/gaia', 'twbs/bootstrap', 'scikit-learn/scikit-learn', 'rust-lang/rust', 'servo/servo', 'pydata/pandas', 'saltstack/salt', 'nodejs/node', 'symfony/symfony-docs', 'zendframework/zf2', 'symfony/symfony', 'kubernetes/kubernetes']
    
    # choose = ['cocos2d/cocos2d-x', 'dotnet/corefx', 'django/django', 'angular/angular.js', 'JuliaLang/julia', 'ceph/ceph', 'joomla/joomla-cms', 'facebook/react', 'hashicorp/terraform', 'rails/rails', 'docker/docker', 'elastic/elasticsearch', 'emberjs/ember.js', 'ansible/ansible']
    
    find = False
    
    while not find:
        # random a repo
        while True:
            try:
                '''
                repo = repos[random.randint(0, len(repos) - 1)]
                repo_ = os.listdir('/DATA/luyao/pr_data/' + repo)[0]
                repo = repo + '/' + repo_
                '''
                repo = choose[random.randint(0, len(choose) - 1)]
                
                break
            except:
                continue
        

        ok_file = '/DATA/luyao/pr_data/%s/list_for_random_generate_c1.json' % repo
        if all_pr_flag:
            ok_file = ok_file.replace('_c1', '_all')

        if os.path.exists(ok_file):
            nums = localfile.get_file(ok_file)
        else:
            nums = os.listdir('/DATA/luyao/pr_data/%s' % repo)

            def like_localize(p):
                if 'confi' in p["title"].lower():
                    return True
                if 'readme' in p["title"].lower():
                    return True
                return False

            def too_small(p):
                if len(p["title"]) <= 20:
                    return True
                if (p["body"] is not None) and (len(p["body"]) <= 20):
                    return True
                return False

            new_num = []
            cnt, tot_cnt = 0, len(nums)
            for x in nums:
                cnt += 1
                if cnt % 100 == 0:
                    print(1.0 * cnt / tot_cnt)

                if x.isdigit():
                    p = get_pull(repo, x)
                    # print('check', repo, x)
                    if (all_pr_flag or (p["merged_at"] is not None)) and (not check_large(p)) and \
                    (not too_small(p)) and (not like_localize(p)):
                        len_f = len(fetch_pr_info(p)) 
                        if (len_f > 0) and (len_f <= 10):
                            new_num.append(x)
            nums = new_num
            
            localfile.write_to_file(ok_file, nums)
        
        
        l = len(nums)
        
        # print(repo, l)
        
        if l <= 100:
            raise Exception('too small', repo)
            continue
        
        if l <= 1000:
            if random.randint(0, 3) > 0:
                continue
        
        ti = 0
        while True:
            ti += 1
            if ti > 100:
                break
            if l > 0:
                x = nums[random.randint(0, l - 1)]
                y = nums[random.randint(0, l - 1)]
                
                if (repo, x, y) in select_set:
                    continue
                
                if (x != y) and (x.isdigit()) and (y.isdigit()):
                    p1 = get_pull(repo, x)
                    p2 = get_pull(repo, y)
                    # print(repo, x, y)
                    
                    '''
                    if not check_both_merged(p1, p2):
                        continue
                    '''
                    if p1["user"]["id"] != p2["user"]["id"]:
                        
                        select_set.add((repo, x, y))
                        select_set.add((repo, y, x))
                        
                        find = True
                        break
    
    return [repo, x, y]


if __name__ == "__main__":
    # print(random_pairs())
    ret = []
    # num = 469600
    num = 50000
    for t in range(num):
        ret.append(random_pairs())
    with open('data/trainset_allpr.txt', 'w') as f:
        for t in ret:
            print("\t".join(t), file=f)
