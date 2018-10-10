from git import *
from detect import *

from val import *

def check_overlap_c(p1, p2):
    for c1 in get_pull_commit(p1):
        for c2 in get_pull_commit(p2):
            if (len(c1['commit']['message']) > 0) and (c1['commit']['message'] == c2['commit']['message']): # repeat commit
                return True
    return False

def check_overlap_equal(p1, p2):
    tot = 0
    c1_l = get_pull_commit(p1)
    c2_l = get_pull_commit(p2)
    for c1 in c1_l:
        for c2 in c2_l:
            if (len(c1['commit']['message']) > 0) and (c1['commit']['message'] == c2['commit']['message']):
                tot += 1
                break
    return tot == min(len(c1_l), len(c2_l))

def check_awareness(pull, pullA):
    # same author
    if pull["user"]["id"] == pullA["user"]["id"]:
        return False

    # case of following up work (not sure)
    if str(pull["number"]) in (get_pr_and_issue_numbers(pullA["title"]) + \
                               get_pr_and_issue_numbers(pullA["body"])):
        return False
    

with open('data/clf/second_msr_pairs.txt') as f:
    for t in f.readlines():
        r, n1, n2 = t.strip().split()
        if n1 > n2:
            n1, n2 = n2, n1
        
        p1 = get_pull(r, n1)
        p2 = get_pull(r, n2)
        
        if check_awareness(p1, p2):
            with open('data/fil_second_msr_pairs.txt', 'a') as outf:
                print(r, n1, n2, file=outf)
            continue


        if check_pro_pick(p1, p2):
            with open('data/fil_second_msr_pairs.txt', 'a') as outf:
                print(r, n1, n2, file=outf)

