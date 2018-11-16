import sys

# treshold ~ precision, recall, saved commit

file1 = 'evaluation/second_msr_pairs_history.txt' # positive
file2 = 'evaluation/second_nondup_history.txt' # negative

#file1 = 'detection/mulc_second_nondup_okret_tds.txt.fil' #negative
#file2 = 'detection/mulc_second_msr_pairs_okret_tds.txt.fil' #positive
'''
if len(sys.argv) == 3:
    file1 = sys.argv[1].strip()
    file2 = sys.argv[2].strip()
'''

treshold = 0.6

def calc(file):
    with open(file) as f:
        ps = f.readlines()

    save = []
    cases = []
    save_tot = 0
    save_times = 0
    
    for p in ps:
        ts = p.strip().split(' : ')
        r, n1, n2 = ts[0].split()
        if ts[1] == '[]': # result is empty
            continue

        vs = ts[1][2:-2].split('), (')
        
        hist, lastc = [], []
        for v in vs:
            proba, x = v.split(',')
            hist.append(float(proba))
            lastc.append(int(x))

        if len(hist) == 1:
            continue

        s = -1
        for i in range(len(hist)):
            if hist[i] >= treshold:
                s = len(hist) - i - 1
                t = lastc[i]
                save_tot += t
                if t > 0:
                    save_times += 1                  
                break

        save.append(s)
        cases.append([r, n1, n2])

        '''
        if s > 0:
            print(r, n1, n2)
        '''
    
    return save, cases, 1.0 * save_tot / len(save)

'''
def P(save):
    no_zero = 0
    for i in save:
        if i > 0:
            no_zero += 1
    return no_zero
    
    no_neg = 0
    for i in save:
        if i >= 0:
            no_neg += 1
'''


print('threshold, precision, false_positive_rate, avg_save')

for tres in range(3700, 7001, 25):

    treshold = 1.0 * tres / 10000

    ret_n, ca_n, _ = calc(file2)
    fp = len(list(filter(lambda x: x >= 0, ret_n)))
    
    repos = set([x[0] for x in ca_n])
    
    ret_p, ca_p, avg_save = calc(file1)
    tp = len(list(filter(lambda x: x >= 0, ret_p)))

    precision = tp / (tp + fp) if tp + fp > 0 else 1.0
    recall = tp / len(ret_p)
    # saved_c = 1.0 * sum(list(filter(lambda x: x > 0, ret_p))) / 2 / len(ret_p)
    
    FPR = fp / len(ret_n)
    
    #print('treshold', treshold)
    #print('precision', precision)
    #print('recall', recall)
    #print('saved_c', saved_c)
    
    # print(treshold, fp, sep='\t')
    print(treshold, precision, FPR, avg_save, sep='\t')
    
    '''
    precision_num = {}
    recall_num = {}
    
    for r in repos:
        precision_num[r] = [0, 0]
        recall_num[r] = [0, 0]

    for i in range(len(ret_n)):
        r = ca_n[i][0]
        
        if ret_n[i] > 0:
            precision_num[r][1] += 1
    
    
    for i in range(len(ret_p)):
        r = ca_p[i][0]

        recall_num[r][1] += 1

        if ret_p[i] > 0:
            precision_num[r][0] += 1
            precision_num[r][1] += 1
            
            recall_num[r][0] += 1
    
    def safe_div(n, d):
        return n / d if d > 0 else 0
    
    pre_tot, pre_num = 0, 0
    rec_tot, rec_num = 0, 0
    
    
    for r in repos:
        if precision_num[r][1] == 0:
            precision = -1
        else:
            precision = 1.0 * precision_num[r][0] / precision_num[r][1]
            pre_tot += precision
            pre_num += 1
            
        if recall_num[r][1] == 0:
            recall = -1
        else:
            recall = 1.0 * recall_num[r][0] / recall_num[r][1]
            rec_tot += recall
            rec_num += 1
        
        print('{:20}'.format(r), \
            precision_num[r][0], precision_num[r][1],\
            '{:.0%}'.format(precision), \
            recall_num[r][0], recall_num[r][1],\
            '{:.0%}'.format(recall), \
            #'%d%d' % (precision_num[r][0], precision_num[r][1]),\
            #'%d/%d' % (recall_num[r][0], recall_num[r][1]),\
            sep='\t')
    
    print(1.0 * pre_tot / pre_num)
    print(1.0 * rec_tot / rec_num)
    '''
