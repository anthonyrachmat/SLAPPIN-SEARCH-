import json
import krovetz


class Query:
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

    def __init__(self, book_keeping, inverted_index_json, inverted_bigram_index_json):
        self.book_keeping = book_keeping
        with open(inverted_index_json) as jf:
            inverted_index = json.load(jf)
        self.inverted_index = inverted_index
        with open(inverted_bigram_index_json) as bjf:
            inverted_bigram_index = json.load(bjf)
        self.inverted_bigram_index = inverted_bigram_index
        self.stemmer = krovetz.PyKrovetzStemmer()
        self.result_dict = {}
        self.results = set()

    def handle_query(self, query):
       
        try:             
            self.results.clear()
            self.result_dict.clear()

            query_words_list = query.split()
            for q_word in query_words_list:
                if q_word in Query.STOPWORDS:
                    query_words_list.remove(q_word)
            
            if len(query_words_list) > 0:
                q_words = []
                for q in query_words_list:
                    q = q.lower()
                    strp_q = q.strip(Query.PUNCTUATION)
                    new_q = self.stemmer.stem(strp_q)
                    q_words.append(new_q)
                query = " ".join(q_words)
                
                
                if len(query_words_list) == 1: # searching single index
                    self.execute_query(query)
                    
                    # ranking results 
                    sorted_results = sorted(self.result_dict.items(), key = lambda item:item[1], reverse = True)            
                    self.getUrls(sorted_results)
                elif len(query_words_list) == 2: # searching bigram index
                    self.execute_bigram_query(query)

                    if len(self.results) == 0: # If unable to find in bigram find in regular index. (ex: anthony rachmat -> anthony)
                        for w in query_words_list:
                            self.execute_query(w) 
                    # ranking results
                    sorted_results = sorted(self.result_dict.items(), key = lambda item:item[1], reverse = True)
                    self.getUrls(sorted_results)

                else: # searching single index
                    for w in query_words_list:
                        self.execute_query(w)
                    sorted_results = sorted(self.result_dict.items(), key = lambda item:item[1], reverse = True)
                    self.getUrls(sorted_results)

            else:
                print("Query invalid. Only contained stop words.")
        except Exception as e:
            print(e)
            print("Error parsing query. Good bye.")

    def getUrls(self, result):
        for r in result:
            self.results.add(self.book_keeping[r[0]])
   
    def execute_query(self, query):
        tokens = self.find_all_tokens(query)
        
        for t in tokens:
            for docId, v in self.inverted_index[t].items(): 
                if docId not in self.result_dict.keys():
                    self.result_dict[docId] = v[1]
                else:
                    self.result_dict[docId] += v[1]
    
    def execute_bigram_query(self, query):
        tokens = self.find_all_bigram_tokens(query)

        for t in tokens:
            for docId, v in self.inverted_bigram_index[t].items():
                if docId not in self.result_dict.keys():
                    self.result_dict[docId] = v[1]
                else:
                    self.result_dict[docId] += v[1]
    
    def find_all_bigram_tokens(self, query):
        tokens = []
        for index in self.inverted_bigram_index.keys():
            if query in index:
                tokens.append(index)
        return tokens

    def find_all_tokens(self, query):
        tokens = []
        for index in self.inverted_index.keys():
            if query in index:
                tokens.append(index)
        return tokens

    def print_results(self, results):
            for r in results:
                print(r)
