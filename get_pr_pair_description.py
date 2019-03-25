import git
import json

file = 'data/msr_positive_pairs.txt'
out = open(file + '.out', 'w')

with open(file) as f:
    for l in f.readlines():
        repo,num1,num2 = l.split()

        p1 = git.get_pull(repo, num1)
        p2 = git.get_pull(repo, num2)

        data = {}
        data['dupPR'] = []
        data['dupPR'].append({
            'pr1.title': p1["title"],
            'pr1.desc':p1["description"],
            'pr2.title': p2["title"],
            'pr2.desc':p2["description"],
            'isDup': 'true'
        })
        with open('prPairs_title_desc.txt', 'w') as outfile:
            json.dump(data, outfile)

out.close()