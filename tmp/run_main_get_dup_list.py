import main

# main.run_and_save('FancyCoder0/INFOX')

with open('data/top_repo_list.txt') as f:
    for line in f.readlines():
        if not line:
            break
        repo = line.strip()
        try:
            main.find_dup_pairs(repo)
        except:
            import time
            time.sleep(30 * 60)
            continue
