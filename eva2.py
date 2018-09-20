from detect import *
from git import *

files = [
#'/home/luyao/PR_get/INTRUDE/data/clf/manual_label_false.txt',
'/home/luyao/PR_get/INTRUDE/data/clf/manual_label_true.txt',
#'/home/luyao/PR_get/INTRUDE/data/clf/openpr_label_false.txt',
'/home/luyao/PR_get/INTRUDE/data/clf/openpr_label_true.txt'
]

out = open('evaluation/manual_label_check_true.txt', 'a+')

for file in files:
    acc_num, tot_num = 0, 0
    with open(file) as f:
        for t in f.readlines():
            repo, n1, n2 = t.strip().split()
            if int(n1) > int(n2):
                n1, n2 = n2, n1
            
            if check_too_big(get_pull(repo, n2)):
                continue

            print(repo, n1, n2)
            
            ret = get_topK(repo, n2, 5)
            li = [int(x[0]) for x in ret]

            tot_num += 1
            if li[0] == int(n1):
                acc_num += 1

            print(repo, n2, 'except =', n1, 'actual =', li[0], ret[0][1], file=out)
            out.flush()


            acc = 1.0 * acc_num / tot_num
            print('acc=', acc, file=out)
            out.flush()

out.close()