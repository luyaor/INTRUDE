import random
import json

from git import *
from comp import *
from util import localfile

def check_both_merged(p1, p2):
    pd = 0
    if (p1["merged_at"] is not None) and (p2["merged_at"] is None):
        pd = 1
    if (p1["merged_at"] is None) and (p2["merged_at"] is not None):
        pd = 1
    if (p1["merged_at"] is not None) and (p2["merged_at"] is not None):
        pd = -1 # both merged
    return (pd == -1)


def is_dup(pull):
    # find duplicate in labels
    for label in pull.get("labels",[]):
        if 'duplicate' in label["name"].lower():
            return True
    """
    # find duplicate in title
    title = pull["title"]
    if (title is not None) and ('duplicate' in title.lower()):
        return True

    # fine duplicate in body
    body = pull["body"]
    if (body is not None) and ('duplicate' in body.lower()):
        return True
    """
    return False

def find_dup_pairs(repo):
    print('waiting for geting all pulls of %s!' % repo)
    sys.stdout.flush()
    pulls = get_pull_list(repo)
    print('finish geting all pulls!')
    sys.stdout.flush()
    
    for pull in pulls:
        #if is_dup(pull):
        if True:
            candidates = get_another_pull(pull)
            for cand in candidates:
                try:
                    pullB = api.get('repos/%s/pulls/%s' % (repo, cand))
                    print("repo:", repo, "pair:", pull["number"], cand)
                    # print("sim:", sim(pull, pullB))
                    sys.stdout.flush()
                except:
                    pass

def get_true_negative(repo):
    print('waiting for geting all pulls of %s!' % repo)
    sys.stdout.flush()
    pulls = get_pull_list(repo)
    print('finish geting all pulls on', repo, len(pulls))
    sys.stdout.flush()

    result = []
    for pullA in pulls:
        for pullB in pulls:
            if int(pullA["number"]) < int(pullB["number"]):
                if location_calc(pullA, pullB) > 0.4:
                    print((repo, pullA["number"], pullB["number"], sim(pullA, pullB)))
                    sys.stdout.flush()
                    result.append((repo, pullA["number"], pullB["number"], sim(pullA, pullB)))
    return result
    

def get_dup(repo):
    pulls = get_pull_list(repo)
    dup_list = []
    for pull in pulls:
        if is_dup(pull):
            dup_list.append(pull["number"])
    return dup_list


# todo remove noise in random pairs
def random_pairs():

    # repos = os.listdir('/DATA/luyao/pr_data')
    
    # choose = ['saltstack/salt']
    
    # choose = ['mozilla-b2g/gaia', 'twbs/bootstrap', 'scikit-learn/scikit-learn', 'rust-lang/rust', 'servo/servo', 'pydata/pandas', 'saltstack/salt', 'nodejs/node', 'symfony/symfony-docs', 'zendframework/zf2', 'symfony/symfony', 'kubernetes/kubernetes']
    
    choose = ['cocos2d/cocos2d-x', 'dotnet/corefx', 'django/django', 'angular/angular.js', 'JuliaLang/julia', 'ceph/ceph', 'joomla/joomla-cms', 'facebook/react', 'hashicorp/terraform', 'rails/rails', 'docker/docker', 'elastic/elasticsearch', 'emberjs/ember.js', 'ansible/ansible']
    
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
        

        ok_file = '/DATA/luyao/pr_data/%s/list_for_random_generate.json' % repo
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
                    if (p["merged_at"] is not None) and (not check_too_big(p)) and \
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
            if ti > 50:
                break
            if l > 0:
                x = nums[random.randint(0, l - 1)]
                y = nums[random.randint(0, l - 1)]
                
                if (x != y) and (x.isdigit()) and (y.isdigit()):
                    p1 = get_pull(repo, x)
                    p2 = get_pull(repo, y)
                    # print(repo, x, y)
                    
                    '''
                    if not check_both_merged(p1, p2):
                        continue
                    '''
                    if p1["user"]["id"] != p2["user"]["id"]:
                        find = True
                        break
    
    return [repo, x, y]


if __name__ == "__main__":
    print(random_pairs())
