/*    _
 | | | | mu
 | |_| | (c) 2026 all rights reserved
 | ._,_| https://github.com/brodyking/mu
 |_|
*/


const PlayerBar = () => {
  const bar = document.createElement("div");
  bar.innerHTML = `
  <div class="container text-center controls">
    <div class="row">
      <div class="col">
        <a class="btn btn-outline-primary" onclick="playerPlayPrevious()">
          <i class="bi bi-skip-backward-fill"></i>
        </a>
      </div>
      <div class="col d-none" id="playerbar-pause">
        <a class="btn btn-primary" onclick="playerPause()">
          <i class="bi bi-pause-fill"></i>
        </a>
      </div>
      <div class="col" id="playerbar-resume">
        <a class="btn btn-primary" onclick="playerResume()">
          <i class="bi bi-play-fill"></i>
        </a>
      </div>
      <div class="col">
        <a class="btn btn-outline-primary" onclick="playerPlayNext()">
          <i class="bi bi-skip-forward-fill"></i>
        </a>
      </div>
      <div class="col">
        <img src="/img/empty_art.png" id="playerbar-art">
      </div>
      <div class="col" style="max-width: 50px;">
        <div class="container text-start metadata">
          <div class="row">
            <div class="col" id="playerbar-title">
              Track title 
            </div>
          </div>
          <div class="row">
            <div class="col" id="playerbar-artist">
              Track artist 
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  `
  return bar
}

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
        <div class="spinner-border text-secondary" role="status" style="width: 3rem; height: 3rem;">
          <span class="visually-hidden">Loading...</span>
        </div>
        <!-- Optional Loading Text -->
        <div class="text-secondary mt-2">loading...</div>
      </div>
    </div>
  `;
  return content
}

const Homepage = () => {
  const content = document.createElement("div");
  content.className = "text-center d-flex flex-column justify-content-center align-items-center h-100";
  content.innerHTML = `
    <h1 class='mt-5 align-self-center fs-1'>µ</h1>
    <p class='mt-3 fs-4'>your personal music library</p>
    <a href="https://github.com/brodyking/mu/" class="btn btn-primary mt-3" data-external>github</a>
  `;
  return content;
};

const Error404 = () => {
  const content = document.createElement("div");
  content.className = "text-center d-flex flex-column justify-content-center align-items-center h-100";
  content.innerHTML = `
    <div class="text-center d-flex flex-column justify-content-center align-items-center h-100">
      <h1 class='mt-5 align-self-center fs-1'>Error 404</h1>
      <p class='mt-3 fs-5'>Page not found.</p>
    </div>
  `;
  return content;
};

const TracksTable = (onlyFavorites = false) => {

  const content = document.createElement("div"); // Parent element for search and table
  content.className = "tracks-page";
  const search = document.createElement("form"); // Search Box
  const table = document.createElement("div"); // Table


  // Search
  search.className = "search-form"
  search.innerHTML = `
    <input type="text" name="term" autocomplete="off" id="tracks-table-search" class="form-control rounded-0 w-100 border-0 border-bottom border-light-gray shadow-none" placeholder="Search tracks..."/>
  `;
  search.addEventListener('submit', async function(event) {
    // Listens for search submit, fetches tracks and updates rows.
    event.preventDefault();
    const formData = new FormData(search);
    const formDataEntries = Object.fromEntries(formData.entries());
    const term = encodeURIComponent(formDataEntries.term)
    if (onlyFavorites) {
      route("/favorites", `?q=${term}`)
    } else {
      route("/tracks", `?q=${term}`)
    }
    window.scrollTo(0, 0)
  });

  // Table
  table.className = "tracks-table-wrapper clusterize";
  table.innerHTML = `
  <table class="table table-striped data-table mb-0">
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
  </table>
  <div id="scrollArea" class="clusterize-scroll">
    <table class="table table-striped data-table" id="tracks-table">
      <tbody id="contentArea">
      </tbody>
    </table>
  </div>
  `;
  table.addEventListener("dblclick", (event) => {
    const row = event.target.closest("tr[data-index]");
    if (!row) return;
    playerCreateQueue(tracksView.ids, Number(row.dataset.index));
    playerPlayCurrent();
  });

  content.appendChild(search);
  content.appendChild(table);
  return content;
};

const AlbumsTable = async () => {
  const content = document.createElement("div");
  content.className = "text-center d-flex flex-column justify-content-center align-items-center h-100";
  content.innerHTML = "<p class='mt-3 fs-4'>coming soon</p>";
  return content;
};;
