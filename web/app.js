async function extract() {
  const url = document.getElementById('urlInput').value.trim();
  const status = document.getElementById('status');
  const out = document.getElementById('out');
  out.textContent = '';
  if (!url) { status.textContent = 'Informe uma URL.'; return; }
  status.textContent = 'Extraindo...';
  try {
    const resp = await fetch(`/api/extract?url=${encodeURIComponent(url)}`);
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    const data = await resp.json();
    status.textContent = 'OK';
    out.textContent = JSON.stringify(data, null, 2);
  } catch (e) {
    status.textContent = 'Erro ao extrair: ' + e.message;
  }
}
document.getElementById('goBtn').addEventListener('click', extract);
document.getElementById('urlInput').addEventListener('keydown', (e)=>{ if(e.key==='Enter') extract(); });
