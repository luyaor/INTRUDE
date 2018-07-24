import os
import re
import sys
import random
import time

from flask import Flask
from flask_github import GitHub

app = Flask(__name__)

app.config['GITHUB_CLIENT_ID'] = os.environ.get('GITHUB_CLIENT_ID')
app.config['GITHUB_CLIENT_SECRET'] = os.environ.get('GITHUB_CLIENT_SECRET')
app.config['GITHUB_BASE_URL'] = 'https://api.github.com/'
app.config['GITHUB_AUTH_URL'] = 'https://github.com/login/oauth/'

api = GitHub(app)
@api.access_token_getter
def token_getter():
    # access_token = '4ddd8df8592018da4fa4002d9493abfc0064883b'
    access_token = '005a690debfb00ff95f7473468bb73e6ecb893f6'
    return access_token

# -----------------------------------------------------------------------------

from sklearn.ensemble import GradientBoostingClassifier
from sklearn.ensemble import AdaBoostClassifier
from sklearn.utils import shuffle
from sklearn.metrics import average_precision_score
from sklearn.metrics import precision_recall_curve
from sklearn import svm
from sklearn import linear_model
import matplotlib.pyplot as plt
from metric_learn import LMNN
from numpy import array

from util import localfile_tool

import fetch_raw_diff
import fetch_pull_files
import fetch_pull_content
from comparer import *

def get_pull(repo, num, renew=False):
    path = 'pr_data/%s/%s/api.json' % (repo, num)
    if os.path.exists(path) and (not renew):
        try:
            return localfile_tool.get_file(path)
        except:
            print(repo, num)
            raise Exception('error on get pull!')
                
    r = api.get('repos/%s/pulls/%s' % (repo, num))
    # time.sleep(0.5)
    localfile_tool.write_to_file(path, r)
    return r


def get_pull_list(repo, renew=False):
    repo = repo.strip()
    pull_list_path = 'pr_data/' + repo + '/pull_list.json'
    if (not renew) and os.path.exists(pull_list_path):
        pulls = localfile_tool.get_file(pull_list_path)
    else:
        pulls = api.request('GET', 'repos/%s/pulls?state=closed' % repo, True)
        open_pulls = api.request('GET', 'repos/%s/pulls?state=open' % repo, True)
        pulls.extend(open_pulls)
        localfile_tool.write_to_file(pull_list_path, pulls)
    return pulls

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

def get_another_pull(pull):
    comments_href = pull["_links"]["comments"]["href"]
    comments = api.request('GET', comments_href, True)
    candidates = []
    for comment in comments:
        candidates.extend(get_pr_numbers(comment["body"]))
    candidates.extend(get_pr_numbers(pull["body"]))
    
    return list(set(candidates))

def run_and_save(repo):
    repo = repo.strip()
    
    skip_exist = True

    pulls = get_pull_list(repo)

    for pull in pulls:
        pull_dir = 'pr_data/' + repo + '/' + str(pull["number"])
        
        if skip_exist and os.path.exists(pull_dir + '/raw_diff.json'):
            continue
        
        localfile_tool.write_to_file(pull_dir + '/api.json', pull)
    
        try:
            file_list = fetch_raw_diff.fetch_raw_diff(pull["diff_url"])
            localfile_tool.write_to_file(pull_dir + '/raw_diff.json', file_list)
        except Exception as e:
            print('Error:', e)
        
            try:
                pull_files = fetch_pull_files.fetch_pull_files(repo, pull["number"])
                localfile_tool.write_to_file(pull_dir + '/pull_files.json', pull_files)
                file_list = [fetch_raw_diff.parse_diff(file["file_full_name"], file["changed_code"]) for file in pull_files]
                localfile_tool.write_to_file(pull_dir + '/raw_diff.json', file_list)
            except Exception as e:
                print('Error:', e)
        '''
        try:
            pull_content = fetch_pull_content.fetch_pull_content(repo, pull["number"])
            with open(pull_dir + '/pull_content.html', 'wb') as fd:
                chunk_size = 1024
                for chunk in pull_content.iter_content(chunk_size):
                    fd.write(chunk)
        except Exception as e:
            print('Error:', e)
        '''
        
        print('finish on', repo, pull["number"])


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


