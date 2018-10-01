from git import *
from detect import *

file = 'evaluation/facebook_react_run_on_select_new.txt'
nf = file.replace('.txt', '') + '_filsamec.txt'

out = open(nf, 'w')
with open(file) as f:
    for t in f.readlines():
        ts = t.split()
        r, n1, n2, v = ts[0], ts[1], ts[2], ts[3]
        
        p1=get_pull(r, n1)
        p2=get_pull(r, n2)

        if (float(v) >= 0.58) and (have_commit_overlap(p1, p2)):
            print('Run', r, n1, '........')
            ret = get_topK(r, n1, 30, True)
            newd = ret[0][0]
            newv = ret[0][1]
            print(r, n1, newd, "%.4f" % newv, sep="\t", file=out)
        else:
            print(t.strip(), file=out)
out.close()
