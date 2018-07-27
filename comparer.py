import os
import re

from collections import Counter

from util import word_extractor
from util import localfile_tool
from util import language_tool

import fetch_raw_diff
import fetch_pull_files

from git import *

def counter_similarity(A_counter, B_counter):
    C = set(A_counter) | set(B_counter)
    tot1 = 0
    tot2 = 0
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
    A_counter = word_extractor.get_counter(A)
    B_counter = word_extractor.get_counter(B)
    return counter_similarity(A_counter, B_counter)

def get_keywords(text):
    return word_extractor.get_top_words_from_text(text, 100)

def text_keywords_similarity(A, B):
    return set_similarity(get_keywords(A), get_keywords(B))

def get_BoW(text):
    return word_extractor.get_words_from_text(text)

def get_file_list(pull):
    return [x["name"] for x in pull['file_list']]

def fetch_pr_info(pull, must_in_local = False):
    path = '/DATA/luyao/pr_data/%s/%s' % (pull["base"]["repo"]["full_name"], pull["number"])
    if os.path.exists(path + '/raw_diff.json') or os.path.exists(path + '/pull_files.json'):
        if os.path.exists(path + '/raw_diff.json'):
            file_list = localfile_tool.get_file(path + '/raw_diff.json')
        elif os.path.exists(path + '/pull_files.json'):
            pull_files = localfile_tool.get_file(path + '/pull_files.json')
            file_list = [fetch_raw_diff.parse_diff(file["file_full_name"], file["changed_code"]) for file in pull_files]
        else:
            raise Exception('error on fetch local file %s' % path)
    else:
        if check_too_big(pull):
            # print('too big for %s / %s ' % (pull["base"]["repo"]["full_name"], pull["number"]))
            return []
    
        if must_in_local:
            raise Exception('not found in local')
        
        file_list = fetch_file_list(pull["base"]["repo"]["full_name"], pull)

    # print(path, [x["name"] for x in file_list])
    return file_list

def get_location(pull):
    location_set = []
    for file in pull["file_list"]:
        for x in file["location"]["add"]:
            location_set.append([file["name"], int(x[0]), int(x[0]) + int(x[1])])
    return location_set

def get_code_from_pr_info(pr_info):
    add_code = []
    del_code = []    
    for file in pr_info:
        add_code += word_extractor.get_words_from_file(file["name"], file["add_code"])
        del_code += word_extractor.get_words_from_file(file["name"], file["del_code"])
    return [add_code, del_code]

def get_code_tokens_overlap(pull, overlap_set):
    new_pr_info = list(filter(lambda x: x["name"] in overlap_set, pull["file_list"]))
    return get_code_from_pr_info(new_pr_info)

def get_delta_code_tokens_keywords(code_tokens_result, top_number=300):
    add_code_tokens = code_tokens_result[0]
    del_code_tokens = code_tokens_result[1]
    
    add_c = word_extractor.get_counter(add_code_tokens)
    del_c = word_extractor.get_counter(del_code_tokens)
    
    changed_c = Counter()
    for t in add_c:
        times = add_c[t] - del_c[t]
        if times > 0:
            changed_c[t] = times
    
    return dict(changed_c.most_common(top_number))

def get_code_keywords_counter_overlap(pull, overlap_set): # return a counter
    return get_delta_code_tokens_keywords(get_code_tokens_overlap(pull, overlap_set))

'''
def get_code_tokens(pull):
    path = '/DATA/luyao/pr_data/%s/%s/code_tokens.json' % (pull["base"]["repo"]["full_name"], pull["number"])
    if os.path.exists(path):
        return localfile_tool.get_file(path)
    result = get_code_from_pr_info(pull["file_list"])
    localfile_tool.write_to_file(path, result)
    return result

def get_code_keywords_counter(pull): # return a counter
    path = '/DATA/luyao/pr_data/%s/%s/code_keywords_counter.json' % (pull["base"]["repo"]["full_name"], pull["number"])
    if os.path.exists(path):
        return localfile_tool.get_file(path)
    result = get_delta_code_tokens_keywords(get_code_tokens(pull))
    localfile_tool.write_to_file(path, result)    
    return result
'''


def location_similarity(la, lb):

    def cross(x1, y1, x2, y2):
        return not((y1 < x2) or (y2 < x1))

    if (la is None) or (lb is None):
        return 0.0
    
    # only calc on overlap files
    a_f = [x[0] for x in la]
    b_f = [x[0] for x in lb]
    c_f = set(a_f) & set(b_f)
    
    la = list(filter(lambda x: x[0] in c_f, la))
    lb = list(filter(lambda x: x[0] in c_f, lb))
    
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

'''
def same_author(A, B):
    return A["user"]["id"] == B["user"]["id"]

def same_code(A, B):
    return code_calc(A, B) >= 0.9

def same_title(A, B):
    return title_calc(A, B) >= 0.9

def same_file_list(A, B):
    return file_list_calc(A, B) >= 0.9
'''

