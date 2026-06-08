<h1 align="center">µ documentation</h1>
<p align="center">
  Welcome to the <b>µ documentation</b>! This is the best place to get started with µ and mµc.
</p>

<h2>Chapters 📁</h2>

- [1.0 - Installation](#10---installation)
  - [1.1 - File Structure](#11---file-structure)
- [2.0 - Basic Usage](#20---basic-usage)
  - [2.1 - Importing Music](#21---importing-music)
  - [2.2 - Listing Tracks, Albums, Artists, Playlists, and Playlist tracks](#22---listing-tracks-albums-artists-playlists-and-playlist-tracks)
  - [2.3 - Searching tracks](#23---searching-tracks)
  - [2.4 - Favoriting tracks](#24---favoriting-tracks)
- [3.0 - Playlists](#30---playlists)
  - [3.1 - Creating and deleting playlists](#31---creating-and-deleting-playlists)
  - [3.2 - Appending, Inserting, and Removing tracks](#32---appending-inserting-and-removing-tracks)
    - [3.2.1 - Appending tracks](#321---appending-tracks)
    - [3.2.2 - Inserting tracks](#322---inserting-tracks)
    - [3.2.3 - Removing tracks](#323---removing-tracks)
  - [3.3 - Listing contents of playlists](#33---listing-contents-of-playlists)

## 1.0 - Installation

Before proceeding, ensure you have Python >=v3.12.13 and VLC downloaded and installed.

Currently, the only way to install µ is as a python package.

First, clone this repository somewhere where it can be left untouched. We recommend creating a folder in your home folder named `.mu` and cloning it there. This is done so you can update the software in the future.
```
mkdir ~/.mu/
cd ~/.mu/
git clone https://github.com/brodyking/mu.git
```

Once the repo is cloned, you can simply install it as a python package.
```
pip install -e .
```

If you wish to update the client, all you have todo is pull the repo.

```
git pull
```

### 1.1 - File Structure

Upon running `mu` for the first time, or utiliznig a library that interacts with µ, `~/Music/mu/` will be created.

```
.
├── albumart/ 
├── mu.db #
└── source/
````

- `albumart/` contains all albumart for all tracks. It does not contain duplicates, and it's location is stored in the database
- `source/` contains all the original mp3 files. 
- `mu.db` contains the SQLite database that stores track metadata and their source + album art locations.

The `~/Music/mu/` folder can be backed up and then restored to preserve your music library.

## 2.0 - Basic Usage

The two basic commands that µ comes with are `mu` and `muc`.

- `mu` allows you to interact with µ through the cli. Almost all operations that are supported by the database are supported through the CLI. 
- `muc` starts the tui client for µ. It is currently the only way to interact with µ. Support for mobile/web is planned.

Chapter 2 will only discuss `mu`. 

### 2.1 - Importing Music

First, navigate to a directory of music you would like to import. Then, you can simply import them with the `import` action.

```
mu import .
```

You can also input different directories, or individual mp3 files.

### 2.2 - Listing Tracks, Albums, Artists, Playlists, and Playlist tracks

By using the `list` action in µ, you can view all the albums, artists, tracks, and playlists in your library.

```
mu list albums # lists all albums
mu list artists # lists all artists
mu list tracks # lists all tracks
mu list playlists # lists all playlists
mu list playlist # lists playlist tracks
```

`mu list tracks` allows for the `-f` or `--favorited` flag, which only returns favorited tracks.

`mu list artists` allows for the `-a` or `--albums` flag, which only returns album artists.

### 2.3 - Searching tracks

You can search your music by using the `mu search` action. Searching uses "prefixes", which tell µ which coloum you are searching. The search algorithm only searches the `tracks` table in the database.

Here are all the prefixes available:
```python
prefixes = [
  "id",
  "favorite",
  "title",
  "artist",
  "album",
  "plays",
  "time",
  "dateadded",
  "tracknumber",
  "albumartist",
  "discnumber",
  "genre",
  "date",
  "filepath",
  "filename",
  "albumart",
]
```

When searching, you must specify the col, followed by a colon, with the term afterwords.

```
{prefix}:{term}
```

Lets say I want to find all tracks by Pink Floyd. Here is the command todo so.

```
mu search "artist:Pink Floyd"
```

All actions that involve selecting a song will use this prefix syntax.

### 2.4 - Favoriting tracks
To favorite track(s), use the same prefix convention while using the `favorite` action. This action toggles it's favorite status. It can be used on multiple tracks or a single track.

Say I'd like to favorite "Covet", 

```
mu favorite "title:Covet"
```


## 3.0 - Playlists
Playlists inside of µ are similar to most other platforms out there. The `playlist` action allows you to interact with them. The only real difference is you cannot have duplicate tracks in a playlist.

Similarly to tracks, all commands that are provided with `playlist` (except `create`) require them. The only available prefixes are `title:` and `id:`

### 3.1 - Creating and deleting playlists
To create a playlist, use the `create` argument.

```
mu playlist create "Gym" # Creates a new empty playlist called "Gym"
```

The create argument also accepts `-d` or `--description` flag, which allows you to add a description to your playlist.

To delete a playlist, use the `delete` argument.

```
mu playlist delete "title:Gym" # Deletes the "Gym playlist"
mu playlist delete "id:1" # Deletes whatever playlist has the ID 1
```

### 3.2 - Appending, Inserting, and Removing tracks
These operations leverage the use of track prefixes alongside playlist prefixes.

#### 3.2.1 - Appending tracks
To append a track to the end of a playlist, use the `append` argument.

```
mu playlist append "title:Gym" "title:Time" # Adds the track "Time" to the end of the "Gym" playlist.
```

#### 3.2.2 - Inserting tracks
To insert a track, its the same syntax but with the position as the final argument. Note that playlists list of tracks start a `0`, not at `1` like you might expect.

```
mu playlist insert "title:Gym" "title:Time" 3 # Inserts the track at the 3rd position
```

You can add multiple tracks aswell, by using the same prefixes supported by `search`.

#### 3.2.3 - Removing tracks

To delete track(s) from a playlist, use the `remove` argument.

```
mu playlist remove "title:Gym" "title:Time" # Removes "Time" from the "Gym" playlist
```

### 3.3 - Listing contents of playlists

To list the contents of a playlist, refer to the `list` action from earlier chapters. Simply use the same prefix system as before.

```
mu list playlist "title:Gym"
```