# ------------------------------------------------------------

def init_model_with_pulls(pulls, save_id=None):
    init_model_from_raw_docs([pull["title"] for pull in pulls] + [pull["body"] for pull in pulls], save_id)
    print('finish init nlp model!')

def init_model_with_repo(repo):
    print('init nlp model with %s data!' % repo)
    save_id = repo.replace('/', '.')
    init_model_with_pulls(get_pull_list(repo))

def get_sim(repo, num1, num2):
    p1 = get_pull(repo, num1)
    p2 = get_pull(repo, num2)
    return sim(p1, p2)

def get_sim_wrap(args):
    return get_sim(*args)

'''
def get_sim(repo, num1, num2):
    return other_feature(get_pull(repo, num1), get_pull(repo, num2))
    
def get_sim_wrap(args):
    return get_sim(*args)
'''


# todo remove noise in random pairs
def random_pairs():
    """
    repos = os.listdir('./pr_data')
    while True:
        try:
            repo = repos[random.randint(0, len(repos) - 1)]
            repo_ = os.listdir('./pr_data/' + repo)[0]
            repo = repo + '/' + repo_
            
            pulls = get_pull_list(repo)
            x = pulls[random.randint(0, len(pulls) - 1)]["number"]
            y = pulls[random.randint(0, len(pulls) - 1)]["number"]
            if (x != y):
                break
        except:
            continue
        
    """
    repos = os.listdir('./pr_data')
    find = False
    while not find:
        # random a repo
        while True:
            try:
                repo = repos[random.randint(0, len(repos) - 1)]
                repo_ = os.listdir('./pr_data/' + repo)[0]
                repo = repo + '/' + repo_
                
                
                if repo == 'rails/rails':
                    continue
                             
                if repo not in ['django/django', 'almasaeed2010/AdminLTE', 'lord/slate', 'nathanmarz/storm']:
                    continue
                
                break
            except:
                continue
        
        nums = os.listdir('./pr_data/%s' % repo)
        
        # random a pair
        l = len(nums)
        
        '''
        if l <= 200:
            continue
        
        if l >= 1000:
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


from multiprocessing import Pool

'''
def print_data():
    X = localfile_tool.get_file('data/classify_data_X_marked.json')
    y = localfile_tool.get_file('data/classify_data_X_marked.json')
        
    false_data = 'data/random_negative_pairs.txt'
    
    f = open(false_data)
    num = 0
    a = []
    for l in f.readlines():
        a.append((l, X[num]))
        num += 1
    
    a = sorted(a, key = lambda x: x[1][0], reverse=True)
    
    for x in a:
        print(x)
'''


'''
def get_feature_vector(data, out=None):
    out = 'data/' + data.replace('data/','').replace('.txt','').replace('/','_') + '_feature_vector'
    X_path = out + '_X.json'
    y_path = out + '_y.json'
    if os.path.exists(X_path) and os.path.exists(y_path):
        print(out, 'already exists!')
        X = localfile_tool.get_file(X_path)
        y = localfile_tool.get_file(y_path)
        return X, y
    X = []
    y = []
