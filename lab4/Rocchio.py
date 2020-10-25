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

__author__ = 'jerry-master and jordipuig37'

### GLOBAL VARIABLES
K = 10 # the k-ths first documents are considered Relevant (k = R)
NROUNDS = 10
R = 100 # maximum number of relevant documents
ALPHA = 1
BETA = 1
"""
def split_word_weight(w):
    i = 0
    for l in w:
        if l == "^":
            return w[0:i], w[i+1:-1] # returns the real word and its weight (assuming w = real_word^weight)
        else:
            i += 1

# specific function to merge dictionaries using Rocchio's law
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
"""

""" UTILITY FUNCTIONS """

# Returns the sum of two dics
def add(d1, d2):
    return {}

# Returns the sum of all the items in dics
def add_all(dics):
    total = {}
    for d in dics:
        total = add(total, d)
    return total

# Returns the multiplication of dic by value
def multiply_by(dic, value):
    for term, weight in dic.items():
        dic[term] = weight * value
    return dic

# Returns the weights from a list of string in dic format
def get_weights(query):
    dict_query = dict()
    for word in query:
        weight = 1
        if "^" in word:
            word, weight = split_word(word)
        dict_query[word] = weight
    return dict_query

# Writes the weights into the query
def set_weights(query, new_weights):
    return query


""" MAIN FUNCTION """

# s: Connection to database
def rocchio(query, s, client, index):
    # Get K most relevant documents
    response = get_docs(query, s, K)
    # Convert them to tf-idf
    response = [toTFIDF(client, index, r.meta.id) for r in response]
    # Add them up, divide by total and multiply by beta
    beta_term = add_all(response)
    beta_term = multiply_by(beta_term, BETA / len(response))

    # Get weights from query in dictionary format
    weights = get_weights(query)
    # Multiply the query by alpha and add everything
    alpha_term = multiply_by(weights, ALPHA)
    new_weights = add_all([alpha_term, beta_term])

    # Put the weights back into string format
    return set_weights(query, new_weights)

    """
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
    """

# s: Connection to database
# nhits: maximum number of documents to retrieve
def get_docs(query, s, nhits):
    q = Q('query_string',query=query[0])
    for i in range(1, len(query)):
        q &= Q('query_string',query=query[i])

    s = s.query(q)
    return s[0:nhits].execute()


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

            # Update query multiple times
            for _ in NROUNDS:
                query = rocchio(query, s)

            # Finally make the query
            response = get_docs(query, s, nhits)

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
