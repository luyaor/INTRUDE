from git import *

# main.run_and_save('FancyCoder0/INFOX')

file = 'data/repoList_morethan200PR.txt' # 'data/top500_repo_list.txt'

with open(file) as f:
    r = f.readlines()

for repo in r:
    while True:
        try:
            run_and_save(repo, True)
            break
        except:
            print('error & restart on ', repo)
            pass

