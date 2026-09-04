const hydrateTracksTable = async (scrollAreaId, contentAreaId, term, only_favorites = false) => {
  const generateRows = (data) => {
    let rows = [];
    let index = 0;
    data.forEach(track => {
      rows.push(`
        <tr ondblclick='playerCreateQueue(${index});playerPlayCurrent();'>
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
        </tr>`);
      index++;
    });
    return rows;
  }

  if (term === null) {
    term = ""
  }

  if (only_favorites) {
    tracks = await getTracksFavorites(encodeURIComponent(term))
  } else {
    tracks = await getTracks(encodeURIComponent(term))
  }

  Clusterize({
    rows: generateRows(tracks),
    scrollId: scrollAreaId,
    contentId: contentAreaId
  })

  search = document.getElementById("tracks-table-search");
  if (search) {
    search.value = term
  }

}
