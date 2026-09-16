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

  const links = [document.getElementById("navbar-tracks"), document.getElementById("navbar-favorites"), document.getElementById("navbar-albums")]
  links.forEach((link) => {
    link.classList.remove("active")
  })

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
      document.getElementById("navbar-tracks").classList.add("active")
      changeWindowTitle("tracks")
      main.replaceChildren(Loading("fetching tracks..."))
      main.appendChild(TracksTable())
      await hydrateTracksTable("scrollArea", "contentArea", params.get("q"))
      main.removeChild(document.getElementById("loading"))
      break;
    // ===== Favorites tab =====
    case "/favorites":
      document.getElementById("navbar-favorites").classList.add("active")
      changeWindowTitle("favorites")
      main.replaceChildren(Loading("fetching favorites..."))
      main.appendChild(TracksTable(only_favorites = true))
      await hydrateTracksTable("scrollArea", "contentArea", params.get("q"), only_favorites = true)
      main.removeChild(document.getElementById("loading"))
      break;
    // ===== Albums tab =====
    case "/albums":
      document.getElementById("navbar-albums").classList.add("active")
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
  event.preventDefault()
  const link = event.target.closest('a');

  if (link && event.target.dataset.external !== undefined && link.hasAttribute('href')) {
    if (confirm(`This is an external link. Are you sure you want to visit?`)) {
      window.open(link.href, '_blank');
    }
  } else if (link && link.hasAttribute('href')) {
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
