import os
import sys

from datetime import datetime, timedelta
from sklearn.utils import shuffle

from clf import *
from git import *
from comp import *
from util import localfile

from multiprocessing import Pool

c = classify()

cite = {}
last_number = None
renew_pr_list_flag = False

filter_out_too_big_pull_flag = False #fix
filter_out_too_old_pull_flag = True

predict_mode = True #fix
filter_larger_number = True
filter_already_cite = False

speed_up = False
filter_overlap_author = False

run_repo = None

def get_time(t):
    return datetime.strptime(t, "%Y-%m-%dT%H:%M:%SZ")

last_detect_repo = None

def speed_up_check(p1, p2):
    if set(p2['title'].lower().split()) & set(p1['title'].lower().split()):
        return True
    if set([x['name'] for x in fetch_pr_info(p1)]) & set([x['name'] for x in fetch_pr_info(p2)]):
        return True
    if check_pattern(p1, p2) == 1:
        return True
    return False

def check_pro_pick(p1, p2):
    if set([x[1] for x in pull_commit_sha(p1)]) & set([x[1] for x in pull_commit_sha(p2)]):
        return True
    return False


def have_commit_overlap(p1, p2):
    return False
    '''
    t = set(pull_commit_sha(p1)) & set(pull_commit_sha(p2))
    p1_user = p1["user"]["id"]
    p2_user = p2["user"]["id"]
    for x in t:
        if (x[1] == p1_user) or (x[1] == p2_user):
            return True
    return False
    '''
    
def get_topK(repo, num1, topK=30, print_progress=False, use_way='new'):
    global last_detect_repo
    if last_detect_repo != repo:
        last_detect_repo = repo
        init_model_with_repo(repo)

    pulls = get_repo_info(repo, 'pull')
    pullA = get_pull(repo, num1)
    
    if filter_already_cite:
        cite[str(pullA["number"])] = get_another_pull(pullA)

    results = {}
    tot = len(pulls)
    cnt = 0
    
    pull_v = {}
    
    for pull in pulls:
        cnt += 1
        
        '''
        if filter_out_too_big_pull_flag:
            if check_large(pull):
                continue
        '''

        if filter_out_too_old_pull_flag:
            if abs((get_time(pullA["updated_at"]) - \
                    get_time(pull["updated_at"])).days) >= 5 * 365: # more than 4 years
                continue

        if filter_larger_number:
            if int(pull["number"]) >= int(num1):
                continue
                
        if predict_mode:
            # same
            if str(pull["number"]) == str(pullA["number"]):
                continue

            # same author
            if pull["user"]["id"] == pullA["user"]["id"]:
                continue

            # case of following up work (not sure)
            if str(pull["number"]) in (get_pr_and_issue_numbers(pullA["title"]) + \
                                       get_pr_and_issue_numbers(pullA["body"])):
                continue
            
            if filter_already_cite:
                # "cite" cases
                if (str(pull["number"]) in cite.get(str(pullA["number"]), [])) or\
                (str(pullA["number"]) in cite.get(str(pull["number"]), [])):
                    continue

            '''
            # create after another is merged
            if (pull["merged_at"] is not None) and \
               (get_time(pull["merged_at"]) < get_time(pullA["created_at"])):
                continue
            '''
        
        if speed_up:
            if not speed_up_check(pullA, pull):
                continue
        
        if filter_overlap_author:
            if check_pro_pick(pullA, pull):
                continue

        if print_progress:
            if cnt % 100 == 0:
                print('progress = ', 1.0 * cnt / tot)        
                sys.stdout.flush()
        
        if use_way == 'new':
            feature_vector = get_pr_sim_vector(pullA, pull)        
            results[pull["number"]] = c.predict_proba([feature_vector])[0][1]
        else:
            results[pull["number"]] = old_way(pullA, pull)

    result = [(x,y) for x, y in sorted(results.items(), key=lambda x: x[1], reverse=True)][:topK] 
    localfile.write_to_file('evaluation/'+repo+'/'+num1+'.json', result)
    
    return result


def load_part(repo):
    sheet_path = 'evaluation/'+repo.replace('/','_')+'_stimulate_top1_sample200_sheet.txt'
    select_set = set()
    if (os.path.exists(sheet_path)) and (os.path.getsize(sheet_path) > 0):
        with open(sheet_path) as f:
            for t in f.readlines():
                tt = t.strip().split()
                select_set.add(str(tt[1]))
    return select_set

