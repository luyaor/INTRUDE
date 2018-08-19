import git
import main
import detect

def prlist(repo):
    return git.get_pull_list(repo)

def start_simulate(repo):
    if repo:
        detect.simulate_timeline(repo, False, 2)
