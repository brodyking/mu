/*    _
 | | | | mu
 | |_| | (c) 2026 all rights reserved
 | ._,_| https://github.com/brodyking/mu
 |_|
*/

// Adds navbar to the dom
const renderNavbar = () => {
  let nav = document.getElementById("nav");
  nav.replaceChildren(Navbar());
}

const renderPlayerBar = () => {
  let bar = document.getElementById("playerbar");
  bar.replaceChildren(PlayerBar());
  document.getElementById("playerbar-seekbar").addEventListener('click', playerScrubFromPlayerBar);
}

const changeWindowTitle = (title = "") => {
  if (title !== "") {
    document.title = `muweb · ${title}`
  } else {
    document.title = `muweb`
  }
}

// Main routing function. Routes + Hydrates
const route = async (pathname, search) => {

  // Set path to current path if one is not provided
  // (happens first time page is loaded)
  if (pathname === undefined) {
    pathname = document.location.pathname;
  } else {
    const url = pathname + (search ? search : "");
    window.history.pushState({}, "", url);
  }

  let params = new URLSearchParams(document.location.search);

  let main = document.getElementById("main")

  // Switch case the current page
  switch (pathname) {
    // ===== Homepage =====
    case "/":
      changeWindowTitle()
      main.replaceChildren(Homepage())
      break;
    // ===== Queuetab =====
    case "/queue":
      changeWindowTitle("queue")
      main.replaceChildren(Loading("fetching queue..."))
      main.appendChild(QueueTable())
      await hydrateQueueTable("scrollArea", "contentArea")
      main.removeChild(document.getElementById("loading"))
      break;
    // ===== Tracks tab =====
    case "/tracks":
      changeWindowTitle("tracks")
      main.replaceChildren(Loading("fetching tracks..."))
      main.appendChild(TracksTable())
      await hydrateTracksTable("scrollArea", "contentArea", params.get("q"))
      main.removeChild(document.getElementById("loading"))
      break;
    // ===== Favorites tab =====
    case "/favorites":
      changeWindowTitle("favorites")
      main.replaceChildren(Loading("fetching favorites..."))
      main.appendChild(TracksTable(only_favorites = true))
      await hydrateTracksTable("scrollArea", "contentArea", params.get("q"), only_favorites = true)
      main.removeChild(document.getElementById("loading"))
      break;
    // ===== Albums tab =====
    case "/albums":
      changeWindowTitle("albums")
      main.replaceChildren(Loading("fetching albums..."))
      main.replaceChildren(await AlbumsTable())
      break;
    // ===== Error 404 =====
    default:
      changeWindowTitle("error 404")
      main.replaceChildren(Error404())
      break;
  }
}

// Intercept <a href="" data-external>, hands off to router.
document.addEventListener('click', function(event) {

  const link = event.target.closest('a');

  if (link && event.target.dataset.external !== undefined) {
    return
  }
  if (link && link.hasAttribute('href')) {
    event.preventDefault()
    route(link.pathname, link.search)
  }
});

// Intercept brower back and forward history 
window.addEventListener('popstate', function(event) {
  event.preventDefault()
  route(event.pathname)
});

route()
window.addEventListener('load', renderNavbar)
window.addEventListener('load', renderPlayerBar)
