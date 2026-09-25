const messages = document.querySelector('#messages');
const input = document.querySelector('#message-input');
const composer = document.querySelector('#composer');
const statusText = document.querySelector('#status-text');
const logCount = document.querySelector('#log-count');
const micButton = document.querySelector('#mic-button');
const avatarCore = document.querySelector('.avatar-core');
let count = 0;

function setStatus(state) {
  const normalized = state.toLowerCase();
  statusText.textContent = normalized.toUpperCase();
  avatarCore.classList.toggle('is-speaking', normalized === 'speaking');
  avatarCore.classList.toggle('is-thinking', normalized === 'thinking');
}

document.querySelector('#avatar-image').addEventListener('error', (event) => {
  event.currentTarget.hidden = true;
  avatarCore.classList.add('using-fallback');
});
document.querySelector('#avatar-image').addEventListener('load', () => avatarCore.classList.remove('using-fallback'));

function addMessage(role, text) {
  const empty = messages.querySelector('.empty-state');
  if (empty) empty.remove();
  const item = document.createElement('article');
  item.className = `message ${role}`;
  item.innerHTML = `<div class="message-meta">${role === 'user' ? 'YOU' : 'JARVIS'}</div><div class="message-text"></div>`;
  item.querySelector('.message-text').textContent = text;
  messages.appendChild(item);
  messages.scrollTop = messages.scrollHeight;
  count += 1;
  logCount.textContent = String(count).padStart(2, '0');
}

async function sendMessage(message) {
  if (!message) return;
  addMessage('user', message);
  input.value = '';
  setStatus('thinking');
  try {
    const response = await fetch('/api/message', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ message }) });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Request failed');
    addMessage('jarvis', data.answer);
  } catch (error) {
    addMessage('jarvis', `Connection error: ${error.message}`);
  } finally {
    setStatus('listening');
    input.focus();
  }
}

composer.addEventListener('submit', (event) => { event.preventDefault(); sendMessage(input.value.trim()); });
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
if (SpeechRecognition) {
  const recognition = new SpeechRecognition();
  recognition.lang = 'en-US';
  recognition.interimResults = false;
  micButton.addEventListener('click', () => {
    setStatus('listening');
    micButton.textContent = '◌';
    recognition.start();
  });
  recognition.onresult = (event) => sendMessage(event.results[0][0].transcript);
  recognition.onerror = () => { setStatus('listening'); };
  recognition.onend = () => { micButton.textContent = '◉'; };
} else {
  micButton.title = 'Browser speech input is unavailable';
  micButton.addEventListener('click', () => { input.placeholder = 'Use the terminal microphone loop for voice input'; input.focus(); });
}
setInterval(async () => { try { const response = await fetch('/api/state'); const state = await response.json(); setStatus(state.state); } catch (_) {} }, 500);
