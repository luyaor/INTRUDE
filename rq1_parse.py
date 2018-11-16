for thres in range(4200, 6801, 25):
    threshold = 1.0 * thres / 10000

    precision = {}
    precision_num = {}
    recall = {}
    recall_num = {}
    
    overall_pre = [0, 0]
    overall_rec = [0, 0]

    with open('evaluation/random_sample_select_pr_result.txt') as f:
        for t in f.readlines():
            if ',' in t:
                r, n1, n2, v, status = t.strip().split(',')
            else:
                r, n1, n2, v, status = t.strip().split()

            v = float(v)

            if 'Unknown' in status:
                continue

            if r not in precision:
                precision[r] = 'N/A'
                precision_num[r] = [0, 0]
            
            if v >= threshold:
                overall_pre[1] += 1
                precision_num[r][1] += 1
                if 'Y' in status:
                    overall_pre[0] += 1
                    precision_num[r][0] += 1
                precision[r] = 1.0 * precision_num[r][0] / precision_num[r][1]

    with open('evaluation/msr_second_part_result.txt') as f:
        for t in f.readlines():
            r, n1, n2, v = t.strip().split()
            v = float(v)

            '''
            if r not in precision:
                continue
            '''
     
            if r not in recall_num:
                recall[r] = 'N/A'
                recall_num[r] = [0, 0]
            
            overall_rec[1] += 1
            recall_num[r][1] += 1
            if v >= threshold:
                overall_rec[0] += 1
                recall_num[r][0] += 1
            recall[r] = 1.0 * recall_num[r][0] / recall_num[r][1]


    def safe_div(n, d):
        return n / d if d > 0 else -1

    '''
    pre = list(filter(lambda x: x != 'N/A', precision.values()))
    rec = list(filter(lambda x: x != 'N/A', recall.values()))

    print(threshold, safe_div(sum(pre), len(pre)), safe_div(sum(rec), len(rec)), sep='\t')
    '''

    if threshold < 0.59:
        overall_pre = [0, 0]

    print(threshold, safe_div(overall_pre[0], overall_pre[1]), safe_div(overall_rec[0], overall_rec[1]), sep='\t')
    
    
    '''
    print(overall_pre[0], overall_pre[1],sep='\t')
    print(overall_rec[0], overall_rec[1],sep='\t')
    
    for r in precision:
        if precision[r] == 'N/A':
            precision[r] = -1
        print('{:20}'.format(r), \
            #precision_num[r][0], precision_num[r][1],\
            recall_num[r][0], recall_num[r][1],\
            #'{:.0%}'.format(precision[r]),\
            '{:.0%}'.format(recall[r]), \
            #'%d%d' % (precision_num[r][0], precision_num[r][1]),\
            #'%d/%d' % (recall_num[r][0], recall_num[r][1]),\
            sep='\t')
    '''
    
    