def load_select(repo):
    path = 'evaluation/'+repo.replace('/','_')+'_select.txt'
    select_set = set()
    with open(path) as f:
        for t in f.readlines():
            select_set.add(t.strip())
    return select_set

def load_select_runned(path):
    s = set()
    with open(path) as f:
        for t in f.readlines():
            p = t.split()
            s.add(p[1].strip())
    return s


def run(num1):
    repo = run_repo
    
    pull = get_pull(repo, num1)

    topk = get_topK(repo, num1, 10)
    if len(topk) == 0:
        return None

    num2, prob = topk[0][0], topk[0][1]
    vet = get_pr_sim_vector(pull, get_pull(repo, num2))

    check_pick = check_pro_pick(pull, get_pull(repo, num2))

    status = 'N/A'

    if (num2 in get_another_pull(pull)) or (num1 in get_another_pull(get_pull(repo, num2))):
        status += '(mention)'

    result = "\t".join([repo, str(num1), str(num2), "%.4f" % prob, str(check_pick)] + \
                    [status] + \
                    ["%.4f" % f for f in vet] + \
                    ['https://www.github.com/%s/pull/%s' % (repo, str(num1)),\
                     'https://www.github.com/%s/pull/%s' % (repo, str(num2))]
            )
    logres = "\t".join([repo, str(num1), str(topk)])

    return (result, logres)


def simulate_timeline(repo, renew=False, run_num=200, rerun=False):
    print('predict_mode=', predict_mode)
    print('filter_already_cite=', filter_already_cite)
    print('filter_larger=', filter_larger_number)
    print('speed_up=', speed_up)

    init_model_with_repo(repo)
    
    part_p = load_select(repo)
        
    select_p = part_p
    
    out_path = 'evaluation/'+repo.replace('/','_')+'_run_on_select_new_mv.txt'

    if os.path.exists(out_path):
        print('keep run!')
        select_p = select_p - load_select_runned(out_path)

    print('start run!')
    
    with Pool(processes=10) as pool:
        all_result = pool.map(run, list(select_p))
    
    for res in all_result:
        if res is not None:
            with open(out_path, 'a+') as f:
                print(res[0], file=f)
            
            with open('evaluation/'+repo.replace('/','_')+'_stimulate_detect_mv.log', 'a+') as f:
                print(res[1], file=f)

if __name__ == "__main__":
    # detection on history (random sampling)
    if len(sys.argv) > 1:
        predict_mode = True
        speed_up = True
        run_repo = sys.argv[1].strip()
        simulate_timeline(run_repo)
    
    '''
    if len(sys.argv) > 1:
        r = sys.argv[1].strip()
        if len(sys.argv) > 2:
            num = int(sys.argv[2].strip())
        else:
            num = 100
        simulate_timeline(r, False, num)
    
    if len(sys.argv) == 1:
        while True:
            try:
                ok = True
                with open('data/run_list.txt') as f:
                    rs = f.readlines()
                    for t in rs:
                        
                        sheet_path = 'evaluation/'+t.strip().replace('/','_')+'_stimulate_detect.log'
                        if (os.path.exists(sheet_path)):
                            continue
                        

                        try:
                            simulate_timeline(t.strip())
                        except Exception as e:
                            ok = False
                            print(e)
                if ok:
                    break
            except:
                continue
    '''

    
    '''
    r = 'spring-projects/spring-framework'
    if len(sys.argv) > 1:
        r = sys.argv[1]
    if len(sys.argv) > 2:
        renew_pr_list_flag = (sys.argv[2] == 'True')
    if len(sys.argv) > 3:
        last_number = int(sys.argv[3])
        print('last = ', last_number)
    '''
    
    '''
    with open('data/run_list.txt') as f:
        repos = f.readlines()
    
    simulate_mode = False
    renew_pr_list_flag = False
    
    for r in repos:
        r = r.strip()
        print('start detect open PR on', r)
        default_time_stp = datetime.utcnow() - timedelta(days=7)
        find_on_openpr(r, default_time_stp)
        
        print('total number=', total_number)
    '''