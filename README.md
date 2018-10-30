# INTRUDE

## *I*de*NT*ifying *R*ed*U*ndancies in Fork-based *DE*velopment


Python library dependencies:

sklearn, numpy, SciPy, matplotlib, gensim, nltk, bs4, flask, GitHub-Flask

---

Configuration:

git.py: LOCAL_DATA_PATH, access_token

nlp.py: model_path

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

``` bash
detect.detect_one(repo, pr_num)
```



detect_on_cross_forks.py: Detection on pull requests of cross-projects.

``` python
detect_on_cross_forks.detect_on_pr(repo_name)
```



stimulate_part_pr.py: stimulate "part PR detection".

``` python
simulate(repo, pr_num1, pr_num2)
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
