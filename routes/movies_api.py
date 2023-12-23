"""The Endpoints to manage the movie recommendations"""
import os
from flask import request, Blueprint, make_response
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

MOVIES_API = Blueprint('request_api', __name__)


def get_blueprint():
    """Return the blueprint for the main app module"""
    return MOVIES_API


for dirname, _, filenames in os.walk('/kaggle/input'):
    for filename in filenames:
        print(os.path.join(dirname, filename))

df_movies = pd.read_csv("Datasets/TMDB/tmdb_5000_movies.csv")
df_credits = pd.read_csv("Datasets/TMDB/tmdb_5000_credits.csv")

tfidf = TfidfVectorizer(stop_words="english")
df_movies['overview'].fillna("", inplace=True)
tfidf_matrix = tfidf.fit_transform(df_movies['overview'])

cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

indices = pd.Series(df_movies.index, index=df_movies["original_title"]).drop_duplicates()


@MOVIES_API.route('/movies/list', methods=['GET'])
def get_list():
    args = request.args
    df_filtered = df_movies

    if args.get('greaterOrEq'):
        df_filtered = df_filtered.loc[df_filtered['vote_average'] >= args.get('greaterOrEq', default=0, type=float)]

    if args.get('lessOrEq'):
        df_filtered = df_filtered.loc[df_filtered['vote_average'] <= args.get('lessOrEq', default=10, type=float)]

    df_filtered = df_filtered[["original_title", "vote_average"]].head(args.get('limit', default=5, type=int))
    response = make_response(df_filtered.to_json(orient='records', indent=2))
    response.headers = {"content-type": ["application/json"]}
    return response


@MOVIES_API.route('/movies/info/<string:_title>', methods=['GET'])
def get_movie_info(_title):
    movie_info = df_movies.loc[df_movies['original_title'] == _title.title()]
    response = make_response(movie_info.head(1).to_json(orient='records', indent=2))
    response.headers = {"content-type": ["application/json"]}
    return response


@MOVIES_API.route('/movies/recommendation/<string:_title>', methods=['GET'])
def get_recommendation(_title):
    _limit = request.args.get("limit", default=5, type=int)
    idx = indices[_title.title()]
    sim_scores = enumerate(cosine_sim[idx])
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:_limit + 1]
    sim_indexes = [i[0] for i in sim_scores]
    return df_movies["original_title"].iloc[sim_indexes].tolist()
