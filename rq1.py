import detect

detect.speed_up = True
detect.filter_larger_number = True
detect.filter_out_too_old_pull_flag = True
detect.filter_already_cite = False
detect.filter_create_after_merge = True
detect.filter_overlap_author = False
detect.filter_out_too_big_pull_flag = False
detect.filter_same_author_and_already_mentioned = True


# For precision
outfile = 'evaluation/random_sample_select_pr_result.txt'
with open(outfile, 'w') as outf:
    pass

with open('data/random_sample_select_pr.txt') as f:
    for t in f.readlines():
        r, n1 = t.split()

        n2, proba = detect.detect_one(r, n1)
        
        with open(outfile, 'a') as outf:
            print(r, n1, n2, proba, sep='\t', file=outf)


# For Recall
outfile = 'evaluation/msr_second_part_result.txt'
with open(outfile, 'w') as outf:
    pass

with open('data/clf/second_msr_pairs.txt') as f:
    for t in f.readlines():
        r, pr1, pr2 = t.split()
        
        n1 = str(max(int(pr1), int(pr2)))
        
        n2, proba = detect.detect_one(r, n1)
        
        with open(outfile, 'a') as outf:
            print(r, n1, n2, proba, sep='\t', file=outf)
