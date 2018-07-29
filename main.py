import os
import re
import sys
import random

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

from util import localfile_tool
from comparer import *
from git import *

dataset = [
    ['data/rly_false_pairs.txt', 0, 'train'],
    ['data/small_part_msr.txt', 1, 'train'],
    ['data/rly_true_pairs.txt', 1, 'train'],
    ['data/small_part_negative.txt', 0, 'test'],
    ['data/small2_part_msr.txt', 1, 'test'],
]

part_params = [1,1,1,1,1,1]
draw_pic = False
model_data_random_shuffle_flag = False
model_data_renew_flag = False
model_data_save_path_suffix = None

# ------------------------------------------------------------
def init_model_with_pulls(pulls, save_id=None):
    t = [str(pull["title"]) for pull in pulls]
    b = []
    for pull in pulls:
        if pull["body"] and (len(pull["body"]) <= 1000):
            b.append(pull["body"])
    init_model_from_raw_docs(t + b, save_id)
    print('finish init nlp model!')
    
def init_model_with_repo(repo):
    print('init nlp model with %s data!' % repo)
    #save_id = repo.replace('/','_') + '_all'
    #init_model_with_pulls(get_pull_list(repo), save_id)
    save_id = repo.replace('/','_') + '_marked2'
    try:
        init_model_with_pulls([], save_id)
    except:
        init_model_with_pulls(shuffle(get_pull_list(repo))[:5000], save_id)

def get_sim(repo, num1, num2):
    p1 = get_pull(repo, num1)
    p2 = get_pull(repo, num2)
    return get_sim_vector(p1, p2)


# ------------------------------------------------------------

def get_feature_vector_from_path(data):
    X_path = data.replace('.txt','') + '_commit_feature_vector_mix' + '_X.json'
    y_path = data.replace('.txt','') + '_commit_feature_vector_mix' + '_y.json'
    if os.path.exists(X_path) and os.path.exists(y_path):
        # print('warning: feature vectore already exists!', out)
        X = localfile_tool.get_file(X_path)
        y = localfile_tool.get_file(y_path)
        return X, y
    else:
        raise Exception('no such file %s' % data)
            
def get_feature_vector(data, label, renew=False, out=None):
    default_path = 'data/' + data.replace('data/','').replace('.txt','').replace('/','_') + '_feature_vector'
    if out is None:
        out = default_path
    else:
        out = default_path + '_' + out

    X_path = out + '_X.json'
    y_path = out + '_y.json'
    
    print('Model Data Input=', data)
    
    if os.path.exists(X_path) and os.path.exists(y_path) and (not renew):
        # print('warning: feature vectore already exists!', out)
        X = localfile_tool.get_file(X_path)
        y = localfile_tool.get_file(y_path)
        return X, y
    
    X = []
    y = []
    
    # run with all PR's info model
    p = {}
    with open(data) as f:
        for l in f.readlines():
            r, n1, n2 = l.strip().split()
            if r not in p:
                p[r] = []
            p[r].append((n1, n2, label))

    print('finish read!')

    out_file = open(out + '_X_and_Y.txt', 'w+')
    
    for r in p:
        print(r)        
        # pull_list = get_pull_list(r)
        # init_other_model([[p["title"] for p in pull_list], [p["body"] for p in pull_list], [ str(p["title"]) + str(p["body"]) for p in pull_list] ])
        # print('init_other_model ok!')
        
        # init_model_with_repo(r)        
        li = shuffle(get_pull_list(r))[:5000]
        for z in p[r]:
            li.append(get_pull(r, z[0]))
            li.append(get_pull(r, z[1]))
        print('model PR num=', len(li))
        init_model_with_pulls(li, r.replace('/','_') + '_marked')
        print('pairs num=', len(p[r]))
        
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
    localfile_tool.write_to_file(X_path, X)
    localfile_tool.write_to_file(y_path, y)
    return (X, y)

def classify(model_type='SVM'):

    if part_params is not None:
        params_set = ['title', 'desc', 'code', 'file_list', 'location', 'pattern']
        used_set = []
        for j in range(len(part_params)):
            if part_params[j]:
                used_set.append(params_set[j])
        name = '+'.join(used_set)
        if len(used_set) == len(part_params):
            name = 'All'
        elif len(used_set) == len(part_params) - 1:
            name = 'D_' + '_'.join(set(params_set) - set(used_set))
        print(name)
    
    
    def get_ran_shuffle(X, y, train_percent = 0.8):
        X, y = shuffle(X, y)
        num = len(X)
        train_num = int (num * train_percent)
        X_train, X_test = X[:train_num], X[train_num:]
        y_train, y_test = y[:train_num], y[train_num:]
        return (X_train, y_train, X_test, y_test)
    

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

        # ran shuffle with train set and test set
        if model_data_random_shuffle_flag:
            X_train, y_train, X_test, y_test = get_ran_shuffle(X_train + X_test, y_train + y_test, 0.9)
        
        return (X_train, y_train, X_test, y_test)
    
    X_train, y_train, X_test, y_test = model_data_prepare(dataset)
    

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
    
    print('Model: training_set', len(X_train), 'testing_set', len(X_test), 'feature_length=', len(X_train[0]))
    
    # model choice
    # print('model: GradientBoostingClassifier')
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
        
    clf = clf.fit(X_train, y_train)
    
    # model result
    # print('coef in model = ', clf.coef_)
    # print(clf.intercept_)
    # print(clf.loss_function_)
    
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
    classify('SVM')

