from flask import jsonify, request, session, redirect, flash
import random
import json
import csv
from pymongo import MongoClient

# create a client instance and connect to a MongoDB server
client2 = MongoClient('mongodb://localhost:27017/')
db = client2["song_recommendation"]

# Specify the collections

song_col = db["songs_data"]
user_int_col = db["user_interaction"]
user_song_col = db["user_song"]
song_index = db["song_index"]
song_sim = db["song_sim"]

weights = {
    "total_likes": 0.5,
    "total_saves": 0.3,
    "avg_rating": 0.2
}


def get_similar_songs(song_id, n):
    similar_songs = []
    # Find the document with the given song_id
    document = song_sim.find_one({"song_id": song_id})

    if document:
        # Add the first n song_ids to the list
        for sim_song in document["sim_songs"][:n]:
            similar_songs.append(sim_song)
    return similar_songs


## Calculates the weighted average rating of a song based on its attributes and weights

def get_weighted_avg_rating(song, weights):
    weighted_avg_rating = (song["total_likes"] * weights["total_likes"] + song["total_saves"] * weights["total_saves"] +
                           song["avg_rating"] * weights["avg_rating"]) / (
                                      weights["total_likes"] + weights["total_saves"] + weights["avg_rating"])
    return weighted_avg_rating


def recommend_songs(user_id, num_recommendations):
    # Retrieve user's liked and saved songs from the database
    user_interaction = user_int_col.find_one({"user_id": user_id})
    liked_songs = user_interaction.get("liked", [])
    saved_songs = user_interaction.get("saved", [])

    # Calculate weights for liked and saved songs based on their count in the database
    liked_songs_count = len(user_interaction.get("liked", []))
    saved_songs_count = len(user_interaction.get("saved", []))
    total_songs_count = liked_songs_count + saved_songs_count
    liked_songs_weight = liked_songs_count / total_songs_count
    saved_songs_weight = saved_songs_count / total_songs_count

    # Rank the liked and saved songs based on their attributes
    ranked_songs = []
    for song_id in liked_songs + saved_songs:
        song = user_song_col.find_one({"track_id": song_id})
        song["weighted_avg_rating"] = get_weighted_avg_rating(song, weights)
        song["total_weight"] = song["total_likes"] * weights["total_likes"] * liked_songs_weight + song["total_saves"] * \
                               weights["total_saves"] * saved_songs_weight + song["weighted_avg_rating"] * weights[
                                   "avg_rating"]
        ranked_songs.append({"track_id": song["track_id"], "total_weight": song["total_weight"]})

    # Sort the songs by total weight in descending order
    ranked_songs = sorted(ranked_songs, key=lambda x: x["total_weight"], reverse=True)

    sorted_track_ids = [song["track_id"] for song in ranked_songs]

    

    # get the indices of the top K most similar songs to the given track_id

    top_track_indexes = []

    for track_id in sorted_track_ids:
        song = song_index.find_one({"track_id": track_id})
        top_track_indexes.append(song["index"])

    # Recommend songs based on user's interaction history and similarity scores
    recommended_songs = set()

    rec_song_indexes = []
    for i, song in enumerate(top_track_indexes[:num_recommendations]):
            if i < 4:
                num_similar_songs = round(num_recommendations * 0.75)
            else:
                num_similar_songs = round(num_recommendations * 0.25)

            similar_songs_indexes = get_similar_songs(song, num_similar_songs)
            rec_song_indexes.extend(similar_songs_indexes)
    
    

    random.shuffle(rec_song_indexes)
    similar_songs = rec_song_indexes[:20]

    for index in similar_songs:

        song = song_index.find_one({"index": index})
        if (song):
            recommended_songs.add(song["track_id"])

    recommended_songs_list = list(recommended_songs)
    records = song_col.find({'track_id': {'$in': recommended_songs_list}},
                            {'track_id': 1, 'track_name': 1, 'track_artist': 1, 'playlist_genre': 1,
                             'track_album_release_date': 1, '_id': 0}).limit(30)
    
    result_dict = {}
    for record in records:
        
        if record['track_id'] not in result_dict:
            result_dict[record['track_id']] = record
            if len(result_dict) == 20:
                break
    
    result_list = list(result_dict.values())

    json_song = json.dumps(result_list)

    return json_song


