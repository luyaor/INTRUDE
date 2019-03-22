import os
import re
import copy
import itertools

from gensim import matutils
from datetime import datetime
from collections import Counter

from util import wordext
from util import localfile

from git import *
from fetch_raw_diff import *

text_sim_type = 'lsi'
# text_sim_type = 'tfidf'

code_sim_type = 'tfidf'
# code_sim_type = 'bow'

extract_sim_type = 'ori_and_overlap'

add_timedelta = False
add_conf = False
add_commit_message = True

feature_conf = ''
if add_timedelta:
    feature_conf += '_time'
if add_conf:
    feature_conf += '_conf'
if add_commit_message:
    feature_conf += '_commit_message'

# ---------------------------------------------------------------------------

def counter_similarity(A_counter, B_counter):
    C = set(A_counter) | set(B_counter)
    tot1, tot2 = 0, 0
    for x in C:
        tot1 += min(A_counter.get(x,0), B_counter.get(x,0))
        tot2 += max(A_counter.get(x,0), B_counter.get(x,0))
    if tot2 == 0:
        return 0
    return 1.0 * tot1 / tot2

def set_similarity(A, B):
    if (A is None) or (B is None):
        return 0
    if (len(A) == 0) or (len(B) == 0):
        return 0
    return len(set(A) & set(B)) / len(set(A) | set(B))
    
def list_similarity(A, B):
    if (A is None) or (B is None):
        return 0
    if (len(A) == 0) or (len(B) == 0):
        return 0
    A_counter = wordext.get_counter(A)
    B_counter = wordext.get_counter(B)
    return counter_similarity(A_counter, B_counter)

def vsm_bow_similarity(A_counter, B_counter):
    return matutils.cossim(list(A_counter.items()), list(B_counter.items()))

# ---------------------------------------------------------------------------

def get_tokens(text):
    return wordext.get_words_from_text(text)

def get_file_list(pull):
    return [x["name"] for x in pull['file_list']]

def get_location(pull):
    location_set = []
    for file in pull["file_list"]:
        for x in file["location"]["add"]:
            location_set.append([file["name"], int(x[0]), int(x[0]) + int(x[1])])
    return location_set

def get_code_from_file_list(pr_info):
    add_code = list(itertools.chain(*[wordext.get_words_from_file(file["name"], file["add_code"]) for file in pr_info]))
    del_code = list(itertools.chain(*[wordext.get_words_from_file(file["name"], file["del_code"]) for file in pr_info]))
    return [add_code, del_code]

def get_code_tokens(pull):
    return get_code_from_file_list(pull["file_list"])

def get_pull_on_overlap(pull, overlap_set):
    new_pull = copy.deepcopy(pull)
    new_pull["file_list"] = list(filter(lambda x: x["name"] in overlap_set, new_pull["file_list"]))
    return new_pull

def get_delta_code_tokens_counter(code_tokens_result):
    add_code_tokens = code_tokens_result[0]
    del_code_tokens = code_tokens_result[1]
    
    add_c = wordext.get_counter(add_code_tokens)
    del_c = wordext.get_counter(del_code_tokens)
    
    changed_c = Counter()
    for t in add_c:
        times = add_c[t] - del_c[t]
        if times > 0:
            changed_c[t] = times
    return changed_c

# ---------------------------------------------------------------------------

def location_similarity(la, lb):

    def cross(x1, y1, x2, y2):
        return not((y1 < x2) or (y2 < x1))

    if (la is None) or (lb is None):
        return 0.0
    
    '''
    # only calc on overlap files
    a_f = [x[0] for x in la]
    b_f = [x[0] for x in lb]
    c_f = set(a_f) & set(b_f)
    
    la = list(filter(lambda x: x[0] in c_f, la))
    lb = list(filter(lambda x: x[0] in c_f, lb))
    '''

    if len(la) + len(lb) == 0:
        return 0.0

    match_a = [False for x in range(len(la))]
    match_b = [False for x in range(len(lb))]
    
    index_b = {}
    for i in range(len(lb)):
        file = lb[i][0]
        if file not in index_b:
            index_b[file] = []
        index_b[file].append(i)
        
    for i in range(len(la)):
        file = la[i][0]
        for j in index_b.get(file,[]):
            if cross(la[i][1], la[i][2], lb[j][1], lb[j][2]):
                match_a[i] = True
                match_b[j] = True
    
    # weigh with code line
    a_match, a_tot = 0, 0
    for i in range(len(la)):
        part_line = la[i][2] - la[i][1]
        a_tot += part_line
        if match_a[i]:
            a_match += part_line
    
    b_match, b_tot = 0, 0
    for i in range(len(lb)):
        part_line = lb[i][2] - lb[i][1]
        b_tot += part_line
        if match_b[i]:
            b_match += part_line
    
    if a_tot + b_tot == 0:
        return 0
    return (a_match + b_match) / (a_tot + b_tot)
    # return (match_a.count(True) + match_b.count(True)) / (len(match_a) + len(match_b))

