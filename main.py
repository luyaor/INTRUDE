import os
import re
import sys
import random

# -----------------------------------------------------------------------------

from sklearn.ensemble import GradientBoostingClassifier
from sklearn.ensemble import AdaBoostClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis
from sklearn.tree import DecisionTreeClassifier

from sklearn.utils import shuffle
from sklearn.metrics import average_precision_score
from sklearn.metrics import precision_recall_curve
from sklearn import svm
from sklearn import linear_model
from sklearn.feature_selection import SelectKBest, f_regression
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

import matplotlib.pyplot as plt
# from metric_learn import LMNN
from numpy import array
from multiprocessing import Pool

from util import localfile_tool

from comparer import *
from git import *


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
    save_id = repo.replace('/','_') + '_all'
    init_model_with_pulls(get_pull_list(repo), save_id)


def get_sim(repo, num1, num2):
    p1 = get_pull(repo, num1)
    p2 = get_pull(repo, num2)
    return get_sim_vector(p1, p2)


'''
def get_sim_wrap(args):
    return get_sim(*args)
'''

'''
def get_sim(repo, num1, num2):
    return other_feature(get_pull(repo, num1), get_pull(repo, num2))
    
def get_sim_wrap(args):
    return get_sim(*args)
'''

# ------------------------------------------------------------

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
    
    
    print('run get_feature_vector!')
    print('input=', data)
    print('out=', out)
    
    
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
        
        li = shuffle(get_pull_list(r))
        li = li[:5000]
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

    '''
    # run with with only PR's info
    pull_list = []
    with open(data) as f:
        for l in f.readlines():
            r, n1, n2 = l.strip().split()
            pull_list.append(get_pull(r, n1))
            pull_list.append(get_pull(r, n2))

    # init NLP model
    # init_model_with_pulls(pull_list)
    
    init_other_model([ [p["title"] for p in pull_list], [p["body"] for p in pull_list], [ str(p["title"]) + str(p["body"]) for p in pull_list] ])
    print('init_other_model ok!')
                     
    # get the feature map of all PR pairs
    with open(data) as f:
        pairs = [tuple(l.strip().split()) for l in f.readlines()]
        r = [get_sim_wrap(p) for p in pairs]
        # with Pool(processes=10) as pool:
        #     r = pool.map(get_sim_wrap, pairs)
        X.extend(r)
        y.extend([label for i in range(len(r))])
    '''
    
    # save to local
    localfile_tool.write_to_file(X_path, X)
    localfile_tool.write_to_file(y_path, y)
    
    return (X, y)


def extract_col(a, c):
    for i in range(len(a)):
        t = []
        for j in range(len(c)):
            if c[j]==1:
                t.append(a[i][j])
        a[i] = t

        
