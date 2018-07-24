from git import *

# main.run_and_save('FancyCoder0/INFOX')


with open('data/top500_repo_list.txt') as f:
    r = f.readlines()

for repo in r:
    while True:
        try:
            run_and_save(repo, True)
            break
        except:
            print('error & restart on ', repo)
            pass

