/*    _
 | | | | mu
 | |_| | (c) 2026 all rights reserved
 | ._,_| https://github.com/brodyking/mu
 |_|
*/

// Gets tracks
const getTracks = async (q) => {
  if (q == undefined) { q = "" }
  if (q.length !== 0 && q.indexOf("%3A") == -1 && q.indexOf("%3D") == -1) {
    q = `artist:${q},albumartist:${q},album:${q},title:${q}`
  }
  try {
    const response = await fetch(`/api/tracks?q=${q}`)
    const data = await response.json()
    return data;
  } catch {
    alert("Invalid search query")
  }
}

// Gets favorited tracks
const getTracksFavorites = async (q) => {
  if (q == undefined) { q = "" }
  if (q.length !== 0 && q.indexOf("%3A") == -1 && q.indexOf("%3D") == -1) {
    q = `artist:${q},albumartist:${q},album:${q},title:${q}`
  }
  const response = await fetch(`/api/tracks?q=${q}&only_favorited=1`)
  const data = await response.json()
  return data;
}

// Gets track by ids
const getTrackById = async (id) => {
  const response = await fetch(`/api/tracks_by_ids?ids=${id}`);
  const data = await response.json();
  return data[0] ?? null;
};

// Get albums
const getAlbums = async (q) => {
  if (q == undefined) { q = "" }
  if (q.length !== 0 && q.indexOf("%3A") == -1 && q.indexOf("%3D") == -1) {
    q = `albumartist:${q},album:${q}`
  }
  const response = await fetch(`/api/albums?q=${q}`)
  const data = await response.json()
  return data;
}
