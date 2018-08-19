from git import *
from clf import *
from comp import *
from util import localfile

m = classify()

def gen_commit_feature_vet(data, label, out=None):
    with open(data) as f:
        pairs = f.readlines()

    default_path = 'data/' + data.replace('data/','').replace('.txt','').replace('/','_') + '_commit_feature_vector_mix'
    if out is None:
        out = default_path
    else:
        out = default_path + '_' + out

    X_path = out + '_X.json'
    y_path = out + '_y.json'
    
    '''
    if os.path.exists(X_path) and os.path.exists(y_path):
        return
    '''
    
    num_total = 0
    
    X, y = [], []
    
    pairs = sorted(pairs, key=lambda x: x.split()[0])
    last_repo = None
    
    for pair in pairs:
        repo, num1, num2 = pair.split()
        # print(pair)
        
        if last_repo != repo:
            init_model_with_repo(repo)
            last_repo = repo

        p1 = get_pull(repo, num1)
        p2 = get_pull(repo, num2)

        cl1 = get_pull_commit(p1)
        cl2 = get_pull_commit(p2)

        if (len(cl1) >= 100) or (len(cl2) >= 100):
            continue

        if check_too_big(p1) or check_too_big(p2):
            continue

        max_s, max_p1, max_p2, max_vet = -1, None, None, [0,0,0,0,0,0]

        for c1 in cl1:
            for c2 in cl2:
                vet = get_commit_sim_vector(c1, c2)
                t = m.predict_proba([vet])[0][1]
                if t > max_s:
                    max_s, max_p1, max_p2, max_vet = t, c1['html_url'], c2['html_url'], vet
        
        max_vet += get_sim(repo, num1, num2)
        
        X.append(max_vet)
        y.append(label)

        num_total += 1
        if num_total % 100 == 0:
            print(num_total)



    localfile_tool.write_to_file(X_path, X)
    localfile_tool.write_to_file(y_path, y)

if __name__ == "__main__":
    gen_commit_feature_vet('data/rly_false_pairs.txt', 0)
    '''
    while True:
        try:
            gen_commit_feature_vet('data/rly_false_pairs.txt', 0)
            gen_commit_feature_vet('data/small_part_msr.txt', 1)
            gen_commit_feature_vet('data/rly_true_pairs.txt', 1)
            gen_commit_feature_vet('data/small_part_negative.txt', 0)
            gen_commit_feature_vet('data/small2_part_msr.txt', 1)
            break
        except:
            pass
    '''
    