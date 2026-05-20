# ms (based music server)

ms is a macos and linux music library management tool and music player. It can
function both from the cli and a gui interface. it is designed to be portable (a
single executable) and backup friendly. All music is stored in a hierarchical
format, and the internal database is a simple sqlite file.

<!--toc:start-->

- [ms (based music server)](#ms-based-music-server)
  - [Install](#install)
    - [Step 1: Download Python and VLC](#step-1-download-python-and-vlc)
    - [Step 2: Download the source code](#step-2-download-the-source-code)
    - [Step 3: Install as python package](#step-3-install-as-python-package)
  - [Usage](#usage)

<!--toc:end-->

## Install

### Step 1: Download Python and VLC

Please ensure you have python version 3.12.13 or newer downloaded, alongside
pip. You must also have VLC downloaded for the client to play back music.

### Step 2: Download the source code

First, clone the repo

```
git clone https://github.com/brodyking/ms.git
```

### Step 3: Install as python package

Navigate to the repo, then install it as a python package

```
pip install .
```

## Usage

Upon running `ms` for the first time, ms will create a folder in your music
directory (`~/Music/ms/`).

- `~/Music/ms/source/` stores your music files.
- `~/Music/ms/albumart/` stores album art files.
- `~/Music/ms/ms.db` is the central database file.

The standard way to operate ms is through the terminal. To learn more about the
commands and use of each command, run `-h` after each command.
