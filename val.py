from git import *
from detect import *

def is_filter_before(pull, pullA):
    # same author
    if pull["user"]["id"] == pullA["user"]["id"]:
        return True

    if check_pro_pick(pullA, pull):
        return True
    
    return False

def check_ok_new(pull, pullA):
    if abs((get_time(pullA["updated_at"]) - \
            get_time(pull["updated_at"])).days) >= 5 * 365: # more than 4 years
        return False

    # case of following up work (not sure)
    if str(pull["number"]) in (get_pr_and_issue_numbers(pullA["title"]) + \
                               get_pr_and_issue_numbers(pullA["body"])):
        return False

    # create after another is merged
    if (pull["merged_at"] is not None) and \
    (get_time(pull["merged_at"]) < get_time(pullA["created_at"])) and \
    ((get_time(pullA["created_at"]) - get_time(pull["merged_at"])).days >= 14):
        return False

    if not speed_up_check(pullA, pull):
        return False

    return True


def check_ok_new_num(r, n1, n2):
    if int(n1) > int(n2):
        n1, n2 = n2, n1
    # n1 < n2
    return check_ok_new(get_pull(r, str(n1)), get_pull(r, str(n2)))


def check_ok(pull, pullA):
    if filter_out_too_old_pull_flag:
        if abs((get_time(pullA["updated_at"]) - \
                get_time(pull["updated_at"])).days) >= 5 * 365: # more than 4 years
            return False

    # same author
    if pull["user"]["id"] == pullA["user"]["id"]:
        return False

    # case of following up work (not sure)
    if str(pull["number"]) in (get_pr_and_issue_numbers(pullA["title"]) + \
                               get_pr_and_issue_numbers(pullA["body"])):
        return False

    # create after another is merged
    if (pull["merged_at"] is not None) and \
    (get_time(pull["merged_at"]) < get_time(pullA["created_at"])) and \
    ((get_time(pullA["created_at"]) - get_time(pull["merged_at"])).days >= 14):
        return False
    
    if not speed_up_check(pullA, pull):
        return False

    if check_pro_pick(pullA, pull):
        return False
    
    return True

def check_ok_num(r, n1, n2):
    if int(n1) > int(n2):
        n1, n2 = n2, n1
    # n1 < n2
    return check_ok(get_pull(r, str(n1)), get_pull(r, str(n2)))

def check_mention(repo, num1, num2):
    num1 = str(num1)
    num2 = str(num2)
    if (num2 in get_another_pull(get_pull(repo, num1))) or (num1 in get_another_pull(get_pull(repo, num2))):
        return True
    return False
                
if __name__ == "__main__":

    filein = 'tmp/val.in'
    fileout = 'tmp/val.out'

    with open(fileout, 'a') as out:
        print('------', file=out)

    with open(filein) as f:
        for t in f.readlines():
            ps = t.strip().split()
            r, n1, n2 = ps[0], ps[1], ps[2]
            if n1 > n2:
                n1, n2 = n2, n1

            with open(fileout, 'a') as out:
                if check_ok(get_pull(r, n1), get_pull(r, n2)):
                    print(t.strip(), file=out)
                else:
                    topk = get_topK(r, n2, 30, True)
                    for (n, proba) in topk:
                        if check_ok(get_pull(r, n), get_pull(r, n2)):
                            print(r, n2, n, proba, 'Unknown', file=out)
                            break


        
        