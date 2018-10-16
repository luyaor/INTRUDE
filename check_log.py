from val import *
from sklearn.utils import shuffle

threhold = 0.59

import os

files = os.listdir('rlog')

# out = 'rlog/all_with_mark_new_all_400.txt'
out = 'rlog/sample_small_data.txt'
with open(out, 'w') as f:
    pass

mark = {}
in_mark = set()
#with open('rlog/label.csv') as f: # old version
with open('rlog/new_labeled.csv') as f:
    for t in f.readlines():
        r, n1, n2, v, status = t.strip().split(',')
        if status.strip() == 'Unknown':
            continue
        in_mark.add((r, n1))
        mark[(r, n1, n2)] = status

have = {}

# only = ['ceph/ceph','joomla/joomla-cms','moby/moby','dotnet/corefx','hashicorp/terraform','emberjs/ember.js']

def check():
    
    totm = 0
    
    for file in files:
        if 'log' not in file:
            continue
        
        if file == 'hashicorp_terraform_stimulate_detect2.log':
            continue
        if file == 'elastic_elasticsearch_stimulate_detect_del.log':
            continue
        '''
        only_check = False
        for o in only:
            if (o.replace('/', '_')) in file:
                only_check = True
        if not only_check:
            continue
        
        if file != 'docker_docker_stimulate_detect.log':
            continue
        '''
        
        print('file=', file)

        num = 0
        tot = 0
        num2 = 0
        num3 = 0
        markn = 0
        
        with open('rlog/' + file) as f:
            pairs = f.readlines()
            
            '''
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
            '''
            
            print(len(pairs), '->', 100)

            
            partc = ['cocos2d_cocos2d-x', 'facebook_react', 'ansible_ansible', 'django_django', 'rails_rails', 'angular_angular.js']
            
            get_way = '2'
            for partr in partc:
                if partr in file:
                    get_way = '1'
                
            if get_way == '1':
                pairs = shuffle(pairs[:400])[:70]
            else:
                pairs = shuffle(pairs)[:70]
            
            w = []
            for t in pairs:
                tot += 1

                rs, vs = t.strip().split(':')
                r, n_big = rs.strip().split()

                op = vs.strip()[2:-2].split('), (')
                
                w.append((r, int(n_big)))
                
                if (r, n_big) in in_mark:
                    markn +=1 
                    
                '''
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
                '''
            
            w = sorted(w)
            
            with open(out,'a') as outf:
                for (r, n) in w:
                    print(r, n, file=outf)
            
            print('markn=',markn)
            totm += markn
    
        # print(tot, num)
        #print(file, ':', num, ',', num2, '/', tot)
        print('totm', totm)
        #return 1.0 * num3 / num2
        
check()
