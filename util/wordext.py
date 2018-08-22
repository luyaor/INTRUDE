import os
import re
import nltk
import itertools
import time
from collections import Counter
from nltk.stem.porter import PorterStemmer
from nltk.stem import WordNetLemmatizer

from . import language_tool

stemmer = PorterStemmer()
lemmatizer = WordNetLemmatizer()

def camel_case_split(identifier):
    matches = re.finditer('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', identifier)
    return [m.group(0) for m in matches]

def word_split_by_char(s):
    """ split the word by some separators
        Args:
            Word
        Returns:
            List of the split words
    """
    # return [s]
    
    old_words = []
    old_words.append(s)
    result = []
    while len(old_words) > 0:
        new_words = []
        for s in old_words:
            if '-' in s:  # Case: ab-cd-ef
                new_words+=s.split('-')
            elif '.' in s:  # Case: ab.cd.ef
                new_words+=s.split('.')
            elif '_' in s:  # Case: ab_cd_ef
                new_words+=s.split('_')
            elif '/' in s:  # Case: ab/cd/ef
                new_words+=s.split('/')
            elif '\\' in s: # Case: ab\cd\ef
                new_words+=s.split('\\')
            else:
                t = camel_case_split(s)
                if len(t) > 1:
                    new_words += t
                result.append(s)
        old_words = new_words
    return result

#def filter_common_words_in_pr(tokens):
#    return list(filter(lambda x: x not in language_tool.get_common_words_in_pr(), tokens))

def stem_process(tokens):
    # Do stem on the tokens.
    for try_times in range(3):
        try:
            result = [stemmer.stem(word) for word in tokens]
            return result
        except:
            print('error on stem_process')
            time.sleep(5)
    return tokens


def lemmatize_process(tokens):
    for try_times in range(3): # NLTK is not thread-safe, use simple retry to fix it.
        try:
            result = [lemmatizer.lemmatize(word) for word in tokens]
        except:
            print('error on lemmatize_process')
            time.sleep(5)
    return tokens

def move_other_char(text):
    return re.sub("[^0-9A-Za-z_]", "", text)

def get_words_from_file(file, text):
    """
        Args:
            file: file full name
            text: the raw text of the file
        Returns:
            A list of the tokens of the result of the participle. 
    """
    if not language_tool.is_text(file):
        return []
    if text is None:
        return []

    tokens = nltk.word_tokenize(text)

    tokens = list(itertools.chain(*[word_split_by_char(token) for token in tokens]))
    # tokens.extend(list(itertools.chain(*[word_split_by_char(token) for token in origin_tokens]))) # Keep original tokens
    
    tokens = list(filter(lambda x: re.search("[0-9A-Za-z_]", x), tokens))
    
    tokens = [x.lower() for x in tokens]
    
    # tokens = filter(lambda x: x not in language_tool.get_language_stop_words(language_tool.get_language(file)), tokens)
    tokens = filter(lambda x: x not in language_tool.get_general_stopwords(), tokens)
    tokens = filter(lambda x: len(x) >= 2, tokens)
    
    tokens = list(tokens)
    
    tokens = stem_process(tokens)
    
    # stemmed_tokens = [PorterStemmer().stem(word) for word in tokens] # do stem on the tokens
    return tokens

def get_words_from_text(text):
    return get_words_from_file('1.txt', text)

def get_counter(tokens):
    tokens = filter(lambda x: x is not None, tokens)
    return Counter(tokens)

def get_top_words(tokens, top_number, list_option = True):
    if tokens is None:
        return None
    counter = get_counter(tokens).most_common(top_number)
    if list_option:
        return [x for x, y in counter]
    else:
        return dict([(x,y) for x, y in counter])

def get_top_words_from_text(text, top_number=10):
    return get_top_words(get_words_from_text(text), top_number)
