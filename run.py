from flask import flash, render_template, redirect, request, get_flashed_messages, jsonify, session
from app import app, login_required
from app.user.routes import *
from app.user.fetch import *
from app.spotifyapi.api import *
from app.user.recommend import *
import json
from pymongo import MongoClient


# Set up MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['song_recommendation']
songs = db['songs_data']


# main landing page.

@app.route('/')
def home():
  return render_template('index.html')

@app.route('/login')
def login_page():
  return render_template('loginpage.html')


@app.route('/register/')
def register():
  return render_template('signup.html')

# rendering dasboard page.

@app.route('/dashboard/')
@login_required
def dashboard():
  return render_template('dashboard.html')

# rendering the explore page.
@app.route('/dashboard/explore')
@login_required
def explore():
  top_tracks =  json.loads(get_top_tracks())
  top_artists =  json.loads(get_top_artists())
  new_releases =  json.loads(get_new_songs())

  return render_template('explore.html',new_releases=new_releases,top_artists=top_artists,top_tracks=top_tracks)

# rendering the home page section

@app.route('/dashboard/home')
@login_required
def homepage():
  home_songs=json.loads(homepage_render())

  for track in home_songs:
        track_id = track['track_id']
        total_likes = render_likes(track_id)
        total_saves = render_saves(track_id)
        image_url = get_track_image(track_id)
        track['total_likes']=total_likes
        track['total_saves']=total_saves
        track['image_url'] = image_url
        

  return render_template('homepage.html',home_songs=home_songs)

# updating the likes route.

@app.route('/dashboard/update_likes', methods=['POST'])
@login_required
def update_likes():
  track_id = request.form['track_id']
  user_id = request.form.get('user_id')
  result = add_track_to_liked(track_id, user_id)
  total_likes = update_likes_count(track_id)
  message = ""

  if result == 1:
      
      message = "Song is already liked"
  elif result == 2:
      
      message = "Song added to liked songs"
    
  response = { 'likes': total_likes, 'message': message }

  return jsonify(response)

#updating the saves route.

@app.route('/dashboard/update_saves', methods=['POST'])
@login_required
def update_saves():
  track_id = request.form['track_id']
  user_id = request.form.get('user_id')
  result = add_track_to_saved(track_id, user_id)
  total_saves = update_saves_count(track_id)
  message = ""

  if result == 1:
      
      message = "Song is already saved"
  elif result == 2:
      
      message = "Song added to saved songs"
    
  response = { 'saves': total_saves, 'message': message }

  return jsonify(response)



#rendering the my songs section

@app.route('/dashboard/mysongs')
@login_required
def mysongs():

  liked_songs=json.loads(render_liked_songs(session['user']['_id']))
  saved_songs=json.loads(render_saved_songs(session['user']['_id']))
  for track in liked_songs:
        track_id = track['track_id']
        image_url = get_track_image(track_id)
        track['image_url'] = image_url
        
  for track in saved_songs:
        track_id = track['track_id']
        image_url = get_track_image(track_id)
        track['image_url'] = image_url
        
  return render_template('mysongs.html', liked_songs=liked_songs, saved_songs=saved_songs)

#rendering the recommendation component

@app.route('/dashboard/recommendation')
@login_required
def recommend():

  user_id = session['user']['_id']
  songs=json.loads(recommend_songs(user_id,20))
  for track in songs:
    track_id = track['track_id']
    image_url = get_track_image(track_id)
    track['image_url'] = image_url
     
  return render_template('recommendation.html',songs=songs)

#rendering the search component. 

@app.route('/dashboard/search', methods=['GET'])
@login_required
def search_songs():
    query = request.args.get('q')
    if not isinstance(query, str):
        return jsonify([])

    search_results = songs.find({
        '$or': [
            {'track_name': {'$regex': query, '$options': 'i'}},
            {'track_artist': {'$regex': query, '$options': 'i'}},
            {'album_name': {'$regex': query, '$options': 'i'}}
        ]
    })

    response = []
    for song in search_results:
        track_id = song['track_id']
        image_url = get_track_image(track_id)
        result = {
            'track_id': track_id,
            'track_name': song['track_name'], 
            'track_artist': song['track_artist'], 
            'album_name': song['album_name'],
            'image_url': image_url
        }
        response.append(result)
    
    # Remove duplicates by converting dicts to tuples
    seen = set()
    response = [tuple(d.items()) for d in response]
    response = [x for x in response if not (x in seen or seen.add(x))]
    response = [dict(t) for t in response]

    return jsonify(response)


@app.route('/dashboard/searchpage')
@login_required
def search_page():
    return render_template('search_page.html')


@app.route('/dashboard/delete_song', methods=['POST'])
@login_required
def delete_song():
   track_id = request.json['track_id']
   tab = request.json['tab']
   user_id = session['user']['_id']
   val = delete_my_song(track_id, tab, user_id)
   if val == 1:
      print("Song deleted successfully")
      return "Success"
   else:
      return "Error"


if __name__ == '__main__':
  app.run(debug=True)


