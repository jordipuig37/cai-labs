#!/usr/bin/env python
"""
Simple module implementing LSH
"""

from __future__ import print_function, division
import numpy as np
import sys
import argparse
import time

__version__ = '0.2.1'
__author__ = 'marias@cs.upc.edu'


def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()

        print('%r (%r, %r) %2.2f sec' %
              (method.__name__, args, kw, te - ts))
        return result

    return timed


class LSH(object):
    """
    implements lsh for digits database in file 'images.npy'
    """

    def __init__(self, k, m, _user_ratings, _movie_ratings):
        """ k is nr. of bits to hash and m is reapeats """
        self._user_ratings = _user_ratings
        self._movie_ratings = _movie_ratings
        self.k, self.m = k, m
        self.hashes = [dict() for _ in range(self.m)]

        self.strlen = len(_user_ratings) * 10 # 10 possible ratings

        np.random.seed(123)
        self.hashbits = np.random.randint(self.strlen, size=(self.m, self.k))

        self.hash_all_movies()

        return

    def hash_all_movies(self):
        """ go through all movies and store them in hash table(s) """
        for movie in self._movie_ratings.keys():
            for i in range(self.m):
                str_hash = self.hashcode(movie, i)

                # store it into the dictionary..
                # (well, the index not the whole array!)
                if str_hash not in self.hashes[i]:
                    self.hashes[i][str_hash] = []
                self.hashes[i][str_hash].append(movie)
        return

    def hashcode(self, movie, i):
        """ get the i'th hash code of movie(0 <= i < m) """
        row = self.hashbits[i]
        str_hash = ""
        for x in row:
            hash_user = x // 10
            hash_rating = x % 10
            # Fill NA with 0
            if str(hash_user) not in self._movie_ratings[movie]:
                rating = 0
            else:
                rating = self._movie_ratings[movie][str(hash_user)]

            if hash_rating < int(2*rating):
                str_hash += '1'
            else:
                str_hash += '0'
        return str_hash

    def candidates(self, movie):
        """ given movie, return set of indices of matching candidates """
        res = set()
        for i in range(self.m):
            code = self.hashcode(movie, i)
            if code in self.hashes[i]:
                res.update(self.hashes[i][code])
        return res

    """Get nearest films using lsh over a list of movies"""
    def get_nearest_films(self, films):
        res = set()
        for film in films:
            for i in range(self.m):
                str_hash = self.hashcode(film, i)
                if str_hash in self.hashes[i]:
                    res.update(self.hashes[i][str_hash])
        return list(res)
