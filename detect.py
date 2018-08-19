import os

from datetime import datetime, timedelta
from sklearn.utils import shuffle

from main import *
from git import *
from gen import *
from comparer import *

c = classify()

cite = {}
last_number = None
renew_pr_list = False

simulate_mode = True

def get_time(t):
    return datetime.strptime(t, "%Y-%m-%dT%H:%M:%SZ")

def get_topK(repo, num1, topK = 10, print_progress = False):
    pulls = repo_get(repo, 'pull')
    pullA = get_pull(repo, num1)
    
    if not simulate_mode:
        cite[str(pullA["number"])] = get_another_pull(pullA)

    results = {}
    tot = len(pulls)
    cnt = 0
    
    pull_v = {}
    
    for pull in pulls:
        cnt += 1
        if simulate_mode:
            if int(pull["number"]) >= int(num1):
                continue
            
        # same
        if str(pull["number"]) == str(num1):
            continue
        
        # same author
        if pullA["user"]["id"] == pull["user"]["id"]:
            continue
        
        # case of following up work 
        if str(pull["number"]) in (get_pr_and_issue_numbers(pullA["title"]) + \
                                   get_pr_and_issue_numbers(pullA["body"])):
            continue
        
        if not simulate_mode:
            # for predict
            # "cite" cases
            if str(pull["number"]) in cite.get(str(pullA["number"]), []):
                continue

            if str(pullA["number"]) in cite.get(str(pull["number"]), []):
                continue

            # revert cases
            if 'revert' in pull["title"].lower():
                continue
        
        # create after another is merged
        if (pull["merged_at"] is not None) and \
           (get_time(pull["merged_at"]) < get_time(pullA["created_at"])):
            continue
        
        '''
        # filter out too big pull
        if check_too_big(pull):
            continue
        
        # filter out too old pull
        if abs((get_time(pullA["updated_at"]) - \
                get_time(pull["updated_at"])).days) >= 4 * 365: # more than 4 years
            continue
        '''
        
        if print_progress:
            if cnt % 1000 == 0:
                print('progress = ', 1.0 * cnt / tot)        
                sys.stdout.flush()
        
        feature_vector = get_pr_sim_vector(pullA, pull)        
        results[pull["number"]] = c.predict_proba([feature_vector])[0][1]
        # pre_results[pull["number"]] = c.predict([feature_vector])[0]
    
    result = [(x,y) for x, y in sorted(results.items(), key=lambda x: x[1], reverse=True)][:topK]
    
    # for x, y in result:
    #     print(x, sim(pullA, api.get('repos/%s/pulls/%s' % (repo, x))))

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


def simulate_timeline(repo, renew=False, run_num=200):
    init_model_with_repo(repo)
    pulls = repo_get(repo, 'pull', renew_pr_list)
        
    all_p = set([str(pull["number"]) for pull in pulls])
    part_p = load_part(repo)
    select_p = set(shuffle(list(all_p - part_p))[:run_num])
    
    log = open('evaluation/'+repo.replace('/','_')+'_stimulate_detect.log', 'a+')
    out = open('evaluation/'+repo.replace('/','_')+'_stimulate_top1_sample200_sheet.txt', 'a+')
    
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
        
        status = 'Y' if (prob >= 0.99) else 'N/A'
        
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
    
    log.close()
    out.close()


def find_on_openpr(repo, time_stp=None):
    print('time_stp', time_stp)
    
    # init model
    pulls = get_pull_list(repo, renew_pr_list)
    
    for pull in pulls:
        cite[str(pull["number"])] = get_another_pull(pull)
    
    init_model_with_repo(repo)
    
    mode = 'a' if last_number else 'w'
    print('write mode=',mode)
    
    out = open('detection/'+repo.replace('/','_')+'_topk.txt', mode)
    out2 = open('detection/'+repo.replace('/','_')+'_top1.txt', mode)
    
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
        print("%s %8s %8s %.4f" % (repo, str(num1), str(num2), prob))
        print(" ".join("%.4f" % f for f in sim))
        #print(",".join(parse_sim(sim)))
        
        print('https://www.github.com/%s/pull/%s' % (repo, str(num1)))
        print('https://www.github.com/%s/pull/%s' % (repo, str(num2)))
        sys.stdout.flush()

        print("%s %8s %8s %.4f" % (repo, str(num1), str(num2), prob), file=out2)
        print(" ".join("%.4f" % f for f in sim), file=out2)
        #print(",".join(parse_sim(sim)), file=out2)
        print('https://www.github.com/%s/pull/%s' % (repo, str(num1)), file=out2)
        print('https://www.github.com/%s/pull/%s' % (repo, str(num2)), file=out2)

        print(repo, num1, ':', topk, file=out)

    out.close()
    out2.close()


def simulate_timeline_only_dup_pair(repo):
    init_model_with_repo(repo)
    top1_num, top1_tot, top5_num = 0, 0, 0
    
    labeled_dup = {}
    with open('data/msr_positive_pairs.txt') as f:
        for t in f.readlines():
            r, n1, n2 = t.strip().split()
            if n1 > n2:
                n1, n2 = n2, n1
            if r == repo:
                li = [int(x[0]) for x in get_topK(repo, n2, 5)]
                if int(n1) == li[0]:
                    top1_num += 1
                if int(n1) in li:
                    top5_num += 1
                top1_tot += 1
    print('top1 acc =', 1.0 * top1_num / top1_tot)
    print('top5 acc =', 1.0 * top5_num / top1_tot)


if __name__ == "__main__":
    
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
                        sheet_path = 'evaluation/'+t.strip().replace('/','_')+'_stimulate_top1_sample200_sheet.txt'
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
    # print(get_topK('pytorch/vision', '492', 10, True))
    # print(get_topK('scikit-learn/scikit-learn', '10365', 10, True))
    # print(get_topK('facebook/react', '12755', 10, True))
    
    r = 'spring-projects/spring-framework'
    if len(sys.argv) > 1:
        r = sys.argv[1]
    if len(sys.argv) > 2:
        renew_pr_list = (sys.argv[2] == 'True')
    if len(sys.argv) > 3:
        last_number = int(sys.argv[3])
        print('last = ', last_number)
    
    print('start detect open PR on', r)
    
    # default_time_stp = datetime.utcnow() - timedelta(days=30)
    default_time_stp = None
    
    find_on_openpr(r, default_time_stp)

    # find_on_openpr('spring-projects/spring-framework')
    '''
