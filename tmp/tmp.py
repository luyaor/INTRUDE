#! /bin/sh -
# test_for_check.py
import re
import fetch_raw_diff
import fetch_pull_files
"""
import json
with open('pr_data/FancyCoder0/INFOX/76/pull_files.json') as f:
    result = json.load(f)
"""

n = '132'

pull_files = fetch_pull_files.fetch_pull_files('FancyCoder0/INFOX', n)
result1 = [fetch_raw_diff.parse_diff(file["file_full_name"], file["changed_code"]) for file in pull_files]

result2 = fetch_raw_diff.fetch_raw_diff('https://github.com/%s/pull/%s.diff' % ('FancyCoder0/INFOX', n))

#print(result1)
#print(result2)

for x in range(len(result1)):
    if result1[x]["add_code"] != result2[x]["add_code"]:
        print(result1[x]["add_code"])
        print('-------')
        print(result2[x]["add_code"])
        break
    if result1[x]["del_code"] != result2[x]["del_code"]:
        print(result1[x]["del_code"])
        print('-------')
        print(result2[x]["del_code"])
        break

# print('result==========', result1 == result2)



"""
from sklearn.feature_extraction.text import TfidfVectorizer
 
tfidf = TfidfVectorizer().fit_transform(documents)
print (tfidf)
"""

"""
def check_two_result(repo):
    pulls = get_pull_list(repo)
    for pull in pulls:
        pull_files = fetch_pull_files.fetch_pull_files(repo, pull["number"])
        result1 = [fetch_raw_diff.parse_diff(file["file_full_name"], file["changed_code"]) for file in pull_files]
        try:
            result2 = fetch_raw_diff.fetch_raw_diff('https://github.com/%s/pull/%s.diff' % (repo, pull["number"]))
            if not (result1 == result2):
                print('diff on', repo, pull["number"])
                import time
                time.sleep(5)
        except:
            continue
"""

"""
with open('list.csv') as f:
    for t in f.readlines():
        line = t.split(',')
        repo = line[0].strip()
        
        if repo == 'repo':
            continue

        num1, num2 = line[1].strip().split(' ')

        p1 = api.get('repos/%s/pulls/%s' % (repo, num1))
        p2 = api.get('repos/%s/pulls/%s' % (repo, num2))

        # print(repo,',',num1, num2,',',location_calc(p1, p2))
        # print('location_calc', )
        print('compare_redundant', compare_redundant(p1,p2))


        print('author = ', check_same_author(p1, p2));
        print('title = ', check_same_title(p1, p2));
        print('file_list = ', check_same_file_list(p1, p2));
        print('code = ', check_same_code(p1, p2));
        print('---')
        sys.stdout.flush()
"""

"""
import logging
logger = logging.getLogger(__name__)
logger.setLevel(level = logging.INFO)
handler = logging.FileHandler("log_for_get_pull.txt")
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)



def sim_mix(result, way = "default"):
    if way == "default":
        value = (result[0] * 5 + result[1] + result[2] * 3 + result[3] * 2 + result[4]) / 12
    elif way == "title":
        value = result[0]
    elif way == "title+desc":
        value = (result[0] + result[1]) / 2
    return value

def calc(repo, num1, num2, way="default"):
    return sim_mix(get_sim(repo, num1, num2), way)

"""