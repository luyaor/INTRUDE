from val import *
from sklearn.utils import shuffle

threhold = 0.59

import os

files = os.listdir('rlog')

# out = 'rlog/all_with_mark_new_all_400.txt'
out = 'rlog/rpart.txt'

mark = {}
#with open('rlog/label.csv') as f: # old version
with open('rlog/new_labeled.csv') as f:
    for t in f.readlines():
        r, n1, n2, v, status = t.strip().split(',')
        mark[(r, n1, n2)] = status

have = {}

only = ['ceph/ceph','joomla/joomla-cms','moby/moby','dotnet/corefx','hashicorp/terraform','emberjs/ember.js']

def check():
    for file in files:
        if 'log' not in file:
            continue
        
        '''
        only_check = False
        for o in only:
            if (o.replace('/', '_')) in file:
                only_check = True
        if not only_check:
            continue
        '''
        if file != 'docker_docker_stimulate_detect.log':
            continue
        
        print('file=', file)

        num = 0
        tot = 0
        num2 = 0
        num3 = 0

        with open('rlog/' + file) as f:
            pairs = f.readlines()

            np = []
            l = len(pairs)
            check_cover = set()
            for i in range(len(pairs)):
                t = pairs[l - i - 1]
                rs, vs = t.strip().split(':')
                r, n_big = rs.strip().split()
                if (r, n_big) in check_cover:
                    continue
                check_cover.add((r, n_big))
                np.append(t)
            pairs = np
            
            print(len(pairs), '->', 800)

            pairs = shuffle(pairs)[:800]

            for t in pairs:
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

                        if proba >= 0.6:
                            num2 += 1

                        break

        #print(file, ':', num, ',', num2, '/', tot)
        #return 1.0 * num3 / num2

check()
