import os
from git import *
from sklearn.utils import shuffle

repo = 'angular/angular.js'

if len(sys.argv) > 1:
    repo = sys.argv[1].strip()

print('repo', repo)

file = 'evaluation/' + repo.replace('/', '_') + '_select.txt'

add_flag = True

gen_num = 100

has = set()
if os.path.exists(file):
    if not add_flag:
        raise Exception('file already exists!')
    with open(file) as f:
        for t in f.readlines():
            has.add(t.strip())
    

pulls = get_repo_info(repo, 'pull')

ps = shuffle(pulls)

cnt = 0
with open(file, 'a+') as f:
    for p in ps:
        if check_large(p):
            continue
        if str(p['number']) in has:
            continue
        cnt += 1
        print(p['number'], file=f)

        if cnt == gen_num:
            break
