const audio = new Audio();
const playerState = {
  queue: Queue
}
audio.preload = "metadata";

const playerCreateQueue = (ids, pos) => {
  playerState.queue = queueCreate(ids, pos)
}

const playerSetMetadata = async () => {
  navigator.mediaSession.metadata = new MediaMetadata({
    title: track.title,
    artist: track.artist,
    album: track.album,
    artwork: track.art_url ? [{ src: track.art_url }] : [{ src: "" }],
  });
  navigator.mediaSession.setActionHandler("nexttrack", () => { playerPlayNext() });
  navigator.mediaSession.setActionHandler("previoustrack", () => { playerPlayPrevious() });
}


const playerScrubFromPlayerBar = (e) => {
  const el = e.currentTarget;
  const rect = el.getBoundingClientRect();
  const clickX = e.clientX - rect.left;
  const percentage = clickX / el.offsetWidth;
  const clickedValue = percentage * el.max;
  audio.currentTime = clickedValue * audio.duration;
};

const playerPause = () => {
  audio.pause();
  hydratePlayerPausedState(paused = true)
}

const playerResume = () => {
  audio.play();
  hydratePlayerPausedState(paused = false)
}

let playToken = 0;

const playerPlayCurrent = async () => {
  const myToken = ++playToken;
  const id = queueGetCurrent(playerState.queue);
  if (id === null) return;

  audio.src = `/api/tracks/${id}/audio`;
  try {
    let main = document.getElementById("main")
    main.appendChild(Loading("fetching and encoding..."))
    await audio.play();
    main.removeChild(document.getElementById("loading"))
  } catch (err) {
    // interrupted by a newer load, ignore
    if (err.name !== "AbortError") {
      alert(err);
      throw err;
    }
  }

  if (myToken !== playToken) return; // a newer play request superseded this one
  playerSetMetadata();
};

const playerPlayNext = async () => {
  playerState.queue = queueNext(playerState.queue)
  playerPlayCurrent(playerState.queue)
  hydrateQueueTableIfActive()

}

const playerPlayPrevious = async () => {
  playerState.queue = queuePrevious(playerState.queue)
  playerPlayCurrent(playerState.queue)
  hydrateQueueTableIfActive()
}

audio.addEventListener("ended", () => {
  playerPlayNext();
  hydratePlayerMetadata();
  hydrateQueueTableIfActive();
});


audio.addEventListener("play", () => {
  hydratePlayerPausedState(paused = false)
});

// 3. Add the 'pause' event listener
audio.addEventListener("pause", () => {
  hydratePlayerPausedState(paused = true)
});

audio.addEventListener('timeupdate', function() {
  // duration is NaN until metadata loads, and assigning NaN to a
  // <progress> throws, which leaves the bar stuck on the last track.
  const done = Number.isFinite(audio.duration) && audio.duration > 0
    ? audio.currentTime / audio.duration
    : 0;
  document.getElementById('playerbar-seekbar').value = done;

  function formatTime(totalSeconds) {

    if (totalSeconds != totalSeconds) {
      // Check if NaN
      return "00:00"
    }

    const minutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;

    const paddedMinutes = String(minutes).split(".")[0].padStart(2, '0');
    const paddedSeconds = String(seconds).split(".")[0].padStart(2, '0');

    return `${paddedMinutes}:${paddedSeconds}`;
  }
  document.getElementById('playerbar-duration').innerText = `${formatTime(audio.currentTime)} / ${formatTime(audio.duration)}`;
});

audio.addEventListener('emptied', () => {
  document.getElementById('playerbar-seekbar').value = 0;
  hydratePlayerMetadata();
  hydrateQueueTableIfActive();
});

