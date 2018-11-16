msr = {}
with open('data/msr_positive_pairs.txt') as f:
    for t in f.readlines():
        r, n1, n2 = t.split()
        msr[(r, n1)] = n2

files = ['evaluation/small_sample_for_recall.txt_leave_file_list.out',
         'evaluation/small_sample_for_recall.txt_leave_code.out',
         'evaluation/small_sample_for_recall.txt_leave_text.out',
         'evaluation/small_sample_for_recall.txt_leave_location.out',
         'evaluation/small_sample_for_recall.txt_leave_pattern.out',
         'evaluation/small_sample_for_recall.txt_new.out']

threshold_select = {}

fixed_recall = 0.15

def check(file):
    num, tot = 0, 0

    num2, num3 = 0, 0

    w = []
    with open(file) as f:
        for t in f.readlines():
            tot += 1
            
            r, n1, n2, v = t.split()

            v = float(v)

            w.append(v)

            
    w = sorted(w, reverse=True)
    
    # print(file, ':', w[39])
    tw = file.split('_')[-1].split('.out')[0]
    if tw == 'list':
        tw = 'file_list'
    
    ind = int(len(w) * fixed_recall)
    print(tw, ':', w[ind])
    
    threshold_select[tw] = w[ind]


for file in files:
    check(file)

print('threshold_select', threshold_select)

way_select = ['file_list', 'code', 'text', 'location', 'pattern', 'new']

def work(way):
    file = 'evaluation/small_sample_for_precision.txt_leave_%s.out' % way
    if way == 'new':
        file = 'evaluation/small_sample_for_precision.txt_new.out'

    p_tot = 0
    p_num = 0

    tot = 0
    threshold = threshold_select[way]
        
    with open(file) as f:
        for t in f.readlines():
            r, n1, n2, v, st = t.split()
            
            if r in ['ceph/ceph', 'dotnet/corefx']: # filter repo with biggest and smallest recall 
                continue

            v = float(v)
    
            if v >= threshold:
                p_tot += 1

                # print(r, n2, n1, v, st, sep='\t')

                if 'Unknown' in st:
                    raise Exception('lack label for', r, n1, n2)
                    # print(r, n1, n2, v, st, sep='\t')
                
                if 'Y' in st:
                    p_num += 1

    
    print(way, 1.0 * p_num / p_tot, p_num, p_tot, sep='\t')
    print('')
    # print(way, 1.0 * p_num / p_tot, sep='\t')


print('way, precision, num, tot, fixed_recall=', fixed_recall, sep='\t')
      
for way in way_select:
    # print('-----%s-----' % way)
    work(way)


