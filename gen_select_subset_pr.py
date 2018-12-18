import os
import sys
from git import *
from sklearn.utils import shuffle

repos = ['hashicorp/terraform',
        'django/django',
        'docker/docker',
        'cocos2d/cocos2d-x',
        'dotnet/corefx',
        'elastic/elasticsearch',
        'JuliaLang/julia',
        'emberjs/ember.js',
        'facebook/react',
        'rails/rails',
        'angular/angular.js',
        'joomla/joomla-cms',
        'ceph/ceph',
        'ansible/ansible']

gen_num = 0

def work(file):
    add_flag = False

    has = set()
    if os.path.exists(file):
        if not add_flag:
            raise Exception('file already exists!')
        with open(file) as f:
            for t in f.readlines():
                r, n = t.strip().split()
                has.add((r, n))

    for repo in repos:
        print('Generating PRs from', repo)
        
        pulls = get_repo_info(repo, 'pull')

        ps = shuffle(pulls)

        cnt = 0
        with open(file, 'a+') as f:
            for p in ps:
                if check_large(p):
                    continue
                if (repo, str(p['number'])) in has:
                    continue
                cnt += 1
                print(repo, p['number'], file=f)

                if cnt == gen_num:
                    break

if __name__ == "__main__":
    file = sys.argv[1].strip()
    gen_num = int(sys.argv[2].strip())
    
    work(file)
    
    