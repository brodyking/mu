const audio = new Audio();
const playerState = {
  queue: Queue
}
audio.preload = "metadata";

const playerCreateQueue = (pos) => {
  playerState.queue = queueCreate(collectIdsFromTracksTable(), pos)
}

const playerSetMetadata = async () => {
  track = await getTrackById(queueGetCurrent(playerState.queue))

  navigator.mediaSession.metadata = new MediaMetadata({
    title: track.title,
    artist: track.artist,
    album: track.album,
    artwork: track.art_url ? [{ src: track.art_url }] : [{ src: "/img/empty_art.png" }],
  });
  navigator.mediaSession.setActionHandler("nexttrack", () => { playerPlayNext() });
  navigator.mediaSession.setActionHandler("previoustrack", () => { playerPlayPrevious() });

  document.getElementById("playerbar-art").src = track.art_url ? track.art_url : "/img/empty_art.png";

  document.getElementById("playerbar-title").innerText = track.title;
  document.getElementById("playerbar-artist").innerText = track.artist;

  document.getElementById("playerbar-pause").classList.remove("d-none")
  document.getElementById("playerbar-resume").classList.add("d-none")

}

const playerPause = () => {
  audio.pause();
  document.getElementById("playerbar-pause").classList.add("d-none")
  document.getElementById("playerbar-resume").classList.remove("d-none")
}

const playerResume = () => {
  audio.play();
  document.getElementById("playerbar-pause").classList.remove("d-none")
  document.getElementById("playerbar-resume").classList.add("d-none")
}

const playerPlayCurrent = async () => {
  const id = queueGetCurrent(playerState.queue);
  if (id === null) return;
  audio.src = `/api/tracks/${id}/audio`;
  await audio.play();
  playerSetMetadata();
};

const playerPlayNext = () => {
  playerState.queue = queueNext(playerState.queue)
  playerPlayCurrent(playerState.queue)
}

const playerPlayPrevious = () => {
  playerState.queue = queuePrevious(playerState.queue)
  playerPlayCurrent(playerState.queue)
}

audio.addEventListener("ended", () => {
  playerPlayNext();
});

