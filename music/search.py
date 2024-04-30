from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from music.auth import login_required
from music.db import get_db

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

bp = Blueprint('search', __name__)
Client_id = '02557908cc4a4a4db760d2506b87f315'
Client_secret = 'd1d2043cfb0c4876b8162845c4441362'

@bp.route('/')
def index():
    db = get_db()
    cursor = db.execute('select * from songs')
    names = list(map(lambda x: x[0], cursor.description))
    print(names)

    # songs = db.execute(
    #     'SELECT s.id, s.name, s.artist_id, a.name'
    #     ' FROM songs s JOIN artists a ON songs.artist_id = a.id'
    # ).fetchall()
    songs = db.execute(
        'SELECT s.id, s.name '
        ' FROM songs s'
    ).fetchall()
    return render_template('search/index.html', songs=songs)

@bp.route('/search', methods=('GET', 'POST'))
@login_required
def song():
    if request.method == 'POST':
        title = request.form['title']
        artist = request.form['artist']

        client_credentials_manager = SpotifyClientCredentials(client_id=Client_id, client_secret=Client_secret)
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

        track_name = []
        track_id = []
        track_results = sp.search(q=f'track:{title} artist:{artist}', type='track', limit=50)
        for t in track_results['tracks']['items']:
            track_name.append(t['name'])
            track_id.append(t['id'])
        print(track_name)
        print(track_id)

        error = None

        if not title:
            error = 'Title is required.'
        elif not artist:
            error = 'Artist is required.'
        if error is not None:
            flash(error)
        else:
            return redirect(url_for('search.song'))

    return render_template('search/song.html')