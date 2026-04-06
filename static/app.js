async function fetchJSON(url, options = {}) {
  const response = await fetch(url, options);
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail || 'Request failed');
  }
  return data;
}

function tokenHeaders() {
  return {
    'Content-Type': 'application/json',
    'X-API-Token': document.getElementById('token').value
  };
}

async function loadAssets() {
  const assets = await fetchJSON('/api/assets');
  const container = document.getElementById('assets');
  container.innerHTML = assets.map(asset => `
    <div class="asset">
      <strong>${asset.name}</strong> — ${asset.host} (${asset.environment})
      <div class="actions">
        <button onclick="runHealth(${asset.id})">Health Check</button>
        <button onclick="runScan(${asset.id})">Port Scan</button>
      </div>
    </div>
  `).join('') || '<p>No assets yet.</p>';
}

async function loadResults() {
  const results = await fetchJSON('/api/results');
  const container = document.getElementById('results');
  container.innerHTML = results.map(row => `
    <div class="result">
      <strong>${row.scan_type}</strong> on asset #${row.asset_id}<br/>
      Status: ${row.status}<br/>
      Details: ${row.details}
    </div>
  `).join('') || '<p>No results yet.</p>';
}

async function createAsset() {
  try {
    await fetchJSON('/api/assets', {
      method: 'POST',
      headers: tokenHeaders(),
      body: JSON.stringify({
        name: document.getElementById('name').value,
        host: document.getElementById('host').value,
        environment: document.getElementById('environment').value,
        owner: document.getElementById('owner').value,
      })
    });
    await loadAssets();
  } catch (error) {
    alert(error.message);
  }
}

async function runHealth(id) {
  try {
    await fetchJSON(`/api/assets/${id}/health-check`, {
      method: 'POST', headers: tokenHeaders()
    });
    await loadResults();
  } catch (error) {
    alert(error.message);
  }
}

async function runScan(id) {
  try {
    await fetchJSON(`/api/assets/${id}/port-scan`, {
      method: 'POST', headers: tokenHeaders()
    });
    await loadResults();
  } catch (error) {
    alert(error.message);
  }
}

loadAssets();
loadResults();
