import time
import os
import re
import requests

import fetch_raw_diff

from flask import Flask
from flask_github import GitHub

from util import localfile

app = Flask(__name__)

app.config['GITHUB_CLIENT_ID'] = os.environ.get('GITHUB_CLIENT_ID')
app.config['GITHUB_CLIENT_SECRET'] = os.environ.get('GITHUB_CLIENT_SECRET')
app.config['GITHUB_BASE_URL'] = 'https://api.github.com/'
app.config['GITHUB_AUTH_URL'] = 'https://github.com/login/oauth/'


LOCAL_DATA_PATH = '/DATA/luyao'

api = GitHub(app)
@api.access_token_getter
def token_getter():
    access_token = '9c34a60a61bfcb213b52d8b388f577f34c379987'
    return access_token

def text2list_precheck(func):
    def proxy(text):
        if text is None:
            return []
        ret = func(text)
        return ret
    return proxy

@text2list_precheck
def get_numbers(text):
    nums = list(filter(lambda x: len(x) >= 3, re.findall('([0-9]+)', text)))
    nums = list(set(nums))
    return nums

@text2list_precheck
def get_version_numbers(text):
    nums = [''.join(x) for x in re.findall('(\d+\.)?(\d+\.)(\d+)', text)]
    nums = list(set(nums))
    return nums

@text2list_precheck
def get_pr_and_issue_numbers(text):
    nums = []
    nums += re.findall('#([0-9]+)', text)
    nums += re.findall('pull\/([0-9]+)', text)
    nums += re.findall('issues\/([0-9]+)', text)
    nums = list(filter(lambda x: len(x) > 0, nums))
    nums = list(set(nums))
    return nums


def check_too_big(pull):
    if not ("changed_files" in pull):
        pull = get_pull(pull["base"]["repo"]["full_name"], pull["number"])
    
    if not ("changed_files" in pull):
        pull = get_pull(pull["base"]["repo"]["full_name"], pull["number"], True)
    
    if pull["changed_files"] > 50:
        return True
    if (pull["additions"] >= 10000) or (pull["deletions"] >= 10000):
        return True
    return False

check_large_cache = {}
def check_large(pull):
    global check_large_cache
    index = (pull["base"]["repo"]["full_name"], pull["number"])
    if index in check_large_cache:
        return check_large_cache[index]
    
    check_large_cache[index] = True # defalue true
    
    if check_too_big(pull):
        return True
    
    try:
        l = len(fetch_pr_info(pull))
    except Exception as e:
        if 'too big' in str(e):
            return True

    '''
    if l == 0:
        try:
            file_list = fetch_file_list(pull, True)
        except:
            path = '/DATA/luyao/pr_data/%s/%s' % (pull["base"]["repo"]["full_name"], pull["number"])
            flag_path = path + '/too_large_flag.json'
            localfile.write_to_file(flag_path, 'flag')
            print('too big', pull['html_url'])
            return True
    '''
    
    path = '/DATA/luyao/pr_data/%s/%s/raw_diff.json' % (pull["base"]["repo"]["full_name"], pull["number"])
    if os.path.exists(path) and (os.path.getsize(path) >= 50 * 1024):
        return True
    
    check_large_cache[index] = False
    return False

'''
def fresh_pr_info(pull):
    file_list = fetch_file_list(pull)
    path = '/DATA/luyao/pr_data/%s/%s' % (pull["base"]["repo"]["full_name"], pull["number"])
    parse_diff_path = path + '/parse_diff.json'
    localfile.write_to_file(parse_diff_path, file_list)
''' 

file_list_cache = {}

def fetch_pr_info(pull, must_in_local = False):
    global file_list_cache
    ind = (pull["base"]["repo"]["full_name"], pull["number"])
    if ind in file_list_cache:
        return file_list_cache[ind]
    
    path = '/DATA/luyao/pr_data/%s/%s' % (pull["base"]["repo"]["full_name"], pull["number"])
    parse_diff_path = path + '/parse_diff.json'
    raw_diff_path = path + '/raw_diff.json'
    pull_files_path = path + '/pull_files.json'


    flag_path = path + '/too_large_flag.json'
    if os.path.exists(flag_path):
        raise Exception('too big', pull['html_url'])
    
    if os.path.exists(parse_diff_path):
        try:
            ret = localfile.get_file(parse_diff_path)
            file_list_cache[ind] = ret
            return ret
        except:
            pass

    if os.path.exists(raw_diff_path) or os.path.exists(pull_files_path):
        if os.path.exists(raw_diff_path):
            file_list = localfile.get_file(raw_diff_path)
        elif os.path.exists(pull_files_path):
            pull_files = localfile.get_file(pull_files_path)
            file_list = [parse_diff(file["file_full_name"], file["changed_code"]) for file in pull_files]
        else:
            raise Exception('error on fetch local file %s' % path)
    else:
        if must_in_local:
            raise Exception('not found in local')
        
        try:
            file_list = fetch_file_list(pull)
        except:
            localfile.write_to_file(flag_path, 'flag')
            raise Exception('too big', pull['html_url'])

    # print(path, [x["name"] for x in file_list])
    localfile.write_to_file(parse_diff_path, file_list)
    file_list_cache[ind] = file_list
    return file_list

    
# -------------------About Repo--------------------------------------------------------

