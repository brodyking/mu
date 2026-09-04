const audio = new Audio();
const state = {
  queue: Queue
}
audio.preload = "metadata";

const playerCreateQueue = (pos) => {
  state.queue = queueCreate(collectIdsFromTracksTable(), pos)
}

const playerSetMetadata = async () => {
  track = await getTrackById(queueGetCurrent(state.queue))
  navigator.mediaSession.metadata = new MediaMetadata({
    title: track.title,
    artist: track.artist,
    album: track.album,
    artwork: track.art_url ? [{ src: track.art_url }] : [],
  });
  navigator.mediaSession.setActionHandler("nexttrack", () => { playerPlayNext() });
  navigator.mediaSession.setActionHandler("previoustrack", () => { playerPlayPrevious() });
}

const playerPlayCurrent = async () => {
  const id = queueGetCurrent(state.queue);
  if (id === null) return;
  audio.src = `/api/tracks/${id}/audio`;
  await audio.play();
  playerSetMetadata();
};

const playerPlayNext = () => {
  state.queue = queueNext(state.queue)
  playerPlayCurrent(state.queue)
}

const playerPlayPrevious = () => {
  state.queue = queuePrevious(state.queue)
  playerPlayCurrent(state.queue)
}

audio.addEventListener("ended", () => {
  playerPlayNext();
});