'''

def get_feature_vector(false_data, true_data, out=None):
    
    # false_data = 'data/false_pairs.txt'
    # ture_data = 'data/true_pairs.txt'
    # false_data = 'data/random_negative_pairs.txt'
    # true_data = 'data/msr_positive_pairs.txt'
    
    if out is None:
        out = 'data/' + (false_data + '_' + true_data).replace('data/','').replace('.txt','').replace('/','_') + '_feature_vector'
    X_path = out + '_X.json'
    y_path = out + '_y.json'
    
    print('run get_feature_vector!')
    print('input=', false_data, true_data)
    print('out=', out)
    
    if os.path.exists(X_path) and os.path.exists(y_path):
        print(out, 'already exists!')
        X = localfile_tool.get_file(X_path)
        y = localfile_tool.get_file(y_path)
        return X, y
    
    X = []
    y = []
    
    
    # run with all PR's info model
    p = {}
    with open(false_data) as f:
        for l in f.readlines():
            r, n1, n2 = l.strip().split()
            if r not in p:
                p[r] = []
            p[r].append((n1, n2, 0))
    with open(true_data) as f:
        for l in f.readlines():
            r, n1, n2 = l.strip().split()
            if r not in p:
                p[r] = []
            p[r].append((n1, n2, 1))
    
    print('finish read!')
    print(p.keys())
    
    out_file = open(out + '_X_and_Y.txt', 'w+')
    
    for r in p:
        print(r)        
        # pull_list = get_pull_list(r)
        # init_other_model([[p["title"] for p in pull_list], [p["body"] for p in pull_list], [ str(p["title"]) + str(p["body"]) for p in pull_list] ])
        # print('init_other_model ok!')
        
        # init_model_with_repo(r)
        
        li = shuffle(get_pull_list(r))
        li = li[:5000]
        for z in p[r]:
            li.append(get_pull(r, z[0]))
            li.append(get_pull(r, z[1]))
        init_model_with_pulls(li, r.replace('/','_') + '_tmp')
        
        print('PR num=', len(li))
        
        for z in p[r]:
            t1 = get_sim(r, z[0], z[1])
            t2 = z[2]
            X.append(t1)
            y.append(t2)
            print(r, z[0], z[1], t1, t2, file=out_file)
    
    out_file.close()

    '''
    # run with with only PR's info
    pull_list = []
    with open(false_data) as f:
        for l in f.readlines():
            r, n1, n2 = l.strip().split()
            pull_list.append(get_pull(r, n1))
            pull_list.append(get_pull(r, n2))
    with open(true_data) as f:
        for l in f.readlines():
            r, n1, n2 = l.strip().split()
            pull_list.append(get_pull(r, n1))
            pull_list.append(get_pull(r, n2))

    # init NLP model
    
    # init_model_with_pulls(pull_list)
    
    init_other_model([ [p["title"] for p in pull_list], [p["body"] for p in pull_list], [ str(p["title"]) + str(p["body"]) for p in pull_list] ])
    print('init_other_model ok!')
                     
    # get the feature map of all PR pairs
    with open(false_data) as f:
        pairs = [tuple(l.strip().split()) for l in f.readlines()]
        r = [get_sim_wrap(p) for p in pairs]
        # with Pool(processes=10) as pool:
        #     r = pool.map(get_sim_wrap, pairs)
        X.extend(r)
        y.extend([0 for i in range(len(r))])
    
    with open(true_data) as f:
        pairs = [tuple(l.strip().split()) for l in f.readlines()]
        r = [get_sim_wrap(p) for p in pairs]
        # with Pool(processes=10) as pool:
        #     r = pool.map(get_sim_wrap, pairs)
        X.extend(r)
        y.extend([1 for i in range(len(r))])
    
    '''
    
    # save to local
    localfile_tool.write_to_file(X_path, X)
    localfile_tool.write_to_file(y_path, y)
    
    return (X, y)

"""
def metric_learn():
    X = localfile_tool.get_file('data/classify_data_X.json')
    y = localfile_tool.get_file('data/classify_data_y.json')
    X, y = shuffle(X, y)
    
    X, y = array(X), array(y)
    lmnn = LMNN(k=5, learn_rate=1e-3)
    lmnn.fit(X, y)
    print(lmnn.metric())

    # print(X[0])
    # print(lmnn.transform(X[0]))
    for i in range(len(X)):
        print(lmnn.transform(X[i]), lmnn.transform(X[i])
"""

def extract_col(a, c):
    for i in range(len(a)):
        t = []
        for j in range(len(c)):
            if c[j]==1:
                t.append(a[i][j])
        a[i] = t

        
def classify(params_flag=[1,1,1,1,1]):
    params_set = ['title', 'desc', 'code', 'file_list', 'location']
    
    used_set = []
    for j in range(len(params_flag)):
        if params_flag[j]:
            used_set.append(params_set[j])
    print('+'.join(used_set))
    
    def data_prepare(): # mix our and msr
        print('data: mix our and msr')
        
        X = localfile_tool.get_file('data/classify_our_data_X.json')
        y = localfile_tool.get_file('data/classify_our_data_y.json')
        X_msr = localfile_tool.get_file('data/improve_false_data_msr_positive_pairs_lsi_X.json')
        y_msr = localfile_tool.get_file('data/improve_false_data_msr_positive_pairs_lsi_y.json')
        X_msr, y_msr = shuffle(X_msr, y_msr)

        X, X_msr = X + X_msr[:320], X_msr[320:]
        y, y_msr = y + y_msr[:320], y_msr[320:]

        X_train, y_train = X, y
        X_test, y_test = X_msr[:400], y_msr[:400]
        return (X_train, y_train, X_test, y_test)
    
    def data_prepare_all(file):        
        X_file, y_file = file + '_X.json', file + '_y.json'
        print('data: all ', X_file, y_file)
        X = localfile_tool.get_file(X_file)
        y = localfile_tool.get_file(y_file)
        X, y = shuffle(X, y)
        num = len(X)
        train_num = int (num * 4 / 5)
        X_train, X_test = X[:train_num], X[train_num:]
        y_train, y_test = y[:train_num], y[train_num:]
        return (X_train, y_train, X_test, y_test)
    
    def data_train_test():
        X_train, y_train = get_feature_vector(
            'data/part_false_data1.txt',
            'data/part_msr_positive_pairs.txt')
        '''
        X_train1, y_train1 = get_feature_vector(
            'data/rly_false_pairs.txt',
            'data/rly_true_pairs.txt')
        
        X_train += X_train1
        y_train += y_train1
        '''
        
        X_test, y_test = get_feature_vector(
            'data/part_false_data2.txt',
            'data/part_last_msr_positive_pairs.txt')
        
        return (X_train, y_train, X_test, y_test)
                                              
        
    def data_prepare2():
        print('data: our -> msr')
        #X_train = localfile_tool.get_file('data/improve_false_data_msr_positive_pairs_tfidf_X.json')
        #y_train = localfile_tool.get_file('data/improve_false_data_msr_positive_pairs_tfidf_y.json')
        
        #X_test = localfile_tool.get_file('data/improve_false_data_msr_positive_pairs_lsi_X.json')
        #y_test = localfile_tool.get_file('data/improve_false_data_msr_positive_pairs_lsi_y.json')
        
        
        X_train = localfile_tool.get_file('data/classify_our_data_X.json')
        y_train = localfile_tool.get_file('data/classify_our_data_X.json')
        X_test = localfile_tool.get_file('data/improve_false_data_msr_positive_pairs_lsi_X.json')
        y_test = localfile_tool.get_file('data/improve_false_data_msr_positive_pairs_lsi_y.json')
        
        X_test, y_test = shuffle(X_test, y_test)
        X_test, y_test = X_test[:500] + X_test[-500:], y_test[:500] + y_test[-500:]   
        return (X_train, y_train, X_test, y_test)
    
    def data_prepare_raw():
        X, y = get_feature_vector(
                         'data/big_false_data.txt',
                         'data/msr_positive_pairs.txt',
                         'data/improve_false_msr_positive_other_improved_TFIDF'
                        )
        X, y = shuffle(X, y)
        num = len(X)
        train_num = int (num * 4 / 5)
        X_train, X_test = X[:train_num], X[train_num:]
        y_train, y_test = y[:train_num], y[train_num:]
        return (X_train, y_train, X_test, y_test)
    
    # X_train, y_train, X_test, y_test = data_train_test()
    # X_train, y_train, X_test, y_test = data_prepare_all('data/part_false_data1_part_msr_positive_pairs_feature_vector')
    X_train, y_train, X_test, y_test = data_prepare_all('data/improve_false_data_msr_positive_pairs_tfidf')
    # X_train, y_train, X_test, y_test = data_prepare2()
    
    extract_col(X_train, params_flag)
    extract_col(X_test, params_flag)
    print('params extract=',params_flag)
    
    print('training_set', len(X_train), 'testing_set', len(X_test), 'feature_length=', len(X_train[0]))
    
    # model choice
    
    #clf = GradientBoostingClassifier(n_estimators=100, learning_rate=0.8, max_depth=15, random_state=0).fit(X_train, y_train)
    #print('model: GradientBoosting')
    # clf = GradientBoostingClassifier(n_estimators=10, learning_rate=1.0, max_depth=7, random_state=0).fit(X_train, y_train)
    # clf = AdaBoostClassifier(n_estimators=10).fit(X_train, y_train)
    
    clf = svm.SVC(random_state=0, probability=1).fit(X_train, y_train)
    print('model: SVM')
    
    
    # clf = linear_model.SGDClassifier(tol=0.01).fit(X_train, y_train)
    
    # print(clf.coef_)
    # print(clf.intercept_)
    # print(clf.loss_function_)
          
    
    # Predict
    # acc = clf.score(X_test, y_test)
    # print('Mean Accuracy:', acc)
    
    y_score = clf.decision_function(X_test)
    average_precision = average_precision_score(y_test, y_score)
    
    print('Average precision score: {0:0.4f}'.format(average_precision))
    
    
    # draw the PR-curve
    precision, recall, _ = precision_recall_curve(y_test, y_score)

    plt.step(recall, precision, color='b', alpha=0.1, where='post')
    plt.fill_between(recall, precision, step='post', alpha=0.1, color='b')

    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.ylim([0.0, 1.05])
    plt.xlim([0.0, 1.0])
    plt.title('Precision-Recall curve')
    
    
    pre_y = clf.predict_proba(X_test)
    
    '''
    for output in ['data/true_output.txt', 'data/false_output.txt', 'data/all_output.txt']:
        choice = ('true' in output)
        with open(output, 'a') as f:
            for i in range(len(X_test)):
                if (y_test[i] == choice) or ('all' in output):
                    """
                    zero = True
                    for t in X_test[i]:
                        if t > 0:
                            zero = False
                    if zero:
                        pre_y[i][1] = 0
                    """
                    print(pre_y[i][1], '+'.join(used_set), file=f)
    '''
                    
    return clf

def draw(way = "default"):
    out = open('data/result_for_true_false.txt', 'w+')
    
    print('------True Result------', file=out)
    with open('data/true_pairs.txt') as f:
        for line in f.readlines():
            if not line:
                break
            
            repo, n1, n2 = line.strip().split()
            
            print(repo, n1, n2)
            print(repo, n1, n2, calc(repo, n1, n2, way), way + "(on_postive_data)", file=out)
            
    
    print('------False Result------', file=out)
    with open('data/false_pairs.txt') as f:
        for line in f.readlines():
            if not line:
                break
            
            repo, n1, n2 = line.strip().split()
            
            print(repo, n1, n2)
            print(repo, n1, n2, calc(repo, n1, n2, way), way + "(on_negative_data)", file=out)
    
    out.close()
    """
    for i in range(40):
        repo, n1, n2 = random_pairs()
        print(repo, n1, n2, calc(repo, n1, n2))
    """





