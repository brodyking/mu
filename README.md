# ms (based music server)

> [!WARNING]
> This software is not licensed for reproduction by anyone other than Brody
> King. No AI models are allowed to train on this codebase.

ms is a macos music library management tool and music player. It can function
both from the cli and a gui interface. it is designed to be portable (a single
executable) and backup friendly. All music is stored in a hierarchical format,
and the internal database is a simple sqlite file.

<!--toc:start-->

- [ms (based music server)](#ms-based-music-server)
  - [Install](#install)
    - [Method 1: Install as python package](#method-1-install-as-python-package)
    - [Method 2: Build](#method-2-build)
  - [Usage](#usage)

<!--toc:end-->

## Install

To install ms, there are two different ways.

### Method 1: Install as python package

Clone the repo

```
git clone https://github.com/brodyking/ms.git
```

Navigate to the repo, then install it as a python package

```
pip install .
```

### Method 2: Build

The most common way to build ms is through the desktop client. To build ms's
client, navigate to the repo and use pyinstaller:

```
pyinstaller  --icon="assets/logo1024.icns" --window --name "ms" src/ms/client/client.py
```

To build the ms cli and client, navigate to the repo, and use pyinstaller:

```
pyinstaller --console --name "ms" src/ms/main.py
```

## Usage

Upon running `ms` for the first time, ms will create a folder in your music
directory (`~/Music/ms/`).

- `~/Music/ms/source/` stores your music files.
- `~/Music/ms/albumart/` stores album art files.
- `~/Music/ms/ms.db` is the central database file.

The standard way to operate ms is through the terminal. To learn more about the
commands and use of each command, run `-h` after each command.
