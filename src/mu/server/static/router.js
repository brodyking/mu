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


  to_put = document.getElementById("main")

  // Switch case the current page
  switch (pathname) {
    // ===== Tracks tab =====
    case "/":
      data = await get_tracks()
      to_put.innerHTML = await TracksTable(data)
      break;
    // ===== Favorites tab =====
    case "/favorites":
      data = await get_tracks("favorite%3D1")
      to_put.innerHTML = await TracksTable(data)
      break;
    // ===== Error 404 =====
    default:
      document.body.innerHTML = "Error 404";
      break;
  }
}

// Intercept <a href="">, hands off to router.
document.addEventListener('click', function (event) {
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
