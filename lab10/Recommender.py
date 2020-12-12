import csv

"""implements a recommender system built from
   a movie list name
   a listing of userid+movieid+rating"""

class Recommender(object):

    #"""initializes a recommender from a movie file and a ratings file"""
    def __init__(self,movie_filename,rating_filename):

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
            if userid in self._user_ratings:
                self._user_ratings[userid].append((movieid,rating))
            else:
                self._user_ratings[userid] = [(movieid,rating)]

            if movieid in self._movie_ratings:
                self._movie_ratings[movieid].append((userid,rating))
            else:
                self._movie_ratings[movieid] = [(userid,rating)]
        f.close

    """returns a list of pairs (userid,rating) of users that
       have rated movie movieid"""
    def get_movie_ratings(self,movieid):
        if movieid in self._movie_ratings:
            return self._movie_ratings[movieid]
        return None

    """returns a list of pairs (movieid,rating) of movies
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

    """returns a list of at most k pairs (movieid,predicted_rating)
       adequate for a user whose rating list is rating_list"""
    def recommend_user_to_user(self,rating_list,k):
        pass
    
    """Gets rating given the user and the film"""    
    def _get_rating(userid, movieid):
        userid, movieid = str(userid), str(movieid)
        for x in _user_ratings[userid]:
            if x[0] == movieid:
                return float(x[1])
        return None

    """Similarity as Pearson Correlation of films"""
    def sim(id1, id2):    
        id1, id2 = str(id1), str(id2)
        
        # Users who have seen both films
        if (not(id1 in self._movie_ratings)) or \
           (not(id2 in self._movie_ratings)): # Non-existing index
            return 0
        users1 = set([x[0] for x in self._movie_ratings[id1]])
        users2 = set([x[0] for x in self._movie_ratings[id2]])
        users = list(users1 & users2)
        
        # Ratings of those users
        rating1 = np.array([self._get_rating(user, id1) for user in users])
        rating2 = np.array([self._get_rating(user, id2) for user in users])
        
        # Pearson correlation
        mean1 = np.mean([float(x[1]) for x in self._movie_ratings[id1]])
        mean2 = np.mean([float(x[1]) for x in self._movie_ratings[id2]])
        num = np.dot(rating1 - mean1, rating2 - mean2)

        sd1 = np.sqrt(np.sum((rating1 - mean1)**2))
        sd2 = np.sqrt(np.sum((rating2 - mean2)**2))
        den = sd1 * sd2
        
        # Special cases
        if (den == 0):
            return 0
        
        return num / den 

    """Gets prediction given user and film, based on item-to-item CF"""
    def pred(user, film):
        user, film = str(user), str(film)
        mean_rating = np.mean([float(x[1]) for x in self._movie_ratings[film]])
        films_user = [x[0] for x in self._user_ratings[user]]
        num, den = 0, 0
        for movie in films_user:
            s = self.sim(film, movie)
            r = self._get_rating(user, movie)
            mean_r = np.mean([float(x[1]) for x in self._movie_ratings[movie]])
            
            num += s * (r - mean_r)
            den += s
        return mean_rating + num / den   

    """returns a list of at most k pairs (movieid,predicted_rating)
       adequate for a user whose rating list is rating_list"""
    def recommend_item_to_item(self,rating_list,k):
        pass

def main():
    r = Recommender("movies.csv","ratings.csv")
    print(len(r.movieid_list())," movies with ratings from ",len(r.userid_list()),"different users")
    print("The name of movie 1 is: ",r.movie_name("1"))
    print("movie 1 was recommended by ",r.get_movie_ratings("1"))
    print("user 1 recommended movies ",r.get_user_ratings("1"))

main()
