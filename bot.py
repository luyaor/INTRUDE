import sys
from flask_mail import Mail, Message

import git
import detect

# Config
detect.speed_up = True
detect.filter_larger_number = True
detect.filter_out_too_old_pull_flag = True
detect.filter_already_cite = True # diff with rq1
detect.filter_create_after_merge = True
detect.filter_overlap_author = False 
detect.filter_out_too_big_pull_flag = False
detect.filter_same_author_and_already_mentioned = True

# Email setting
mail = Mail(git.app)
    

def work(r, n):
    # n2, prob = detect_one(r, n)
    n2, prob = '133', 0.5 # For test

    print('%s is most duplicate to %s %s, score: %.2f' % (n2, r, n, prob))

    p = git.get_pull(r, n)
    p2 = git.get_pull(r, n2)

    comment_template = 'Hi %s,\n We are researchers working on identifying redundant development/duplicated PRs. We have found there is a pull request: %s which might be a potentially duplicate to this one. We would like to build the link between developers to reduce redundant development. We would really appreciate if you could help us to validate and give us feedback.'
    
    comment_data = {"body": comment_template % (p['user']['login'], p2['html_url'])}

    # Post a comments
    # Notice: Make sure in git.py token_getter token could be available, it used this account to post comment.
    ret = git.api.post('repos/%s/issues/%s/comments' % (r, n), data=comment_data)

    # Send email
    # msg = Message("Hello", sender="from@example.com", recipients=["to@example.com"])
    # mail.send(msg)

if __name__ == "__main__":
    # Input    
    # r, n = sys.argv[1].strip(), sys.argv[2].strip()
    r, n = 'FancyCoder0/INFOX', '152' # For test

    work(r, n)
    