# ---------------------------------------------------------------------------

import nlp
model = None
def init_model_from_raw_docs(documents, save_id=None):
    global model
    model = nlp.Model([get_tokens(document) for document in documents], save_id)
    print('init nlp model for text successfully!')


def get_text_sim(A, B):
    A = get_tokens(A)
    B = get_tokens(B)
    if model is None:
        return [list_similarity(A, B)]
    
    if text_sim_type == 'lsi':
        sim = model.query_sim_lsi(A, B)

    if text_sim_type == 'tfidf':
        sim = model.query_sim_tfidf(A, B)

    # len_mul = model.query_vet_len_mul(A, B)
    len_mul = len(A) * len(B)

    return [sim]
    
    
code_model = None
def init_code_model_from_tokens(documents, save_id=None):
    global code_model
    code_model = nlp.Model(documents, save_id)
    print('init nlp model for code successfully!')

def counter2list(A):
    a_c = []
    for x in A:
        for t in range(A[x]):
            a_c.append(x)
    return a_c

def vsm_tfidf_similarity(A, B):
    return code_model.query_sim_tfidf(counter2list(A), counter2list(B))

# ---------------------------------------------------------------------------

'''
#detect cases: feat(xxxx)

def special_pattern(a):
    x1 = get_pr_and_issue_numbers(a)
    x2 = re.findall('\((.*?)\)', a)
    x1 = list(filter(lambda x: len(x) > 1, x1))
    return x1 + x2

def title_has_same_pattern(a, b):
    if set(special_pattern(a)) & set(special_pattern(b)):
        return True
    else:
        return False
'''

def check_pattern(A, B):
    ab_num = set([A["number"], B["number"]])
    a_text = str(A["title"]) + ' ' + str(A["body"])
    b_text = str(B["title"]) + ' ' + str(B["body"])

    a_set = set(get_numbers(a_text)) - ab_num
    b_set = set(get_numbers(b_text)) - ab_num
    if a_set & b_set:
        return 1
    else:
        a_set = set(get_pr_and_issue_numbers(a_text)) - ab_num
        b_set = set(get_pr_and_issue_numbers(b_text)) - ab_num
        if a_set and b_set and (a_set != b_set):
            return -1
        return 0

def check_version_numbers(A, B):
    ab_num = set([A["number"], B["number"]])
    a_text = str(A["title"]) + ' ' + str(A["body"])
    b_text = str(B["title"]) + ' ' + str(B["body"])

    a_set = set(get_version_numbers(a_text))
    b_set = set(get_version_numbers(b_text))
    if a_set & b_set:
        return 1
    elif a_set and b_set and (len(a_set & b_set) == 0):
        return -1
    else:
        return 0
    

def get_code_sim(A, B):
    A_overlap_code_tokens = get_code_tokens(A)
    B_overlap_code_tokens = get_code_tokens(B)
    
    A_delta_code_counter = get_delta_code_tokens_counter(A_overlap_code_tokens)
    B_delta_code_counter = get_delta_code_tokens_counter(B_overlap_code_tokens)
    
    if code_sim_type == 'bow':
        code_sim = vsm_bow_similarity(A_delta_code_counter, B_delta_code_counter)
        return [code_sim]
    if code_sim_type == 'jac':
        code_sim = counter_similarity(A_delta_code_counter, B_delta_code_counter)
        return [code_sim]
    if code_sim_type == 'tfidf':
        code_sim = vsm_tfidf_similarity(A_delta_code_counter, B_delta_code_counter)
        return [code_sim]
    if code_sim_type == 'bow_two':
        code_sim_add = vsm_bow_similarity(wordext.get_counter(A_overlap_code_tokens[0]),
                                          wordext.get_counter(B_overlap_code_tokens[0]))
        code_sim_del = vsm_bow_similarity(wordext.get_counter(A_overlap_code_tokens[1]),
                                          wordext.get_counter(B_overlap_code_tokens[1]))
        return [code_sim_add, code_sim_del]
    if code_sim_type == 'bow_three':
        code_sim_delta = vsm_bow_similarity(A_delta_code_counter, B_delta_code_counter)
        code_sim_add = vsm_bow_similarity(wordext.get_counter(A_overlap_code_tokens[0]),
                                          wordext.get_counter(B_overlap_code_tokens[0]))
        code_sim_del = vsm_bow_similarity(wordext.get_counter(A_overlap_code_tokens[1]),
                                          wordext.get_counter(B_overlap_code_tokens[1]))
        return [code_sim_delta, code_sim_add, code_sim_del]
