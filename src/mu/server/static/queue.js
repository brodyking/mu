const Queue = {
  ids: [],
  pos: 0,
};

const queueCreate = (ids = [], pos = 0) => ({
  ...Queue,
  ids,
  pos,
});

const queueIndexInBounds = (queue, index) =>
  index >= 0 && index < queue.ids.length;

const queueNext = (queue) => {
  if (queueIndexInBounds(queue, queue.pos + 1)) {
    return { ...queue, pos: queue.pos + 1 };
  }
  return { ...queue };
};

const queuePrevious = (queue) => {
  if (queueIndexInBounds(queue, queue.pos - 1)) {
    return { ...queue, pos: queue.pos - 1 };
  }
  return { ...queue };
};

const queueJumpTo = (queue, index) => {
  if (queueIndexInBounds(queue, index)) {
    return { ...queue, pos: index };
  }
  return { ...queue };
};

const queueGetCurrent = (queue) => {
  return queueIndexInBounds(queue, queue.pos) ? queue.ids[queue.pos] : null;
};

const queueGetUpcoming = (queue) => {
  return queue.ids.slice(queue.pos + 1);
};

const queueGetPast = (queue) => {
  return queue.ids.slice(0, queue.pos);
};

const queueInsert = (queue, id, pos) => {
  if (queueIndexInBounds(queue, pos)) {
    const newIds = [...queue.ids];
    newIds.splice(pos, 0, id);
    return { ...queue, ids: newIds };
  }
  return { ...queue };
};

const queueAppend = (queue, id) => {
  return { ...queue, ids: [...queue.ids, id] };
};

