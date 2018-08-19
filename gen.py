from git import *

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
    """
    repos = os.listdir('/DATA/luyao/pr_data')
    while True:
        try:
            repo = repos[random.randint(0, len(repos) - 1)]
            repo_ = os.listdir('/DATA/luyao/pr_data/' + repo)[0]
            repo = repo + '/' + repo_
            
            pulls = get_pull_list(repo)
            x = pulls[random.randint(0, len(pulls) - 1)]["number"]
            y = pulls[random.randint(0, len(pulls) - 1)]["number"]
            if (x != y):
                break
        except:
            continue
        
    """
    repos = os.listdir('/DATA/luyao/pr_data')
    
    # choose = ['nathanmarz/storm', 'django/django', 'almasaeed2010/AdminLTE', 'lord/slate', 'angular/angular.js']
    
    choose = ['mozilla-b2g/gaia', 'ceph/ceph', 'dotnet/corefx', 'nodejs/node', 'scikit-learn/scikit-learn']
              
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
        
        nums = os.listdir('/DATA/luyao/pr_data/%s' % repo)
        
        # random a pair
        l = len(nums)
        
        if l <= 200:
            continue
        
        '''
        if l >= 5000:
            continue
        '''
        
        def like_localize(p):
            if 'confi' in p["title"].lower():
                return True
            if 'readme' in p["title"].lower():
                return True
        
        def too_small(p):
            if len(p["title"]) <= 20:
                return True
            if (p["body"] is not None) and (len(p["body"]) <= 20):
                return True
            
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
                    try:
                        if (len(fetch_pr_info(p1, True)) <= 30) and (len(fetch_pr_info(p2, True)) <= 30):
                            if p1["user"]["id"] != p2["user"]["id"]:
                                if like_localize(p1) or like_localize(p2):
                                    continue
                                if too_small(p1) or too_small(p2):
                                    continue

                                find = True
                                break
                    except:
                        pass
    return [repo, x, y]
