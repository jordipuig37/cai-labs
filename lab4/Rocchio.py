"""
.. module:: SearchIndexWeight

SearchIndex
*************

:Description: SearchIndexWeight

    Performs a AND query for a list of words (--query) in the documents of an index (--index)
    You can use word^number to change the importance of a word in the match

    --nhits changes the number of documents to retrieve

:Authors: jerry-master and jordipiug37


:Version:

:Created on: 04/07/2017 10:56

"""
from __future__ import print_function
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError

import argparse

from elasticsearch_dsl import Search
from elasticsearch_dsl.query import Q

from TFIDFViewer import to_dict_TFIDF

__author__ = 'jerry-master and jordipiug37'

### Global variable k and n
k = 10 # the k-ths first documents are considered Relevant (k = R)
n = 10
alpha = 1
beta = 1

def split_word_weight(w):
    i = 0
    for l in w:
        if l == "^":
            return w[0:i], w[i+1:-1] # returns the real word and its weight (assuming w = real_word^weight)
        else:
            i += 1

# specific function to merge dictionarys using Rocchino's law
def merge_dicts(dict_a, a, dict_b, b, k):
    result = dict()
    for term, w in dict_a.items():
        new_weight = a * w
        result[term] = new_weight
    
    for term, w in dict_b.items():
        new_weight = b * w / k
        if term in result:
            result[term] += new_weight
        else:
            result[term] = new_weight

    return result


def rocchio(query, response, index):
    # convert the query list of strings to a dictionary (?)
    dict_query = dict()
    for word in query:
        weight = 1
        if "^" in word:
            word, weight = split_word(word)
        dict_query[word] = weight

    # compute the TF-IDF for each document in response[0:k]
    # and merge with the dict_query
    # client = Elasticsearch()
    for file in response[0:k]:
        doc = toTFIDF(client, index, file)
        dict_query = merge_dicts(dict_query, alpha, doc, beta, k)

    return dict_query



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--index', default=None, help='Index to search')
    parser.add_argument('--nhits', default=10, type=int, help='Number of hits to return')
    parser.add_argument('--query', default=None, nargs=argparse.REMAINDER, help='List of words to search')

    args = parser.parse_args()

    index = args.index
    query = args.query
    print(query)
    nhits = args.nhits

    try:
        client = Elasticsearch()
        s = Search(using=client, index=index)

        if query is not None:
            for i in range(n):
                q = Q('query_string',query=query[0])
                for i in range(1, len(query)):
                    q &= Q('query_string',query=query[i])

                s = s.query(q)
                response = s[0:nhits].execute()

                query = rocchio(query, response, index)

            for r in response:  # only returns a specific number of results
                print(f'ID= {r.meta.id} SCORE={r.meta.score}')
                print(f'PATH= {r.path}')
                print(f'TEXT: {r.text[:50]}')
                print('-----------------------------------------------------------------')

        else:
            print('No query parameters passed')

        print (f"{response.hits.total['value']} Documents")

    except NotFoundError:
        print(f'Index {index} does not exists')
