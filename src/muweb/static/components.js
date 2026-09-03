/*    _
 | | | | mu
 | |_| | (c) 2026 all rights reserved
 | ._,_| https://github.com/brodyking/mu
 |_|
*/


const Navbar = () => {
  const element = document.createElement("div");
  element.innerHTML = `
    <div class="sidebar sidebar-narrow-unfoldable border-end">
      <div class="sidebar-header">
        <div class="sidebar-brand">
          <a class="nav-item fs-2 text-secondary text-decoration-none" href="/">µ</a>
        </div>
      </div>
      <ul class="sidebar-nav">
        <li class="nav-item">
          <a class="nav-link" href="/tracks">
            <i class="nav-icon bi bi-music-note"></i>
            <span class="nav-link-text">tracks</span>
          </a>
        </li>

        <li class="nav-item">
          <a class="nav-link" href="/favorites">
            <i class="nav-icon bi bi-heart-fill"></i>
            <span class="nav-link-text">favorites</span>
          </a>
        </li>

        <li class="nav-item">
          <a class="nav-link" href="/albums">
            <i class="nav-icon bi bi-vinyl-fill"></i>
            <span class="nav-link-text">albums</span>
          </a>
        </li>

        <li class="nav-item mt-auto">
          <a class="nav-link" href="https://github.com/brodyking/mu" data-external>
            <i class="nav-icon bi bi-github"></i>
            <span class="nav-link-text">github</span>
          </a>
        </li>
      </ul>
    </div>`
  return element;
}

const Loading = () => {
  const content = document.createElement("div");
  content.innerHTML = `
    <!-- Full-Screen Loading Overlay -->
    <div id="loading-overlay" class="position-fixed top-0 start-0 w-100 h-100 d-flex align-items-center justify-content-center" style="z-index: 9999;">
      <div class="text-center">
        <!-- CoreUI / Bootstrap Spinner -->
        <div class="spinner-border text-body" role="status" style="width: 3rem; height: 3rem;">
          <span class="visually-hidden">Loading...</span>
        </div>
        <!-- Optional Loading Text -->
        <div class="text-light mt-2">loading...</div>
      </div>
    </div>
  `;
  return content
}

const Homepage = () => {
  const content = document.createElement("div");
  content.className = "text-center d-flex flex-column justify-content-center align-items-center min-vh-100";
  content.innerHTML = `
    <h1 class='mt-5 align-self-center fs-1'>µ</h1>
    <p class='mt-3 fs-4'>your personal music library</p>
    <a href="https://github.com/brodyking/mu/" class="btn btn-primary mt-3" data-external>github</a>
  `;
  return content;
};

const Error404 = () => {
  const content = document.createElement("div");
  content.className = "text-center d-flex flex-column justify-content-center align-items-center min-vh-100";
  content.innerHTML = `
    <div class="text-center d-flex flex-column justify-content-center align-items-center min-vh-100">
      <h1 class='mt-5 align-self-center fs-1'>Error 404</h1>
      <p class='mt-3 fs-5'>Page not found.</p>
    </div>
  `;
  return content;
};


const TracksTable = async (onlyFavorites = false) => {

  // Generates the HTML for the table's rows.
  const generateRows = (data) => {
    let rows = "";
    let index = 0;
    data.forEach(track => {
      rows += `
        <tr ondblclick='startQueue("${index}")'>
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
      index++;
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
    <input type="text" name="term" autocomplete="off" class="form-control rounded-0 w-100 border-0 border-bottom border-light-gray shadow-none" placeholder="Search tracks..."/>
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
  <table class="table table-striped data-table" id="tracks-table">
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
  const content = document.createElement("div");
  content.className = "text-center d-flex flex-column justify-content-center align-items-center min-vh-100";
  content.innerHTML = "<p class='mt-3 fs-4'>coming soon</p>";
  return content;
};
