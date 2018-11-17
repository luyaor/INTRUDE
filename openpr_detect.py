import os
import sys

import git
import detect

detect.speed_up = True
detect.filter_already_cite = True
detect.filter_create_after_merge = True
detect.filter_same_author_and_already_mentioned = True

if len(sys.argv) < 2:
    print('Please input repo name')
    sys.exit()
    
repo = sys.argv[1].strip()

openprs = git.api.request('GET', 'repos/%s/pulls?state=open' % (repo))
# git.get_repo_info(repo, 'pull', True) # refresh pull requests list

for openpr in openprs:
    num1 = str(openpr['number'])
    num2, sim = detect.detect_one(repo, num1)
    print("%s %s : %s %.4f" % (repo, num1, str(num2), sim))
