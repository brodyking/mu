<h1 align="center">µ documentation</h1>
<p align="center">
  Welcome to the <b>µ documentation</b>! This is the best place to get started with µ and mµc.
</p>

<h2>Chapters 📁</h2>

- [1.0 - Installation](#10---installation)
  - [1.1 - File Structure](#11---file-structure)
- [2.0 - Basic Usage](#20---basic-usage)
  - [2.1 - Importing Music](#21---importing-music)
  - [2.2 - Listing Tracks, Albums, and Artists](#22---listing-tracks-albums-and-artists)
  - [2.2 - Searching tracks](#22---searching-tracks)
  - [2.3 Favoriting tracks](#23-favoriting-tracks)

## 1.0 - Installation

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

### 2.2 - Listing Tracks, Albums, and Artists 

Tracks, albums, and artists are all actions you can input into µ.

```
mu tracks # lists all tracks
mu albums # lists all albums
mu artists # lists all artists
```

`mu tracks` allows for the `-f` or `--favorited` flag, which only returns favorited tracks.

`mu artists` allows for the `-a` or `--albums` flag, which only returns album artists.

### 2.2 - Searching tracks

You can search your music by using the `mu search` action. Searching uses "prefixes", which tell µ which coloum you are searching. 

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

### 2.3 Favoriting tracks

To favorite track(s), use the same prefix convention while using the `favorite` action. This action toggles it's favorite status. It can be used on multiple tracks or a single track.

Say I'd like to favorite "Covet", 

```
mu favorite "title:Covet"
```
