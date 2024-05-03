from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)
from werkzeug.exceptions import abort

from music.auth import login_required
from music.db import get_db

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

bp = Blueprint('search', __name__)
Client_id = '02557908cc4a4a4db760d2506b87f315'
Client_secret = 'd1d2043cfb0c4876b8162845c4441362'


@bp.route('/search', methods=('GET', 'POST'))
@login_required
def song():
    if request.method == 'POST':

        title = request.form['title']
        artist = request.form['artist']

        error = None
        if not title:
            error = 'Title is required.'
        elif not artist:
            error = 'Artist is required.'
        if error is not None:
            flash(error)
        else:
            client_credentials_manager = SpotifyClientCredentials(
                client_id=Client_id, client_secret=Client_secret)
            sp = spotipy.Spotify(
                client_credentials_manager=client_credentials_manager)
            track_results = sp.search(
                q=f'track:{title} artist:{artist}', type='track', limit=50)['tracks']['items']
            return render_template('search/song.html', songs=track_results)

    return render_template('search/song.html', songs=[])


@bp.route('/search/playlist', methods=('GET', 'POST'))
@login_required
def search_playlists():
    if request.method == 'POST':

        spotify_username = request.form['username']

        error = None
        if not spotify_username:
            error = 'Username is required.'
        if error is not None:
            flash(error)
        else:
            client_credentials_manager = SpotifyClientCredentials(
                client_id=Client_id, client_secret=Client_secret)
            sp = spotipy.Spotify(
                client_credentials_manager=client_credentials_manager)
            try:
                user = sp.user(spotify_username)
                print(user)
                playlists = sp.user_playlists(spotify_username)
                return render_template('search/playlist.html', playlists=playlists['items'], user=user)
            except Exception as ex:
                print(ex)
                error = 'Username not found'
                flash(error)

    return render_template('search/playlist.html', playlists=[], user=None)
