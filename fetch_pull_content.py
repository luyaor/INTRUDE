import requests
from requests.adapters import HTTPAdapter
from bs4 import BeautifulSoup

def fetch_pull_content(project_full_name, pull_number):
    url = 'https://github.com/%s/pull/%s' % (project_full_name, pull_number)
    s = requests.Session()
    s.mount('https://github.com', HTTPAdapter(max_retries=3))

    try:
        diff_page = s.get(url, timeout=120)
        if diff_page.status_code != requests.codes.ok:
            raise Exception('error on fetch compare page on %s!' % project_full_name)
    except:
        raise Exception('error on fetch compare page on %s!' % project_full_name)
    
    return diff_page

def parse_pull_content(content):
    diff_page_soup = BeautifulSoup(content, 'html.parser')

    result = []

    for commit_link in diff_page_soup.find_all('a', {'class': 'commit-link'}):
        try:
            href = commit_link.get('href')
            result.append(href)
        except:
            continue

    for pull_link in diff_page_soup.find_all('a', {'class': 'issue-link'}):
        try:
            href = pull_link.get('href')
            result.append(href)
        except:
            continue
    
    result = list(set(result))
    
    for r in result:
        print(url, r)

if __name__ == '__main__':
    fetch_pull_content('apache/spark', '1944')
    
    