# ---------------------------------------------------------------------------


def calc_sim(A, B):
    pattern_issue_number = check_pattern(A, B)
    # pattern_version_number = check_version_numbers(A, B)
    title_sim = get_text_sim(A["title"], B["title"])
    desc_sim = get_text_sim(A["body"], B["body"])
    file_list_sim = list_similarity(get_file_list(A), get_file_list(B))
    
    if ('merge_commit_flag' in A) and ('merge_commit_flag' in B):
        file_list_sim = set_similarity(get_file_list(A), get_file_list(B))

    overlap_files_set = set(get_file_list(A)) & set(get_file_list(B))
    
    A_overlap, B_overlap = get_pull_on_overlap(A, overlap_files_set), get_pull_on_overlap(B, overlap_files_set)
    code_sim = get_code_sim(A, B) + get_code_sim(A_overlap, B_overlap)

    location_sim = [location_similarity(get_location(A), get_location(B))] + \
                    [location_similarity(get_location(A_overlap), get_location(B_overlap))]
    
    '''
    common_words = list(set(get_tokens(A["title"])) & set(get_tokens(B["title"])))
    overlap_title_len = len(common_words)
    
    if model is not None:
        title_idf_sum = model.get_idf_sum(common_words)
    else:
        title_idf_sum = 0
    '''
    
    def get_time(t):
        return datetime.strptime(t, "%Y-%m-%dT%H:%M:%SZ")

    overlap_files_len = len(overlap_files_set)
    
    ret = {
            'title': title_sim,
            'desc': desc_sim,
            'code': code_sim,
            'file_list': [file_list_sim, overlap_files_len],
            'location': location_sim, 
            'pattern': [pattern_issue_number],
           }
    
    if add_conf:
        conf = 0
        for file in overlap_files_set:
            file_name = os.path.splitext(os.path.basename(file))[0]
            if (file_name in A["title"]) and (file_name in B["title"]):
                conf = 1
                break
        ret['conf'] = [conf]

    if add_timedelta:
        delta_time = abs((get_time(A['created_at']) - get_time(B['created_at'])).days)
        ret['time'] = [delta_time]
    
    if add_commit_message:
        def concat_commits(commits):
            total_message = ''
            for c in commits:
                message = c['commit']['message']
                total_message += message + '\n'
            return total_message
        
        try:
            commit_sim = get_text_sim(concat_commits(get_pull_commit(A)), concat_commits(get_pull_commit(B)))
        except:
            commit_sim = [0.0]

        ret['commit_message'] = commit_sim
    
    return ret

def sim_to_vet(r):
    vet = []
    for v in [r['title'],r['desc'],r['code'],r['file_list'],r['location'], r['pattern']]:
        vet += v

    if add_timedelta:
        vet += r['time']
    
    if add_conf:
        vet += r['conf']
    
    if add_commit_message:
        vet += r['commit_message']
    
    return vet

# pull requests sim
def get_pr_sim(A, B):
    A["file_list"] = fetch_pr_info(A) if not check_large(A) else []
    B["file_list"] = fetch_pr_info(B) if not check_large(B) else []
    
    A["title"] = str(A["title"] or '')
    A["body"] = str(A["body"] or '')
    
    B["title"] = str(B["title"] or '')
    B["body"] = str(B["body"] or '')
    
    return calc_sim(A, B)
    
def get_pr_sim_vector(A, B):
    return sim_to_vet(get_pr_sim(A, B))

def leave_feat(A, B, way):
    r = get_pr_sim(A, B)
    if 'text' in way:
        r['title'] = r['desc'] = []
    elif 'code' in way:
        r['code'] = []
    elif 'file_list' in way:
        r['file_list'] = []
    elif 'location' in way:
        r['location'] = []
    elif 'pattern' in way:
        r['pattern'] = []
    return sim_to_vet(r)
        
    
def old_way(A, B):
    A["title"] = str(A["title"] or '')
    A["body"] = str(A["body"] or '')
    
    B["title"] = str(B["title"] or '')
    B["body"] = str(B["body"] or '')

    return model.query_sim_tfidf(get_tokens(A["title"]), get_tokens(B["title"])) + \
    model.query_sim_tfidf(get_tokens(A["body"]), get_tokens(B["body"]))

    
# commits sim
def get_commit_sim_vector(A, B):
    def commit_to_pull(x):
        t = {}
        t["number"] = x['sha']
        t['title'] = t['body'] = str(x['commit']['message'] or '')
        t["file_list"] = fetch_commit(x['url'])
        t['commit_flag'] = True
        return t
    ret = calc_sim(commit_to_pull(A), commit_to_pull(B))
    return sim_to_vet(ret)
