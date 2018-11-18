# INTRUDE

## *I*de*NT*ifying *R*ed*U*ndancies in Fork-based *DE*velopment


Python library dependencies:

sklearn, numpy, SciPy, matplotlib, gensim, nltk, bs4, flask, GitHub-Flask

---

Configuration:

git.py: `LOCAL_DATA_PATH`, `access_token`

nlp.py: `model_path`

---

RQ1:

1. `python rq1.py`
    
    (It will take `data/random_sample_select_pr.txt` & `data/clf/second_msr_pairs.txt` as input, and write the output into files: `evaluation/random_sample_select_pr_result.txt` & `evaluation/msr_second_part_result.txt`.)

2. manually label output file: `evaluation/random_sample_select_pr_result.txt`, add Y/N/Unknown at end (see `evaluation/random_sample_select_pr_result_example.txt` as example)

3. `python rq1_parse.py`

   (It will print precision & recall at different threshold to stdout.)


RQ2:

1. `python rq2.py data/clf/second_msr_pairs.txt`

   `python rq2.py data/clf/second_nondup.txt`
   
   (It will take `data/clf/second_msr_pairs.txt` & `data/clf/second_nondup.txt` as input, and write the output into files: `evaluation/second_msr_pairs_history.txt` & `evaluation/second_nondup_history.txt`.)

2. `python rq2_parse.py`

   (It will print precision, FPR, saved commits at different threshold to stdout.)

RQ3:
1. `python rq3.py new`

   `python rq3.py old`

    (It will take `data/clf/second_msr_pairs.txt` as input, and write the output into files: `result_on_topk_new.txt` & `result_on_topk_old.txt`)
   
2. `python rq3_parse.py new`

   `python rq3_parse.py old`
 
   (It will print topK recall for our method and another method to stdout.)

RQ4:
1. `python rq4.py`

    (It will take `data/small_sample_for_precision.txt` & `data/small_sample_for_recall.txt` as input, and write the output into files: `evaluation/small_sample_for_precision.txt_XXXX.out.txt` & `evaluation/small_sample_for_recall.txt_XXXX.out.txt`)
   
2. manually label **all** the output files: `evaluation/small_sample_for_precision.txt_XXXX.out.txt`, add Y/N/Unknown at end (see `evaluation/small_sample_for_precision.txt_new_example.out` as example)

3. `python rq4_parse.py`

   (It will print precision for all the leave-one-out models under a fixed recall to stdout.)


---
Main API:
```
python detect.py repo # detect all the PRs of repo
python detect.py repo pr_num # detect one PR

python openpr_detect.py repo # detect all the open PRs of repo

python detect_on_cross_forks.py repo1 repo2 # detect the PRs between repo1 and repo2

python print_html.py result_file # print html for the PR pairs
```

---

clf.py: Classification Model using Machine Learning.

``` python
# Set up the input dataset
c = classify()
c.predict_proba(feature_vector)

init_model_with_repo(repo) # prepare for prediction
```



nlp.py: Natural Language Processing model for calculating the text similarity.


``` python
m = Model(texts)
text_sim = query_sim_tfidf(tokens1, tokens2)
```


comp.py: Calculate the similarity for feature extraction.

``` 
# Set up the params of compare (different metrics).
# Check for init NLP model.
feature_vector = get_pr_sim_vector(pull1, pull2)
```



detect.py: Detection on (open) pull requests.

``` python
detect.detect_one(repo, pr_num)
```


detect_on_cross_forks.py: Detection on pull requests of cross-projects.

``` python
detect_on_cross_forks.detect_on_pr(repo_name)
```


test_commit.py: compare on granularity of commits.



---

git.py: About GitHub API setting and fetching.

``` python
get_repo_info('FancyCoder0/INFOX',
              'fork' / 'pull' / 'issue' / 'commit' / 'branch',
              renew_flag)

get_pull(repo, num, renew)
get_pull_commit(pull, renew)
fetch_file_list(pull, renew)
get_another_pull(pull, renew)
check_too_big(pull)
```


fetch_raw_diff.py: Get data from API, parse the raw diff.

``` python
parse_diff(file_name, diff) # parse raw diff
fetch_raw_diff(url) # parse raw diff from GitHub API
```



gen.py: Generate the random pairs & potential pairs(from duplicate labels)

``` python
repo, pr_num1, pr_num2 = random_pairs()
```



---