def get_repo_info(repo, type, renew=False):
    save_path = LOCAL_DATA_PATH + '/pr_data/' + repo + '/%s_list.json' % type
    if type == 'fork':
        save_path = LOCAL_DATA_PATH + '/result/' + repo + '/forks_list.json'

    if (os.path.exists(save_path)) and (not renew):
        try:
            return localfile.get_file(save_path)
        except:
            pass

    print('start fetch new list for ', repo, type)
    if (type == 'pull') or (type == 'issue'):
        ret = api.request('GET', 'repos/%s/%ss?state=closed' % (repo, type), True)
        ret.extend(api.request('GET', 'repos/%s/%ss?state=open' % (repo, type), True))
    else:
        if type == 'branch':
            type = 'branche'
        ret = api.request('GET', 'repos/%s/%ss' % (repo, type), True)
    
    localfile.write_to_file(save_path, ret)
    return ret

def fetch_commit(url, renew=False):
    save_path = LOCAL_DATA_PATH + '/pr_data/%s.json' % url.replace('https://api.github.com/repos/','')
    if os.path.exists(save_path) and (not renew):
        try:
            return localfile.get_file(save_path)
        except:
            pass
    
    c = api.get(url)
    time.sleep(0.7)
    file_list = []
    for f in c['files']:
        if 'patch' in f:
            file_list.append(fetch_raw_diff.parse_diff(f['filename'], f['patch']))
    localfile.write_to_file(save_path, file_list)
    return file_list


# ------------------About Pull Requests----------------------------------------------------

def get_pull(repo, num, renew=False):
    save_path = LOCAL_DATA_PATH + '/pr_data/%s/%s/api.json' % (repo, num)
    if os.path.exists(save_path) and (not renew):
        try:
            return localfile.get_file(save_path)
        except:
            pass

    r = api.get('repos/%s/pulls/%s' % (repo, num))
    time.sleep(1.0)
    localfile.write_to_file(save_path, r)
    return r

def get_pull_commit(pull, renew=False):
    save_path = LOCAL_DATA_PATH + '/pr_data/%s/%s/commits.json' % (pull["base"]["repo"]["full_name"], pull["number"])
    if os.path.exists(save_path) and (not renew):
        try:
            return localfile.get_file(save_path)
        except:
            pass
    commits = api.request('GET', pull['commits_url'], True)
    time.sleep(0.7)
    localfile.write_to_file(save_path, commits)
    return commits

def get_another_pull(pull, renew=False):
    save_path = LOCAL_DATA_PATH + '/pr_data/%s/%s/another_pull.json' % (pull["base"]["repo"]["full_name"], pull["number"])
    if os.path.exists(save_path) and (not renew):
        try:
            return localfile.get_file(save_path)
        except:
            pass

    comments_href = pull["_links"]["comments"]["href"]
    comments = api.request('GET', comments_href, True)
    time.sleep(0.7)
    candidates = []
    for comment in comments:
        candidates.extend(get_pr_and_issue_numbers(comment["body"]))
    candidates.extend(get_pr_and_issue_numbers(pull["body"]))
    
    result = list(set(candidates))
    
    localfile.write_to_file(save_path, result)
    return result

def fetch_file_list(pull, renew=False):
    repo, num = pull["base"]["repo"]["full_name"], str(pull["number"])
    save_path = LOCAL_DATA_PATH + '/pr_data/' + repo + '/' + num + '/raw_diff.json'

    if os.path.exists(save_path) and (not renew):
        try:
            return localfile.get_file(save_path)
        except:
            pass
    
    t = api.get('repos/%s/pulls/%s/files?page=3' % (repo, num))
    file_list = []
    if len(t) > 0:
        raise Exception('too big', pull['html_url'])
    else:
        li = api.request('GET', 'repos/%s/pulls/%s/files' % (repo, num), True)
        time.sleep(0.8)
        for f in li:
            if f.get('changes', 0) <= 5000 and ('filename' in f) and ('patch' in f):
                file_list.append(fetch_raw_diff.parse_diff(f['filename'], f['patch']))

    localfile.write_to_file(save_path, file_list)
    return file_list


pull_commit_sha_cache = {}
def pull_commit_sha(p):
    index = (p["base"]["repo"]["full_name"], p["number"])
    if index in pull_commit_sha_cache:
        return pull_commit_sha_cache[index]
    c = get_pull_commit(p)
    ret = [(x["sha"], x["commit"]["author"]["name"]) for x in list(filter(lambda x: x["commit"]["author"] is not None, c))]
    pull_commit_sha_cache[index] = ret
    return ret

# ------------------Data Pre Collection----------------------------------------------------
def run_and_save(repo, skip_big=False):
    repo = repo.strip()
    
    skip_exist = True

    pulls = get_repo_info(repo, 'pull', True)

    for pull in pulls:
        num = str(pull["number"])
        pull_dir = LOCAL_DATA_PATH + '/pr_data/' + repo + '/' + num
        
        pull = get_pull(repo, num)
        
        if skip_big and check_too_big(pull):
            continue

        if skip_exist and os.path.exists(pull_dir + '/raw_diff.json'):
            continue
        
        fetch_file_list(repo, pull)
        
        print('finish on', repo, num)


if __name__ == "__main__":
    #r = get_pull('angular/angular.js', '16629', 1)
    #print(r['changed_files'])
    # get_pull_commit(get_pull('ArduPilot/ardupilot', '8008'))

    print(len(get_repo_info('FancyCoder0/INFOX', 'fork', True)))
    print(len(get_repo_info('FancyCoder0/INFOX', 'pull', True)))
    print(len(get_repo_info('FancyCoder0/INFOX', 'issue', True)))
    print(len(get_repo_info('FancyCoder0/INFOX', 'commit', True)))
    print(len(get_repo_info('tensorflow/tensorflow', 'branch', True)))
    
    print(len(fetch_file_list(get_pull('FancyCoder0/INFOX', '113', True))))
    print(get_another_pull(get_pull('facebook/react', '12503'), True))
    print([x['commit']['message'] for x in get_pull_commit(get_pull('facebook/react', '12503'),True)])
