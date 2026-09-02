/*    _
 | | | | mu
 | |_| | (c) 2026 all rights reserved
 | ._,_| https://github.com/brodyking/mu
 |_|
*/


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


  main = document.getElementById("main")

  // Switch case the current page
  switch (pathname) {
    // ===== Homepage =====
    case "/":
      main.innerHTML = Homepage()
      break;
    // ===== Tracks tab =====
    case "/tracks":
      main.replaceChildren(await TracksTable())
      break;
    // ===== Favorites tab =====
    case "/favorites":
      main.replaceChildren(await TracksTable(true))
      break;
    // ===== Albums tab =====
    case "/albums":
      main.replaceChildren(await AlbumsTable())
      break;
    // ===== Error 404 =====
    default:
      main.innerHTML = `<h1>Error 404</h1>`;
      break;
  }
}

// Intercept <a href="">, hands off to router.
document.addEventListener('click', function(event) {

  if (event.target.dataset.external !== undefined) {
    return
  }

  const link = event.target.closest('a');
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
