from val import *

threhold = 0.59

import os

files = os.listdir('rlog')

out = 'rlog/all_with_mark_new.txt'

mark = {}
with open('rlog/label.csv') as f:
    for t in f.readlines():
        r, n1, n2, v, status = t.strip().split(',')
        mark[(r, n1, n2)] = status

have = {}

for file in files:
    if 'log' not in file:
        continue
    
    print('file=', file)
    
    num = 0
    tot = 0
    
    with open('rlog/' + file) as f:
        for t in f.readlines():
            tot += 1
            
            rs, vs = t.strip().split(':')
            r, n_big = rs.strip().split()
            
            op = vs.strip()[2:-2].split('), (')
            
            for can in op:
                n_small, proba = can.split(',')
                proba = float(proba)
                
                if proba < threhold:
                    continue
                
                if check_ok_new_num(r, n_small, n_big):
                    st = mark.get((r, n_big, n_small), 'Unknown')
                    
                    if st == 'Unknown':
                        if check_mention(r, n_small, n_big):
                            st += '(mention)'
                    
                    if (r, n_big) in have:
                        if have[(r, n_big)] != n_small:
                            print('error=', r, n_big, n_small, have[(r, n_big)])
                            continue
                            # raise Exception('error')
                    have[(r, n_big)] = n_small
                    
                    with open(out, 'a') as outf:
                        print(r, n_big, n_small, proba, st, sep='\t', file=outf)
                    num += 1
                    break
    
    print(file, ':', num, '/', tot)
                
