const API_KEY = 'changeme';

async function predict() {
  const text = document.getElementById('input-text').value.trim();
  if (!text) return;

  const btn = document.getElementById('predict-btn');
  btn.disabled = true;
  btn.textContent = 'Analyzing…';

  try {
    const res = await fetch('/api/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-API-Key': API_KEY },
      body: JSON.stringify({ text }),
    });
    const data = await res.json();

    const card = document.getElementById('result-card');
    card.style.display = 'block';

    const label = document.getElementById('pred-label');
    label.textContent = data.prediction;
    label.className = 'badge ' + data.prediction;

    document.getElementById('pred-conf').textContent =
      (data.confidence * 100).toFixed(1) + '%';
    document.getElementById('pred-probs').textContent =
      JSON.stringify(data.probabilities, null, 2);
  } finally {
    btn.disabled = false;
    btn.textContent = 'Analyze';
    loadPredictions();
  }
}

async function loadPredictions() {
  try {
    const res = await fetch('/api/sentiments?limit=10');
    const data = await res.json();
    const tbody = document.querySelector('#predictions-table tbody');
    tbody.innerHTML = (data.items || []).map(item => `
      <tr>
        <td>${item.text_original}</td>
        <td><span class="badge ${item.prediction}">${item.prediction}</span></td>
        <td>${(item.confidence * 100).toFixed(1)}%</td>
        <td>${item.ingested_at}</td>
      </tr>
    `).join('');
  } catch (e) {
    console.error('Failed to load predictions', e);
  }
}

document.getElementById('predict-btn').addEventListener('click', predict);
document.getElementById('input-text').addEventListener('keydown', e => {
  if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); predict(); }
});

loadPredictions();
