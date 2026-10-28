'use strict';
document.documentElement.classList.add('js');
const normalise = value => value.toLowerCase().trim();
let movement = 'all';
function filterList(id) {
  const list = document.getElementById(id);
  if (!list) return;
  const search = document.querySelector(`[data-search="${id}"]`);
  const query = normalise(search?.value || '');
  let visible = 0;
  for (const item of list.children) {
    const text = item.dataset.find || normalise(item.textContent);
    const match = text.includes(query) && (id !== 'lesson-list' || movement === 'all' || item.dataset.stage === movement);
    item.hidden = !match;
    if (match) visible++;
  }
  const empty = document.querySelector(`[data-empty="${id}"]`);
  if (empty) empty.hidden = visible !== 0;
}
document.querySelectorAll('[data-search]').forEach(input => input.addEventListener('input', () => filterList(input.dataset.search)));
document.querySelectorAll('[data-movement]').forEach(button => button.addEventListener('click', () => {
  movement = button.dataset.movement;
  document.querySelectorAll('[data-movement]').forEach(item => item.setAttribute('aria-pressed', String(item === button)));
  filterList('lesson-list');
}));
const index = document.querySelector('.site-index');
document.addEventListener('keydown', event => {
  if (event.key === 'Escape' && index?.open) {
    index.open = false;
    index.querySelector('summary').focus();
  }
});
document.addEventListener('click', event => {
  if (index?.open && !index.contains(event.target)) index.open = false;
});
const topLink = document.querySelector('.to-top');
const updateTop = () => topLink?.classList.toggle('visible', window.scrollY > 300);
window.addEventListener('scroll', updateTop, { passive: true });
updateTop();
const key = 'aura-teacher-reading-bookmarks-v1';
function readBookmarks() {
  try {
    const value = JSON.parse(localStorage.getItem(key) || '[]');
    return Array.isArray(value) ? [...new Set(value.filter(n => Number.isInteger(n) && n >= 1 && n <= 60))] : [];
  } catch { return []; }
}
function displayBookmarks() {
  const saved = readBookmarks();
  document.querySelectorAll('[data-bookmark]').forEach(button => {
    const active = saved.includes(Number(button.dataset.bookmark));
    button.setAttribute('aria-pressed', String(active));
    button.textContent = active ? 'Reading saved · Remove bookmark' : 'Save this reading on this device';
  });
  document.querySelectorAll('[data-progress]').forEach(node => { node.textContent = `${saved.length} reading${saved.length === 1 ? '' : 's'} saved on this device. Bookmarks are not assessments.`; });
}
document.querySelectorAll('[data-bookmark]').forEach(button => button.addEventListener('click', () => {
  const number = Number(button.dataset.bookmark);
  const saved = readBookmarks();
  const next = saved.includes(number) ? saved.filter(n => n !== number) : [...saved, number];
  try {
    localStorage.setItem(key, JSON.stringify(next));
    displayBookmarks();
    const status = document.querySelector('[data-bookmark-status]');
    if (status) status.textContent = next.includes(number) ? 'This reading is saved in this browser.' : 'The reading bookmark has been removed.';
  } catch {
    const status = document.querySelector('[data-bookmark-status]');
    if (status) status.textContent = 'This browser could not save the bookmark. You can still read every page.';
  }
}));
document.querySelector('[data-clear-bookmarks]')?.addEventListener('click', () => {
  try { localStorage.removeItem(key); displayBookmarks(); }
  catch { document.querySelector('[data-progress]').textContent = 'This browser could not change its saved readings.'; }
});
displayBookmarks();
