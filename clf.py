import os
import re
import sys
import random
import copy

from sklearn.ensemble import *
from sklearn.metrics import *
from sklearn.linear_model import LogisticRegression
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis
from sklearn.tree import DecisionTreeClassifier
from sklearn.utils import shuffle
from sklearn import svm
from sklearn import linear_model
from sklearn.feature_selection import SelectKBest, f_regression
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split

import matplotlib.pyplot as plt
from numpy import array
from multiprocessing import Pool

from util import localfile

from comp import *
from git import *

# ----------------INPUT & CONFIG------------------------------------

default_model = 'boost'

data_folder = '/home/luyao/PR_get/INTRUDE/data/clf'

dataset = []


dataset = [
    [data_folder + '/rly_true_pairs.txt', 1, 'train'],
    [data_folder + '/rly_false_pairs.txt', 0, 'train'],
    [data_folder + '/small_part_msr.txt', 1, 'train'],
    [data_folder + '/small2_part_msr.txt', 1, 'train'],
    [data_folder + '/small_part_negative.txt', 0, 'train'],
]


dataset += [
    [data_folder + '/manual_label_false.txt', 0, 'test'],
    [data_folder + '/manual_label_true.txt', 1, 'test'],
    [data_folder + '/openpr_label_false.txt', 0, 'test'],
    [data_folder + '/openpr_label_true.txt', 1, 'test'],
]

'''
dataset += [
    [data_folder + '/msr_positive_pairs.txt', 1, 'train'],
    [data_folder + '/big_false_data.txt', 0, 'train'],
]
'''

model_data_save_path_suffix = 'text_%s_code_%s_%s' % (text_sim_type, code_sim_type, extract_sim_type)

if add_timedelta:
    model_data_save_path_suffix += '_add_time'

part_params = None


draw_pic = False
model_data_random_shuffle_flag = False
model_data_renew_flag = False

# ------------------------------------------------------------

print('text_sim_type=', text_sim_type)
print('code_sim_type=', code_sim_type)
print('extract_sim_type=', extract_sim_type)
print('Data Type:', model_data_save_path_suffix)

# ------------------------------------------------------------

def init_model_with_pulls(pulls, save_id=None):    
    t = [str(pull["title"]) for pull in pulls]
    b = []
    for pull in pulls:
        if pull["body"] and (len(pull["body"]) <= 1000):
            b.append(pull["body"])
    init_model_from_raw_docs(t + b, save_id)
    
    if code_sim_type == 'tfidf':
        c = []
        pulls = pulls[:1000]
        for pull in pulls: # only added code
            try:
                if not check_too_big(pull):
                    p = copy.deepcopy(pull)
                    p["file_list"] = fetch_pr_info(p)
                    c.append(get_code_tokens(p)[0])
            except Exception as e:
                print('Error on get', pull['url'])
        
        init_code_model_from_tokens(c, save_id + '_code' if save_id is not None else None)


def init_model_with_repo(repo, save_id=None):
    print('init nlp model with %s data!' % repo)
    #save_id = repo.replace('/','_') + '_all'
    #init_model_with_pulls(get_pull_list(repo), save_id)
    if save_id is None:
        save_id = repo.replace('/','_') + '_marked'
    else:
        save_id = repo.replace('/','_') + '_' + save_id

    try:
        init_model_with_pulls([], save_id)
    except:
        init_model_with_pulls(shuffle(get_repo_info(repo, 'pull'))[:5000], save_id)

# ------------------------------------------------------------
'''
def get_feature_vector_from_path(data):
    X_path = data.replace('.txt','') + '_commit_feature_vector_mix' + '_X.json'
    y_path = data.replace('.txt','') + '_commit_feature_vector_mix' + '_y.json'
    if os.path.exists(X_path) and os.path.exists(y_path):
        # print('warning: feature vectore already exists!', out)
        X = localfile.get_file(X_path)
        y = localfile.get_file(y_path)
        return X, y
    else:
        raise Exception('no such file %s' % data)
'''

def get_feature_vector(data, label, renew=False, out=None):
    print('Model Data Input=', data)
    
    default_path = data.replace('.txt','') + '_feature_vector'
    out = default_path if out is None else default_path + '_' + out
    X_path, y_path = out + '_X.json', out + '_y.json'
    
    if os.path.exists(X_path) and os.path.exists(y_path) and (not renew):
        print('warning: feature vectore already exists!', out)
        X = localfile.get_file(X_path)
        y = localfile.get_file(y_path)
        return X, y

    X, y = [], []
    
    # run with all PR's info model
    p = {}
    with open(data) as f:
        all_pr = f.readlines()
    
    # tiny test
    # all_pr = shuffle(all_pr, random_state=12345)[:100]
    
    for l in all_pr:
        r, n1, n2 = l.strip().split()
        if r not in p:
            p[r] = []
        p[r].append((n1, n2, label))

    out_file = open(out + '_X_and_Y.txt', 'w+')
    
    for r in p:
        print('Start running on', r)

        # init NLP model
        init_model_with_repo(r)
        
        print('pairs num=', len(p[r]))

        # calc feature vet
        def get_sim(repo, num1, num2):
            p1 = get_pull(repo, num1)
            p2 = get_pull(repo, num2)
            return get_pr_sim_vector(p1, p2)

        # sequence
        for z in p[r]:
            x0, y0 = get_sim(r, z[0], z[1]), z[2]
            X.append(x0)
            y.append(y0)
            print(r, z[0], z[1], x0, y0, file=out_file)
        
        '''
        # run parallel
        for label in [0, 1]:
            pairs = []
            for z in p[r]:
                if z[2] == label:
                    pairs.append((r, z[0], z[1]))
            with Pool(processes=10) as pool:
                result = pool.map(get_sim_wrap, pairs)
            X.extend(result)
            y.extend([label for i in range(len(result))])
        '''

    out_file.close()

    # save to local
    localfile.write_to_file(X_path, X)
    localfile.write_to_file(y_path, y)
    return (X, y)

