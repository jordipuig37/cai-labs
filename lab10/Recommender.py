import csv
import os
import numpy as np
from lsh import LSH
from heapq import heapify, heappush, heappop

from easyinput import read # to read from a file or terminal

"""implements a recommender system built from
   a movie list name
   a listing of userid+movieid+rating"""

class Recommender(object):

    #"""initializes a recommender from a movie file and a ratings file"""
    def __init__(self,movie_filename,rating_filename, k, m):

        # read movie file and create dictionary _movie_names
        self._movie_names = {}
        f = open(movie_filename,"r",encoding="utf8")
        reader = csv.reader(f)
        next(reader)  # skips header line
        for line in reader:
            movieid = line[0]
            moviename = line[1]
            # ignore line[2], genre
            self._movie_names[movieid] = moviename
        f.close()

        # read rating file and create _movie_ratings (ratings for a movie)
        # and _user_ratings (ratings by a user) dicts
        self._movie_ratings = {}
        self._user_ratings = {}
        f = open(rating_filename,"r",encoding="utf8")
        reader = csv.reader(f)
        next(reader)  # skips header line
        for line in reader:
            userid = line[0]
            movieid = line[1]
            rating = line[2]
            # ignore line[3], timestamp
            if userid not in self._user_ratings:
                self._user_ratings[userid] = {} # each user is a dict with movies and ratings
            self._user_ratings[userid][movieid] = float(rating)

            if movieid not in self._movie_ratings:
                self._movie_ratings[movieid] = {}
            self._movie_ratings[movieid][userid] = float(rating)
        f.close()

        self.me = LSH(k, m, self._user_ratings, self._movie_ratings)

    """returns a list of pairs (userid,rating) of users that
       have rated movie movieid"""
    def get_movie_ratings(self,movieid):
        if movieid in self._movie_ratings:
            return self._movie_ratings[movieid]
        return None

    """returns a dictionary of pairs (movieid,rating) of movies
       rated by user userid"""
    def get_user_ratings(self,userid):
        if userid in self._user_ratings:
            return self._user_ratings[userid]
        return None

    """returns the list of user id's in the dataset"""
    def userid_list(self):
        return self._user_ratings.keys()

    """returns the list of movie id's in the dataset"""
    def movieid_list(self):
        return self._movie_ratings.keys()

    """returns the name of movie with id movieid"""
    def movie_name(self,movieid):
        if movieid in self._movie_names:
            return self._movie_names[movieid]
        return None

    """Similarity as Pearson Correlation of users"""
    # given two users in dictionary format returns their similarity
    def user_sim(self, u1, u2):
        movies1 = set(u1.keys())
        movies2 = set(u2.keys())
        movies = list(movies1 & movies2)
        if len(movies) == 0:
            return 0
        # Ratings of those movies
        rating1 = np.array([float(u1[movie]) for movie in movies])
        rating2 = np.array([float(u2[movie]) for movie in movies])

        # Pearson correlation
        mean1 = np.mean(rating1)
        mean2 = np.mean(rating2)
        num = np.dot(rating1 - mean1, rating2 - mean2)

        sd1 = np.sqrt(np.sum((rating1 - mean1)**2))
        sd2 = np.sqrt(np.sum((rating2 - mean2)**2))
        den = sd1 * sd2

        # Special cases
        if (den == 0):
            return 0

        return num / den

    def sum_sims(self, ref_u, movie, users, factor):
        total = 0
        for user in users:
            d = self.user_sim(ref_u, self.get_user_ratings(user))
            r_b = np.mean(list(self.get_user_ratings(user).values()))
            if movie in self.get_user_ratings(user):
                rbs = self.get_user_ratings(user)[movie]
            else:
                rbs = 0 # what?
            total += d * (rbs - r_b)**factor
        return total

    def predict_user_to_user(self, ref_user, movie, users):
        s1 = self.sum_sims(ref_user, movie, users, 1)
        s2 = self.sum_sims(ref_user, movie, users, 0)
        mean_ref = np.mean(list(ref_user.values()))
        if s2 == 0:
            return mean_ref # o 0?
        return mean_ref + s1 / s2

    """ This function takes a list of tuples and returns an equivalent dictionary
        assuming no key is repeated"""
    def dictionarize(self, list_of_tuples):
        result = dict()
        for k, v in list_of_tuples:
            result[k] = v
        return result

    """ This function takes a dictionary of lists and returns a list of list of tuples
        where each pair is (move, mean(rating))"""
    def compute_list_means(self, lists):
        l = []
        for movie, list_of_ratings in lists.items():
            l.append((movie, np.mean(list_of_ratings)))
        return l

    """ returns all the ratings of all the users in users.
        also the result is a dictionary of lists of ratigns for movies
        (K,V) = ('movieid', [list_of_ratings]). """
    def get_ratings(self, users):
        ratings = dict()
        for user in users:
            for movie, r in self.get_user_ratings(user).items():
                if movie not in ratings:
                    ratings[movie] = []
                ratings[movie].append(float(r))
        return ratings

    """ Returns the list of k nearest users to the reference. """
    def search_kNN_users(self, reference, k):
        closest = []
        for userID, uRatings in self._user_ratings.items():
            d = self.user_sim(reference, uRatings)
            if len(closest) < k:
                closest.append((d, userID))
            elif len(closest) == k:
                closest.append((d, userID))
                heapify(closest)
            else:
                heappush(closest, (d,userID))
                heappop(closest)
        l = []
        for d, u in closest:
            l.append(u)
        return l

    def get_movies_from_users(self, users):
        s = set()
        for user in users:
            mov = set(self._user_ratings[user].keys())
            s = s | mov
        return list(s)

    """ . """
    def best_rated(self, ref_user, users, k):
        # for each user add the movie rating to dictionary a list
        predicted = []
        movies = self.get_movies_from_users(users)
        for movie in movies:
            predicted.append((movie, self.predict_user_to_user(ref_user, movie, users)))
        predicted.sort(key = lambda x: x[1])
        return predicted[0:k]

    """ returns a list of at most k pairs (movieid,predicted_rating)
       adequate for a user whose rating list is rating_list """
    def recommend_user_to_user(self, rating_list, k):
        # 1. kNN with Similarity
        c = 20 ### on definim aixo¿????
        ref = self.dictionarize(rating_list) # transform the rating_list into a dictionary
        users = self.search_kNN_users(ref, c) # a list of usersID
        # 2. best movies from 1.
        candidates = self.best_rated(ref, users, k)
        # 3. select k best movies not in rating_list
        response = []
        for movie, rating in candidates:
            if movie not in ref:
                response.append(movie)
        return response

    """Gets rating given the user and the film"""
    def _get_rating(userid, movieid):
        userid, movieid = str(userid), str(movieid)
        for x in _user_ratings[userid]:
            if x[0] == movieid:
                return float(x[1])
        return None

    """ Similarity as Pearson Correlation of films """
    def sim(self, id1, id2):
        id1, id2 = str(id1), str(id2)

        # Users who have seen both films
        if (not(id1 in self._movie_ratings)) or \
        (not(id2 in self._movie_ratings)): # Non-existing index
            return 0
        users1 = set(self._movie_ratings[id1].keys())
        users2 = set(self._movie_ratings[id2].keys())
        users = list(users1 & users2)
        if len(users) == 0:
            return 0
        # Ratings of those users
        rating1 = np.array([self._movie_ratings[id1][user] for user in users])
        rating2 = np.array([self._movie_ratings[id2][user] for user in users])

        # Pearson correlation
        mean1 = np.mean(list(self._movie_ratings[id1].values()))
        mean2 = np.mean(list(self._movie_ratings[id2].values()))
        num = np.dot(rating1 - mean1, rating2 - mean2)

        sd1 = np.sqrt(np.sum((rating1 - mean1)**2))
        sd2 = np.sqrt(np.sum((rating2 - mean2)**2))
        den = sd1 * sd2

        # Special cases
        if (den == 0):
            return 0

        return num / den

    """Gets prediction given user and film, based on item-to-item CF"""
    def pred(self, rating_list, film):
        film = str(film)
        # Shouldn't happend
        if film not in self._movie_ratings:
            print('Film not existing')
            return 0
        mean_rating = np.mean(list(self._movie_ratings[film].values()))
        num, den = 0, 0
        for x in rating_list:
            movie = x[0]
            s = abs(self.sim(film, movie))
            r = x[1] # user rating of movie
            mean_r = np.mean(list(self._movie_ratings[movie].values()))

            num += s * (r - mean_r)
            den += s
        # Special case
        if den == 0:
            return mean_rating
        return mean_rating + num / den

    """returns a list of at most k pairs (movieid,predicted_rating)
       adequate for a user whose rating list is rating_list"""
    def recommend_item_to_item(self,rating_list,k):
        films = set([x[0] for x in rating_list])
        nearest_films = self.me.get_nearest_films(films)
        recom = []
        for movie in nearest_films:
            if not(movie in films):
                recom.append((movie, self.pred(rating_list, movie)))
        recom.sort(key=lambda x : -x[1])
        return recom[:k]

def read_list():
    l = []
    a = read(str)
    b = read(float)
    while a is not None and b is not None:
        l.append((a, b))
        a = read(str)
        b = read(float)
    return l


def main():
    os.chdir('./ml-latest-small/')
    r = Recommender("movies.csv","ratings.csv", 20, 1)
    rating_list = read_list()
    print("user to user random recomendations", r.recommend_user_to_user(rating_list, 7))
    print("item to item random recomendations", r.recommend_item_to_item(rating_list, 7))


main()
