/*    _
 | | | | mu
 | |_| | (c) 2026 all rights reserved
 | ._,_| https://github.com/brodyking/mu
 |_|
*/


const TracksTable = async (data) => {
  rows = ""
  data.forEach(track => {
    rows += `
    <tr>
        <td>`+ track.id + `</td>
        <td>`+ (track.favorite ? `❤️` : " ") + `</td>
        <td>`+ track.title + `</td>
        <td>`+ track.artist + `</td>
        <td>`+ track.album + `</td>
        <td>`+ track.plays + `</td>
        <td>`+ track.time + `</td>
        <td>`+ track.dateadded + `</td>
        <td>`+ track.tracknumber + `</td>
        <td>`+ track.albumartist + `</td>
        <td>`+ track.discnumber + `</td>
        <td>`+ track.genre + `</td>
        <td>`+ track.date + `</td>
      </tr >
    `
  })
  return `
  <table class="table" id="tracks-table">
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
