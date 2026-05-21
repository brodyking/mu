# μ - your personal music library

μ (mu) is a macos and linux music library management tool and music player. It
can function both from the cli and a tui interface. Mu is designed to be
portable (a single executable) and backup friendly. All music is stored in a
hierarchical format, and the internal database is a simple sqlite file.

<!--toc:start-->

- [μ - your personal music library](#μ-your-personal-music-library)
  - [Install](#install)
    - [Step 1: Download Python and VLC](#step-1-download-python-and-vlc)
    - [Step 2: Download the source code](#step-2-download-the-source-code)
    - [Step 3: Install as python package](#step-3-install-as-python-package)
  - [Usage](#usage)

<!--toc:end-->

## Install

### Step 1: Download Python and VLC

Please ensure you have python version 3.12.13 or newer downloaded, alongside
pip. You must also have VLC downloaded for the client to play music.

### Step 2: Download the source code

First, clone the repo

```
git clone https://github.com/brodyking/mu.git
```

### Step 3: Install as python package

Navigate to the repo, then install it as a python package

```
pip install .
```

## Usage

Upon running `mu` for the first time, ms will create a folder in your music
directory (`~/Music/mu/`).

- `~/Music/mu/source/` stores your music files.
- `~/Music/mu/albumart/` stores album art files.
- `~/Music/mu/ms.db` is the central database file.

The standard way to operate ms is through the terminal. To learn more about the
commands and use of each command, run `-h` after each command.
