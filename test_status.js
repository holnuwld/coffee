const fs = require('fs');

async function testStatus() {
  const comp = JSON.parse(fs.readFileSync('c:/cowork/coffee/competition-series-2025_full.json', 'utf8'));
  const sample = comp.slice(35, 45);
  for (const p of sample) {
    const url = `https://archerscoffee.com/products/${p.handle}`;
    const res = await fetch(url, { headers: { 'User-Agent': 'Mozilla/5.0' } });
    console.log(p.handle, '-> status:', res.status, 'content length:', (await res.text()).length);
  }
}
testStatus();
