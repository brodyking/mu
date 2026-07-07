<h1 align="center">µ  / known bugs</h1>
<p align="center">
    Before reporting bug(s) in µ/mµc, please ensure they are not on this list.
</p>
<p align="center">
    Quick links: <a href="./README.md">README.md</a> &middot; <a href="./DOCS.md">DOCS.md</a>
</p>

## Chapters 📁

- [Chapters 📁](#chapters-)
- [Contributing ✏️](#contributing-️)
- [Bugs (µ) 🪳](#bugs-µ-)
- [Bugs (mµc) 🪳](#bugs-mµc-)


## Contributing ✏️
To report bugs, feel free to open a issue or add directly to this list via a pull request. This software is in development, and bugs are to be expected. Please note that not everything on this list is of high priority, or will get fixed.

**This is not a feature request list.** 

## Bugs (µ) 🪳
N/A

## Bugs (mµc) 🪳
- [x] Favoriting does not update now-playing favorite icon
- [x] Favoriting a track does not update in playlist list
  - Occours only if a playlist is not yet loaded, or reloaded.
  - This is due to the fact that tracks are stored as objects, not ids, inside of playlists.
  - Planned fix is to only store ID's, and reference the track dict stored by the client.
- [x] Playlist list is not auto focused on app startup.
- [x] App crashes if skip is spammed
- [x] Clicking on album in now playing doesn't complete an actual search
- [ ] Clicking on favorite button in now playing doesn't favorite
