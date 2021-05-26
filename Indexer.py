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
import pickle 
import math

class Indexer:
    STOPWORDS = ["a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being", "below"
                           , "between", "both", "but", "by", "can't", "cannot", "could", "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during", "each"
                           , "few", "for", "from", "further", "had", "hadn't", "has", "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here", "here's", "hers"
                           , "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", "let's", "me"
                           , "more", "most", "mustn't", "my", "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought", "our", "ours", "ourselves", "out", "over"
                           , "own", "same", "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such", "than", "that", "that's", "the", "their", "theirs", "them"
                           , "themselves", "then", "there", "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this", "those", "through", "to", "too", "under", "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll"
                           , "we're", "we've", "were", "weren't", "what", "what's", "when", "when's", "where", "where's", "which", "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would", "wouldn't"
                           , "you", "you'd", "you'll", "you're", "you've", "your", "yours", "yourself", "yourselves"
                         ]
    PUNCTUATION = '''!()-[]{};:'"\, <>./?@#$%^&*_~\''''
    
    def __init__(self, corpus_dictionary):
        self.invertedIndex = {}
        self.corpus_dictionary = corpus_dictionary
        self.path = os.path.join(os.path.abspath(os.getcwd()), "WEBPAGES_RAW")
        self.stemmer = krovetz.PyKrovetzStemmer()
        self.unique_doc_id = 0
        self.unique_words = 0
        self.doc_dic = {}

    def tokenize_corpus(self):
        print("Creating inverted index...")
        for docId, url in self.corpus_dictionary.items():
            print("Indexing file: " + docId)
            html_path = os.path.join(self.path, docId)
            self.unique_doc_id += 1 # Counting number of unique document ids in index (M1)

            with open(html_path, 'r', encoding = 'utf8') as f:
                page = f.read()
            soup = BeautifulSoup(page, 'lxml')
            
            ## tokenizing all text
            reg_tokens = nltk.word_tokenize(soup.text)
            self.calc_term_frequency(docId, reg_tokens, 1)

            ## tokenizing titles
            title = soup.find_all("title")
            for t in title:
                t_tokens = nltk.word_tokenize(t.text)
                self.calc_term_frequency(docId, t_tokens, 7)

            ## tokenizing h1
            h1_list = soup.find_all("h1")
            for h1 in h1_list:
                h1_tokens = nltk.word_tokenize(h1.text)
                self.calc_term_frequency(docId, h1_tokens, 6)

            ## tokenizing h2
            h2_list = soup.find_all("h2")
            for h2 in h2_list:
                h2_tokens = nltk.word_tokenize(h2.text)
                self.calc_term_frequency(docId, h2_tokens, 5)
            
            ## tokenizing h3
            h3_list = soup.find_all("h3")
            for h3 in h3_list:
                h3_tokens = nltk.word_tokenize(h3.text)
                self.calc_term_frequency(docId, h3_tokens, 4)

            ## tokenizing strong words
            strong_words = soup.find_all("strong")
            for s in strong_words:
                s_tokens = nltk.word_tokenize(s.text)
                self.calc_term_frequency(docId, s_tokens, 3)

            ## tokenizing bold words
            bold_words = soup.find_all("b")
            for b in bold_words:
                b_tokens = nltk.word_tokenize(b.text)
                self.calc_term_frequency(docId, b_tokens, 2)
        print(self.unique_doc_id)
        print("Inverted index created.")
    
    def calc_term_frequency(self, docId, token_list, frequency):
        
        for token in token_list: 
            strp_word = token.strip(Indexer.PUNCTUATION)
            word = self.stemmer.stem(strp_word)
            if word not in Indexer.STOPWORDS:
                if word not in self.invertedIndex.keys():
                    self.invertedIndex[word] = {docId:[frequency]}
                    self.unique_words += 1 #Counting number of unique words (M1)
                else:
                    if docId not in self.invertedIndex[word].keys():
                        self.invertedIndex[word][docId] = [frequency]
                    else:
                        self.invertedIndex[word][docId][0] += frequency
            
    def calc_tfidf(self):
        for token, d in self.invertedIndex.items():
            for doc, l in d.items():
                freq = l[0]
                tf = self.tf(freq)
                idf = self.idf(token)
                tf_idf = tf*idf
                self.invertedIndex[token][doc] = [freq, tf_idf]

    def bigram_tokenize(self):
        print("Creating bigram inverted index...")
        for docId, url in self.corpus_dictionary.items():
            print("Indexing file: " + docId)
            html_path = os.path.join(self.path, docId)
            self.unique_doc_id += 1 # Counting number of unique document ids in index

            with open(html_path, 'r', encoding = 'utf8') as f:
                page = f.read()
            
            soup = BeautifulSoup(page, 'lxml')

            #tokenizing all text
            reg_tokens = nltk.word_tokenize(soup.text)
            self.calc_term_frequency_bigram(docId, reg_tokens, 1)
            
            #tokenizing all titles
            title = soup.find_all("title")
            for t in title:
                t_tokens = nltk.word_tokenize(t.text)
                self.calc_term_frequency_bigram(docId, t_tokens, 7)

            #tokenizing h1
            h1_list = soup.find_all("h1")
            for h1 in h1_list:
                h1_tokens = nltk.word_tokenize(h1.text)
                self.calc_term_frequency_bigram(docId, h1_tokens, 6)

            #tokenizing h2
            h2_list = soup.find_all("h2")
            for h2 in h2_list:
                h2_tokens = nltk.word_tokenize(h2.text)
                self.calc_term_frequency_bigram(docId, h2_tokens, 5)
            
            #tokenizing h3
            h3_list = soup.find_all("h3")
            for h3 in h3_list:
                h3_tokens = nltk.word_tokenize(h3.text)
                self.calc_term_frequency_bigram(docId, h3_tokens, 4)

            #tokenizing strong words
            strong_words = soup.find_all("strong")
            for s in strong_words:
                s_tokens = nltk.word_tokenize(s.text)
                self.calc_term_frequency_bigram(docId, s_tokens, 3)

            #tokenizing b words
            bold_words = soup.find_all("b")
            for b in bold_words:
                b_tokens = nltk.word_tokenize(b.text)
                self.calc_term_frequency_bigram(docId, b_tokens, 2)

        print("Inverted bi-gram index created.")

    def calc_term_frequency_bigram(self, docId, token_list, frequency):
        tracker = 1
        for token in token_list:
            if tracker < len(token_list):
                strp_word1 = token.strip(Indexer.PUNCTUATION)
                strp_word2 = token_list[tracker].strip(Indexer.PUNCTUATION)
                word1 = self.stemmer.stem(strp_word1)
                word2 = self.stemmer.stem(strp_word2)
                if word1 not in Indexer.STOPWORDS and word2 not in Indexer.STOPWORDS:
                    t = word1 + " " + word2
                    if t not in self.invertedIndex.keys():
                        self.invertedIndex[t] = {docId:[frequency]}
                        self.unique_words += 1
                    else:
                        if docId not in self.invertedIndex[t].keys():
                            self.invertedIndex[t][docId] = [frequency]
                        else:
                            self.invertedIndex[t][docId][0] += frequency
            tracker += 1


    def save_index(self, name):
        json_file = json.dumps(self.invertedIndex)
        f = open(name, "w")
        f.write(json_file)
       
        f.close()

    def tf(self, frequency):
        tf = 1 + math.log10(frequency)
        return tf

    def invert_dict(self):  # change {term:{docID:frequency}}  into {docID:{word:frequency}}
        for k, v in self.invertedIndex.items():
            for k1, v1 in v.items():
                self.doc_dic[k1] = {k:v1[0]}
        
    def idf(self, token):
        df = len(self.invertedIndex[token].keys())
        idf = math.log10(len(self.doc_dic.keys())/df)
        return idf

