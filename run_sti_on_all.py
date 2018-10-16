from git import *
from sim_part2 import *

num, tot = 0, 0

outfile = 'tmp/ret_f.txt'

with open('tmp/check_list_f.csv') as f:
    for t in f.readlines():
        tot += 1
        print(tot)

        v = t.split(',')
        r, n2, n1 = v[0], v[1], v[2]
        p1 = get_pull(r, n1)
        p2 = get_pull(r, n2)

        l1 = len(get_pull_commit(p1))
        l2 = len(get_pull_commit(p2))
        
        if not ((l1 <= 100) and (l2 <= 100)):
            continue
            
        status, history, history_ret = simulate(r, n1, n2)
        
        with open(outfile, 'a+') as outf:
            print(r, n1, n2, history, file=outf)
