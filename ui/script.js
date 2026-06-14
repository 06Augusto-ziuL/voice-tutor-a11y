const state = {
  historico: [],
  gravando: false,
  mediaRecorder: null,
  chunks: [],
  audioCtx: null
};

const messagesEl    = document.getElementById('messages');
const placeholderEl = document.getElementById('placeholder');
const textInput     = document.getElementById('text-input');
const sendBtn       = document.getElementById('send-btn');
const micBtn        = document.getElementById('mic-btn');
const playerPanel   = document.getElementById('player-panel');
const audioEl       = document.getElementById('audio-el');
const playBtn       = document.getElementById('play-btn');
const progressBar   = document.getElementById('progress-bar');
const timeCur       = document.getElementById('time-cur');
const timeTot       = document.getElementById('time-tot');
const transPreview  = document.getElementById('transcription-preview');

const SILENCE_THRESHOLD = 15; // Ajuste de sensibilidade do volume (0-255)
const SILENCE_MS = 1500;      // Milissegundos em silêncio para interromper

function adicionarMensagem(role, texto) {
  placeholderEl.style.display = 'none';
  const div = document.createElement('div');
  div.classList.add('msg', role);
  div.textContent = texto;
  messagesEl.appendChild(div);
  messagesEl.scrollTop = messagesEl.scrollHeight;
  return div;
}

function adicionarLoading() {
  const div = document.createElement('div');
  div.classList.add('msg', 'assistant', 'loading');
  div.innerHTML = '<span></span><span></span><span></span>';
  messagesEl.appendChild(div);
  messagesEl.scrollTop = messagesEl.scrollHeight;
  return div;
}

async function enviarMensagem(textoOverride) {
  const texto = (textoOverride ?? textInput.value).trim();
  if (!texto) return;

  textInput.value = '';
  autoResize(textInput);
  sendBtn.disabled = true;
  transPreview.style.display = 'none';

  adicionarMensagem('user', texto);
  const loadingEl = adicionarLoading();

  try {
    const res = await fetch('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ pergunta: texto, historico: state.historico }),
    });

    if (!res.ok) throw new Error(`Erro ${res.status}`);
    const data = await res.json();

    loadingEl.remove();
    adicionarMensagem('assistant', data.resposta);

    state.historico.push({ role: 'user', content: texto });
    state.historico.push({ role: 'assistant', content: data.resposta });

    await carregarAudio();

  } catch (err) {
    loadingEl.remove();
    adicionarMensagem('assistant', `Erro ao conectar: ${err.message}`);
  } finally {
    sendBtn.disabled = false;
  }
}

function usarSugestao(texto) {
  textInput.value = texto;
  textInput.focus();
}

function onKeyDown(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    enviarMensagem();
  }
}

function autoResize(el) {
  el.style.height = 'auto';
  el.style.height = Math.min(el.scrollHeight, 120) + 'px';
}

async function toggleMic() {
  if (state.gravando) {
    await pararGravacao();
  } else {
    await iniciarGravacao();
  }
}

async function iniciarGravacao() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    state.chunks = [];

    const mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
      ? 'audio/webm;codecs=opus'
      : '';
    state.mediaRecorder = mimeType
      ? new MediaRecorder(stream, { mimeType })
      : new MediaRecorder(stream);

    state.mediaRecorder.ondataavailable = e => {
      if (e.data && e.data.size > 0) state.chunks.push(e.data);
    };

    state.mediaRecorder.onstop = () => {
      stream.getTracks().forEach(t => t.stop());
      if (state.audioCtx) {
        state.audioCtx.close();
        state.audioCtx = null;
      }
    };

    state.mediaRecorder.start(250);
    state.gravando = true;

    micBtn.classList.add('recording');
    micBtn.title = 'Parar gravação';
    micBtn.textContent = '\u23F9\uFE0F';

    transPreview.textContent = 'Gravando... Pode falar!';
    transPreview.style.display = 'block';

    monitorarSilencioWebAudio(stream);

  } catch (err) {
    alert('Não foi possível acessar o microfone: ' + err.message);
  }
}

function monitorarSilencioWebAudio(stream) {
  state.audioCtx = new (window.AudioContext || window.webkitAudioContext)();
  const analyser = state.audioCtx.createAnalyser();
  analyser.fftSize = 256;
  const source = state.audioCtx.createMediaStreamSource(stream);
  source.connect(analyser);

  const dataArray = new Uint8Array(analyser.frequencyBinCount);
  let tempoSilencioIniciado = null;

  function verificar() {
    if (!state.gravando) return;

    analyser.getByteFrequencyData(dataArray);
    let soma = 0;
    for (let i = 0; i < dataArray.length; i++) soma += dataArray[i];
    let media = soma / dataArray.length;

    if (media < SILENCE_THRESHOLD) {
      if (!tempoSilencioIniciado) {
        tempoSilencioIniciado = Date.now();
      } else if (Date.now() - tempoSilencioIniciado > SILENCE_MS) {
        pararGravacao(); 
        return; 
      }
    } else {
      tempoSilencioIniciado = null; 
    }
    requestAnimationFrame(verificar);
  }
  
  verificar();
}

