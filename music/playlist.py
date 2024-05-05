from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)
from werkzeug.exceptions import abort

from music.auth import login_required
from music.db import get_db

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import datetime

bp = Blueprint('playlist', __name__)
Client_id = '02557908cc4a4a4db760d2506b87f315'
Client_secret = 'd1d2043cfb0c4876b8162845c4441362'

notify_after = 0


@bp.route('/playlist/<playlist_id>', methods=('GET', 'POST'))
@login_required
def playlist(playlist_id):
    client_credentials_manager = SpotifyClientCredentials(
        client_id=Client_id, client_secret=Client_secret)
    sp = spotipy.Spotify(
        client_credentials_manager=client_credentials_manager)
    playlist = sp.playlist(playlist_id)
    songs = [t['track'] for t in playlist['tracks']['items']]
    return render_template('playlist/index.html', songs=songs, songs_to_recover=[])


def add_songs_to_db_and_playlist(playlist_id):
    client_credentials_manager = SpotifyClientCredentials(
            client_id=Client_id, client_secret=Client_secret)
    sp = spotipy.Spotify(
        client_credentials_manager=client_credentials_manager)
    db = get_db()
    songs = sp.playlist_items(playlist_id)['items']
    for song in songs:
        track = song['track']
        exists = db.execute(
                    """SELECT * FROM songs where id=(?)""", (track['id'],)
        ).fetchone()
        if exists == None:
            artist = sp.artist(track['artists'][0]['id'])
            db.execute(
                """INSERT OR IGNORE INTO artists (id, name, spotify_url) VALUES (?,?,?)""", (
                    artist['id'], artist['name'], artist['external_urls']['spotify'],)
            )
            db.execute(
                """INSERT OR IGNORE INTO songs (id, name, artist_id, spotify_url) VALUES (?,?,?,?)""", (
                    track['id'], track['name'], track['artists'][0]['id'], track['external_urls']['spotify'],)
            )
            added_at = datetime.datetime.strptime(song['added_at'], "%Y-%m-%dT%H:%M:%SZ")
            db.execute(
                """INSERT OR IGNORE INTO playlists_songs (playlist_id, song_id, added_at) VALUES (?,?,?)""", (
                    playlist_id, track['id'], added_at,)
            )
    db.commit()

@bp.route('/playlist/track', methods=('GET', 'POST'))
@login_required
def add_playlist():
    username = request.args.get('username')
    playlist_id = request.args.get('playlist_id')
    spotify_url = request.args.get('spotify_url')
    db = get_db()
    playlist = db.execute(
        f"""SELECT * FROM playlists WHERE id = (?)""", (playlist_id,)
    ).fetchone()
    user_id = (db.execute(
        """SELECT * FROM users WHERE username = (?)""", (username,)
    ).fetchone())['id']
    if playlist is None:
        client_credentials_manager = SpotifyClientCredentials(
            client_id=Client_id, client_secret=Client_secret)
        sp = spotipy.Spotify(
            client_credentials_manager=client_credentials_manager)
        playlist = sp.playlist(playlist_id)
        db.execute(
            """INSERT INTO playlists (id, name, user_id, spotify_url) VALUES (?,?,?,?)""", (
                playlist_id, playlist['name'], user_id, spotify_url,)
        )
        db.commit()
    add_songs_to_db_and_playlist(playlist_id)
    exists = db.execute(
                """SELECT * FROM users_playlists where playlist_id = ? and user_id = ?""", (
                    playlist_id, user_id,)
        ).fetchall()
    if len(exists) > 0:
        error = "Playlist already tracked "
        flash(error)
        return redirect(url_for('search.search_playlists'))
    else:
        db.execute(
            """INSERT INTO users_playlists (user_id, playlist_id) VALUES (?,?)""", (
                user_id, playlist_id,)
        )
        db.commit()
        return redirect(url_for('home.index'))


@bp.route('/playlist/check_playlist', methods=('GET', 'POST'))
@login_required
def check_playlist():
    client_credentials_manager = SpotifyClientCredentials(
        client_id=Client_id, client_secret=Client_secret)
    sp = spotipy.Spotify(
        client_credentials_manager=client_credentials_manager)
    playlist_id = request.args.get('playlist_id')
    playlist = sp.playlist(playlist_id)
    songs_id = [t['track']['id'] for t in playlist['tracks']['items']]
    db = get_db()
    songs_in_db = db.execute(
        """SELECT ps.song_id, ps.added_at, s.name, a.name as artist_name FROM
        playlists_songs ps JOIN songs s ON ps.song_id=s.id JOIN artists a ON s.artist_id=a.id
        WHERE ps.playlist_id = (?)""", (playlist_id,)
    ).fetchall()
    songs_to_recover = []
    for song in songs_in_db:
        if song['song_id'] not in songs_id and (datetime.datetime.now() - song['added_at']).days > notify_after:
            songs_to_recover.append(song['song_id'])
    query = "SELECT s.name, a.name as artist_name, s.spotify_url FROM songs s JOIN artists a ON s.artist_id=a.id WHERE s.id IN ({seq})".format(
        seq=','.join(['?']*len(songs_to_recover)))
    songs_to_recover = db.execute(query, songs_to_recover).fetchall()
    query = "SELECT s.name, a.name as artist_name, s.spotify_url FROM songs s JOIN artists a ON s.artist_id=a.id WHERE s.id IN ({seq})".format(
        seq=','.join(['?']*len(songs_id)))
    songs = db.execute(query, songs_id).fetchall()
    add_songs_to_db_and_playlist(playlist_id)
    return render_template('playlist/index.html', songs=songs, songs_to_recover=songs_to_recover)
