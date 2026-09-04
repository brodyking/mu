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
      main.replaceChildren(Homepage())
      break;
    // ===== Tracks tab =====
    case "/tracks":
      main.replaceChildren(TracksTable())
      hydrateTracksTable("scrollArea", "contentArea", params.get("q"))
      break;
    // ===== Favorites tab =====
    case "/favorites":
      main.replaceChildren(TracksTable(only_favorites = true))
      hydrateTracksTable("scrollArea", "contentArea", params.get("q"), only_favorites = true)
      break;
    // ===== Albums tab =====
    case "/albums":
      main.replaceChildren(Loading())
      main.replaceChildren(await AlbumsTable())
      break;
    // ===== Error 404 =====
    default:
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
