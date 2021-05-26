import sys
import json
from lxml import etree, html
import requests
from io import StringIO
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import os
import krovetz
import nltk
from Indexer import Indexer
from Query import Query
import slappingui
 

if __name__ == "__main__":
    json_file_path = open(sys.argv[1])
    book_keeping = json.load(json_file_path)

    '''
        Single Word Index --  Commented out b/c we have already created this index.

    index = Indexer(book_keeping)
    index.tokenize_corpus()
    index.invert_dict()
    index.calc_tfidf()
    index.save_index("index.json") # one word index

        Bi-gram Index -- Commented out b/c we have already created this index.
    
    bigram_index = Indexer(book_keeping)
    bigram_index.bigram_tokenize()
    bigram_index.invert_dict()
    bigram_index.calc_tfidf()
    bigram_index.save_index("bigramindex.json") # bigram index
    '''
    
    view = slappingui.slappinGUI(book_keeping, "index.json", "bigramindex.json") 