def classify(model_type=default_model):
    def model_data_prepare(dataset):        
        X_train, y_train = [], []
        X_test, y_test = [], []
        
        for s in dataset:
            new_X, new_y = get_feature_vector(s[0], s[1], model_data_renew_flag, model_data_save_path_suffix)
            if s[2] == 'train':
                X_train += new_X
                y_train += new_y
            elif s[2] == 'test':
                X_test += new_X
                y_test += new_y

        def get_ran_shuffle(X, y, train_percent = 0.5):
            X, y = shuffle(X, y, random_state=12345)
            num = len(X)
            train_num = int (num * train_percent)
            X_train, X_test = X[:train_num], X[train_num:]
            y_train, y_test = y[:train_num], y[train_num:]
            return (X_train, y_train, X_test, y_test)

        # ran shuffle with train set and test set
        if model_data_random_shuffle_flag:
            X_train, y_train, X_test, y_test = get_ran_shuffle(X_train + X_test, y_train + y_test)
            
        return (X_train, y_train, X_test, y_test)
    
    print('Data Loading.........')
    
    X_train, y_train, X_test, y_test = model_data_prepare(dataset)
    
    '''
    X_train_new, y_train_new = [], []
    
    for i in range(len(y_train)):
        X_train_new.append(X_train[i])
        y_train_new.append(y_train[i])
        if y_train[i] == 0:
            for j in range(10):
                X_train_new.append(X_train[i])
                y_train_new.append(y_train[i])

    X_train, y_train = X_train_new, y_train_new
    '''
    
    if part_params:
        def extract_col(a, c):
            for i in range(len(a)):
                t = []
                for j in range(len(c)):
                    if c[j]==1:
                        t.append(a[i][j])
                a[i] = t
        extract_col(X_train, part_params)
        extract_col(X_test, part_params)
        print('extract=', part_params)
    
    print('--------------------------')
    print('Model: training_set', len(X_train), 'testing_set', len(X_test), 'feature_length=', len(X_train[0]))
    
    # model choice

    # clf = GradientBoostingClassifier(n_estimators=160, learning_rate=1.0, max_depth=15, random_state=0).fit(X_train, y_train)
    # clf = AdaBoostClassifier(n_estimators=60).fit(X_train, y_train)
    # clf =  DecisionTreeClassifier(max_depth=50)
    
    print('------ model: ', model_type, '------' )
    if model_type == 'SVM':
        clf = svm.SVC(random_state=0, probability=1)
    elif model_type == 'LogisticRegression':
        clf = LogisticRegression()
    elif model_type == 'SGDClassifier':
        clf = linear_model.SGDClassifier(tol=0.01)
    elif model_type == 'boost':
        clf = AdaBoostClassifier(n_estimators=100, learning_rate=0.1).fit(X_train, y_train)

    # clf = GradientBoostingClassifier(n_estimators=200, learning_rate=0.3, max_depth=25, random_state=0)
    
    
    clf = clf.fit(X_train, y_train)
    
    # model result
    # print('coef in model = ', clf.coef_)
    # print(clf.intercept_)
    # print(clf.loss_function_)
    
    if model_type == 'boost':
        print(clf.feature_importances_)
    
    # Predict
    acc = clf.score(X_test, y_test)
    print('Mean Accuracy:', acc)
    
    y_score = clf.decision_function(X_test)
    average_precision = average_precision_score(y_test, y_score)
    print('Average precision score: {0:0.4f}'.format(average_precision))
    
    if draw_pic:
        # draw the PR-curve
        precision, recall, _ = precision_recall_curve(y_test, y_score)

        plt.step(recall, precision, color='b', alpha=0.1, where='post')
        plt.fill_between(recall, precision, step='post', alpha=0.1, color='b')

        plt.xlabel('Recall')
        plt.ylabel('Precision')
        plt.ylim([0.0, 1.05])
        plt.xlim([0.0, 1.0])
        plt.title('Precision-Recall curve')
    
    return clf

if __name__ == "__main__":
    classify()
