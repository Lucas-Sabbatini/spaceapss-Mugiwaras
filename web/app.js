async function extract() {
  const url = document.getElementById('urlInput').value.trim();
  const status = document.getElementById('status');
  const out = document.getElementById('out');
  out.textContent = '';
  if (!url) { status.textContent = 'Informe uma URL.'; return; }
  status.textContent = 'Extraindo...';
  try {
    // Detecta se está rodando em Codespaces e ajusta a URL do backend
    // URL fixa do backend Azure Functions no Codespace fornecido
    const backendUrl = 'https://humble-halibut-rvx7r4q7g6357j4-7071.app.github.dev';
    const resp = await fetch(`${backendUrl}/api/extract?url=${encodeURIComponent(url)}`);
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
