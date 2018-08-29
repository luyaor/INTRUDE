import sys

from flask import Flask
from flask_pymongo import PyMongo

app = Flask(__name__)

app.config["MONGO_URI"] = "mongodb://localhost:27017/intrude_db?connect=false"

mongo = PyMongo(app)

pr_list = mongo.db.detect.find()


sys.path.append('/home/luyao/PR_get/INTRUDE')
import git

def check_meaningless(title):
    title = title.lower()
    if 'revert' in title:
        return True
    if ('fix' in title) and ('typo' in title):
        return True
    if (('update' in title) or ('upgrade' in title)) and (('version' in title) or ('doc' in title)):
        return True
    if 'readme' in title:
        return True
    
    return False

for pr in pr_list:
    if 'num2' in pr:
        r, n1, n2, proba = pr['repo'], pr['num'], pr['num2'], float(pr['proba'])
    else:
        print('error=')
        print(pr)
        continue

    p1 = git.get_pull(r, n1)
    p2 = git.get_pull(r, n2)

    if proba >= 0.99:
        t1, t2 = p1['title'], p2['title']
        if check_meaningless(t1):
            print(t1)
            print(t2)
            print('--------')
        
        
# ------------------------------------------------------------------------------------------------







'''
sys.path.append('/home/luyao/PR_get/INTRUDE')
import git
@app.route('/test')
def test():
    repo_list = mongo.db.detect.distinct('repo')
    for repo in repo_list:
        pull_list = git.get_pull_list(repo)
        for pull in pull_list:
            pull['_id'] = repo + '/' + str(pull['number'])
            pull['repo_name'] = repo
            mongo.db.pull_list.save(pull)
    return 'Done!'
'''
    
'''
@app.route('/loadmark/<path:repo>')
def load_mark(repo):
    csv_path = '/home/luyao/PR_get/INTRUDE/evaluation/' + \
                 repo.replace('/','_') + '_mark.csv'

    if not os.path.exists(csv_path):
        return 'not found!'

    with open(csv_path) as f:
        for t in f.readlines():
            p = t.strip().split(',')
            
            if len(p) == 14:
                mark = p[5]
            else:
                mark = p[4]
            
            if mark != 'N/A':
                r, n1, n2, proba = p[0], p[1], p[2], float(p[3])
                
                _id = r + '/' + n1
                ori = mongo.db.detect.find_one({'_id': _id})
                if (ori is not None) and (ori['num2'] != n2):
                    s = 'con=' + r + n1 + n2 + ori['num2']
                    raise Exception(s)
                
                mongo.db.detect.update({'_id': _id}, {'$set': {'num': n1, 'num2': n2, 'prob': proba, 'mark': mark}}, upsert=True)
    return 'done!'
'''