import nlp
model = None
def init_model_from_raw_docs(documents, save_id=None):
    global model
    model = nlp.Model([get_BoW(document) for document in documents], save_id)
    print('init nlp model successfully!')

def text_sim(A, B, text_type="default"):
    A = get_BoW(A)
    B = get_BoW(B)
    if model is None:
        # print('set_similarity')
        return set_similarity(A, B)
    else:
        #print('model_similarity')
        # return model.query_sim_lsi(A, B)
        return model.query_sim_tfidf(A, B)
        # return model.query_sim_common_words_idf(A, B)

'''
#detect cases: feat(xxxx)

def special_pattern(a):
    x1 = get_pr_numbers(a)
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
    a_set = set(get_numbers(A["title"]) + get_numbers(A["body"])) - ab_num
    b_set = set(get_numbers(B["title"]) + get_numbers(B["body"])) - ab_num
    if a_set & b_set:
        return 1
    else:
        a_set = set(get_pr_numbers(A["title"]) + get_pr_numbers(A["body"])) - ab_num
        b_set = set(get_pr_numbers(B["title"]) + get_pr_numbers(B["body"])) - ab_num
        if a_set and b_set and (a_set != b_set):
            return -1
        return 0


def calc_sim(A, B):
    pattern = check_pattern(A, B)
    title_sim = text_sim(A["title"], B["title"])
    desc_sim = text_sim(A["body"], B["body"])
    file_list_sim = set_similarity(get_file_list(A), get_file_list(B))
    
    overlap_files_set = set(get_file_list(A)) & set(get_file_list(B))

    location_sim = location_similarity(get_location(A), get_location(B))
    
    common_words = list(set(get_BoW(A["title"])) & set(get_BoW(B["title"])))
    overlap_title_len = len(common_words)
    
    if model is not None:
        title_idf_sum = model.get_idf_sum(common_words)
    else:
        title_idf_sum = 0
                
    overlap_files_len = len(overlap_files_set)

    # code_sim = counter_similarity(get_code_keywords_counter(A), get_code_keywords_counter(B))
    code_sim = counter_similarity(get_code_keywords_counter_overlap(A, overlap_files_set),
                                  get_code_keywords_counter_overlap(B, overlap_files_set))

    # anthor way: use just added code
    # code_sim = text_keywords_similarity(get_code(A), get_code(B))    
    # time_sim = (get_time(A["created_at"]) - get_time(B["created_at"])).days
    
    return {
            'title': title_sim,
            'desc': desc_sim,
            'code': code_sim,
            'file_list': file_list_sim,
            'location': location_sim, 
            'pattern': pattern,
            'overlap_files_len': overlap_files_len,
            'overlap_title_len': overlap_title_len,
            'title_idf_sum': title_idf_sum,
           }

def sim_to_vet(r):
    return [r['title'],r['desc'],r['code'],r['file_list'],r['location'], r['pattern'],\
            # r['overlap_files_len'],r['overlap_title_len'],r['title_idf_sum'],
           ]


# pull requests sim
def get_sim_vector(A, B):
    A["file_list"] = fetch_pr_info(A)
    B["file_list"] = fetch_pr_info(B)
    ret = calc_sim(A, B)
    return sim_to_vet(ret)

def get_sim_vector_on_commit(A, B):
    def commit_to_pull(x):
        t = {}
        t["number"] = x['sha']
        t['title'] = t['body'] = x['commit']['message']
        t["file_list"] = fetch_commit(pull['commit_flag'])
        t['commit_flag'] = True
        return t
    ret = calc_sim(commit_to_pull(A), commit_to_pull(B))
    return sim_to_vet(ret)


def parse_sim(sim):
    tres_hold = {
        'title': 0.5,
        'desc': 0.4,
        'code': 0.5,
        'file_list': 0.7,
        'location': 0.7,
    }
    r = []
    for clue in tres_hold:
        if abs(sim[clue] - 1.0) <= 1e-5:
            r.append('Same on ' + clue)
        elif sim[clue] >= tres_hold[clue]:
            r.append('High on ' + clue)
    if sim['pattern'] == 1:
        r.append('Related to the same Issue')
    return r


'''
other_model = [None, None, None]
def init_other_model(d_3, t=None):
    global other_model
    for num in range(3):
        if t is not None:
            save_id = t + str(num)
        else:
            save_id = None
        other_model[num] = nlp.Model([get_BoW(document) for document in d_3[num]], save_id)
    
def other_feature(A, B):
    f = []
    for x in [A["title"], A["body"], str(A["title"]) + str(A["body"])]:
        for y in [B["title"], B["body"], str(B["title"]) + str(B["body"])]:
            tx = get_BoW(x) 
            ty = get_BoW(y)
            common = list(set(tx) & set(ty))
            for n in range(3):
                f.append(other_model[n].get_idf_sum(common))
    return f
              
'''