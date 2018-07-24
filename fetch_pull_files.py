import os
from selenium import webdriver
import requests
from bs4 import BeautifulSoup

def fetch_pull_files(repo, pr_num):
    """Compare the fork with the main branch.
    Args:
        repo_full_name: for example: 'moby/moby'
        pull_request_number: 21495
    Return:
        A list of dict contains following fields :
        file_list {
            file_full_name,
            file_suffix,
            diff_link,
            changed_line,
            changed_code
        }
    """

    url = 'https://www.github.com/%s/pull/%s/files' % (repo, str(pr_num))

    # url = 'https://www.github.com/MarlinFirmware/Marlin/compare/1.1.x...SkyNet3D:SkyNet3D-Devel' # return 15 + load more
    
    # url = 'https://www.github.com/Smoothieware/Smoothieware/compare/edge...Nutz95:edge' # return 65 + load more
    
    print("start fetch: %s" % url)

    driver = webdriver.PhantomJS(service_args=['--ignore-ssl-errors=true', '--ssl-protocol=any'])
    driver.set_page_load_timeout(60) # set timeout time
    
    # driver = webdriver.PhantomJS()
    for try_times in range(3):
        try:
            driver.get(url)
            # print('page title:', driver.title)
            break
        except:
            continue

    if try_times >= 3:
        raise Exception('error on fetch %s' % url)
        
    try:
        repo_content = driver.find_element_by_class_name("repository-content")
    except:
        print("The page is empty!")
        return []

    file_list = []
    total_changed_line_of_source_code = -1
    try:
        diff_list = repo_content.find_element_by_id("files")
    except:
        print('diff_list is empty')
        return []

    # with open('1.html', 'w') as f:
    #     f.write(diff_list.get_attribute('innerHTML'))

    diff_num = 0
    # TODO(Luyao Ren) change to get the list of diff.
    # TODO(Luyao Ren) change analysis part using Beautiful Soup to speed up.
    while True:
        try:
            diff = diff_list.find_element_by_id('diff-' + str(diff_num))
            diff_num += 1
        except:
            # print('diff end on', diff_num)
            try:
                # Some page is loading dynamic, so we need to get more diff.
                # Example: https://github.com/Smoothieware/Smoothieware/compare/edge...Nutz95:edge
                load_url = diff_list.find_elements_by_class_name('js-diff-progressive-container')[-1].find_element_by_tag_name('include-fragment').get_attribute('src')
                # print('more load url:', load_url)
                driver.get('https://github.com/' + load_url)
                diff_list = driver.find_element_by_tag_name('body')
                continue
            except:
                break
        try:
            diff_info = diff.find_element_by_class_name('file-info')
            diff_link = diff_info.find_element_by_tag_name('a').get_attribute('href')
            changed_line = diff_info.text.split(' ')[0].strip().replace(',', '')
            file_full_name = diff_info.text.split(' ')[1].strip()
            # print(diff_num, changed_line, file_full_name)
            file_name, file_suffix = os.path.splitext(file_full_name)
            changed_code = diff.text
        except:
            print("error on parsing %s: diff%d" % (url, diff_num))
            break

        try:
            # This is for the case that "Large diffs are not rendered by default" on Github
            # Example: https://github.com/MarlinFirmware/Marlin/compare/1.1.x...SkyNet3D:SkyNet3D-Devel
            # print('try load %s' % file_full_name)
            load_container = diff.find_element_by_class_name('js-diff-load-container')
            # print("This file: %s need load code." % file_full_name)
            load_url = load_container.find_element_by_xpath('//include-fragment[1]') \
                .get_attribute('data-fragment-url')
            try:
                # print('https://github.com%s' % load_url)
                changed_code = requests.get('https://github.com' + load_url).text
            except:
                print("Error on get load code!")
        except:
            pass
        
        file_list.append({"file_full_name": file_full_name, "file_suffix": file_suffix,
                          "diff_link": diff_link, "changed_line": changed_line, "changed_code": changed_code})
    return file_list


if __name__ == '__main__':
    # Used for testing
    # fetch_pull_files('FancyCoder0/INFOX', 146)
    t = fetch_pull_files('mozilla-b2g/gaia', 12565)
    for c in t:
        print(c["changed_code"])
    