def classify(model_type='SVM', params_flag=[1,1,1,1,1,1]):
    params_set = ['title', 'desc', 'code', 'file_list', 'location', 'pattern']
    
    used_set = []
    for j in range(len(params_flag)):
        if params_flag[j]:
            used_set.append(params_set[j])
    name = '+'.join(used_set)
    if len(used_set) == len(params_flag):
        name = 'All'
    elif len(used_set) == len(params_flag) - 1:
        name = 'D_' + '_'.join(set(params_set) - set(used_set))
    print(name)
    
    def get_ran_shuffle(X, y, train_percent = 0.8):
        X, y = shuffle(X, y)
        num = len(X)
        train_num = int (num * train_percent)
        X_train, X_test = X[:train_num], X[train_num:]
        y_train, y_test = y[:train_num], y[train_num:]
        return (X_train, y_train, X_test, y_test)
    
    def get_small_commit_data():
        X_train, y_train = get_feature_vector_from_path('data/rly_false_pairs.txt')
        X_train2, y_train2 = get_feature_vector_from_path('data/small_part_msr.txt')
        X_train += X_train2
        y_train += y_train2
    
        X_test, y_test = get_feature_vector_from_path('data/small_part_negative.txt')
        X_test2, y_test2 = get_feature_vector_from_path('data/small2_part_msr.txt')    
        X_test += X_test2
        y_test += y_test2
        
        # X_train, y_train, X_test, y_test = get_ran_shuffle(X_train + X_test, y_train + y_test, 0.75)
        
        return (X_train, y_train, X_test, y_test)
        
    def get_small_data():
        renew_flag = False
        path_suffix = None
        
        # path_suffix = '_common_words_idf'
        
        # path_suffix = 'test'
        
        # path_suffix = '_bow'
        
        # path_suffix = '_lsi'
        
        # X_train, y_train = [], []
        
        # path_suffix = 'test_on_more_feature'
        
        # path_suffix = 'commit_granularity'
        
        # path_suffix = 'no_split_word'
        
        X_train, y_train = get_feature_vector('data/rly_false_pairs.txt', 0, renew_flag, path_suffix)
        
        
        X_train2, y_train2 = get_feature_vector('data/small_part_msr.txt', 1, renew_flag, path_suffix)
        X_train += X_train2
        y_train += y_train2
        
        X_train3, y_train3 = get_feature_vector('data/rly_true_pairs.txt', 1, renew_flag, path_suffix)
        X_train += X_train3
        y_train += y_train3
        
        # X_test, y_test = [], []
        
        X_test, y_test = get_feature_vector('data/small_part_negative.txt', 0, renew_flag, path_suffix)
        X_test2, y_test2 = get_feature_vector('data/small2_part_msr.txt', 1, renew_flag, path_suffix)
        
        # X_test, y_test = get_feature_vector('data/big_false_data.txt', 0, renew_flag)
        # X_test2, y_test2 = get_feature_vector('data/msr_positive_pairs.txt', 1, renew_flag)
        
        X_test += X_test2
        y_test += y_test2
        
        # X_train, y_train, X_test, y_test = get_ran_shuffle(X_train + X_test, y_train + y_test, 0.9)
        
        return (X_train, y_train, X_test, y_test)
    
    '''
    def data_train_test():
        renew_flag = True
        
        X_train1, y_train1 = get_feature_vector('data/part_false_data1.txt', 0, renew_flag)
        X_train2, y_train2 = get_feature_vector('data/part_msr_positive_pairs.txt', 1, renew_flag)
        X_train3, y_train3 = get_feature_vector('data/rly_true_pairs.txt', 1, renew_flag)
    
        X_train = X_train1 + X_train2 + X_train3
        y_train = y_train1 + y_train2 + y_train3 
        
        X_test1, y_test1 = get_feature_vector('data/part_false_data2.txt', 0, renew_flag)
        X_test2, y_test2 = get_feature_vector('data/part_last_msr_positive_pairs.txt', 1, renew_flag)
        
        X_test = X_test1 + X_test2
        y_test = y_test1 + y_test2
        
        # X_train, y_train, X_test, y_test = get_ran_shuffle(X_train + X_test, y_train + y_test)
        
        return (X_train, y_train, X_test, y_test)
    
    def data_all():
        X_train1, y_train1 = get_feature_vector('data/part_false_data1.txt', 0, renew_flag)
        X_train2, y_train2 = get_feature_vector('data/part_msr_positive_pairs.txt', 1, renew_flag)
        X_train3, y_train3 = get_feature_vector('data/rly_true_pairs.txt', 1, renew_flag)
        X_train = X_train1 + X_train2 + X_train3
        y_train = y_train1 + y_train2 + y_train3
        X_train, y_train, X_test, y_test = get_ran_shuffle(X_train + X_test, y_train + y_test)
    '''

    def data_all():
        renew_flag = False
        path_suffix = None
        # path_suffix = 'tfidf'
        
        # path_suffix = 'test_on_more_feature'
        
        X_train, y_train = get_feature_vector('data/big_false_data.txt', 0, renew_flag, path_suffix)
        
        X_train2, y_train2 = get_feature_vector('data/msr_positive_pairs.txt', 1, renew_flag, path_suffix)
        X_train += X_train2
        y_train += y_train2
        
        X_train3, y_train3 = get_feature_vector('data/rly_true_pairs.txt', 1, renew_flag, path_suffix)
        X_train += X_train3
        y_train += y_train3
        
        X_train, y_train, X_test, y_test = get_ran_shuffle(X_train, y_train)
        return (X_train, y_train, X_test, y_test)
    
    
    # X_train, y_train, X_test, y_test = data_all()
    
    X_train, y_train, X_test, y_test = get_small_data()
    
    # X_train, y_train, X_test, y_test = get_small_commit_data()
    
    '''
    def fil(X, y):
        n = len(X)
        X_ , y_ = [], []
        for i in range(n):
            if X[i] is not None:
                X_.append(X[i])
                y_.append(y[i])
        return X_, y_
    
    X_train, y_train = fil(X_train, y_train)
    X_test, y_test = fil(X_test, y_test)
    '''
    
    
    draw_pic = False
    
    
    # params_flag = [1 for i in range(9)]
    
    
    extract_col(X_train, params_flag)
    extract_col(X_test, params_flag)
    print('extract=', params_flag)
    
    
    print('training_set', len(X_train), 'testing_set', len(X_test), 'feature_length=', len(X_train[0]))
    
    # model choice
    
    # print('model: GradientBoostingClassifier')
    # clf = GradientBoostingClassifier(n_estimators=160, learning_rate=1.0, max_depth=15, random_state=0).fit(X_train, y_train)
    
    # clf = GradientBoostingClassifier(n_estimators=10, learning_rate=1.0, max_depth=7, random_state=0).fit(X_train, y_train)
    # clf = AdaBoostClassifier(n_estimators=60).fit(X_train, y_train)
    
    print('------ model: ', model_type, '------' )
    
    if model_type == 'SVM':
        clf = svm.SVC(random_state=0, probability=1)
    elif model_type == 'LogisticRegression':
        clf = LogisticRegression()
    elif model_type == 'SGDClassifier':
        clf = linear_model.SGDClassifier(tol=0.01)
    
    # clf = GradientBoostingClassifier(n_estimators=1000, max_depth=30, random_state=0).fit(X_train, y_train)
    # clf =  DecisionTreeClassifier(max_depth=50)
    
    clf = clf.fit(X_train, y_train)
    
    
    # print('coef in model = ', clf.coef_)
    # print(clf.intercept_)
    # print(clf.loss_function_)
    
    '''
    anova_filter = SelectKBest(f_regression, k=6)
    anova_svm = make_pipeline(anova_filter, clf)
    anova_svm.fit(X_train, y_train)
    y_pred = anova_svm.predict(X_test)
    print(classification_report(y_test, y_pred))
    acc = anova_svm.score(X_test, y_test)
    print('Mean Accuracy:', acc)
    y_score = anova_svm.decision_function(X_test)
    average_precision = average_precision_score(y_test, y_score)
    print('Average precision score: {0:0.4f}'.format(average_precision))
    '''
    
    
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


        pre_y = clf.predict_proba(X_test)


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
                        print(pre_y[i][1], name, file=f)

    
    
    return clf

# -----------------------------------------------------------------

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

if __name__ == "__main__":
    classify('SVM')

