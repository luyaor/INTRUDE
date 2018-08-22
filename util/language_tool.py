import os

FLAGS_load_language_data = False

text_suffix = []
general_stopwords = []

language_data_path = os.path.dirname(os.path.realpath(__file__)) + '/data'

def init():
    """ Load the language data.
    """
    global FLAGS_load_language_data
    if FLAGS_load_language_data:
        return
    with open(language_data_path + '/text_suffix.txt') as read_file:
        for line in read_file.readlines():
            text_suffix.append(line.strip())

    with open(language_data_path + '/general_stopwords.txt') as read_file:
        for line in read_file.readlines():
            if line:
                word = line.strip()
                general_stopwords.append(word)
    
    FLAGS_load_language_data = True

def get_general_stopwords():
    init()
    return general_stopwords

'''
def get_common_words_in_pr():
    init()
    return common_words_in_pr
'''

def is_text(file):
    """ The file is text
        Args:
            file full name
        Returns:
            True/False
    """
    init()
    if '.' not in file:
        return False
    file_name, file_suffix = os.path.splitext(file)
    file_suffix = file_suffix.strip()
    if file_suffix in text_suffix:
        return True
    else:
        return False
