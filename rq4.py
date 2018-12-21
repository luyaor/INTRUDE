import os
import sys
import importlib

ways = ['file_list', 'code', 'text', 'location', 'pattern', 'new']
files = ['data/small_sample_for_precision.txt', 'data/small_sample_for_recall.txt']

import clf
import detect

def run(leave_way, infile):

    way = 'leave_' + leave_way
    print('way=', way)
    print('input file=', infile)

    if leave_way == 'new':
        way = 'new'

    out = infile.replace('data/','evaluation/') + '_' + way + '.out'

    def load(file):
        runned = set()
        if not os.path.exists(file):
            return runned

        with open(file) as f:
            for t in f.readlines():
                r, n2 = t.split()[:2]
                runned.add((r, n2))
        return runned

    runned_cases = load(out)


    importlib.reload(clf)
    if leave_way == 'text':
        clf.part_params = [0,0,1,1,1,1,1,1,1]
    elif leave_way == 'code':
        clf.part_params = [1,1,0,0,1,1,1,1,1]
    elif leave_way == 'file_list':
        clf.part_params = [1,1,1,1,0,0,1,1,1]
    elif leave_way == 'location':
        clf.part_params = [1,1,1,1,1,1,0,0,1]
    elif leave_way == 'pattern':
        clf.part_params = [1,1,1,1,1,1,1,1,0]
    elif leave_way != 'new':
        print('------error!-----')

    importlib.reload(detect)
    detect.speed_up = True
    detect.filter_larger_number = True
    detect.filter_out_too_old_pull_flag = True
    detect.filter_already_cite = False
    detect.filter_create_after_merge = True
    detect.filter_overlap_author = False
    detect.filter_out_too_big_pull_flag = False
    detect.filter_same_author_and_already_mentioned = True

    with open(infile) as f:
        pairs = f.readlines()

        for t in pairs:
            ts = t.strip().split()

            r, n2 = ts[0], ts[1]

            if (r, n2) in runned_cases:
                print('pass', (r, n2))
                continue

            ret = detect.get_topK(r, n2 , 1, True, way)
            
            if len(ret) < 1:
                n1, proba = -1, -1
            else:
                n1, proba = ret[0]

            with open(out, 'a') as outf:
                print(r, n2, n1, proba, sep='\t', file=outf)

for way in ways:
    for file in files:
        run(way, file)
