import os
import sys

from datetime import datetime, timedelta
from sklearn.utils import shuffle

from clf import *
from git import *
from comp import *

c = classify()

cite = {}
last_number = None
renew_pr_list_flag = False

filter_out_too_big_pull_flag = True
filter_out_too_old_pull_flag = True

predict_mode = True
filter_larger_number = True
filter_already_cite = False

speed_up = True

def get_time(t):
    return datetime.strptime(t, "%Y-%m-%dT%H:%M:%SZ")

last_detect_repo = None

def speed_up_check(p1, p2):
    if set(p2['title'].split()) & set(p1['title'].split()):
        return True
    if set([x['name'] for x in fetch_pr_info(p1)]) & set([x['name'] for x in fetch_pr_info(p2)]):
        return True
    if check_pattern(p1, p2) == 1:
        return True
    return False

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
        
        if filter_out_too_big_pull_flag:
            if check_large(pull):
                continue
        
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
            # revert cases
            if 'revert' in pull["title"].lower():
                continue
            '''
            
            '''
            # create after another is merged
            if (pull["merged_at"] is not None) and \
               (get_time(pull["merged_at"]) < get_time(pullA["created_at"])):
                continue
            '''
        
        if speed_up:
            if not speed_up_check(pullA, pull):
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

def simulate_timeline(repo, renew=False, run_num=200, rerun=False):
    print('predict_mode=', predict_mode)
    print('filter_already_cite=', filter_already_cite)
    print('filter_larger=', filter_larger_number)

    init_model_with_repo(repo)
    pulls = get_repo_info(repo, 'pull', renew_pr_list_flag)

    all_p = set([str(pull["number"]) for pull in pulls])
    
    # part_p = load_part(repo)
    part_p = load_select(repo)
    
    log = open('evaluation/'+repo.replace('/','_')+'_stimulate_detect.log', 'a+')
    '''
    if not rerun:
        select_p = set(shuffle(list(all_p - part_p))[:run_num])
        out = open('evaluation/'+repo.replace('/','_')+'_stimulate_top1_sample200_sheet.txt', 'a+')
    else:
        select_p = part_p
        out = open('evaluation/'+repo.replace('/','_')+'_stimulate_top1_sample200_sheet_rerun.txt', 'a+')
    '''
    select_p = part_p
    out_path = 'evaluation/'+repo.replace('/','_')+'_run_on_select_new.txt'
    
    if os.path.exists(out_path):
        print('keep run!')
        select_p = select_p - load_select_runned(out_path)
    
    out = open(out_path, 'a+')
    
    for pull in pulls:
        num1 = str(pull["number"])
        
        if num1 not in select_p:
            continue
        
        print('Run on PR #%s' % num1)
        
        topk = get_topK(repo, num1, 10)
        if len(topk) == 0:
            continue

        num2, prob = topk[0][0], topk[0][1]
        vet = get_pr_sim_vector(pull, get_pull(repo, num2))
        pre = c.predict([vet])[0]
        
        status = 'N/A'
        
        if (num2 in get_another_pull(pull)) or (num1 in get_another_pull(get_pull(repo, num2))):
            status += '(mention)'
        
        print("\t".join([repo, str(num1), str(num2), "%.4f" % prob, str(pre)] + \
                        [status] + \
                        ["%.4f" % f for f in vet] + \
                        ['https://www.github.com/%s/pull/%s' % (repo, str(num1)),\
                         'https://www.github.com/%s/pull/%s' % (repo, str(num2))]
                       ),
              file=out)
        out.flush()

        print(repo, num1, ':', topk, file=log)
        log.flush()
    
    log.close()
    out.close()


total_number = 0

openpr_suffix = 'weekly'

def find_on_openpr(repo, time_stp=None):
    print('time_stp', time_stp)
    predict_mode = True
    filter_already_cite = True
    filter_larger_number = False
    
    pulls = get_repo_info(repo, 'pull', renew_pr_list_flag)
    '''
    for pull in pulls:
        cite[str(pull["number"])] = get_another_pull(pull)
    '''
    pulls = api.request('GET', 'repos/%s/pulls?state=open' % repo, True)
    
    if filter_already_cite:
        for pull in pulls:
            cite[str(pull["number"])] = get_another_pull(pull)

    # init model
    init_model_with_repo(repo)
    
    mode = 'a' if last_number else 'w'
    print('write mode=',mode)
    
    out = open('detection/firehouse/'+repo.replace('/','_')+'_topk_' + openpr_suffix + '.txt', mode)
    out2 = open('detection/firehouse/'+repo.replace('/','_')+'_top1_' + openpr_suffix + '.txt', mode)
    
    global total_number
    
    for pull in pulls:
        if time_stp and (get_time(pull["created_at"]) < time_stp):
            continue
                
        if pull["state"] != "open":
            continue
 
        if 'revert' in pull["title"].lower():
            continue
        
        num1 = str(pull["number"])
        
        if last_number and int(num1) >= last_number:
            continue
        
        print('run on', repo, num1)
        
        topk = get_topK(repo, num1, 10)
        num2 = topk[0][0]
        prob = topk[0][1]

        sim = get_pr_sim_vector(pull, get_pull(repo, num2))
        
        if prob >= 0.95:
            total_number += 1
            
        print("%s %8s %8s %.4f" % (repo, str(num1), str(num2), prob))
        print(" ".join("%.4f" % f for f in sim))
        print('https://www.github.com/%s/pull/%s' % (repo, str(num1)))
        print('https://www.github.com/%s/pull/%s' % (repo, str(num2)))
        sys.stdout.flush()

        print("%s %8s %8s %.4f" % (repo, str(num1), str(num2), prob), file=out2)
        print(" ".join("%.4f" % f for f in sim), file=out2)
        print('https://www.github.com/%s/pull/%s' % (repo, str(num1)), file=out2)
        print('https://www.github.com/%s/pull/%s' % (repo, str(num2)), file=out2)
        print(repo, num1, ':', topk, file=out)

    out.close()
    out2.close()


def detect_one(repo, num):
    print('detect on', repo, num)
    ret = get_topK(repo, num , 1, True)
    if len(ret) < 1:
        return -1, -1
    else:
        return ret[0][0], ret[0][1]

if __name__ == "__main__":

    # detection on history (random sampling)
    if len(sys.argv) > 1:
        predict_mode = True
        r = sys.argv[1].strip()
        simulate_timeline(r)
    
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