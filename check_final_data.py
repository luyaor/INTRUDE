from val import *
from datetime import datetime

def get_time(t):
    return datetime.strptime(t, "%Y-%m-%dT%H:%M:%SZ")


file = 'tmp/check_list.csv'
for t in open(file).readlines():
    ts = t.split()
    r, n1, n2 = ts[0], ts[1], ts[2]
    pullA = get_pull(r, n1)
    pull = get_pull(r, n2)
    
    if not check_ok_new(pull, pullA):
        print('error', t.strip())

    '''
    if (pull["merged_at"] is not None) and \
    (get_time(pull["merged_at"]) < get_time(pullA["created_at"])):
        z = int((get_time(pullA["created_at"]) - get_time(pull["merged_at"])).days)
        if z > 0:
            print(t.strip(), z)
    '''