import sys

import git
import comp

def detect(repo):
    issue_list = git.get_repo_info(repo, 'issue', False)
    for i in issue_list:
        max_s, max_i = -1, None
        
        for i2 in issue_list:
            if i['number'] <= i2['number']:
                continue

            s1 = comp.get_text_sim(i['title'], i2['title'])
            s2 = comp.get_text_sim(i['body'], i2['body'])
            
            if s1 + s2 >= max_s:
                max_s = s1 + s2;
                max_i = i2['number']
        
        if max_s >= 1.0:
            print(i['number'], max_i, max_s)

if __name__ == "__main__":
    
    if len(sys.argv) > 1:
        r = sys.argv[1].strip()
        detect(r)
    