/*    _
 | | | | mu
 | |_| | (c) 2026 all rights reserved
 | ._,_| https://github.com/brodyking/mu
 |_|
*/


const Homepage = () => {
  return `
    <div class="text-center">
      <h1 class='mt-5'>mu</h1>
      <h3 class='mt-3'>your personal music library</h3>
      <a href="https://github.com/brodyking/mu/" class="btn btn-dark mt-3" data-external>github</a>
    </div>
  `
}

const TracksTable = async (data) => {
  rows = ""
  data.forEach(track => {
    rows += `
    <tr>
        <td title="${track.id}">${track.id}</td>
        <td title="${track.favorite ? "Favorite" : "Not Favorited"}"> <i class="text-danger bi bi-heart${track.favorite ? `-fill` : " "}"></i></td>
        <td title="${track.title}">${track.title}</td>
        <td title="${track.artist}">${track.artist}</td>
        <td title="${track.album}">${track.album}</td>
        <td title="${track.plays}">${track.plays}</td>
        <td title="${track.time}">${track.time}</td>
        <td title="${track.dateadded}">${track.dateadded}</td>
        <td title="${track.tracknumber}">${track.tracknumber}</td>
        <td title="${track.albumartist}">${track.albumartist}</td>
        <td title="${track.discnumber}">${track.discnumber}</td>
        <td title="${track.genre}">${track.genre}</td>
        <td title="${track.date}">${track.date}</td>
      </tr >
    `
  })
  return `
  <table class="table table-striped" id="tracks-table">
    <thead>
      <th>id</th>
      <th>favorite</th>
      <th>title</th>
      <th>artist</th>
      <th>album</th>
      <th>plays</th>
      <th>time</th>
      <th>dateadded</th>
      <th>tracknumber</th>
      <th>albumartist</th>
      <th>discnumber</th>
      <th>genre</th>
      <th>date</th>
    </thead>
    <tbody id="tracks-table-body">
      ${rows}
    </tbody>
  </table>
  `
}

const AlbumsTable = async (data) => {
  rows = ""
  data.forEach(album => {

    rows += `
    <tr>
        <td title="${album.title}">${album.title}</td>
        <td title="${album.albumartist}">${album.albumartist}</td>
        <td title="${album.tracks.length}">${album.tracks.length}</td>
      </tr >
    `
  })
  return `
  <table class="table table-striped" id="tracks-table">
    <thead>
      <th>album</th>
      <th>albumartist</th>
      <th>tracks</th>
    </thead>
    <tbody id="tracks-table-body">
      ${rows}
    </tbody>
  </table>
  `
}
