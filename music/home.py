from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)
from werkzeug.exceptions import abort

from music.auth import login_required
from music.db import get_db

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

bp = Blueprint('home', __name__)
Client_id = '02557908cc4a4a4db760d2506b87f315'
Client_secret = 'd1d2043cfb0c4876b8162845c4441362'

@bp.route('/')
def index():
    user_id = session.get('user_id')
    if user_id != None:
        db = get_db()
        print(user_id)
        playlists = db.execute(
            f"""SELECT p.name, p.id 
                FROM
                playlists p 
                JOIN 
                users_playlists up ON p.id=up.playlist_id 
                WHERE up.user_id = {user_id}"""
        ).fetchall()
        print(playlists)
        return render_template('home/index.html', playlists=playlists) 
    return redirect(url_for('auth.login'))
