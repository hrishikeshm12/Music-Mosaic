import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import json

import os
from dotenv import load_dotenv

load_dotenv()

#spotfy API credentials. 
client_id = os.environ.get('client_id')
client_secret = os.environ.get('client_secret')

# authenticate with Spotify API using client credentials
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def get_track_image(track_id):
    # get the track information
    track = sp.track(track_id)

    # get the album cover image
    image_url = track['album']['images'][0]['url']

    return image_url

def get_top_tracks():
  
    client_id = client_id
    client_secret =client_secret

    # Create a Spotify API client using the client credentials flow
    client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
                           
    playlist = sp.playlist('37i9dQZEVXbMDoHDwVN2tF')
    tracks = playlist['tracks']['items'][:30]  # Slice to get only the first 30 tracks

    # Extract the relevant data for each track
    results = []
    for i, track in enumerate(tracks):
        track_data = {}
        track_data['id'] = i
        track_data['name'] = track['track']['name']
        track_data['image'] = track['track']['album']['images'][0]['url']
        track_data['singer'] = track['track']['artists'][0]['name']
        track_data['album'] = track['track']['album']['name']
        track_data['popularity'] = track['track']['popularity']
        track_id = track['track']['id']
        track_data['audio'] = track['track']['preview_url']
        track_info = sp.track(track_id)
        track_data['total_views'] = track_info['popularity']
        #track_data['genre'] = sp.artist(track['track']['artists'][0]['id'])['genres'][0]
        results.append(track_data)
    #print(results)
    return json.dumps(results)
    


def get_top_artists():
    
    client_id = client_id
    client_secret =client_secret

    # Create a Spotify API client using the client credentials flow
    client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    # Get the top artists from Spotify
    results = sp.search(q='year:2022', type='artist', limit=30)
    top_artists = results['artists']['items']

    # Extract the relevant data for each artist
    data = []
    for artist in top_artists:
        artist_data = {}
        artist_data['name'] = artist['name']
        artist_data['image'] = artist['images'][0]['url'] if artist['images'] else None
        artist_data['followers'] = artist['followers']['total']
        artist_data['popularity'] = artist['popularity']

        # Get the top track for the artist
        top_track = sp.artist_top_tracks(artist['id'], country='US')['tracks'][0]
        artist_data['album'] = top_track['album']['name']
        artist_data['song'] = top_track['name']
        artist_data['views'] = top_track['popularity']
        
        data.append(artist_data)
       
    
    return json.dumps(data)


def get_new_songs():
    
    client_id = client_id
    client_secret =client_secret

    # Create a Spotify API client using the client credentials flow
    client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    
    # Get new releases from Spotify's "New Releases" section
    # Set the language parameter to 'en' for English songs
    new_releases = sp.new_releases(country='US', limit=30)

    # Extract the relevant data for each album
    results = []
    for album in new_releases['albums']['items']:
        album_data = {}
        album_data['name'] = album['name']
        album_data['image'] = album['images'][0]['url']
        album_data['artist'] = album['artists'][0]['name']
        album_data['release_date'] = album['release_date']
        album_data['total_tracks'] = album['total_tracks']
        results.append(album_data)
    #print(results)
    return json.dumps(results)


