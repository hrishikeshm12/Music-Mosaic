from flask import jsonify, request, session, redirect, flash
import random
import json



from pymongo import MongoClient

# create a client instance and connect to a MongoDB server
client2 = MongoClient('mongodb://localhost:27017/')
songdb = client2["song_recommendation"]
song_db = songdb["songs_data"]
song_user=songdb['user_song']
user_interaction=songdb["user_interaction"]

def homepage_render():

    records = song_db.aggregate([{'$sample': {'size': 50}}, {'$project': {'_id': 0, 'track_id': 1, 'track_name': 1,'track_artist': 1,'playlist_genre': 1}}])
    result_list = list(records)
    json_song = json.dumps(result_list)
    return json_song


def render_likes(track_id):

    document = song_user.find_one({'track_id': track_id})
    # Return the total likes for the track
    return document['total_likes']


def render_saves(track_id):

    document = song_user.find_one({'track_id': track_id})
    # Return the total likes for the track
    return document['total_saves']


def update_likes_count(track_id):

    document = song_user.find_one({'track_id': track_id})
    # Increment the like count and update the document in the collection
    song_user.update_one({'_id': document['_id']}, {'$inc': {'total_likes': 1}})
    return song_user.find_one({'track_id': track_id})['total_likes']


def update_saves_count(track_id):

    document = song_user.find_one({'track_id': track_id})
    # Increment the like count and update the document in the song_user
    song_user.update_one({'_id': document['_id']}, {'$inc': {'total_saves': 1}})
    return song_user.find_one({'track_id': track_id})['total_saves']

# update the data to individual users

def add_track_to_liked(track_id, user_id):

    
   
    # check if the track_id is already present in the liked array for the given user_id
    query = {"user_id": user_id, "liked": {"$in": [track_id]}}
    document = user_interaction.find_one(query)
    
    if document:
        # the track_id is already present in the liked array
        return 1
    else:
        # the track_id is not present in the liked array, add it
        result = user_interaction.update_one({"user_id": user_id},{"$addToSet": {"liked": track_id}} )
        if result.modified_count > 0:
            return 2  # track_id was added
        else:
            return 0  # some error occurred


def add_track_to_saved(track_id, user_id):

    # check if the track_id is already present in the saved array for the given user_id
    query = {"user_id": user_id, "saved": {"$in": [track_id]}}
    document = user_interaction.find_one(query)
    
    if document:
        # the track_id is already present in the saved array
        return 1
    else:
        # the track_id is not present in the saved array, add it
        result = user_interaction.update_one({"user_id": user_id},{"$addToSet": {"saved": track_id}} )
        if result.modified_count > 0:
            return 2  # track_id was added
        else:
            return 0  # some error occurred
    


# fetching liked and saved songs.


def render_liked_songs(user_id):
    # Connect to MongoDB and get the "users" and "songs" collections.
   
    
    # Find the user document with the given user_id and get their liked track IDs.
    user = user_interaction.find_one({"user_id": user_id})
    liked_tracks = user.get("liked", [])
    
    # Query the "songs" collection for the details of the liked songs.
    projection = {'_id': 0, 'track_id': 1, 'track_name': 1,'track_artist': 1,'playlist_genre': 1}
    liked_songs = list(song_db.find({"track_id": {"$in": liked_tracks}}, projection))

    # Remove duplicates
    liked_songs = list({song['track_id']: song for song in liked_songs}.values())

    result_list = list(liked_songs)
    json_song = json.dumps(result_list)
    # Return the list of liked songs
    return json_song 

def render_saved_songs(user_id):
    # Connect to MongoDB and get the "users" and "songs" collections.
   
    
    # Find the user document with the given user_id and get their saved track IDs.
    user = user_interaction.find_one({"user_id": user_id})
    saved_tracks = user.get("saved", [])
    
    # Query the "songs" collection for the details of the saved songs.
    projection = {'_id': 0, 'track_id': 1, 'track_name': 1,'track_artist': 1,'playlist_genre': 1}
    saved_songs = list(song_db.find({"track_id": {"$in": saved_tracks}}, projection))

    # Remove duplicates
    saved_songs = list({song['track_id']: song for song in saved_songs}.values())

    result_list = list(saved_songs)
    json_song = json.dumps(result_list)
    # Return the list of saved songs
    return json_song 



# Delete song from liked and saved tabs.
def delete_my_song(track_id,tab,user_id):

    document = user_interaction.find_one({'user_id': user_id})

    # Remove the track_id from the corresponding array
    if tab == 'liked':
        user_interaction.update_one({'user_id': user_id}, {'$pull': {'liked': track_id}})
    elif tab == 'saved':
        user_interaction.update_one({'user_id': user_id}, {'$pull': {'saved': track_id}})

    return 1

