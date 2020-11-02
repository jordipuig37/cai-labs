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

from heapq import heapify, heappush, heappop
from easyinput import read

__author__ = 'jerry-master and jordipuig37'

### GLOBAL VARIABLES
K = 10 # the k-ths first documents are considered Relevant
NROUNDS = 5
R, r = 1000, 2 # maximum number of relevant terms
ALPHA = 1
BETA = 1

""" UTILITY FUNCTIONS """

# Returns the sum of two dics
def truncate(dic,R):
    cont = 0
    heap = []
    for t,w in dic.items():
        if (cont == R):
            heapify(heap)
        elif (cont < R):
            heap.append((w,t))
        else:
            heappush(heap, (w,t))
            heappop(heap)
        cont += 1

    res = dict()
    for w,t in heap:
        res[t] = w
    return res

def add(d1, d2):
    # More efficient if d1 < d2
    if (len(d1) > len(d2)):
        return add(d2, d1)

    result = d1
    for term, w in d2.items():
        if term in result:
            result[term] += w
        else:
            result[term] = w
    return result

# Returns the sum of all the items in dics
def add_all(dics):
    total = {}
    for d in dics:
        total = add(total, d)
        total = truncate(total, R)
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
        if '^' in word:
            word, weight = word.split('^')
            if '~' in weight:
                fuzzy, weight = weight.split('~')
                word = word + '~' + fuzzy
        dict_query[word] = float(weight)
    return dict_query

# Writes the weights from a dictionary into the query in stringformat
def set_weights(new_weights):
    query = []
    for term, weight in new_weights.items():
        s = term + "^" + str(weight)
        query.append(s)
    return query


""" MAIN FUNCTION """

# s: Connection to database
def rocchio(query, s, client, index):
    # Get K most relevant documents
    response = get_docs(query, s, K)
    # Convert them to tf-idf
    response = [truncate(to_dict_TFIDF(client, index, r.meta.id), R) for r in response]
    # Add them up, divide by total and multiply by beta
    if len(response) == 0:
        return query
    beta_term = add_all(response)
    beta_term = multiply_by(beta_term, BETA / len(response))

    # Get weights from query in dictionary format
    weights = get_weights(query)
    # Multiply the query by alpha and add everything
    alpha_term = multiply_by(weights, ALPHA)
    new_query = add_all([alpha_term, beta_term])
    new_query = truncate(new_query, r)

    # Put the weights back into string format
    return set_weights(new_query)

# s: Connection to database
# nhits: maximum number of documents to retrieve
def get_docs(query, s, nhits):
    q = Q('query_string',query=query[0])
    for i in range(1, len(query)):
        q &= Q('query_string',query=query[i])

    s = s.query(q)
    return s[0:nhits].execute()


def get_args_from_terminal():
    print("Enter values for parameters:")
    print("K: ", end="")
    k = read(int)
    print("NROUNDS: ", end="")
    n = read(int)
    print("R: ", end="")
    R = read(int)
    print("alpha: ", end="")
    a = read(int)
    print("beta: ", end="")
    b = read(int)
    return k, n, R, a, b


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--index', default=None, help='Index to search')
    parser.add_argument('--nhits', default=10, type=int, help='Number of hits to return')
    parser.add_argument('--query', default=None, nargs=argparse.REMAINDER, help='List of words to search')

    args = parser.parse_args()

    K, NROUNDS, R, A, B = get_args_from_terminal()
    index = args.index
    query = args.query
    print(query)
    nhits = args.nhits

    try:
        client = Elasticsearch()
        s = Search(using=client, index=index)

        if query is not None:

            # Update query multiple times
            for _ in range(NROUNDS):
                query = rocchio(query, s, client, index)

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
