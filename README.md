<div align="center">
<h1>µ - your personal music library</h1>
<br><img src="./.github/banner.png" height="220px"><br><br>
<p>
  μ (<code>mu</code>) is an opinionated MacOS and Linux music library management tool designed to be <b>backup friendly</b> and <b>programmable</b>. All music is stored in a hierarchical format, and the internal database is a simple SQLite file.</p>

<img src="./.github/screenshot.png" alt="Screenshot of muc" width="100%">

<p>
  µ comes with mµc (<code>muc</code>), a tui music player built for µ that focuses on speed and simplicity.
</p>
</div>


## Table of Contents

<!-- TOC -->

- [Table of Contents](#table-of-contents)
- [What is µ?](#what-is-%C2%B5)
- [What is mµc?](#what-is-m%C2%B5c)
- [Installation](#installation)
    - [File Structure](#file-structure)
- [Whats included](#whats-included)
- [µ Basic Commands](#%C2%B5-basic-commands)
    - [Importing from iTunes](#importing-from-itunes)
    - [Importing mp3 files](#importing-mp3-files)
    - [µ query syntax](#%C2%B5-query-syntax)
    - [Removing and favoriting tracks](#removing-and-favoriting-tracks)
    - [Listing and searching](#listing-and-searching)
    - [Playlists](#playlists)
- [mµc Basic Usage](#m%C2%B5c-basic-usage)
    - [Keybindings](#keybindings)
        - [Tab Navigation](#tab-navigation)
        - [Pane Navigation](#pane-navigation)
        - [Table Navigationn](#table-navigationn)
        - [Tracks Table Navigation](#tracks-table-navigation)
        - [Playback/Media Keys](#playbackmedia-keys)
        - [Playlist/Queue Table Navigation](#playlistqueue-table-navigation)

<!-- /TOC -->

## What is µ?
µ at its core is just a python library used to interface with a simple SQLite database file. It keeps track of what music you have in your library, where it is located, what playlists you have, etc. It was built from the ground up to allow other applications to interface with it. Even you, the reader, can programmatically search, import, and categorize music with µ. This is achieved through an easy to use python API and search query syntax.

**µ is not a player.** The only functionallity µ takes responsibility over is the management of your library and how you interface with it. This standardization will hopefully allow for other players to be created and given support. You can use µ entirely from the CLI by using the `mu` command. This includes functionality such as searching, importing, favoriting, and playlists.

## What is mµc?
mµc is a terminal music player. It will probably be where you spend most of your time using µ, and is currently the only supported client for µ. It is included by default when installing µ, and can be started with the `muc` command.

## Installation

µ is supported on MacOS, Linux, and Windows.

mµc is only supported on Macos and Linux. While mµc might work on windows, bugs are expected.

It is highly advised to use a terminal such as [kitty](https://github.com/kovidgoyal/kitty), [ghostty](https://github.com/ghostty-org/ghostty), [weztern](https://github.com/wezterm/wezterm), or [konsole](https://github.com/kde/konsole) if you plan on using mµc. These terminals work better with the [Textual](https://github.com/textualize/textual) framework mµc is based upon.

Before proceeding, ensure you have Python >=v3.12.13.

First, clone the repo.

```
git clone https://github.com/brodyking/mu.git
```

Then from within the repo, install the package with pip.

```bash
pip install .
```

To update µ later on, simply uninstall µ and then follow the installation steps above again.

```bash
pip uninstall mu
```

### File Structure

Upon running `mu` for the first time, or utilizing a library that interacts with µ, `~/Music/mu/` will be created.

```
.
├── albumart/ 
├── mu.db #
└── source/
```

- `albumart/` contains all albumart for all tracks. It does not contain duplicates, and it's location is stored in the database alongside each track.
- `source/` contains all the original mp3 files. 
- `mu.db` contains the SQLite database that stores track metadata, playlist data, etc.

The `~/Music/mu/` folder can be backed up and then restored to preserve your music library. Note that when the library is moved to a new location, track locations will need to be adjusted in the database.

## Whats included

The two basic CLI commands that µ come with are `mu` and `muc`.

- `mu` allows you to interact with µ through the CLI. Almost all operations that are supported by the api are supported through the CLI.
- `muc` starts the tui client for µ. It is currently the only way to interact with µ. Support for mobile/web is planned.

Chapter 2 will only discuss `mu`.

## µ Basic Commands

Upon running `mu` for the first time, an output similar to this will be shown.

```
Usage: mu [OPTIONS] COMMAND [ARGS]...

  your personal music library

Options:
  --install-completion  Install completion for the current shell.
  --show-completion     Show completion for the current shell, to copy it or
                        customize the installation.
  --help                Show this message and exit.

Commands:
  scan      refresh metadata (alias: s)
  version   get version (alias: v)
  itunes    import an itunes library xml (alias: it)
  list      list different parts of your library (alias: ls)
  playlist  modify playlists (alias: p)
  track     modify tracks (alias: t)

  created and maintained by brody king at https://github.com/brodyking/mu
```

Most of these commands are self-explanatory.

- **Scan** goes through all tracks in `~/Music/mu/source/`, and updates their metadata. 
- **Version** prints the current µ version.

### Importing from iTunes

To import an existing library from iTunes, use the `itunes` command, or its alias `it` to an XML export of your iTunes library.

This can be done by going to **File > Library > Export Library**

```bash
mu itunes ~/Desktop/Library.xml
```

### Importing mp3 files

To import new mp3 files to your library, use the `track` subparser (aliased
 as `t`), with the `import` command (aliased as `i`)

 ```bash
 # Full command
 mu track import ~/Desktop/Time.mp3

 # Same command, easier to type.
 mu t i ~/Desktop/Time.mp3
 ```

 This command can be used to import folders of music, or just individual mp3 files. All tracks imported are coppied into the `~/Music/mu/source/` folder.

### µ query syntax

The same `track` subparser mentioned above has other commands. Those being `remove` (alias `rm`) and `favorite` (alias `f`). But to use these commands, you must understand µ query syntax.

When selecting albums, tracks, playlists, etc, you have to query for them. This is done by matching a column with a value. It's easiest to just show a few examples.

If I want to find all the tracks by *Pink Floyd*, I can query by matching the artist column.

```
"artist=Pink Floyd"
```

The `=` operand looks for an exact match. If this is undesired, use the `:` operand.

```
"artist:Pink"
```
The query above would return tracks by *Pink Floyd*, alongside all other tracks with the artist containing *Pink*

And operationns are done with the `&` operand.

```
"artist=Pink Floyd&album=The Dark Side Of The Moon"
```
The query above would return only tracks by *Pink Floyd* in *The Dark Side Of The Moon*.

Or operations are done with the `+` operand.

```
"artist=Pink Floyd+artist=David Gilmour"
```

The above query would return all tracks by *Pink Floyd* and all tracks by *David Gilmour*.

### Removing and favoriting tracks

To favorite a track, use the `track` subparser with the `favorite` (alias `f`) and µ Query Syntax to select the song.

```
mu track favorite "id=1"
```

This favorites the track with the id == 1.

**Note: All tracks and playlists are given their own ID. Artists and Albums are not given IDs.**

To remove a track, use the same subparser with the `remove` command (alias `rm`)

```
mu track remove "id=1"
```

It may be important to note that removing a track doesn't delete it, it just gets removed from the database. Running a `scan` command will bring it back into the library, so make sure to delete its source file aswell.

### Listing and searching

The `list` (alias `ls`) subparser is used to list tracks, albums, artists, playlists, and playlists contents, alongside searching through them.

```
mu list tracks <query>
mu list albums <query>
mu list artists <query>
mu list playlists <query>
mu list playlist <query>
```

You can include a search query after these commands to filter through them. This is the most efficient way to search, as it is done at the SQL level.

```
mu list albums "artist:Pink Floyd"
```
The above query returns all albums by Pink Floyd.

**Note: Tracks, Albums, and Artists all query the `tracks` table. This means you can use all the same columns across different types.**

### Playlists

The `playlist` (alias `p`) subparser is used to create, modify, and delete playlists.

You can create a playlist with the `create` (alias `c`) command.

```
mu playlist create "Workout"
```

The above command will return a newly created, empty playlist. Each playlist has its own unique ID.

Most playlist commands are self-explanatory.

```
Commands:
  append  append track(s) into playlist(s) (alias: a)
  create  create a new playlist (alias: c)
  delete  delete a playlist (alias: d)
  insert  insert track(s) into playlist(s) at a specified position...
  remove  remove track(s) from playlist(s) (alias: rm)
```

## mµc Basic Usage

To get started using mµc, simply run `muc` in the terminal of your choosing. 

### Keybindings

mµc utilizes vim-style keybindings almost everywhere in the application.

#### Tab Navigation

You can just to any tab with the following keybindings.

| Key | Tab |
| --- | --- |
| `Q` | Queue |
| `F` | Favorites |
| `T` | Tracks |
| `A` | Albums |
| `R` | Artists |
| `P` | Playlists |
| `O` | Optionns |

You can also move to the next/previous tab with `H`/`L`.

#### Pane Navigation

In tabs such as `Playlists` or `Options`, you will be given multiple tables. You can change focus by using `ctrl+h` and `ctrl+l`.

#### Table Navigationn

Standard `j`/`k` keys for up and down are supported. To just to the top/bottom of the current table, just `J`/`K`.

If you are unable to see a rows full contents, you can press `Tab` to view a vertical table of the row.

To copy the contents of a row to your clipboard, press `y`.

If the table supports it, you can press `/` to enable the search field. 

**Note: Every table that supports searching supports µ query syntax.**

#### Tracks Table Navigation
The tracks table, used in `Favorites`, `Tracks` and `Playlists` allows for sorting and adding options.

Press `,` to open the sort popup.

Press `.` to open the add-to popup. From there, you can add a track to the queue or to a playlist.

#### Playback/Media Keys

To pause/play playback, use the spacebar. 

To go to the next/previous track, use `h`/`l`.

To increase/decrease volume, use `+`/`-`.

#### Playlist/Queue Table Navigation
In both the `Playlist` and `Queue`, you can remove tracks with the `d` key. 