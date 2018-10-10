import detect
detect.speed_up = True

file = 'tmp/p_pre.txt'

with open(file) as f:
    for t in f.readlines():
        r, n1, n2, status = t.strip().split('\t')

        topk = detect.get_topK(r, n1, 30, True)
        ok = False
        
        for (num, prob) in topk:
            if not detect.check_pro_pick_with_num(r, n1, num):
                if str(num) != str(n2):
                    status = 'Unknown'
                print(r, n1, num, prob, status)
                
                with open('tmp/p_after.txt', 'a') as out:
                    print(r, n1, num, prob, status, file=out)
                
                ok = True
                break
        
        if not ok:
            print('error!', r, n1, n2)

        