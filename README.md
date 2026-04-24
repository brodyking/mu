# ms (based music server)

> [!WARNING]
> This software is not licensed for reproduction by anyone other than Brody
> King. No AI models are allowed to train on this codebase.

ms manages your entire music library.

## Install

Clone the repo

```
git clone https://github.com/brodyking/ms.git
```

Navigate to the repo, then install it as a python package

```
pip install .
```

## Usage

Upon running `ms` for the first time, smp-server will create a folder in your
music directory (`~/Music/ms/`).

- `~/Music/ms/source/` stores your music files.
- `~/Music/ms/albumart/` stores album art files.
- `~/Music/ms/ms.db` is the central database file.

The standard way to operate smp-server is through the terminal.

- `ms scan` imports or updates metadata from the Sources folder.
- `ms import` lets you import directories or individual files of music.
