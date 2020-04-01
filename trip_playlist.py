import sys
import random
from secrets import API_KEY
import requests
import json
import spotipy
import spotipy.util as util
from secrets import client_secret, client_id, redirect_uri

# Gets username from CLI

if len(sys.argv) > 1:
    username = sys.argv[1]
else:
    print("Please provide username")
    print("usage: python3 trip_playlist.py [username]")
    sys.exit()


# Scope and token for spotipy requests

scope = 'playlist-modify-public user-library-read'
token = util.prompt_for_user_token(username, scope, client_id, client_secret, redirect_uri)


### Following funcs are used for spotipy

def get_playlist_id(results): # retrieves playlist id for newly created playlist
    for item in results['items']:
        playlist_name = item['name']
        playlist_id = item['id']
        if playlist_name == created_playlist_name:
            return playlist_id


def show_saved_tracks_uris(results, list): # Gets all users' saved tracks uris
    for item in results['items']:
        track = item['track']
        list.append(track['uri'])


def show_saved_tracks_times(results, list): # Gets individual track durations for all users' saved tracks
    for item in results['items']:
        track = item['track']
        list.append(round((track['duration_ms']) / 60000, 2))


def add_songs_to_new_playlist(times, ids, max): # Adds random songs from user's saved tracks to newly created playlist
    total = 0
    playlist_songs = []
    while total < max:
        song_index = random.randint(0, len(all_songs_times))
        total += times[song_index]
        playlist_songs.append(ids[song_index])
    print(total)
    return playlist_songs



# Asks user where they are and where they are going
current_location = input('What is your current location?: ')
print()
destination = input('Where are you going?: ')
print()

# Asks user mode of transportation
mode = input('Are you driving, walking, or bicycling?: ')
print()

# Sends request to Maps API, converts to python format. Gets duration in seconds and converts to minutes
gmaps_url = 'https://maps.googleapis.com/maps/api/directions/json?origin={}&destination={}&key={}&mode={}'.format((
    current_location.replace(" ", "+")),
    (destination.replace(" ", "+")), API_KEY, mode.lower())

json_obj = requests.get(gmaps_url)
results = json.loads(json_obj.text)

duration = results['routes'][0]['legs'][0]['duration']['value']
duration_in_minutes = round(int(duration) / 60, 2)

created_playlist_name = input('What do you want to name your playlist?: ')
created_playlist_id = ' '



# Creates playlist
if token:
    sp = spotipy.Spotify(auth=token)
    sp.trace = False
    createPlaylist = sp.user_playlist_create(username, created_playlist_name,
                                             description='%s to %s' % (current_location, destination))


else:
    print("Can't authenticate")
    sys.exit()


# Using function defined previously, retrieves created playlist id
if token:
    sp = spotipy.Spotify(auth=token)
    sp.trace = False
    userPlaylists = sp.current_user_playlists(limit=50)
    created_playlist_id = get_playlist_id(userPlaylists)


else:
    print("Can't authenticate")
    sys.exit()


# Gets all users' songs by uri and time, returns to separate lists
all_songs_uris = []
all_songs_times = []
if token:
    sp = spotipy.Spotify(auth=token)
    sp.trace = False
    results = sp.current_user_saved_tracks()
    show_saved_tracks_times(results, all_songs_times)
    show_saved_tracks_uris(results, all_songs_uris)
    while results['next']:
        results = sp.next(results)
        show_saved_tracks_uris(results, all_songs_uris)
        show_saved_tracks_times(results, all_songs_times)
else:
    print("Can't authenticate")
    sys.exit()


# Adds songs to created playlist
song_list = add_songs_to_new_playlist(all_songs_times, all_songs_uris, duration_in_minutes)

if token:
    sp = spotipy.Spotify(auth=token)
    sp.trace = False
    addSongs = sp.user_playlist_add_tracks(username, created_playlist_id, song_list)
    print()
    print('Playlist created!')
else:
    print("Can't authenticate")
    sys.exit()
