/*    _
 | | | | mu
 | |_| | (c) 2026 all rights reserved
 | ._,_| https://github.com/brodyking/mu
 |_|
*/


const Homepage = () => {
  return `
    <div class="text-center d-flex flex-column justify-content-center align-items-center min-vh-100">
      <h1 class='mt-5 align-self-center fs-1'>µ</h1>
      <p class='mt-3 fs-4'>your personal music library</p>
      <a href="https://github.com/brodyking/mu/" class="btn btn-primary mt-3" data-external>github</a>
    </div>
  `
}

const Error404 = () => {
  return `
    <div class="text-center d-flex flex-column justify-content-center align-items-center min-vh-100">
      <h1 class='mt-5 align-self-center fs-1'>Error 404</h1>
      <p class='mt-3 fs-5'>Page not found.</p>
    </div>
  `
}

const TracksTable = async (onlyFavorites = false) => {

  // Generates the HTML for the table's rows.
  const generateRows = (data) => {
    let rows = "";
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
        </tr>`;
    });
    return rows;
  }

  const data = onlyFavorites ? await getTracksFavorites() : await getTracks() // Get tracks from api
  const content = document.createElement("div"); // Parent element for search and table
  const search = document.createElement("form"); // Search Box
  const table = document.createElement("div"); // Table


  // Search
  search.className = "search-form"
  search.innerHTML = `
    <input type="text" name="term" class="form-control rounded-0 w-100 border-0 border-bottom border-light-gray shadow-none" placeholder="Search tracks..."/>
  `;
  search.addEventListener('submit', async function(event) {
    // Listens for search submit, fetches tracks and updates rows.
    event.preventDefault();
    const formData = new FormData(search);
    const formDataEntries = Object.fromEntries(formData.entries());
    results = null
    if (onlyFavorites) {
      results = await getTracksFavorites(encodeURIComponent(formDataEntries.term));
    } else {
      results = await getTracks(encodeURIComponent(formDataEntries.term));
    }
    document.getElementById("tracks-table-body").innerHTML = generateRows(results);
    window.scrollTo(0, 0)
  });

  // Table
  table.className = "tracks-table-wrapper";
  table.innerHTML = `
  <table class="table table-striped" id="tracks-table">
    <thead>
      <tr>
        <th>id</th>
        <th></th>
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
      </tr>
    </thead>
    <tbody id="tracks-table-body">
      ${generateRows(data)}
    </tbody>
  </table>
  `;

  content.appendChild(search);
  content.appendChild(table);
  return content;
};

const AlbumsTable = async () => {

  // Generates the HTML for the table's rows.
  const generateRows = (data) => {
    let rows = "";
    data.forEach(album => {
      rows += `
        <tr>
          <td title="${album.title}">${album.title}</td>
          <td title="${album.albumartist}">${album.albumartist}</td>
          <td title="${album.tracks.length}">${album.tracks.length}</td>
        </tr>`;
    });
    return rows;
  }

  const data = await getAlbums() // Get tracks from api
  const content = document.createElement("div"); // Parent element for search and table
  const search = document.createElement("form"); // Search Box
  const table = document.createElement("div"); // Table


  // Search
  search.className = "search-form"
  search.innerHTML = `
    <input type="text" name="term" class="form-control rounded-0 w-100 border-0 border-bottom border-light-gray shadow-none" placeholder="Search albums..."/>
  `;
  search.addEventListener('submit', async function(event) {
    // Listens for search submit, fetches tracks and updates rows.
    event.preventDefault();
    const formData = new FormData(search);
    const formDataEntries = Object.fromEntries(formData.entries());
    results = await getAlbums(encodeURIComponent(formDataEntries.term));
    document.getElementById("albums-table-body").innerHTML = generateRows(results);
    window.scrollTo(0, 0)
  });

  // Table
  table.className = "albums-table-wrapper";
  table.innerHTML = `
    <table class="table table-striped" id="albums-table">
      <thead>
        <th>album</th>
        <th>albumartist</th>
        <th>tracks</th>
      </thead>
      <tbody id="albums-table-body">
      ${generateRows(data)}
      </tbody>
    </table>
  `;

  content.appendChild(search);
  content.appendChild(table);
  console.log(table)
  return content;
};

