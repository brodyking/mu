const audio = new Audio();
const playerState = {
  queue: Queue
}
audio.preload = "metadata";

const playerCreateQueue = (ids, pos) => {
  playerState.queue = queueCreate(ids, pos)
}

const playerSetMetadata = async () => {
  track = await getTrackById(queueGetCurrent(playerState.queue))

  navigator.mediaSession.metadata = new MediaMetadata({
    title: track.title,
    artist: track.artist,
    album: track.album,
    artwork: track.art_url ? [{ src: track.art_url }] : [{ src: "" }],
  });
  navigator.mediaSession.setActionHandler("nexttrack", () => { playerPlayNext() });
  navigator.mediaSession.setActionHandler("previoustrack", () => { playerPlayPrevious() });

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

  document.getElementById("playerbar-pause").classList.remove("d-none")
  document.getElementById("playerbar-resume").classList.add("d-none")

}

const playerControlsSetState = (paused) => {
  if (paused) {
    document.getElementById("playerbar-pause").classList.add("d-none")
    document.getElementById("playerbar-resume").classList.remove("d-none")
  } else {
    document.getElementById("playerbar-pause").classList.remove("d-none")
    document.getElementById("playerbar-resume").classList.add("d-none")
  }
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
  playerControlsSetState(paused = true)
}

const playerResume = () => {
  audio.play();
  playerControlsSetState(paused = false)
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
  hydrateQueueTableIfActive()
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
  hydrateQueueTableIfActive()
});


audio.addEventListener("play", () => {
  playerControlsSetState(paused = false)
});

// 3. Add the 'pause' event listener
audio.addEventListener("pause", () => {
  playerControlsSetState(paused = true)
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
});

