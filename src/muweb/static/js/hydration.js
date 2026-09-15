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

const hydrateQueueTable = async (scrollAreaId, contentAreaId, term) => {
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
    scrollId: scrollAreaId,
    contentId: contentAreaId,
  });

}


const hydrateTracksTable = async (scrollAreaId, contentAreaId, term, only_favorites = false) => {
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

  console.log(rows)

  tracksView.ids = rows.map((track) => track.id);

  if (tracksView.clusterize) {
    tracksView.clusterize.destroy(false);
    tracksView.clusterize = null;
  }

  tracksView.clusterize = new Clusterize({
    rows: generateRows(rows),
    scrollId: scrollAreaId,
    contentId: contentAreaId,
  });

  const search = document.getElementById("tracks-table-search");
  if (search) {
    search.value = term;
  }
};
