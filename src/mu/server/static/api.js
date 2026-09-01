/*    _
 | | | | mu
 | |_| | (c) 2026 all rights reserved
 | ._,_| https://github.com/brodyking/mu
 |_|
*/

// Gets tracks
const get_tracks = async (q) => {
  if (q == undefined) { q = "" }
  const response = await fetch(`/api/tracks?q=${q}`)
  const data = await response.json()
  return data;
}

