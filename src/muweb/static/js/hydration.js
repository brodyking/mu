/*    _
 | | | | mu
 | |_| | (c) 2026 all rights reserved
 | ._,_| https://github.com/brodyking/mu
 |_|
*/

const tracksView = {
  ids: [],
  clusterize: null,
};

const escapeHtml = (value) =>
  String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");

const hydratePlayerPausedState = (paused) => {
  if (paused) {
    document.getElementById("playerbar-pause").classList.add("d-none")
    document.getElementById("playerbar-resume").classList.remove("d-none")
  } else {
    document.getElementById("playerbar-pause").classList.remove("d-none")
    document.getElementById("playerbar-resume").classList.add("d-none")
  }
}

const hydratePlayerMetadata = async () => {
  track = await getTrackById(queueGetCurrent(playerState.queue))

  if (track.art_url) {
    document.getElementById("playerbar-art").src = track.art_url
    document.getElementById("playerbar-art").classList.remove("opacity-0")
    document.getElementById("playerbar-art").classList.add("opacity-100")
  } else {
    document.getElementById("playerbar-art").classList.remove("opacity-100")
    document.getElementById("playerbar-art").classList.add("opacity-0")
  }

  document.getElementById("playerbar-title").innerText = track.title;
  document.getElementById("playerbar-title").href = `/tracks?q=title%3D"${track.title}"`;
  document.getElementById("playerbar-artist").innerText = track.artist;
  document.getElementById("playerbar-artist").href = `/tracks?q=artist%3D"${track.artist}"`;
  document.getElementById("playerbar-album").innerText = track.album;
  document.getElementById("playerbar-album").href = `/tracks?q=album%3D"${track.album}"`;

  if (track.favorite) {
    document.getElementById("playerbar-favorite").classList.remove("bi-heart")
    document.getElementById("playerbar-favorite").classList.add("bi-heart-fill")
  } else {
    document.getElementById("playerbar-favorite").classList.remove("bi-heart-fill")
    document.getElementById("playerbar-favorite").classList.add("bi-heart")
  }
  hydratePlayerPausedState(paused = false)
}

const hydrateQueueTableIfActive = async (scrollAreaId, contentAreaId) => {
  if (window.location.pathname == "/queue") {
    await hydrateQueueTable("scrollArea", "contentArea")
  }
}

const hydrateQueueTable = async () => {
  const cell = (value) => {
    const safe = escapeHtml(value);
    return `<td title="${safe}">${safe}</td>`;
  };

  const generateRows = (data) =>
    data.map((track, index) => `
      <tr data-index="${index}" data-id="${escapeHtml(track.id)}">
        ${cell(track.id)}
        <td title="${track.favorite ? "Favorite" : "Not Favorited"}"><i class="text-primary bi bi-heart${track.favorite ? "-fill" : ""}"></i></td>
        ${cell(track.title)}
        ${cell(track.artist)}
        ${cell(track.album)}
        ${cell(track.plays)}
        ${cell(track.time)}
        ${cell(track.dateadded)}
        ${cell(track.tracknumber)}
        ${cell(track.albumartist)}
        ${cell(track.discnumber)}
        ${cell(track.genre)}
        ${cell(track.date)}
      </tr>`);

  const tids = queueGetUpcoming(playerState.queue) ?? []
  if (tids.length == 0) { return }

  const tracks = tids ? await getTracksById(tids) : []

  const trackById = new Map(tracks.map(track => [track.id, track]))
  const ordered_tracks = tids
    .map(tid => trackById.get(tid))
    .filter(Boolean) // drop any ids that didn't resolve to a track
  const rows = ordered_tracks ?? [];

  tracksView.ids = rows.map((track) => track.id);

  if (tracksView.clusterize) {
    tracksView.clusterize.destroy(false);
    tracksView.clusterize = null;
  }

  tracksView.clusterize = new Clusterize({
    rows: generateRows(rows),
    scrollId: "scrollArea",
    contentId: "contentArea",
  });

  const total = document.getElementById("tracks-total-count")
  total.innerText = `${rows.length.toLocaleString('en-US')} results`;

}


const hydrateTracksTable = async (term, only_favorites = false) => {
  const cell = (value) => {
    const safe = escapeHtml(value);
    return `<td title="${safe}">${safe}</td>`;
  };

  const generateRows = (data) =>
    data.map((track, index) => `
      <tr data-index="${index}" data-id="${escapeHtml(track.id)}">
        ${cell(track.id)}
        <td title="${track.favorite ? "Favorite" : "Not Favorited"}"><i class="text-primary bi bi-heart${track.favorite ? "-fill" : ""}"></i></td>
        ${cell(track.title)}
        ${cell(track.artist)}
        ${cell(track.album)}
        ${cell(track.plays)}
        ${cell(track.time)}
        ${cell(track.dateadded)}
        ${cell(track.tracknumber)}
        ${cell(track.albumartist)}
        ${cell(track.discnumber)}
        ${cell(track.genre)}
        ${cell(track.date)}
      </tr>`);

  if (term === null) {
    term = "";
  }

  const tracks = only_favorites
    ? await getTracksFavorites(encodeURIComponent(term))
    : await getTracks(encodeURIComponent(term));

  const rows = tracks ?? [];

  tracksView.ids = rows.map((track) => track.id);

  if (tracksView.clusterize) {
    tracksView.clusterize.destroy(false);
    tracksView.clusterize = null;
  }

  tracksView.clusterize = new Clusterize({
    rows: generateRows(rows),
    scrollId: "scrollArea",
    contentId: "contentArea",
  });

  const search = document.getElementById("tracks-table-search");
  if (search) {
    search.value = term;
  }
  const total = document.getElementById("tracks-total-count")
  total.innerText = `${rows.length.toLocaleString('en-US')} results`;
};
