// Router, builds dom based upon the pathname
const route = async () => {
  let pathname = document.location.pathname;
  switch (pathname) {
    case "/":
      data = await get_tracks()
      await generate_tracks_table(data)
      break;
    case "/favorites":
      data = await get_tracks("favorite%3D1")
      await generate_tracks_table(data)
      break;
    default:
      document.body.innerHTML = "Error 404";
      break;
  }
}

// Gets tracks
const get_tracks = async (q) => {
  if (q == undefined) {
    q = ""
  }
  const response = await fetch(`/api/tracks?q=${q}`)
  const data = await response.json()
  return data;
}


const generate_nav = () => {
  document.body.innerHTML += `
    <nav class="navbar navbar-expand-lg bg-body-tertiary">
      <div class="container-fluid">
        <a class="navbar-brand" href="#">mu</a>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarNav">
          <ul class="navbar-nav">
            <li class="nav-item">
              <a class="nav-link" href="/">tracks</a>
            </li>
            <li class="nav-item">
              <a class="nav-link" href="/favorites">favorites</a>
            </li>
          </ul>
        </div>
      </div>
    </nav>
  `
}

const generate_tracks_table = async (data) => {
  
  document.body.innerHTML += `
    <table class='table'>
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
      <tbody id='tracks-table-body'>
      </tbody>
    </table>
    `
  html = ""
  data.forEach(track => {
    html += `
      <tr>
        <td>`+track.id+`</td>
        <td>`+(track.favorite ? `❤️` : " ")+`</td>
        <td>`+track.title+`</td>
        <td>`+track.artist+`</td>
        <td>`+track.album+`</td>
        <td>`+track.plays+`</td>
        <td>`+track.time+`</td>
        <td>`+track.dateadded+`</td>
        <td>`+track.tracknumber+`</td>
        <td>`+track.albumartist+`</td>
        <td>`+track.discnumber+`</td>
        <td>`+track.genre+`</td>
        <td>`+track.date+`</td>
      </tr>
    ` 
  })

  document.getElementById("tracks-table-body").innerHTML += html
}

generate_nav()
route()
