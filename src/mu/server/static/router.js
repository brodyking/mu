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
      data = await get_tracks()
      main.innerHTML = await TracksTable(data)
      break;
    // ===== Favorites tab =====
    case "/favorites":
      data = await get_tracks("favorite%3D1")
      main.innerHTML = await TracksTable(data)
      break;
    // ===== Albums tab =====
    case "/albums":
      data = await get_albums()
      main.innerHTML = await AlbumsTable(data)
      break;
    // ===== Error 404 =====
    default:
      main.innerHTML = `<h1>Error 404</h1>`;
      break;
  }
}

// Intercept <a href="">, hands off to router.
document.addEventListener('click', function (event) {

  if (event.target.dataset.external !== undefined) {
    return
  }

  event.preventDefault()
  const link = event.target.closest('a');
  if (link && link.hasAttribute('href')) {
    route(link.pathname, link.search)
  }
});

// Intercept brower back and forward history 
window.addEventListener('popstate', function (event) {
  event.preventDefault()
  route(event.pathname)
});

route()