function pararGravacao() {
  if (!state.mediaRecorder || !state.gravando) return;

  return new Promise(resolve => {
    state.mediaRecorder.addEventListener('stop', () => {
      processarAudioGravado();
      resolve();
    }, { once: true });

    state.gravando = false;
    micBtn.classList.remove('recording');
    micBtn.title = 'Gravar áudio';
    micBtn.textContent = '\uD83C\uDFA4';
    transPreview.textContent = 'Processando...';

    state.mediaRecorder.stop(); 
  });
}

async function processarAudioGravado() {
  const mimeType = state.mediaRecorder?.mimeType || 'audio/webm';
  const blob = new Blob(state.chunks, { type: mimeType });

  if (blob.size < 500) {
    transPreview.textContent = 'Gravação muito curta ou vazia.';
    setTimeout(() => transPreview.style.display = 'none', 3000);
    return;
  }

  const ext = mimeType.includes('ogg') ? 'gravacao.ogg' : 'gravacao.webm';
  const formData = new FormData();
  formData.append('arquivo', blob, ext);

  try {
    const res = await fetch('/transcrever', { method: 'POST', body: formData });
    if (!res.ok) throw new Error(`Erro ${res.status}`);
    const data = await res.json();
    const texto = data.texto.trim();

    if (texto) {
      transPreview.style.display = 'none';
      enviarMensagem(texto); 
    } else {
      transPreview.textContent = 'Nada transcrito.';
      setTimeout(() => transPreview.style.display = 'none', 3000);
    }
  } catch (err) {
    transPreview.textContent = `Erro na transcrição: ${err.message}`;
  }
}

async function carregarAudio() {
  audioEl.src = `/audio?t=${Date.now()}`;
  audioEl.load();

  audioEl.oncanplay = () => {
    abrirPlayer();
    timeTot.textContent = formatarTempo(audioEl.duration);
    audioEl.play().catch(() => {});
    atualizarPlayBtn(true);
  };
}

function abrirPlayer() {
  playerPanel.classList.remove('hidden');
}

function togglePlay() {
  if (audioEl.paused) {
    audioEl.play();
    atualizarPlayBtn(true);
  } else {
    audioEl.pause();
    atualizarPlayBtn(false);
  }
}

function atualizarPlayBtn(tocando) {
  playBtn.textContent = tocando ? '⏸' : '▶';
}

function seekAudio(val) {
  if (audioEl.duration) {
    audioEl.currentTime = (val / 100) * audioEl.duration;
  }
}

function setSpeed(val) {
  audioEl.playbackRate = parseFloat(val);
}

function formatarTempo(seg) {
  if (!seg || isNaN(seg)) return '0:00';
  const m = Math.floor(seg / 60);
  const s = Math.floor(seg % 60).toString().padStart(2, '0');
  return `${m}:${s}`;
}

audioEl.addEventListener('timeupdate', () => {
  if (audioEl.duration) {
    progressBar.value = (audioEl.currentTime / audioEl.duration) * 100;
    timeCur.textContent = formatarTempo(audioEl.currentTime);
  }
});

audioEl.addEventListener('ended', () => {
  atualizarPlayBtn(false);
  progressBar.value = 0;
  timeCur.textContent = '0:00';
});

(function desenharOnda() {
  const canvas = document.getElementById('waveform-canvas');
  const ctx = canvas.getContext('2d');
  let frame;

  function resize() {
    canvas.width = canvas.offsetWidth * window.devicePixelRatio;
    canvas.height = canvas.offsetHeight * window.devicePixelRatio;
    ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
  }

  window.addEventListener('resize', resize);
  resize();

  let t = 0;
  function draw() {
    const w = canvas.offsetWidth;
    const h = canvas.offsetHeight;
    ctx.clearRect(0, 0, w, h);

    const playing = !audioEl.paused && !audioEl.ended;
    const bars = 48;
    const barW = w / bars;

    for (let i = 0; i < bars; i++) {
      const progress = audioEl.duration ? audioEl.currentTime / audioEl.duration : 0;
      const done = (i / bars) <= progress;
      const amp = playing
        ? 0.3 + 0.7 * Math.abs(Math.sin(i * 0.5 + t * 0.08))
        : 0.15 + 0.05 * Math.abs(Math.sin(i * 0.6));

      const bh = Math.max(4, amp * h * 0.75);
      const x = i * barW + barW * 0.2;
      const bWidth = barW * 0.55;
      const y = (h - bh) / 2;

      ctx.fillStyle = done ? '#a855f7' : '#2a2d4a';
      ctx.beginPath();
      ctx.roundRect(x, y, bWidth, bh, 2);
      ctx.fill();
    }

    t++;
    frame = requestAnimationFrame(draw);
  }

  draw();
})();