/*    _
 | | | | mu
 | |_| | (c) 2026 all rights reserved
 | ._,_| https://github.com/brodyking/mu
 |_|
*/

// Gets tracks
const getTracks = async (q, order_by = null) => {
  if (q == undefined) {
    console.error(`${q} is undefined`)
    return
  }
  if (q.length !== 0 && q.indexOf("%3A") == -1 && q.indexOf("%3D") == -1) {
    q = `artist:${q},albumartist:${q},album:${q},title:${q}`
  }
  try {
    let url = `/api/tracks?q=${q}`
    if (order_by != null) {
      url += `&order_by=${order_by}`
    }
    const response = await fetch(url)
    const data = await response.json()
    return data;
  } catch (err) {
    alert(`Invalid search query (${err})`)
  }
}


// Gets favorited tracks
const getTracksFavorites = async (q) => {
  if (q == undefined) {
    console.error(`${q} is undefined`)
    return
  }
  if (q.length !== 0 && q.indexOf("%3A") == -1 && q.indexOf("%3D") == -1) {
    q = `artist:${q},albumartist:${q},album:${q},title:${q}`
  }
  try {
    const response = await fetch(`/api/tracks?q=${q}&only_favorited=1`)
    const data = await response.json()
    return data;
  } catch (err) {
    alert(`Invalid search query (${err})`)
  }
}

// Gets track by id
const getTrackById = async (id) => {
  if (id !== id) {
    console.error(`${id} is not a number.`)
    return null
  }
  const response = await fetch(`/api/tracks_by_ids?ids=${id}`);
  const data = await response.json();
  return data[0] ?? null;
};

// Get tracks by ids, in batches to keep URLs short
const getTracksById = async (ids, batchSize = 500) => {
  const batches = [];
  for (let i = 0; i < ids.length; i += batchSize) {
    batches.push(ids.slice(i, i + batchSize));
  }

  try {
    const results = await Promise.all(
      batches.map(async (batch) => {
        const params = new URLSearchParams();
        batch.forEach((id) => params.append("ids", id));
        const response = await fetch(`/api/tracks_by_ids?${params}`);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return response.json();
      })
    );
    return results.flat();
  } catch (err) {
    alert(`Error fetching tracks (${err})`)
    return [];
  }
};

// // Get albums
// const getAlbums = async (q) => {
//   if (q == undefined) { q = "" }
//   if (q.length !== 0 && q.indexOf("%3A") == -1 && q.indexOf("%3D") == -1) {
//     q = `albumartist:${q},album:${q}`
//   }
//   const response = await fetch(`/api/albums?q=${q}`)
//   const data = await response.json()
//   return data;
// }

// Favorite track
const putFavorite = async (id) => {

  if (id !== id) {
    console.error(`${id} is not a number.`)
    return []
  }

  const url = `/api/tracks/${id}/favorite`;

  try {
    const response = await fetch(url, {
      method: 'PUT', // Specify the HTTP method
      headers: {
        'Content-Type': 'application/json', // Tell the server we are sending JSON
      },
      body: []
    });

    const data = await response.json(); // Parse response payload
    return data[0] ?? null;
  } catch (error) {
    console.error('Error during PUT request:', error);
  }

}
