<h1 align="center">µ documentation</h1>
<p align="center">
  Welcome to the <b>µ documentation</b>! This is the best place to get started with µ and mµc.
</p>

<h2>Chapters 📁</h2>

- [1.0 - Installation](#10---installation)
- [1.1 - File Structure](#11---file-structure)

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

## 1.1 - File Structure

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