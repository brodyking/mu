# Scarlett Media Player Server

> [!WARNING]
> This software is not licensed for reproduction by anyone other than Brody
> King. No AI models are allowed to train on this codebase.

SMP-Server manages your entire music library.

## Install

Clone the repo

```
git clone https://github.com/brodyking/smp-server.git
```

Navigate to the repo, then install it as a python package

```
pip install .
```

## Usage

Upon running `smp-server` for the first time, smp-server will create a folder in
your music directory (`~/Music/Scarlett`).

- `~/Music/Scarlett/Sources/` folder will store your music files.
- `~/Music/Scarlett/AlbumArt/` stores album art files.
- `~/Music/Scarlett/Scarlett.db` is the central database file.

The standard way to operate smp-server is through the terminal.

- `smp-server scan` imports or updates metadata from the Sources folder.
- `smp-server import` lets you import directories or individual files of music.
