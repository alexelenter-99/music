DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS songs;
DROP TABLE IF EXISTS artists;
DROP TABLE IF EXISTS playlists;
DROP TABLE IF EXISTS users_playlists;
DROP TABLE IF EXISTS playlists_songs;


CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE artists (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  spotify_url TEXT
);

CREATE TABLE songs (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  artist_id INTEGER NOT NULL,
  spotify_url TEXT,
  FOREIGN KEY (artist_id) REFERENCES artists (id)
);

CREATE TABLE playlists (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  user_id INTEGER NOT NULL,
  spotify_url TEXT,
  FOREIGN KEY (user_id) REFERENCES users (id)
);

CREATE TABLE users_playlists (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  playlist_id INTEGER NOT NULL,
  FOREIGN KEY (user_id) REFERENCES users (id),
  FOREIGN KEY (playlist_id) REFERENCES playlists (id)
);

CREATE TABLE playlists_songs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  playlists_id INTEGER NOT NULL,
  song_id INTEGER NOT NULL,
  FOREIGN KEY (playlists_id) REFERENCES playlists (id),
  FOREIGN KEY (song_id) REFERENCES songs (id)
);