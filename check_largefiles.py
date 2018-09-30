import os
repos = ['facebook/react','rails/rails','elastic/elasticsearch','ansible/ansible','docker/docker','angular/angular.js','laravel/framework','Apple/swift','cms-sw/cmssw','tensorflow/tensorflow','mrdoob/three.js','spring-projects/spring-framework','emberjs/ember.js']

out = open('large_files_list.txt', 'w')
for repo in repos:
    repo_path = '/DATA/luyao/pr_data/%s' % repo
    nums = os.listdir(repo_path)
    for num in nums:
        if not num.isdigit():
            continue
        t = repo_path + '/' + num + '/too_large_flag.json'
        if os.path.exists(t):
            print(t)
            print(t, file=out)
out.close()
