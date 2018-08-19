import sys

from git import *
from comparer import *


def detect(repo):
    issue_list = repo_get(repo, 'issue')
    for i in issue_list:
        max_s, max_i = -1, None
        
        for i2 in issue_list:
            if i['number'] <= i2['number']:
                continue

            s1 = get_text_sim(i['title'], i2['title'])
            s2 = get_text_sim(i['body'], i2['body'])
            
            if s1 + s2 >= max_s:
                max_s = s1 + s2;
                max_i = i2['number']
        
        print(i['number'], max_i, max_s)

if __name__ == "__main__":
    
    if len(sys.argv) > 1:
        r = sys.argv[1].strip()
        detect(r)
    