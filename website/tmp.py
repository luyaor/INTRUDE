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
