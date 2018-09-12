from detect import *

files = [
#'/home/luyao/PR_get/INTRUDE/data/clf/manual_label_false.txt',
'/home/luyao/PR_get/INTRUDE/data/clf/manual_label_true.txt',
#'/home/luyao/PR_get/INTRUDE/data/clf/openpr_label_false.txt',
'/home/luyao/PR_get/INTRUDE/data/clf/openpr_label_true.txt'
]

for file in files:
    acc_num, tot_num = 0, 0
    with open(file) as f:
        for t in f.readlines():
            repo, n1, n2 = t.strip().split()
            if n1 > n2:
                n1, n2 = n2, n1

            li = [int(x[0]) for x in get_topK(repo, n2, 5)]

            tot_num += 1
            if li[0] == n1:
                acc_num += 1

        acc = 1.0 * acc_num / tot_num
        print('acc=', acc)

