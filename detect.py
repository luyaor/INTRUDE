# ------------------------------------------------------------
from datetime import datetime, timedelta

from main import *
from git import *
from gen import *
from comparer import *

c = classify()

cite = {}
last_number = None
renew_pr_list = False

def get_time(t):
    return datetime.strptime(t, "%Y-%m-%dT%H:%M:%SZ")

def get_topK(repo, num1, topK = 10, print_progress = False):
    pulls = get_pull_list(repo)
    pullA = get_pull(repo, num1) # api.get('repos/%s/pulls/%s' % (repo, num1))
    
    cite[str(pullA["number"])] = get_another_pull(pullA)

    results = {}
    tot = len(pulls)
    cnt = 0
    
    pull_v = {}
    
    for pull in pulls:
        cnt += 1
        # same
        if str(pull["number"]) == str(num1):
            continue
        
        # same author
        if pullA["user"]["id"] == pull["user"]["id"]:
            continue
        
        # for predict
        # "cite" cases
        if str(pull["number"]) in cite.get(str(pullA["number"]), []):
            continue
        
        if str(pullA["number"]) in cite.get(str(pull["number"]), []):
            continue

        # revert cases
        if 'revert' in pull["title"].lower():
            continue
        
        # filter out too big pull
        if check_too_big(pull):
            continue
        
        # filter out too old pull
        if abs((get_time(pullA["updated_at"]) - get_time(pull["updated_at"])).days) >= 4 * 365: # more than 4 years
            continue
        
        # create after another is merged
        if (pull["merged_at"] is not None) and (get_time(pull["merged_at"]) < get_time(pullA["created_at"])):
            continue

        if print_progress:
            if cnt % 1000 == 0:
                print('progress = ', 1.0 * cnt / tot)        
                sys.stdout.flush()
        
        feature_vector = get_sim_vector(pullA, pull)        
        results[pull["number"]] = c.predict_proba([feature_vector])[0][1]
        # pre_results[pull["number"]] = c.predict([feature_vector])[0]
    
    result = [(x,y) for x, y in sorted(results.items(), key=lambda x: x[1], reverse=True)][:topK]
    
    # for x, y in result:
    #     print(x, sim(pullA, api.get('repos/%s/pulls/%s' % (repo, x))))

    return result


                         
def find_on_openpr(repo, time_stp=None):
    print('time_stp', time_stp)
    
    # init model
    pulls = get_pull_list(repo, renew_pr_list)
    
    for pull in pulls:
        cite[str(pull["number"])] = get_another_pull(pull)
    
    try:
        init_model_with_pulls(None, repo.replace('/','_') + '_marked')
    except:
        print('no exist model!')
        li = shuffle(pulls)[:5000]        
        init_model_with_pulls(li, repo.replace('/','_') + '_marked2')
    
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

        sim = calc_sim(pull, get_pull(repo, num2))
        print("%s %8s %8s %.4f" % (repo, str(num1), str(num2), prob))
        print(",".join("{}:{}".format(k, v) for k, v in sim.items()))
        print(",".join(parse_sim(sim)))
        
        print('https://www.github.com/%s/pull/%s' % (repo, str(num1)))
        print('https://www.github.com/%s/pull/%s' % (repo, str(num2)))
        sys.stdout.flush()

        print("%s %8s %8s %.4f" % (repo, str(num1), str(num2), prob), file=out2)
        print(",".join("{}:{}".format(k, v) for k, v in sim.items()), file=out2)
        print(",".join(parse_sim(sim)), file=out2)
        print('https://www.github.com/%s/pull/%s' % (repo, str(num1)), file=out2)
        print('https://www.github.com/%s/pull/%s' % (repo, str(num2)), file=out2)

        print(repo, num1, ':', topk, file=out)

    out.close()
    out2.close()

if __name__ == "__main__":
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
