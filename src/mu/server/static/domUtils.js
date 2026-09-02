const collectIdsFromSelector = (selector = '.data-table tr td:first-child') => {
  return Array.from(document.querySelectorAll(selector))
    .map(cell => cell.textContent.trim());
};
