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

```
pip install .
```

To update µ later on, simply uninstall µ and then follow the installation steps above again.

```
pip uninstall mu
```

### 1.1 - File Structure

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

## 1.2 - Whats included

The two basic CLI commands that µ come with are `mu` and `muc`.

- `mu` allows you to interact with µ through the CLI. Almost all operations that are supported by the api are supported through the CLI.
- `muc` starts the tui client for µ. It is currently the only way to interact with µ. Support for mobile/web is planned.

Chapter 2 will only discuss `mu`.

## 2.0 - µ Basic Commands

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

## 2.1 - Importing from iTunes

To import an existing library from iTunes, use the `itunes` command, or its alias `it` to an XML export of your iTunes library.

This can be done by going to **File > Library > Export Library**

```
mu itunes ~/Desktop/Library.xml
```

## 2.2 Track commands