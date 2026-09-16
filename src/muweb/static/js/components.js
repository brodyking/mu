/*    _
 | | | | mu
 | |_| | (c) 2026 all rights reserved
 | ._,_| https://github.com/brodyking/mu
 |_|
*/


const PlayerBar = () => {
  const bar = document.createElement("div");
  bar.id = "playerbar-row";
  bar.classList = `w-100 bg-body border`;
  bar.innerHTML = `

      <div id="playerbar-info">
        <div class="d-flex gap-0">
          <img id="playerbar-art" class="ms-1 me-2 border-1 opacity-0">
          <div class="container text-start align-middle metadata p-0 pt-1 m-0">
            <div class="row">
              <div class="col fw-bold">
                <a href="/tracks" id="playerbar-title">Title </a>
              </div>
            </div>
            <div class="row">
              <div class="col">
                by <a href="/tracks" id="playerbar-artist">Artist</a>
              </div>
            </div>
            <div class="row">
              <div class="col">
                from <a href="/tracks" id="playerbar-album">Album</a>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div id="playerbar-transport">

        <div class="transport-side transport-left">
          <div class="d-none" id="playerbar-pause">
            <a class="btn" onclick="playerPause()">
              <i class="bi bi-pause-fill"></i>
            </a>
          </div>
          <div id="playerbar-resume">
            <a class="btn" onclick="playerResume()">
              <i class="bi bi-play-fill"></i>
            </a>
          </div>
        </div>
        
          <div id="playerbar-seek" >
            <progress id="playerbar-seekbar" value="0" max="1"></progress>
            <a id="playerbar-duration" class="btn disabled border-0">00:00 / 00:00</a>
          </div>

        <div class="transport-side transport-right">
          <a class="btn" onclick="playerPlayPrevious()">
            <i class="bi bi-skip-backward-fill"></i>
          </a>
          <a class="btn" onclick="playerPlayNext()">
            <i class="bi bi-skip-forward-fill"></i>
          </a>
        </div>

      </div>

      <div id="playerbar-actions">
        <a href="/queue" class="btn">
          <i class="bi bi-music-note-list"></i>
        </a>
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
        <li class="nav-item ">
          <a class="nav-link" href="/api/" data-external>
            <i class="nav-icon bi bi-book"></i>
            <span class="nav-link-text">api</span>
          </a>
        </li>
      </ul>
    </div>`
  return element;
}

const Loading = (info = "loading...") => {
  const content = document.createElement("div");
  content.id = "loading"
  content.innerHTML = `
    <!-- Full-Screen Loading Overlay -->
    <div id="loading-overlay" class="position-fixed top-0 start-0 w-100 h-100 d-flex align-items-center justify-content-center" style="z-index: 9999; background-color: color-mix(in srgb, var(--cui-body-bg) 50%, transparent);">
      <div class="text-center">
        <!-- CoreUI / Bootstrap Spinner -->
        <div class="spinner-border text-body" role="status" style="width: 3rem; height: 3rem;">
          <span class="visually-hidden">Loading...</span>
        </div>
        <!-- Optional Loading Text -->
        <div class="text-body mt-2">${info}</div>
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

const trackColgroup = `
  <colgroup>
    <col style="width: 60px">   <!-- id -->
    <col style="width: 36px">   <!-- favorite icon -->
    <col style="width: 200px">    <!-- title -->
    <col style="width: 100px">    <!-- artist -->
    <col style="width: 100px">    <!-- album -->
    <col style="width: 60px">   <!-- plays -->
    <col style="width: 60px">   <!-- time -->
    <col style="width: 100px">  <!-- dateadded -->
    <col style="width: 90px">   <!-- tracknumber -->
    <col style="width: 15%">    <!-- albumartist -->
    <col style="width: 80px">   <!-- discnumber -->
    <col style="width: 100px">  <!-- genre -->
    <col style="width: 90px">   <!-- date -->
  </colgroup>
`;

const TracksTable = (onlyFavorites = false) => {

  const content = document.createElement("div"); // Parent element for search and table
  content.className = "tracks-page";
  const search = document.createElement("form"); // Search Box
  const table = document.createElement("div"); // Table


  // Search
  search.className = "search-form"
  search.innerHTML = `
    <input type="text" name="term" autocomplete="off" id="tracks-table-search" class="form-control rounded-0 w-100 border-0 border-bottom border-light-gray shadow-none" placeholder="Search tracks..." onfocus="this.select()"/>
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
  <table class="table data-table mb-0">
    ${trackColgroup}
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
    <table class="table data-table" id="tracks-table">
      ${trackColgroup}
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

const QueueTable = (onlyFavorites = false) => {

  const content = document.createElement("div"); // Parent element for search and table
  content.className = "queue-page";
  const table = document.createElement("div"); // Table

  // Table
  table.className = "tracks-table-wrapper clusterize";
  table.innerHTML = `
  <table class="table data-table mb-0">
    ${trackColgroup}
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
    <table class="table data-table" id="tracks-table">
      ${trackColgroup}
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

  content.appendChild(table);
  return content;
};

const AlbumsTable = async () => {
  const content = document.createElement("div");
  content.className = "text-center d-flex flex-column justify-content-center align-items-center h-100";
  content.innerHTML = "<p class='mt-3 fs-4'>coming soon</p>";
  return content;
};;
