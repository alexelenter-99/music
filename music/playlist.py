from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)
from werkzeug.exceptions import abort

from music.auth import login_required
from music.db import get_db

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

bp = Blueprint('playlist', __name__)
Client_id = '02557908cc4a4a4db760d2506b87f315'
Client_secret = 'd1d2043cfb0c4876b8162845c4441362'


@bp.route('/playlist/<playlist_id>', methods=('GET', 'POST'))
@login_required
def playlist(playlist_id):
    client_credentials_manager = SpotifyClientCredentials(
        client_id=Client_id, client_secret=Client_secret)
    sp = spotipy.Spotify(
        client_credentials_manager=client_credentials_manager)
    playlist = sp.playlist(playlist_id)
    songs = [t['track'] for t in playlist['tracks']['items']]
    print(songs[0])
    return render_template('playlist/index.html', songs=songs)
